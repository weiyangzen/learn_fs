# sources/distributed-fs/ceph-client/mm/percpu-vm.c

## Purpose
`percpu-vm.c` is the default vmalloc-backed backend for dynamic per-CPU chunks. It reserves per-CPU virtual areas, populates pages per CPU on demand, maps and unmaps them, performs cache/TLB maintenance, and decides when sparsely used chunks should be reclaimed.

## Important APIs, Types, And Functions
- `pcpu_chunk_page()` resolves a populated virtual address back to its page.
- `pcpu_get_pages()` provides a serialized temporary page pointer array indexed by `pcpu_page_idx()`.
- `pcpu_alloc_pages()` and `pcpu_free_pages()` allocate/free backing pages for all possible CPUs in a page range.
- `pcpu_map_pages()` and `pcpu_unmap_pages()` map/unmap per-CPU backing pages into chunk virtual addresses and maintain page-to-chunk reverse mappings.
- `pcpu_pre_unmap_flush()`, `pcpu_post_unmap_tlb_flush()`, and `pcpu_post_map_flush()` perform architecture cache/TLB maintenance over the whole chunk range.
- `pcpu_populate_chunk()` and `pcpu_depopulate_chunk()` are the backend population hooks.
- `pcpu_create_chunk()` and `pcpu_destroy_chunk()` reserve/free vmalloc areas and chunk metadata.
- `pcpu_should_reclaim_chunk()` decides whether a chunk should move to depopulation/sidelined lists.

## Control Flow
Population obtains the shared pages array under `pcpu_alloc_mutex`, allocates one page per CPU per requested page index using CPU-local NUMA nodes, maps each CPU's pages into the reserved vmalloc address range, sets page-to-chunk links, and flushes caches after mapping. On map failure it unmaps any partial CPU ranges, flushes TLBs, and frees allocated pages. Depopulation gets the same temporary array, flushes caches before unmap, records current mapped pages into the array, unmaps each CPU range, and frees the pages; callers perform any required post-unmap TLB flush unless vmalloc lazy flushing suffices. Chunk creation allocates metadata, reserves one vmalloc area per group with atom-size constraints, computes the base address from group 0, updates stats, and traces creation. Reclaim excludes first/reserved chunks and selects isolated chunks with empty pages or chunks with at least 25 percent empty populated pages when the global empty-populated-page pool exceeds the high watermark.

## State And Persistence Behavior
Runtime state includes reserved `vm_struct` areas, backing pages, page-to-chunk reverse mappings, populated bitmaps/counters in `pcpu_chunk`, the shared temporary pages array, stats, and trace events. There is no disk persistence. Pages can be depopulated and later repopulated, unlike the KM backend.

## Dependencies And Integration Points
The backend depends on vmalloc/vmap APIs, page allocator, CPU/node topology, `pcpu_alloc_mutex`, `pcpu_lock`, per-CPU group offsets/sizes, cache/TLB flush APIs, page-to-chunk reverse mapping, stats, and tracepoints. It supplies backend hooks consumed by the generic percpu allocator.

## Risks
- The temporary pages array is single global state and must only be used under `pcpu_alloc_mutex`.
- Partial allocation/map failures require exact rollback to avoid leaked pages or stale mappings.
- Cache and TLB flush ranges span low to high unit CPUs; wrong bounds can leave stale aliases.
- Reclaim heuristics must not depopulate first or reserved chunks and must keep global empty populated page accounting consistent.
- Address-to-page reverse lookup must not be used on immutable pre-mapped chunks.

## Test Signals
- Dynamic percpu allocation/free stress across CPUs and NUMA nodes with forced allocation failures.
- Reclaim tests that create empty populated pages and verify chunks move through to-depopulate and sidelined lists.
- Validate map/unmap with DEBUG_VM, KASAN, and lockdep for `pcpu_alloc_mutex` usage.
- Inspect tracepoints and `percpu_stats` before and after chunk creation, population, depopulation, and destruction.
