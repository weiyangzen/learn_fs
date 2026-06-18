<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.c

Purpose: Main V3D DRM platform driver: parameter ioctls, file open/close, fdinfo stats, DRM ioctl table, platform probe/remove, MMIO/clock/reset setup, generation detection, and module registration.

Important APIs/types/functions: `v3d_get_param_ioctl()` exposes register-backed and capability parameters. `v3d_open()` allocates per-file stats and scheduler entities for all queues, then initializes perfmon xarray. `v3d_postclose()` tears them down. `v3d_get_stats()` reads seqcount-protected stats for fdinfo. Probe maps hub/core/SMS/GCA/bridge regs, enables clock, configures DMA mask from MMU debug, reads hardware generation/cores/revision, initializes perfmon, reset, scratch page, GEM, IRQ, DRM, and sysfs.

Control flow: Probe is staged with unwinds for DRM unregister, IRQ disable, GEM destroy, DMA free, and clock disable. Generation data comes first from OF match and then hardware ident, with `WARN_ON` if they differ. Remove destroys sysfs/DRM/GEM, frees scratch page, powers off SMS, and disables clock.

State and persistence: Device state includes generation/revision, mapped registers, clock/reset handles, MMU scratch page, queues, perfmon info, stats, global reset counter, and DRM registration. Per-file state includes scheduler entities, stats, and perfmons.

Dependencies and integration points: Integrates platform/OF, DRM render ioctls/syncobj/GEM, GPU scheduler, V3D BO/MMU/IRQ/perfmon/sysfs/scheduler/submit modules, DMA API, clocks, reset controls, and debugfs/fdinfo.

Risks and test signals: Risks include probe unwind ordering, single-core assumption, hardware/DT generation mismatch, reset fallback bridge mapping, missing IRQ cleanup on remove, and DRM_AUTH requirements. Tests should cover supported compatible strings, open/close, get-param capabilities, fdinfo, probe failures, and module unload after active jobs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_drv.c -->
