<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Makefile

Purpose: Lists V3D driver objects for kbuild.

Important APIs/types/functions: Core objects include BO, driver, fence, GEM, IRQ, MMU, perfmon, trace points, scheduler, sysfs, and submit code. `v3d_debugfs.o` is conditional on `CONFIG_DEBUG_FS`. `obj-$(CONFIG_DRM_V3D)` emits `v3d.o`; trace points get `-I$(src)`.

Control flow: Kbuild links all functional slices into one DRM render driver.

State and persistence: No runtime state.

Dependencies and integration points: Shows integration with files outside this work item (`v3d_sched.c`, `v3d_submit.c`, `v3d_sysfs.c`, trace points).

Risks and test signals: Build tests should catch missing object dependencies and debugfs conditional coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/Makefile -->
