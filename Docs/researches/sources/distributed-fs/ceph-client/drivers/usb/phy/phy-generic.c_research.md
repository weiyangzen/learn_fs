<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.c

## Purpose

`phy-generic.c` implements the generic "NOP" USB transceiver. It provides a minimal legacy `usb_phy` for boards where PHY hardware is autonomous or controlled only by a clock, reset GPIO, VCC regulator, optional VBUS regulator, and optional VBUS-detect GPIO.

## Important APIs, Types, and Functions

Exported helpers are `usb_phy_generic_register()`, `usb_phy_generic_unregister()`, `usb_gen_phy_init()`, `usb_gen_phy_shutdown()`, and `usb_phy_gen_create_phy()`. OTG operations include `nop_set_suspend()`, `nop_set_vbus()`, `nop_set_peripheral()`, and `nop_set_host()`. The platform driver uses `usb_phy_generic_probe()` and `usb_phy_generic_remove()`.

## Control Flow

`usb_phy_gen_create_phy()` reads optional `clock-frequency`, reset GPIO, VBUS-detect GPIO, `main_clk`, `vcc`, and exclusive `vbus` regulator; allocates `usb_otg`; and initializes generic PHY/OTG callbacks. Probe optionally requests threaded VBUS GPIO IRQ, initializes OTG state from GPIO, sets init/shutdown callbacks, registers the PHY, stores drvdata, and marks wakeup capability from `wakeup-source`.

Init enables VCC and clock and toggles reset. Shutdown asserts reset, disables clock, and disables VCC. VBUS IRQ updates `last_event`, OTG state, and notifiers when VBUS changes. `set_vbus` controls the VBUS regulator for host power when present.

## State and Persistence Behavior

State is `struct usb_phy_generic`: clock, regulators, GPIOs, VBUS state, VBUS regulator enabled flag, and current draw. Hardware state is limited to reset GPIO level, regulator enable/load, clock enable, and VBUS event state.

## Dependencies and Integration Points

It depends on platform devices, device properties, GPIO descriptors, clocks, regulator framework, IRQs, and legacy USB PHY/OTG registration. Other drivers, such as Keystone and AM335x, reuse `usb_phy_gen_create_phy()`.

## Risks and Test Signals

Risks include regulator enable/disable imbalance on error paths, VBUS IRQ before gadget registration, optional-resource error handling, and wakeup interaction with suspend regulator control. Tests should cover no-resource NOP PHY, reset timing, clock-frequency setting, VCC failure, VBUS GPIO rising/falling, vbus regulator set_vbus, host/gadget registration, wakeup-source property, and removal with VBUS regulator enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-generic.c -->
