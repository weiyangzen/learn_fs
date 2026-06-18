# sources/distributed-fs/ceph-client/arch/sparc/mm/srmmu.c

Purpose: implements the SPARC32 SRMMU memory-management core for sun4m/sun4d/LEON-style systems. It builds kernel mappings, allocates non-cacheable page-table memory, manages hardware MMU contexts, maps I/O ranges, detects SRMMU module variants, and installs CPU-specific cache/TLB operation tables.

Important APIs/types/functions: exported or architecture-visible entry points include `load_mmu()`, `srmmu_paging_init()`, `switch_mm()`, `destroy_context()`, `init_new_context()`, `get_pgd_fast()`, `pte_alloc_one()`, `pte_free()`, `pmd_set()`, `srmmu_get_nocache()`, `srmmu_free_nocache()`, `srmmu_mapiorange()`, `srmmu_unmapiorange()`, `arch_zone_limits_init()`, and `mmu_info()`. Important state includes `srmmu_modtype`, `srmmu_name`, `sparc32_cachetlb_ops`, `local_ops`, `srmmu_context_table`, `srmmu_ctx_table_phys`, the nocache bitmap, context lists, and hardware-bug flags.

Control flow: boot calls `load_mmu()`, which probes the chip with `get_srmmu_type()`, chooses operations for HyperSparc, Swift, TurboSparc, Tsunami, Viking/MXCC, or LEON, then initializes IOMMU/SMP support. `srmmu_paging_init()` discovers context count from PROM, runs bootmem setup, sizes and maps the nocache pool, inherits PROM mappings, maps low memory with large SRMMU PTEs, creates the context table, and preallocates IO/DVMA/fixmap/pkmap page-table skeletons. Runtime `switch_mm()` allocates or reuses contexts and writes context descriptors before setting the SRMMU context register.

State and persistence: all state is runtime kernel state: non-cacheable pools, page tables, context ownership lists, cache/TLB op pointers, chip feature flags, and exported VAC dimensions. No filesystem persistence exists, but the code establishes long-lived boot mappings and hardware context-table state.

Dependencies and integration points: depends on PROM memory/CPU properties, `memblock`, `bootmem_init()`, SPARC page-table helpers, `bit_map_*`, SRMMU accessors in `srmmu_access.S`, CPU-specific assembly files, SMP cross-call helpers, IOMMU/DVMA setup, and `/proc/cpuinfo`-style `mmu_info()` reporting.

Risks: this file sits on the boot and MMU critical path. Alignment errors in nocache allocation, stale context descriptors, missing cache/TLB flushes, or wrong chip detection can corrupt memory. CPU erratum handling is especially fragile for Swift and Viking. SMP wrappers must avoid unnecessary cross-calls while still flushing remote CPUs that ran an address space.

Test signals: boot SPARC32 under each supported CPU family, verify `/proc/cpuinfo` MMU details and nocache usage, stress fork/exec/context recycling, map/unmap SBUS/DVMA devices, run DMA workloads on Viking/Swift, exercise SMP TLB shootdowns, and run memory-management stress with high pkmap/fixmap and page-table churn.
