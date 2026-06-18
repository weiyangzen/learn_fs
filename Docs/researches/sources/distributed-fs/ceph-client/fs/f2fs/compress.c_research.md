# sources/distributed-fs/ceph-client/fs/f2fs/compress.c

## Purpose

`fs/f2fs/compress.c` implements F2FS filesystem-level compression. It manages compression context allocation, algorithm backends, compression and decompression I/O contexts, compressed-cluster read/write paths, overwrite and truncate behavior for compressed clusters, compressed-page caching, and global/per-mount memory caches used by compression.

## Important APIs, Types, and Functions

The backend abstraction is `struct f2fs_compress_ops`, with optional init/destroy hooks and required compression/decompression hooks. Backends are compiled for LZO, LZ4/LZ4HC, ZSTD, and LZO-RLE depending on Kconfig. Public helpers include `f2fs_is_compressed_page()`, `f2fs_compress_control_folio()`, `f2fs_init_compress_ctx()`, `f2fs_destroy_compress_ctx()`, `f2fs_compress_ctx_add_page()`, `f2fs_is_compress_backend_ready()`, `f2fs_is_compress_level_valid()`, `f2fs_decompress_cluster()`, `f2fs_end_read_compressed_page()`, `f2fs_cluster_is_empty()`, `f2fs_cluster_can_merge_page()`, `f2fs_all_cluster_page_ready()`, `f2fs_sanity_check_cluster()`, `f2fs_is_compressed_cluster()`, `f2fs_is_sparse_cluster()`, `f2fs_prepare_compress_overwrite()`, `f2fs_compress_write_end()`, `f2fs_truncate_partial_cluster()`, `f2fs_write_multi_pages()`, `f2fs_compress_write_end_io()`, `f2fs_alloc_dic()`, `f2fs_decompress_end_io()`, `f2fs_put_folio_dic()`, `f2fs_cluster_blocks_are_contiguous()`, `COMPRESS_MAPPING()`, cache invalidation/load helpers, and init/destroy helpers for mempools and slabs.

## Control Flow

Writeback batches pages into a `compress_ctx`. `f2fs_write_multi_pages()` checks `cluster_may_compress()`: the file must need compression, not be atomic, the cluster must be full, checkpoint must be healthy, and all pages must be within EOF. It then calls `f2fs_compress_pages()`, which initializes the backend, allocates compressed pages from a mempool, vmaps raw and compressed page arrays, invokes the selected backend, writes the F2FS compression header (`clen`, optional checksum, reserved fields), zero-fills the tail, frees unused compressed pages, and records the valid compressed page count. If compression is ineffective or impossible, the cluster falls back to `f2fs_write_raw_pages()`.

`f2fs_write_compressed_pages()` converts a compressed cluster into on-disk blocks. It obtains the dnode, validates that each cluster slot has a block address, allocates a `compress_io_ctx`, marks compressed pages with private context, optionally encrypts them, sets writeback on raw pages, stores `COMPRESS_ADDR` in the cluster header slot, invalidates or rewrites old blocks, submits out-of-place writes for compressed payload pages, updates compressed block accounting, unlocks raw pages, and frees context arrays after submission. Completion runs through `f2fs_compress_write_end_io()`, which frees compressed pages, waits until all pending compressed pages finish, ends writeback on raw pages, releases arrays, and decrements writeback counters last.

Read completion uses `f2fs_alloc_dic()` to create a `decompress_io_ctx`, allocate compressed pages, optionally preallocate decompression buffers, and attach the context to compressed folios. `f2fs_end_read_compressed_page()` decrements read counters, marks failure, optionally caches the compressed page, and calls `f2fs_decompress_cluster()` after the last page. Decompression maps buffers, validates compressed length, calls the backend, verifies optional checksums, marks fsck-needed on checksum mismatch, and completes through `f2fs_decompress_end_io()`. If fs-verity is enabled for the inode, decompressed folios are verified on the verity workqueue before unlocking.

Overwrite and truncate paths call `f2fs_prepare_compress_overwrite()` and `prepare_compress_overwrite()` to lock and read the entire compressed cluster into page cache before partial updates. `f2fs_truncate_partial_cluster()` zeroes the partial cluster tail, writes it back, truncates page cache, and truncates blocks after the rounded page boundary.

## State and Persistence Behavior

On disk, a compressed cluster starts with `COMPRESS_ADDR` in the first logical block slot, followed by compressed data blocks in the remaining slots and holes/new addresses for unused tail slots. The compressed byte stream begins with an F2FS compression header containing compressed length, checksum, and reserved fields. In-memory state includes `compress_ctx` raw and compressed page arrays, `compress_io_ctx` for writeback completion, `decompress_io_ctx` for read completion, compressed block counters in the inode, private folio markers using `F2FS_COMPRESSED_PAGE_MAGIC`, and an optional compressed-page cache backed by `sbi->compress_inode` mapping physical block addresses to cached compressed folios.

## Dependencies and Integration Points

This file depends on F2FS node and segment mapping, dnode updates, out-of-place data writeback, fscrypt, fsverity, tracepoints, iostat/page counters, low-memory policy, mount options such as `COMPRESS_CACHE`, slab and mempool allocation, and kernel compression libraries. Kconfig selects which algorithm backends exist; `f2fs_is_compress_backend_ready()` prevents use of unavailable backends for compressed files.

## Risks and Edge Cases

Major risks include partial-cluster updates, fallback correctness when compression expands data, writeback cancellation after partial submission, checkpoint races for quota files, compressed cluster corruption, checksum mismatch handling, memory allocation under low-memory mode, fscrypt bounce-page cleanup, fsverity verification ordering, and use-after-free around `sbi` during writeback completion. The code deliberately decrements page counters last in completion paths and can defer `decompress_io_ctx` freeing to `post_read_wq` outside task context.

## Test Signals

Tests should cover all enabled algorithms and compression levels, compression fallback for incompressible data, encrypted compressed files, verity compressed files, checksum success and mismatch, read I/O failure, partial overwrite of compressed clusters, truncate inside compressed clusters, sparse cluster detection, GC/writeback interaction, quota inode compressed writes, compressed-page cache hit/miss/invalidation, low-memory decompression mode, and Kconfig builds with each backend disabled.
