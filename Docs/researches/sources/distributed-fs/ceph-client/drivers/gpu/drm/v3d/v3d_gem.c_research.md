<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_gem.c

Purpose: Initializes and destroys V3D GEM/MMU/scheduler state, performs hardware reset and cache maintenance, configures page table base, hugepage support, and invariant core state.

Important APIs/types/functions: `v3d_init_core()` and `v3d_init_hw_state()` program invariant core cache/TMU state. Reset helpers idle AXI/GCA/SMS, use reset control or bridge reset, reinitialize hardware, page table, IRQs, and perfmon state. Cache helpers invalidate/clean L3/L2/slice caches with `cache_clean_lock`. `v3d_huge_mnt_init()` configures transparent hugepage support. `v3d_gem_init()` allocates queue stats/fence contexts, initializes locks and DRM MM, allocates a 4 MiB page table, initializes hardware/MMU, hugepages, and scheduler. `v3d_gem_destroy()` tears down scheduler, stats, DRM MM, and page table.

Control flow: Probe calls `v3d_gem_init()` after scratch-page allocation. Reset is called on GPU hang and disables IRQs before hardware reset and re-enables via `v3d_irq_reset()`. Destroy runs after DRM unregister and expects no active jobs.

State and persistence: State includes queue stats, fence contexts, locks, DRM MM address space, page table DMA memory, hardware cache/MMU registers, and optional hugepage mount.

Dependencies and integration points: Integrates V3D registers, reset controls/bridge regs, IRQ, MMU, scheduler, perfmon, DRM MM, DMA coherent allocation, transparent hugepage GEM support, and tracepoints.

Risks and test signals: Risks include reset races, cache-clean/invalidate interference, 4 MiB contiguous page-table allocation failure, active jobs at destroy, and generation-specific reset/SMS behavior. Tests should cover init/destroy, GPU hang reset, CSD cache clean, THP on/off, and allocation failure unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/v3d/v3d_gem.c -->
