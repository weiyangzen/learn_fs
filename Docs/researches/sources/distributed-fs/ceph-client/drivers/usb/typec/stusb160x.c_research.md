# sources/distributed-fs/ceph-client/drivers/usb/typec/stusb160x.c

## Purpose

`stusb160x.c` is the STUSB160x Type-C controller driver. It configures port mode/current advertisement, registers a Type-C port, manages VBUS/VCONN regulators, handles attach/detach interrupts, and updates USB role-switch state.

## Important APIs, Types, and Functions

`struct stusb160x` stores regmap, regulators (`vdd`, `vsys`, `vconn`, selected main supply), Type-C port/capabilities/partner, port type, power opmode, VBUS state, and USB role switch. Important functions are `stusb160x_get_caps()`, `stusb160x_get_fw_caps()`, `stusb160x_chip_init()`, `stusb160x_attach()`, `stusb160x_detach()`, `stusb160x_irq_handler()`, `stusb160x_irq_init()`, suspend/resume handlers, and regmap readable/writeable/volatile/precious callbacks.

## Control Flow

Probe initializes regmap and supplies, gets the `connector` fwnode, purges fw_devlink links for legacy DT connector nodes, selects main supply, reads chip capabilities, applies optional firmware overrides, initializes chip mode and interrupt masks, registers the Type-C port, sets the initial power opmode, and either requests an IRQ plus role switch or enables source VBUS permanently when no IRQ exists. IRQ handling checks alert/status registers and calls attach or detach on CC attach transitions. Resume synchronizes regcache, reconciles missed attach/detach state, and unmasks CC interrupts.

## State and Persistence Behavior

Driver state tracks registered partner pointer, selected port type/opmode, whether VBUS is currently enabled, and regulator handles. Hardware registers are cached via maple regcache for nonvolatile register state. Attach state is not persisted and is resynchronized from status on init/resume.

## Dependencies and Integration Points

It depends on I2C regmap, regulators, Type-C class, USB role-switch, firmware connector properties, PM callbacks, and STUSB160x register semantics. It integrates VBUS sourcing/sinking and partner/accessory information into Linux Type-C objects.

## Risks and Test Signals

Risks include limited PD support (`usb_pd = false`), duplicate or missing partner handling if attach transitions are noisy, optional regulator combinations, role-switch only acquired when IRQ exists, VCONN disable paths depending on register reads, and wake/resume attach changes. Test signals include source/sink/DRP firmware overrides, current advertisement programming, attach/detach IRQs for normal/debug/audio accessories, VBUS/VCONN regulator enable and unwind, no-IRQ source behavior, suspend/resume attach reconciliation, and regcache synchronization.
