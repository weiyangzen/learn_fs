# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb.c

Purpose: USB bus frontend for MT7663U devices. It implements USB register access, bulk copy, probe/disconnect, queue setup, and USB suspend/resume.

Important APIs and functions: `mt7615_device_table[]` matches two MT7663 USB IDs. `mt7663u_rr()`, `mt7663u_wr()`, `mt7663u_rmw()`, and `mt7663u_copy()` perform vendor-request register access under `usb_ctrl_mtx`. `mt7663u_stop()` overrides mac80211 stop for USB, canceling ROC/scan/MAC work and stopping TX. `mt7663u_probe()` clones ops, resets USB device, initializes mt76 USB, reads revision, powers on MCU if needed, allocates MCU/data queues, and enters shared USB/SDIO registration. PM callbacks stop/resume RX/TX and coordinate firmware HIF suspend.

Control flow: USB probe allocates device state, takes a USB device reference, resets hardware, sets interface drvdata, initializes USB bus ops, handles firmware power state, allocates queues, then calls `mt7663_usb_sdio_register_device()`. Disconnect unregisters hw, cleans queues, clears drvdata/ref, and frees mt76 state.

State and persistence: Tracks USB interface drvdata, USB device refcount, queue allocation, power-off flag, running/initialized bits, worker/work cancellation state, and firmware HIF suspend. No host persistence; firmware blobs are declared.

Dependencies: Linux USB APIs, mt76 USB helpers, shared USB/SDIO helpers, mt7663 USB MCU init/power-on, Connac firmware suspend, and register definitions.

Risks: Vendor register access must be serialized. Probe error paths must release USB refs and queue resources. Power-on polling currently returns 0 after timeout path assignment unless `ret` is propagated carefully in future edits. Stop/disconnect must cancel delayed work before freeing device.

Test signals: USB enumeration, register read/write over vendor requests, firmware power-on/load, queue allocation, traffic, disconnect cleanup, suspend/resume with RX/TX restart, and no leaks of USB device refs.
