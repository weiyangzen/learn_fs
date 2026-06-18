<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_debugfs.c

Purpose: Provides V3D debugfs files for register dumps, hardware identity, BO stats, measured clock, and DRM MM state.

Important APIs/types/functions: Register definition arrays gate hub/GCA/core/CSD registers by V3D generation. `v3d_v3d_debugfs_regs()` dumps applicable registers. `v3d_v3d_debugfs_ident()` prints revision/features/core topology. `v3d_debugfs_bo_stats()` reports allocation counters. `v3d_measure_clock()` configures a performance counter, sleeps one second, and reports MHz. `v3d_debugfs_mm()` prints `drm_mm`. `v3d_debugfs_init()` registers files.

Control flow: DRM debugfs open invokes each show callback with a `drm_debugfs_entry`; callbacks resolve `v3d_dev`, read registers under no explicit runtime PM guard, and print seq output.

State and persistence: Read-only diagnostics over live registers and in-memory stats/MM allocator.

Dependencies and integration points: Uses DRM debugfs, seq_file, V3D register macros, bo locks, and MM lock.

Risks and test signals: Risks include reading registers when device is powered off/unplugged, generation gating mistakes, and measure_clock perturbing perf counters. Test by reading all files on supported generations and under active workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_debugfs.c -->
