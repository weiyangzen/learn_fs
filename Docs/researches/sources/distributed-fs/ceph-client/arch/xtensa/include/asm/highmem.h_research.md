<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/highmem.h

## Purpose
Defines highmem permanent and local mapping layout for Xtensa, including cache-color aware pkmap allocation.

## Important APIs, Types, And Functions
Key macros and functions are `PKMAP_BASE`, `LAST_PKMAP`, `PKMAP_NR`, `PKMAP_ADDR`, `kmap_prot`, `get_pkmap_color`, `get_next_pkmap_nr`, `no_more_pkmaps`, `get_pkmap_entries_count`, `get_pkmap_wait_queue_head`, `kmap_local_map_idx`, `kmap_local_unmap_idx`, `pkmap_page_table`, `flush_cache_kmaps`, `arch_kmap_local_post_unmap`, and `kmap_init`.

## Control Flow
For aliasing caches, pkmap allocation advances per-color indexes so virtual mappings match data-cache color. Local mapping index helpers select color-aware fixmap slots. Unmap flushes the kernel TLB range for the page.

## State And Persistence
Runtime state includes pkmap page tables, per-color last index arrays, and per-color wait queues declared elsewhere.

## Dependencies And Integration Points
Depends on highmem, cache aliasing constants, fixmap slots, TLB flush, and generic kmap code.

## Risks And Edge Cases
Wrong coloring can produce D-cache aliases. Slot exhaustion and wait queues must be per-color. Local unmap TLB flushing is required to avoid stale temporary mappings.

## Test Signals
Run highmem stress, kmap local nesting tests, page-cache I/O above lowmem, and cache alias workloads on highmem-capable Xtensa.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/highmem.h -->
