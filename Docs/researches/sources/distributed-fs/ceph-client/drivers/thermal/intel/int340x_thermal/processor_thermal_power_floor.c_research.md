# sources/distributed-fs/ceph-client/drivers/thermal/intel/int340x_thermal/processor_thermal_power_floor.c

## Purpose

`processor_thermal_power_floor.c` exposes and notifies the processor thermal power-floor condition, where hardware has reduced power to a minimum possible level.

## Important APIs, Types, and Functions

Exports include `proc_thermal_read_power_floor_status()`, `proc_thermal_power_floor_set_state()`, `proc_thermal_power_floor_get_state()`, `proc_thermal_check_power_floor_intr()`, and `proc_thermal_power_floor_intr_callback()`. It reads status and interrupt-active bits from `SOC_WT_RES_INT_STATUS_OFFSET`, and enables interrupt reporting via `processor_thermal_mbox_interrupt_config()`.

## Control Flow

Userspace toggles reporting through the common `power_limits/power_floor_enable` sysfs attribute. Enabling/disabling is serialized by `pf_lock` and updates a global `enable_state`. IRQ top-half checks the active bit; threaded callback sends `sysfs_notify()` for `power_limits/power_floor_status`.

## State and Persistence Behavior

`enable_state` is static global driver state, while hardware status is read from MMIO. Interrupt configuration persists in mailbox-controlled hardware registers until disabled or reset.

## Dependencies and Integration Points

It depends on the processor thermal mailbox, PCI device conversion from `proc_priv->dev`, common power-limit sysfs group, and the newer PCI IRQ path.

## Risks and Test Signals

Risks include global enable state across possible devices, no local check for feature presence in callbacks, and notification depending on threaded IRQ clearing elsewhere. Test signals include sysfs enable idempotence, mailbox failure propagation, interrupt-active check from IRQ context, and `sysfs_notify()` on power-floor transitions.
