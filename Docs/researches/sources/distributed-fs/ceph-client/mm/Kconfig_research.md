# sources/distributed-fs/ceph-client/mm/Kconfig

## Purpose
`mm/Kconfig` defines the memory-management configuration surface for this kernel tree. It controls swap, zswap, zsmalloc, slab hardening, memory models, hotplug, compaction, migration, CMA, THP, NUMA, device memory, BPF-visible memory control support through dependent objects, and many debug/test options.

## Important APIs, types, and functions
As Kconfig input, the important entities are symbols and dependency relationships rather than functions. Relevant symbols for this work item include `ZSWAP`, `ZSMALLOC`, `MEMORY_HOTPLUG`, `HAVE_BOOTMEM_INFO_NODE`, `BALLOON`, `BALLOON_MIGRATION`, `COMPACTION`, `MIGRATION`, `CMA`, `CMA_DEBUGFS`, `CMA_SYSFS`, `CMA_AREAS`, `MEMCG`, `BPF_SYSCALL`, and `USERFAULTFD`.

## Control flow
Configuration selection flows from menus, choices, defaults, `depends on`, and `select`. For example, `CMA` depends on `MMU` and selects `MIGRATION` and `MEMORY_ISOLATION`; `BALLOON_MIGRATION` depends on `MIGRATION && BALLOON`; memory hotremove selects bootmem-info support on selected architectures; and zswap compressor choices select the appropriate crypto algorithms.

## State and persistence
The file has no runtime state, but selected symbols persist into `.config` and generated autoconf headers, which determine compiled code, static defaults, exposed sysfs/debugfs features, and boot-time behavior.

## Dependencies and integration points
It integrates with architecture Kconfig symbols, generated build configuration, `mm/Makefile`, documentation references, and runtime kernel parameters mentioned in help text such as `zswap.enabled`, `zswap.compressor`, memory-hotplug auto-online policy, THP defaults, and page allocator shuffling.

## Risks and test signals
Risks include invalid dependency combinations, silently missing mm features, security-sensitive defaults such as slab merging or uninitialized mmap, and symbols selected without required architecture support. Test signals are `olddefconfig`, randconfig/allmodconfig builds, feature-specific boot tests for CMA, ballooning, memory hotplug, zswap, THP, and Kconfig dependency linting.
