# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ras.h

Purpose: small internal header exposing QAIC RAS MHI driver registration to the main QAIC module.

Important APIs and types: declares `qaic_ras_register` and `qaic_ras_unregister`; it defines no structures.

Control flow: `qaic_drv.c` calls the register function during module init and unregisters during module exit. The implementation handles all channel probe/remove work.

State and persistence: none in the header. Runtime state is held by `qaic_ras.c` in `qaic_device` counters and MHI buffers.

Dependencies and integration: used inside the QAIC driver only; not a userspace ABI.

Risks and test signals: ensure declaration stays synchronized with implementation and module init unwind calls unregister only after successful registration paths.
