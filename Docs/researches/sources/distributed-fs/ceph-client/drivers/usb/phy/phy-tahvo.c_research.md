<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tahvo.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tahvo.c

## Purpose

`phy-tahvo.c` is the Tahvo USB transceiver driver used by Nokia/Retu-Tahvo platforms. It registers a legacy USB PHY, exposes host/peripheral mode control through sysfs, reports VBUS through sysfs and extcon, controls Tahvo USB registers, and connects/disconnects gadget or host state on VBUS changes.

## Important APIs, Types, and Functions

`struct tahvo_usb` stores platform device, USB PHY, VBUS state, mutex, interface clock, IRQ, selected mode, and extcon device. Important functions are `check_vbus_state()`, `tahvo_usb_become_host()`, `tahvo_usb_stop_host()`, `tahvo_usb_become_peripheral()`, `tahvo_usb_stop_peripheral()`, `tahvo_usb_power_off()`, `tahvo_usb_set_suspend()`, `tahvo_usb_set_host()`, `tahvo_usb_set_peripheral()`, `tahvo_usb_vbus_interrupt()`, sysfs `otg_mode` handlers, `tahvo_usb_probe()`, and `tahvo_usb_remove()`.

## Control Flow

Probe allocates state and `usb_otg`, selects default mode from Kconfig, enables the optional interface clock, reads initial VBUS, registers extcon cables, powers the transceiver off, initializes PHY/OTG callbacks, registers the USB2 PHY, stores drvdata, and requests a threaded VBUS IRQ. Host/peripheral set callbacks bind or unbind host/gadget and power the transceiver according to the selected sysfs mode. `otg_mode_store()` switches mode, stopping the previous role and either powering into the new role if a host/gadget is present or powering off. VBUS IRQ serializes through a mutex and updates gadget connection, OTG state, USB PHY events, extcon state, and sysfs notification.

## State and Persistence Behavior

Runtime state is in `tahvo_usb`, extcon, PHY/OTG pointers, and selected mode. Hardware state persists in Tahvo `USBR` register bits controlling host/peripheral switches, suspend, regulator output, and mode. The selected mode is not file-backed; it resets on driver reload.

## Dependencies and Integration Points

The driver depends on Retu MFD register access, extcon provider APIs, legacy USB PHY/OTG, USB gadget VBUS helpers, platform IRQs, sysfs device groups, and an optional `usb_l4_ick` clock.

## Risks and Test Signals

Risks include sysfs `vbus_show()` notifying `"vbus_state"` while the attribute is named `vbus`, `clk_enable()` without prepare, missing error check for `usb_add_phy()` paths beyond return, and races among sysfs mode changes, IRQ, and host/gadget callbacks mitigated only by `serialize`. Tests should cover default host/peripheral builds, sysfs mode changes with and without host/gadget, VBUS IRQ connect/disconnect, extcon state updates, suspend bit toggling, clock absent/present, remove with IRQ active, and sysfs notification behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-tahvo.c -->
