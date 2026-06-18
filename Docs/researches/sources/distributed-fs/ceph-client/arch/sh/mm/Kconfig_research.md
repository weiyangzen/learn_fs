# sources/distributed-fs/ceph-client/arch/sh/mm/Kconfig

Purpose: declares SuperH memory-management configuration options.

Important options: `MMU`, `NOMMU`, `PAGE_OFFSET`, `MEMORY_START`, `MEMORY_SIZE`, `29BIT`, `32BIT`, `PMB`, `X2TLB`, `VSYSCALL`, `NUMA`, memory model selections, `IOREMAP_FIXED`, `UNCACHED_MAPPING`, `HAVE_SRAM_POOL`, hugepage sizes, `SCHED_MC`, and cache mode choices.

Control flow: Kconfig constraints select MMU model, address translation mode, optional PMB/vDSO/NUMA/fixmap features, hugepage geometry, and cache behavior used by the C/assembly files in this subset.

State and persistence: build configuration becomes compiled constants and conditional code, not runtime persistence.

Dependencies and integration: consumed by arch SH Makefiles and generic memory-management Kconfig.

Risks: incompatible selections can produce invalid address layouts or cache/TLB code paths. Defaults like memory start/size shape boot memblock setup.

Test signals: build matrix across MMU/NOMMU, 29/32-bit, cache modes, hugepage sizes, and PMB/vsyscall options.
