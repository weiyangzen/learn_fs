# sources/distributed-fs/ceph-client/drivers/hv/mshv_regions.c

## Purpose

`mshv_regions.c` implements guest memory-region backing for MSHV root partitions. It supports pinned RAM, movable/HMM-backed RAM faulted on GPA intercepts, MMIO mappings, huge-page chunking, encrypted-partition host-access transitions, and mmu interval invalidation.

## Important APIs, Types, and Functions

- `mshv_region_create()` allocates a flexible-array region and derives Hyper-V map flags from user flags.
- `mshv_region_pin()`, `mshv_region_map()`, `mshv_region_share()`, `mshv_region_unshare()`, and invalidation helpers manage page pinning and Hyper-V mappings.
- `mshv_region_handle_gfn_fault()` faults and maps a batch around an intercepted GFN for movable memory.
- `mshv_region_movable_init/fini()` register/remove an `mmu_interval_notifier`.
- Internal range/chunk walkers coalesce contiguous present pages and use 2 MiB large-page mappings when aligned and supported.

## Control Flow

Pinned regions pin all user pages in batches with `FOLL_LONGTERM`, optionally release host access for SNP partitions, then map GPA pages. Movable regions initially map GPA as no-access; when Hyper-V reports a GPA intercept, the root run loop locates the region and calls `mshv_region_handle_gfn_fault()`, which uses HMM to fault pages, verifies the notifier sequence, locks the region, stores `struct page *` pointers, and remaps the affected range with normal access. MMU invalidation remaps affected pages to no-access and clears page pointers, unpinning if needed.

## State and Persistence Behavior

Each `mshv_mem_region` stores guest PFN range, userspace start, map flags, type, partition pointer, refcount, optional interval notifier, mutex, and page array. Regions are linked from `partition->pt_mem_regions` and destroyed by refcount, which unmaps GPA pages, restores host access for encrypted partitions, invalidates pages, removes movable notifiers, and frees memory.

## Dependencies and Integration Points

The file depends on HMM, mmu interval notifiers, page pinning, Hyper-V mapping/host-access hypercalls, and partition state from `mshv_root.h`. It is called from memory ioctls and GPA intercept handling in `mshv_root_main.c`.

## Risks and Edge Cases

Invalidation failure is explicitly dangerous because Hyper-V could retain mappings to freed pages. Huge-page support only accepts compound head pages with PMD order and aligned GFN/count. `page_count = HVPFN_DOWN(mend - mstart)` can become zero for sub-page invalidation ranges. Encrypted-region destroy refuses to unpin if sharing back to host fails, intentionally avoiding host crash but leaking inaccessible pages. Long-term pinning has memory-management impact.

## Test Signals

Test pinned map/unmap, movable no-access initial mapping, GPA intercept fault batching, mmu invalidation during guest execution, huge-page and misaligned fallback, SNP share/unshare error paths, overlapping region rejection at callers, and KASAN/lockdep under concurrent unmap and fault.
