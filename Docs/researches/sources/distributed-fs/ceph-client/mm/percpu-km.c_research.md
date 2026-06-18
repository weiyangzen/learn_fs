# sources/distributed-fs/ceph-client/mm/percpu-km.c

## Purpose
`percpu-km.c` is the contiguous-kernel-memory backend for dynamic per-CPU chunks, intended for NOMMU-style architectures that select `CONFIG_NEED_PER_CPU_KM`. It allocates each chunk as one contiguous `alloc_pages()` block instead of using vmalloc mappings.

## Important APIs, Types, And Functions
- `pcpu_create_chunk()` allocates allocator metadata plus a contiguous backing allocation, assigns page-to-chunk reverse mappings, and marks the whole chunk populated.
- `pcpu_destroy_chunk()` frees contiguous backing pages and chunk metadata.
- `pcpu_addr_to_page()` translates addresses with `virt_to_page()`.
- `pcpu_verify_alloc_info()` enforces the backend's single-group constraint and warns about rounded-up page waste.
- `pcpu_populate_chunk()`, `pcpu_depopulate_chunk()`, and `pcpu_post_unmap_tlb_flush()` are no-op backend hooks because the chunk is fully and permanently mapped.
- `pcpu_should_reclaim_chunk()` always returns false.

## Control Flow
Creation allocates a `pcpu_chunk`, allocates a power-of-two contiguous page block sized from the only percpu group, records the chunk pointer in every backing page, sets `data` and `base_addr`, marks all pages populated under `pcpu_lock`, updates stats, and emits a tracepoint. Destruction reverses those steps. Verification rejects allocation layouts with more than one group and warns if the power-of-two allocation is larger than the exact chunk size.

## State And Persistence Behavior
Chunks are fully populated for their lifetime. Runtime state is the contiguous page allocation, page-to-chunk reverse map, `pcpu_chunk` metadata, stats, and trace events. No depopulation or reclaim state is used.

## Dependencies And Integration Points
It depends on the generic percpu allocator helpers included by the build unit, page allocator `alloc_pages()`/`__free_pages()`, page address translation, `pcpu_group_sizes`, `pcpu_set_page_chunk()`, and tracepoints. It is mutually incompatible with paged first-chunk SMP configurations.

## Risks
- Requires all units in a single group and no NUMA-aware grouping.
- Power-of-two contiguous allocation can waste memory and fail under fragmentation.
- No reclaim support means empty populated pages remain allocated until chunk destruction.
- Misuse on an architecture expecting vmalloc-style sparse population would break address translation and TLB assumptions.

## Test Signals
- Build NOMMU or `CONFIG_NEED_PER_CPU_KM` configurations and verify first-chunk compatibility.
- Allocate/free enough dynamic percpu areas to create and destroy chunks.
- Validate warnings for non-power-of-two chunk page counts and rejection of multi-group allocation info.
