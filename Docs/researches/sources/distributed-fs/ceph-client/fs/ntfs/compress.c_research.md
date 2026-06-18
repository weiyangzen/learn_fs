# sources/distributed-fs/ceph-client/fs/ntfs/compress.c

## Purpose

`compress.c` implements NTFS compressed attribute read and write support. It owns a shared decompression buffer, decodes NTFS compression blocks into page-cache pages, compresses 4 KiB sub-blocks with an LZ77-style encoder, writes compressed blocks to newly allocated clusters, and exposes a compressed write path for unnamed data streams.

## Important APIs, Types, And Functions

- `allocate_compression_buffers()` and `free_compression_buffers()` manage the global `ntfs_compression_buffer`.
- `zero_partial_compressed_page()` and `handle_bounds_compressed_page()` zero regions beyond initialized size during compressed reads.
- `ntfs_decompress()` parses NTFS compressed sub-block headers, symbol tokens, and phrase tokens, writing decompressed bytes into an array of destination pages and finalizing completed pages.
- `ntfs_read_compressed_block(struct folio *folio)` loads all pages overlapping the compression block(s) that contain the requested folio, reads the compressed clusters from the block device, distinguishes sparse/uncompressed/compressed compression blocks, and fills page-cache pages.
- `struct compress_context`, `ntfs_hash()`, `ntfs_best_match()`, and `ntfs_skip_position()` implement hash-chain match finding for compression.
- `ntfs_compress_block()` compresses one 4 KiB NTFS sub-block or emits an uncompressed sub-block if compression is ineffective.
- `ntfs_write_cb()` compresses a whole compression block, decides whether to store compressed, sparse/all-zero, or uncompressed data, punches the old block, allocates new clusters, updates runlist and mapping pairs, and writes data through BIOs.
- `ntfs_compress_write()` is the public compressed write path. It expands the attribute if needed, reads/locks all pages in each affected compression block, copies user data into those pages, calls `ntfs_write_cb()`, and releases pages.

## Control Flow And Algorithms

Compressed reads start by aligning the requested page index to compression-block boundaries, calculating the target page within the block, and grabbing all destination pages that are not dirty or already uptodate. For each compression block, the code locks the global compression buffer, reads physical clusters through the attribute runlist and the block device mapping, then chooses a decode path. A fully sparse block zeroes destination pages. A block with all clusters present and no sparse break is copied as uncompressed. Otherwise `ntfs_decompress()` decodes sub-block headers and LZ phrase tokens.

`ntfs_decompress()` operates while holding `ntfs_cb_lock`. It validates sub-block boundaries, handles uncompressed sub-blocks by copying 4096 bytes, and handles compressed sub-blocks by reading tag bytes. A zero tag bit copies a literal; a one tag bit reads a 16-bit phrase token, derives backward offset and length from the current destination offset, and copies possibly overlapping data. Page finalization is staged so the lock is dropped before page unlock/put operations.

Compression writes operate per compression block. `ntfs_compress_write()` ensures the stream is large enough, then for each affected compression block reads all block pages, copies from the iov iterator into the relevant page offsets, and calls `ntfs_write_cb()`. `ntfs_write_cb()` vmaps source pages, allocates temporary destination pages, compresses each 4 KiB sub-block, detects all-zero compressed output, appends a terminator for compressed blocks, rounds to cluster size, or falls back to uncompressed data. It then punches the old compression-block range, allocates clusters for the new representation, merges the allocation into the runlist, updates mapping pairs, and writes pages via BIO.

The compressor uses a hash table of 3-byte sequences, a bounded search depth, lazy parsing, and a "nice match" early stop. It emits NTFS phrase tokens whose offset/length bit split changes as the current sub-block offset grows.

## State And Persistence Behavior

Global state is `ntfs_compression_buffer`, protected by `ntfs_cb_lock`. Read state is the page cache: pages are kmap'ed, filled, marked uptodate, unlocked, and put. Write state changes both data and metadata: old cluster ranges are punched to holes, new clusters are allocated, `ni->runlist` is merged, mapping pairs are persisted with `ntfs_attr_update_mapping_pairs()`, BIO writes send compressed/uncompressed bytes to disk, and `NInoSetFileNameDirty()` plus `mark_mft_record_dirty()` mark metadata for writeback.

Sparse all-zero compression blocks are represented by punching the old block and allocating no new clusters. Compressed and sparse size accounting is delegated to mapping-pair update and attribute metadata helpers.

## Dependencies And Integration Points

The file depends on Linux fs, block, vmalloc, slab, page-cache, BIO, and iov-iterator APIs. NTFS dependencies include `attrib.h` for runlist mapping, hole punching, expansion, and mapping-pair updates; `inode.h` for inode access; `lcnalloc.h` for cluster allocation; `mft.h` for dirtying MFT records; and core NTFS conversion/logging helpers.

It integrates with the read-folio path for compressed unnamed `$DATA`, compressed write operations, cluster allocation/freeing, block-device mapping reads, and the attribute engine's mapping-pair persistence.

## Risks And Edge Cases

- The global compression buffer serializes all compressed reads and parts of read decoding, limiting concurrency.
- `ntfs_decompress()` assumes `PAGE_SIZE >= 4096` and depends on callers having mapped destination pages with `kmap_local_page()`.
- Several BIO allocation and page allocation paths have limited recovery. `bio_alloc()` is not always checked before use.
- `ntfs_compress_block()` documents returning `0` on error but returns `-ENOMEM` through an unsigned return type when context allocation fails; callers treat nonzero as a size, which can mis-handle allocation failure.
- `ntfs_write_cb()` calls `vunmap(outbuf)` even when `outbuf` allocation failed and can call `submit_bio_wait(bio)` with `bio == NULL` if no data was added, depending on path.
- The compressed write path clears dirty/uptodate only for `i < ip`, where `ip` tracks the last copied page and may not cover every modified page in edge cases.
- Read classification of "uncompressed compression block" depends on whether all clusters in the compression unit are physically present; malformed compressed data and mixed sparse/allocated layouts must be handled carefully.
- Error paths after punching old clusters but before successful write can lose data or leave metadata inconsistent.

## Test Signals

Tests should cover compressed reads of sparse blocks, uncompressed blocks, valid compressed blocks with literals and overlapping phrase tokens, corrupted sub-block headers, EOF inside a compression block, initialized-size zeroing, dirty destination pages that must not be overwritten, writes that compress well, writes that fall back to uncompressed, all-zero writes that become sparse, partial-block writes, expansion before compressed write, ENOSPC or BIO failure after punching, and concurrent compressed reads to validate buffer locking.
