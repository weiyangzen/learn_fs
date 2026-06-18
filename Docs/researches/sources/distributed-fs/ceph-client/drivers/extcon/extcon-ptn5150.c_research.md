# sources/distributed-fs/ceph-client/drivers/extcon/extcon-ptn5150.c

## Purpose
NXP PTN5150 USB Type-C CC logic driver that reports extcon USB/USB_HOST state and also drives Type-C orientation and USB role-switch integration. It handles attach/detach interrupts from an I2C CC controller and optionally drives a VBUS GPIO.

## Important APIs, Types, and Functions
`struct ptn5150_info` holds extcon, I2C/regmap, optional INT/VBUS GPIOs, IRQ work, mutex, `typec_switch`, and `usb_role_switch`. `ptn5150_check_state()` reads `PTN5150_REG_CC_STATUS`, derives orientation, attachment role, VBUS detection, extcon state, VBUS GPIO output, and USB role. `ptn5150_irq_work()` clears interrupt status, calls `ptn5150_check_state()` for attach, and resets extcon, VBUS, USB role, and orientation for detach. `ptn5150_init_dev_type()` reads device ID and clears stale interrupts. Probe wires GPIOs/IRQ, extcon properties, Type-C switch, role switch, cleanup action, and initial state.

## Control Flow
Probe requires a DT node, gets optional `vbus` output GPIO and either an I2C IRQ or `int` GPIO IRQ, registers a falling-edge threaded IRQ, allocates extcon, declares VBUS and polarity capabilities, clears stale interrupts, resolves the optional `connector` child to an orientation switch, resolves a USB role switch, installs a cleanup action, and then calls `ptn5150_check_state()` under the mutex for cold-plug state. The IRQ top-level handler schedules work. Work reads interrupt status; any attach bit triggers full CC-state classification, while non-attach interrupt status is treated as detach cleanup.

## State and Persistence
State is intentionally mostly hardware-derived. The driver does not cache the last role except through extcon/typec/role-switch frameworks. Work is serialized by `mutex`. The cleanup action cancels pending work and releases role/orientation switches. Hardware interrupt status registers clear on read.

## Dependencies and Integration Points
Uses regmap over I2C, GPIO descriptors, extcon provider properties, USB role switch, Type-C mux/switch APIs, OF fwnodes, and devm cleanup. The optional connector child can supply both orientation and role switch references.

## Risks
`gpiod_set_value_cansleep(info->vbus_gpiod, ...)` is called even when the VBUS GPIO is absent and set to NULL, which is only safe if the GPIO helper tolerates NULL for this API on the target kernel. Role/orientation switch acquisition is mandatory once attempted; missing role switch can fail probe. Detach handling treats any interrupt status without attach bit as detach, so unrecognized interrupt bits clear the connection. Error returns from `usb_role_switch_set_role()` and `typec_switch_set()` are logged but extcon state may already have changed.

## Test Signals
Exercise CC1 and CC2 orientation, DFP-attached device mode, UFP-attached host mode, detach cleanup, absent and present VBUS GPIO, I2C IRQ versus INT GPIO path, role switch failures, orientation switch failures, and resume scheduling a pending interrupt check.
