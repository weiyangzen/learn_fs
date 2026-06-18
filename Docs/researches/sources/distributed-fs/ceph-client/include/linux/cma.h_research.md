# sources/distributed-fs/ceph-client/include/linux/cma.h

Purpose: This header exposes the Contiguous Memory Allocator interface for declaring reserved CMA areas and allocating/releasing contiguous page ranges from them.

Important APIs/types/functions: It defines `MAX_CMA_AREAS` from `CONFIG_CMA_AREAS`, `CMA_MAX_NAME`, `CMA_MIN_ALIGNMENT_PAGES`, `CMA_MIN_ALIGNMENT_BYTES`, opaque `struct cma`, global `totalcma_pages`, getters `cma_get_base`, `cma_get_size`, `cma_get_name`, declaration helpers `cma_declare_contiguous_nid`, `cma_declare_contiguous`, `cma_declare_contiguous_multi`, `cma_init_reserved_mem`, allocation helpers `cma_alloc`, `cma_release`, frozen variants, iterator `cma_for_each_area`, intersection test `cma_intersects`, and `cma_reserve_pages_on_error`.

Control flow: Early boot or reserved-memory code declares or initializes CMA regions. Runtime users allocate contiguous pages from a selected area with count/alignment/no-warn arguments and later release them. Iterator and intersection helpers support diagnostics and memory-management decisions.

State and persistence behavior: CMA areas persist after early declaration and own pageblocks marked for migratable contiguous allocations. `totalcma_pages` records aggregate reserved pages. Allocations mutate page ownership and migration state until released.

Dependencies and integration points: It includes init, types, and NUMA support. It integrates with memblock/reserved memory setup, buddy allocator pageblocks, DMA subsystems, device drivers needing physically contiguous memory, and NUMA placement.

Risks: Alignment must respect pageblock constraints. Overlapping or wrongly sized regions can steal memory or break DMA. Failure to release CMA pages causes long-lived memory pressure. Frozen allocation paths need careful pairing with frozen releases.

Test signals: Boot logs for CMA reservation, DMA allocation tests, page migration/compaction stress, NUMA-specific area declarations, `/proc/meminfo` CMA counters, and driver allocation/release loops are useful signals.
