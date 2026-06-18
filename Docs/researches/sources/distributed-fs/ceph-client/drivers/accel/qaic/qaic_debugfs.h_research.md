# sources/distributed-fs/ceph-client/drivers/accel/qaic/qaic_debugfs.h

Purpose: declares the QAIC debugfs and bootlog integration points while compiling them out cleanly when `CONFIG_DEBUG_FS` is disabled.

Important APIs and types: when debugfs is enabled it declares `qaic_bootlog_register`, `qaic_bootlog_unregister`, and `qaic_debugfs_init`. When disabled it provides inline no-op versions returning success or doing nothing.

Control flow: this header is consumed by `qaic_drv.c` and `qaic_debugfs.c`. The no-op branch lets module init and DRM device registration use the same call sites regardless of debugfs configuration.

State and persistence: the header owns no state. It controls whether runtime bootlog/debugfs state from `qaic_debugfs.c` exists.

Dependencies and integration: includes DRM file declarations and relies on `struct qaic_drm_device` being visible through prior includes. It is part of the QAIC module surface, not UAPI.

Risks and test signals: build both `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`, ensuring callers do not accidentally depend on debugfs-only side effects.
