# sources/distributed-fs/ceph-client/drivers/phy/ti/phy-twl4030-usb.c

## Purpose
TWL4030/TPS65950 USB transceiver driver for OMAP OTG. It manages TWL USB registers, USB LDO regulators, ULPI mode, VBUS/ID IRQ detection, MUSB mailbox notifications, runtime PM autosuspend, generic PHY, and legacy `usb_phy`.

## APIs, Flow, And State
`struct twl4030_usb` stores legacy PHY, regulators, IRQ/link state, connection atomic, pending mailbox flag, runtime flags, and delayed ID workaround work. Probe reads `usb_mode`, creates generic PHY/provider, initializes LDO/regulator state, registers legacy PHY and `vbus` sysfs, enables runtime PM, requests IRQ, and optionally creates a legacy lookup. Runtime resume enables regulators, powers PHY, enables clock bits, opens I2C access, sets ULPI mode, closes access, and waits 50 ms. IRQ reads PM hardware conditions, classifies VBUS/ID, manages runtime PM references, calls `musb_mailbox()`, schedules ID workaround polling, and notifies sysfs.

## Dependencies And Integration
Depends on TWL MFD I2C helpers, regulators, generic PHY, legacy USB PHY, MUSB mailbox, runtime PM, sysfs, platform IRQ, and delayed work.

## Risks And Tests
Several I2C writes ignore errors. Probe uses `err` after optional platform-data lookup without clear initialization in pure DT flow. Ordering is complex across IRQ/runtime PM/regulators. Test DT and pdata probe, regulator sequencing, runtime suspend/resume, VBUS/ID IRQs, mailbox retry, sysfs updates, system sleep, and remove cleanup.
