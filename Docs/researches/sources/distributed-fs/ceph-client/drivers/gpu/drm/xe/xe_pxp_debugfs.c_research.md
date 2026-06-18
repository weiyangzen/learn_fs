<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.c

Purpose: creates debugfs entries under `pxp/` for observing PXP state and manually queuing a simulated termination interrupt.

Important APIs and control flow: `xe_pxp_debugfs_register()` copies a local `drm_info_list`, patches `data` to the target `struct xe_pxp`, creates the `pxp` directory, and registers `info` and `terminate`. `pxp_info()` locks `pxp->mutex` and prints status plus key instance. `pxp_terminate()` checks readiness, skips inactive PXP, and invokes `xe_pxp_irq_handler()` under `xe->irq.lock` with `KCR_PXP_STATE_TERMINATED_INTERRUPT`.

State and dependencies: uses PXP status enum from `xe_pxp_types.h`, `xe_pxp_get_readiness_status()`, `drm_debugfs_create_files()`, and KCR interrupt bit definitions. It does not own PXP lifetime; allocation is `drmm_kmalloc()` tied to DRM device lifetime.

Risks and test signals: debugfs terminate can race with normal PXP state transitions, so the IRQ lock and PXP state machine must remain robust. Manual testing should read `pxp/info`, trigger `pxp/terminate`, and observe queue invalidation and key instance changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp_debugfs.c -->
