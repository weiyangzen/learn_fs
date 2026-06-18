<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags-layout.h -->
# sources/distributed-fs/ceph-client/include/linux/page-flags-layout.h

## Purpose
This header computes how non-flag fields are packed into `page->flags`: zone, sparsemem section, NUMA node, KASAN tag, last CPU/PID, LRU generation, and LRU refs.

## Important APIs, types, and functions
It defines `ZONES_SHIFT`, `ZONES_WIDTH`, `SECTIONS_SHIFT`, `SECTIONS_WIDTH`, `NODES_WIDTH`, optional `NODE_NOT_IN_PAGE_FLAGS`, `KASAN_TAG_WIDTH`, `LAST__PID_SHIFT/MASK`, `LAST__CPU_SHIFT/MASK`, `LAST_CPUPID_SHIFT/WIDTH`, optional `LAST_CPUPID_NOT_IN_PAGE_FLAGS`, `LRU_REFS_WIDTH`, `NR_NON_PAGEFLAG_BITS`, and `NR_UNUSED_PAGEFLAG_BITS`.

## Control flow
All logic is compile-time preprocessor selection. It chooses bit widths based on configured zones, sparsemem mode, vmemmap mode, NUMA bits, KASAN tagging, NUMA balancing, LRU generation widths, and available bits after `NR_PAGEFLAGS`. It emits build errors when configured fields cannot fit.

## State and persistence
No runtime state is stored. The computed layout is persistent ABI between memory-management code, generated bounds, and architecture assumptions for the kernel build.

## Dependencies and integration points
It depends on NUMA settings, generated bounds, sparsemem architecture constants, KASAN configs, NUMA balancing, LRU generation constants, and `BITS_PER_LONG`. It integrates with `page-flags.h`, page allocator, memory hotplug, vmscan, and page/folio metadata accessors.

## Risks and test signals
Risks include insufficient flag bits on unusual 32-bit/NUMA/sparsemem configs, node or last-cpupid falling out of flags and requiring alternate lookup, KASAN tag width pressure, and VDSO/bounds generation constraints. Test allyesconfig-like MM configs, 32-bit sparsemem, NUMA balancing, KASAN SW/HW tags, LRU generation, generated bounds, and compile-time error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/page-flags-layout.h -->
