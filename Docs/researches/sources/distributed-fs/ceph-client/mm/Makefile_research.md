# sources/distributed-fs/ceph-client/mm/Makefile

## Purpose
`mm/Makefile` maps memory-management configuration symbols to built objects and sets sanitizer/instrumentation exceptions for core allocator paths. It is the build integration point for the `mm/` implementation files in this work item.

## Important APIs, types, and functions
Important variables include `obj-y`, `mmu-y`, `page-alloc-y`, `memory-hotplug-y`, and many `obj-$(CONFIG_...)` lines. Relevant mappings are unconditional `backing-dev.o`, `obj-$(CONFIG_BALLOON) += balloon.o`, `obj-$(CONFIG_HAVE_BOOTMEM_INFO_NODE) += bootmem_info.o`, `obj-$(CONFIG_CMA) += cma.o`, and conditional `obj-$(CONFIG_MEMCG) += bpf_memcontrol.o` under `CONFIG_BPF_SYSCALL`.

## Control flow
The build first establishes sanitizer exclusions for allocator files, then builds the core `mm` object set and conditionally appends feature objects. `ifdef CONFIG_MMU`, `CONFIG_SWAP`, `CONFIG_CMA`, and `CONFIG_BPF_SYSCALL` blocks further refine object inclusion.

## State and persistence
The Makefile has no runtime state. Its persistent effect is the compiled kernel image or modules selected by `.config`, including whether debug/test objects and feature-specific mm code are present.

## Dependencies and integration points
It integrates generated Kconfig symbols with Kbuild, sanitizer tooling, KCOV/KCSAN/KASAN configuration, mm subdirectories such as `kasan/`, `kfence/`, `damon/`, and external users expecting core mm exports.

## Risks and test signals
Risks include missing object inclusion for selected Kconfig symbols, accidental instrumentation of fragile allocator paths, feature objects built without dependencies, and ordering issues for core objects. Test signals include allyesconfig/allmodconfig/randconfig builds, sanitizer-enabled builds, BPF+MEMCG combinations, CMA/balloon/hotplug configurations, and link checks for exported mm symbols.
