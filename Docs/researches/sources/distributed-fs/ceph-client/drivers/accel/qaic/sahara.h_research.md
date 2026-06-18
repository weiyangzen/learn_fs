# sources/distributed-fs/ceph-client/drivers/accel/qaic/sahara.h

Purpose: declares the Sahara MHI service registration hooks for the QAIC module.

Important APIs and types: exposes `sahara_register` and `sahara_unregister`; no data structures are exported.

Control flow: `qaic_drv.c` registers the Sahara MHI driver during module init after the control MHI driver, and unregisters during module exit.

State and persistence: no header-owned state. Runtime protocol state is per MHI channel in `sahara.c`.

Dependencies and integration: internal QAIC-only header used to keep the firmware loader service separate from the main driver.

Risks and test signals: verify init unwind unregisters earlier services correctly if Sahara registration fails, and compile coverage catches signature drift.
