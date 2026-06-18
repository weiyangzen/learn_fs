# sources/distributed-fs/ceph-client/fs/squashfs/block.c

## Purpose

`block.c` implements the low-level SquashFS read path for metadata and data blocks. It reads packed, possibly unaligned compressed blocks from the block device into BIO pages, optionally reuses compressed pages through an internal cache mapping, and either copies uncompressed data into a `squashfs_page_actor` or dispatches compressed input to the selected decompressor thread ops.

## Important APIs, Types, and Functions

The exported API is `squashfs_read_data()`. Internal helpers are `copy_bio_to_actor()`, `squashfs_bio_read_cached()`, `squashfs_get_cache_page()`, and `squashfs_bio_read()`. It depends on `struct squashfs_sb_info`, `struct bio`, `struct address_space`, and `struct squashfs_page_actor`.

## Control Flow

`squashfs_read_data()` distinguishes data blocks from metadata blocks by whether `length` is nonzero. For metadata, it first reads the two-byte size header, extracts compressed/uncompressed state, advances the index, and then reads the block payload. For file data, it decodes size and compression state from the supplied block-list entry. After bounds checks against `output->length` and `msblk->bytes_used`, it reads the byte range into a BIO. Compressed payloads go through `msblk->thread_ops->decompress`; uncompressed payloads are copied directly to the actor.

## State and Persistence Behavior

Persistent state lives in `msblk`: device block sizing, filesystem byte limit, optional compressed-page `cache_mapping`, panic-on-error flag, selected decompressor stream, and thread ops. BIO pages are temporary. Cached compressed head/tail pages are inserted into `cache_mapping` when the device block size equals page size; `CONFIG_SQUASHFS_COMP_CACHE_FULL` may cache all compressed BIO pages.

## Dependencies and Integration Points

This is the common dependency for metadata cache fills, fragment reads, file data reads, table reads, symlink reads, and decompressor option reads. It integrates with the block layer (`bio_*`, `submit_bio_wait`), page cache (`filemap_add_folio`, `find_get_page`), decompressor wrappers, and `page_actor`.

## Risks and Edge Cases

Critical risks are malformed image sizes, integer boundary mistakes around unaligned device/page offsets, stale or non-uptodate cached pages, actor length mismatches, and missing decompressor stream. The error path frees BIO pages and can panic when mounted with `errors=panic`.

## Test Signals

Mount and read images with compressed and uncompressed metadata/data blocks, corrupted block sizes, truncated devices, page-sized and non-page-sized device blocks, direct and cached file modes, all compression wrappers, and `errors=panic`/`continue`. Repeated adjacent reads should exercise compressed-page cache reuse.
