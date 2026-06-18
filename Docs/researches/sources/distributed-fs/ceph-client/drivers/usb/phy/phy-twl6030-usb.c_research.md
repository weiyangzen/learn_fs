<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-twl6030-usb.c -->
# sources/distributed-fs/ceph-client/drivers/usb/phy/phy-twl6030-usb.c

## Purpose
TWL6030 USB transceiver companion for OMAP MUSB. It detects VBUS and ID events through TWL I2C registers, controls the USB LDO and VBUS boost path, and reports link state to MUSB through `musb_mailbox()`.

## Important APIs, Types, And Functions
`struct twl6030_usb` stores the `phy_companion`, regulator, two IRQs, delayed initial-status work, VBUS work, `linkstat`, `asleep`, and `vbus_enable`. `twl6030_writeb()`/`twl6030_readb()` wrap TWL I2C. `twl6030_start_srp()` pulses SRP. `twl6030_set_vbus()` schedules `otg_set_vbus_work()`. `twl6030_usb_irq()` handles VBUS, `twl6030_usbotg_irq()` handles ID, and `vbus_show()` exposes sysfs status.

## Control Flow
Probe requires DT, gets two IRQs, installs comparator callbacks with `omap_usb2_set_comparator()`, initializes the LDO/regulator/comparator bits, requests threaded IRQs, unmasks TWL interrupts, and schedules initial status work. IRQs read TWL status, update `linkstat`, enable/disable `usb3v3`, call `musb_mailbox()`, and notify sysfs. Remove cancels work, masks interrupts, frees IRQs, and releases the regulator.

## State And Persistence
State is `linkstat`, `asleep`, `vbus_enable`, regulator enablement, and TWL USB/charger/ID register programming. VBUS drive is deferred to work so atomic contexts do not perform I2C writes.

## Dependencies And Integration Points
Depends on TWL MFD I2C/interrupt helpers, regulator core, MUSB mailbox status values, OMAP USB2 comparator registration, platform IRQs, and `ti,twl6030-usb`.

## Risks
IRQ handlers update `linkstat` without the sysfs spinlock, so reads are best-effort. Negative I2C read errors are returned through a `u8` helper. Mailbox or regulator failures can desynchronize `linkstat` and hardware state. Delayed work calls IRQ handlers directly, making teardown ordering important.

## Test Signals
VBUS attach/detach, ID-ground changes, SRP, VBUS drive callback, mailbox failures, regulator failures, sysfs `vbus`, probe deferral, and remove while delayed work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/phy/phy-twl6030-usb.c -->
