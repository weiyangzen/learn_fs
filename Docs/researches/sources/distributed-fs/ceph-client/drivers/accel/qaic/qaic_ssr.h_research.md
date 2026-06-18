# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_ssr.h

Purpose: declares the QAIC subsystem-restart interface used by the main driver and datapath cleanup paths.

Important APIs and types: forward-declares `struct drm_device` and `struct qaic_device`, and declares `qaic_ssr_register`, `qaic_ssr_unregister`, `qaic_clean_up_ssr`, and `qaic_ssr_init`.

Control flow: `qaic_drv.c` initializes per-device SSR storage during device creation, registers the MHI driver at module init, unregisters at exit, and calls cleanup during reset/remove.

State and persistence: the header has no state; implementation state is stored in `qaic_device`.

Dependencies and integration: bridges the main QAIC driver to `qaic_ssr.c` without exposing wire protocol structures.

Risks and test signals: compile-check users with incomplete struct declarations and validate init/register/unregister ordering in probe failure paths.
