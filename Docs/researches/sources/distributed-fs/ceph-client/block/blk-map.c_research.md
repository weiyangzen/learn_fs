# sources/distributed-fs/ceph-client/block/blk-map.c

## Purpose
`blk-map.c` maps user or kernel buffers into passthrough block requests. It chooses between direct page mapping, iterator-backed bvec reuse, and copied bounce buffers depending on alignment, address type, queue limits, and caller-provided `rq_map_data`.

## Important APIs, Types, And Functions
External APIs are `blk_rq_append_bio()`, `blk_rq_map_user_iov()`, `blk_rq_map_user()`, `blk_rq_map_user_io()`, `blk_rq_unmap_user()`, and `blk_rq_map_kern()`. `struct bio_map_data` preserves a copied `iov_iter` and ownership flags so completion can copy read data back and free pages. Internal mapping paths include `bio_copy_user_iov()`, `bio_map_user_iov()`, `blk_rq_map_user_bvec()`, `bio_map_kern()`, and `bio_copy_kern()`.

## Control Flow
User mapping first classifies whether copying is required: caller-supplied map data, DMA alignment mismatch, non-user iterators, stack objects, or virtual-boundary gaps force a bounce path. ITER_BVEC can be reused directly but falls back to copying if queue limits would require splitting. Each produced bio is appended through `blk_rq_append_bio()`, which calls `bio_split_io_at()` and rejects mappings that would need splitting. Unmap walks the original bio list, copies read data back for copied user buffers, releases pinned pages for direct mappings, unmaps integrity metadata, and drops bio references. Kernel mapping directly maps vmalloc/linear buffers when aligned and copies otherwise, with read completion copying data back from bounce pages.

## State And Persistence
State is attached to bios via `bi_private` and `bi_end_io`, plus request fields `bio`, `biotail`, `__data_len`, `nr_phys_segments`, and `phys_gap_bit`. Lifetimes are sensitive: copied user iterators are deep-copied because caller iovecs can be stack-backed, and unmap must run in process context if data must be copied to user memory.

## Dependencies And Integration Points
This file depends on iov_iter import/copy helpers, bio page pinning, queue DMA alignment and virtual-boundary limits, merge/split helpers from `blk-merge.c`, integrity unmapping, and passthrough request users such as SG_IO and driver-specific command paths.

## Risks And Test Signals
Risk areas include user copy faults, short iterators, stack-buffer kernel mapping, vmalloc cache invalidation, request append failures after partial mapping, and cleanup consistency across mixed copied/direct bios. Tests should include unaligned user buffers, ITER_BVEC passthrough over hardware limits, read copy-back from workqueue/orphan context, `rq_map_data` null-mapped paths, vmalloc reads, and integrity metadata unmap.
