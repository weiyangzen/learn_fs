# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/mmu.h

Purpose: defines the Book3S64 MMU abstraction shared by hash and radix modes, including page-size definitions, process/partition table formats, per-mm context state, and early MMU dispatch.

Important APIs/types/functions: `struct mmu_psize_def`, `struct prtb_entry`, `struct patb_entry`, `mm_context_t`, context helpers for hash slices, globals for PID/LPID bits and page sizes, `mmu_early_init_devtree()`, `hash__early_init_mmu()`, `radix__early_init_mmu()`, `early_init_mmu()`, `early_init_mmu_secondary()`, `setup_initial_memory_limit()`, `radix_init_pseries()`, and hash `get_user_context()`/`get_user_vsid()`.

Control flow: early init dispatches to radix or hash based on `radix_enabled()`/`early_radix_enabled()`. Initial memory limits use hash restrictions unless early radix is selected. Hotplug cleanup and context helpers are config-gated.

State and persistence: `mm_context_t` persists per process and tracks PID/context IDs, active CPUs, coprocessor and VAS window users, hash slice state, VDSO pointer, page-table fragments, IOMMU memory lists, and memory protection keys. Global MMU sizing state persists after early boot.

Dependencies and integration points: integrates with hash MMU definitions, radix process/partition tables, pkeys, pSeries, CPU hotplug, IOMMU, VAS, scheduler mm cpumasks, and memory hotplug.

Risks: hash and radix share fields with different meanings, especially `id` versus extended hash context IDs. Early dispatch must match firmware/CPU capabilities. PID/LPID sizing controls table allocation and hardware limits.

Test signals: hash and radix boots, CPU hotplug, pSeries radix init, memory hotplug, process creation with high address ranges, pkey tests, and IOMMU/VAS users of `mm_context_t`.
