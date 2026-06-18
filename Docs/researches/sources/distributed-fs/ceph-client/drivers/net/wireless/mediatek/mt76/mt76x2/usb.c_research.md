# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb.c

Purpose: Linux USB driver binding for MT76x2U devices. It declares USB IDs, allocates the mt76 device, performs USB initialization, validates ASIC revision, registers mac80211 hardware, and handles disconnect and power management.

Important APIs: `mt76x2u_probe`, `mt76x2u_disconnect`, `mt76x2u_suspend`, `mt76x2u_resume`, the `mt76x2u_driver` `usb_driver`, and the static `mt76_driver_ops` passed to `mt76_alloc_device`.

Control flow: probe gets and resets the USB device, stores interface data, initializes MCU and mt76 USB transport, reads `MT_ASIC_VERSION`, rejects non-MT76x2 ASICs, then calls `mt76x2u_register_device`. Failure unwinds queues, device memory, interface data, and USB refcount. Disconnect marks removal, unregisters mac80211, cleans hardware, and releases the USB device. Resume restarts RX and reinitializes hardware.

State and persistence: persistent matching comes from `MODULE_DEVICE_TABLE`; runtime state is the USB interface data pointer, `MT76_REMOVED`, initialized queues, firmware identity, and mac80211 registration state.

Dependencies and integration: integrates with USB core, module firmware declarations, mt76 USB helpers, mt76x02 common callbacks for TX/RX/station handling, and `mt76x2u_ops` from `usb_main.c`.

Risks: probe error unwinding must stay symmetric with later initialization changes. `usb_reset_device` can disturb composite devices if assumptions change. Resume calls full hardware init after RX resume, so firmware or register failures must leave queues safely stopped.

Test signals: plug/unplug supported IDs, unsupported ASIC rejection, suspend/resume and reset_resume, firmware-missing failures, queue cleanup after failed probe, and `lsusb`/dmesg ASIC revision reporting.
