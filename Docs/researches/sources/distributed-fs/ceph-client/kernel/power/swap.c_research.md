# sources/distributed-fs/ceph-client/kernel/power/swap.c

## Purpose
Stores and retrieves hibernation images on swap-backed block devices. It manages swap-map metadata, hibernation signatures, asynchronous BIO I/O, optional compression/decompression, CRC validation, hardware signatures, and sysfs/boot controls for compression threading.

## Important APIs, Types, and Functions
Externally used entry points are `alloc_swapdev_block()`, `free_all_swap_pages()`, `swsusp_swap_in_use()`, `swsusp_write()`, `swsusp_read()`, `swsusp_check()`, `swsusp_close()`, and `swsusp_unmark()`. Global state includes `swsusp_hardware_signature`, `swsusp_header_flags`, `swsusp_header`, `swsusp_extents`, `root_swap`, `hib_resume_bdev_file`, `clean_pages_on_read`, and `clean_pages_on_decompress`.

Key structures are `struct swap_map_page`, `struct swap_map_page_list`, `struct swap_map_handle`, `struct swsusp_header`, `struct swsusp_extent`, `struct hib_bio_batch`, `struct crc_data`, `struct cmp_data`, and `struct dec_data`. Compression constants define 32-page uncompressed chunks, worst-case compressed size, default thread count, and read-buffer bounds.

## Control Flow
Saving starts in `swsusp_write()`: it obtains a swap writer, verifies enough swap for uncompressed mode, reads the snapshot header from `snapshot_read_next()`, writes it as the first image page, then calls either `save_image()` or `save_compressed_image()`. `swap_write_page()` allocates a swap slot, writes the page, appends the sector to the current swap-map page, and links map pages as needed. `swap_writer_finish()` writes the header signature through `mark_swapfiles()`, flushes the final map page, frees allocated slots on error, and closes the block device.

Compressed save starts compression kthreads plus one CRC32 kthread, batches pages from `snapshot_read_next()` into per-thread uncompressed buffers, compresses with `crypto_acomp`, writes a length header plus compressed payload pages, updates CRC over uncompressed bytes, and records compressed size.

Resume starts with `swsusp_check()`, which opens the resume block device, reads the swap header, looks for `HIBERNATE_SIG`, restores the original swap signature immediately, captures image flags, and validates optional hardware signature. `swsusp_read()` obtains the swap-map list, reads the image header, then calls either `load_image()` or `load_compressed_image()`. Uncompressed load reads pages into buffers returned by `snapshot_write_next()` and finalizes the snapshot. Compressed load maintains a ring of read pages, starts decompression workers and CRC worker, validates compressed/uncompressed lengths, feeds decompressed pages to `snapshot_write_next()`, finalizes the image, and checks CRC when present.

## State and Persistence Behavior
The persistent on-disk marker is `struct swsusp_header` in the resume swap area. It stores the original swap signature, hibernation signature `S1SUSPEND`, first swap-map sector, flags, CRC32, and optional hardware signature. Swap-map pages form the persistent sector list for all image pages. Runtime `swsusp_extents` tracks allocated swap slots so failures and `swsusp_unmark()` can free them.

## Dependencies and Integration Points
Depends on swap slot allocation, block device open/read/write, BIOs, blk plugs, crypto acomp, kthreads, CRC32, CPU count, VM allocation, cache flushing for executable restored pages, and snapshot streaming from `snapshot.c`. `hibernate.c` chooses flags and calls read/write/check; `/dev/snapshot` uses swap allocation helpers for user-space hibernation.

## Risks
Risks include corrupting swap signatures, leaking hibernation swap slots, malformed swap maps causing invalid reads, BIO error propagation mistakes, insufficient low-memory reserves during async I/O, compression length validation bugs, CRC mismatches, hardware signature false positives/negatives, cache maintenance gaps on architectures needing clean executable pages, and races around block-device ownership.

## Test Signals
Test compressed and `SF_NOCOMPRESS_MODE` images, LZO and LZ4, `hibernate_compression_threads=` boot/sysfs values, low-swap and low-memory failures, BIO read/write errors, CRC mismatch injection, hardware signature mismatch, resume offset handling, `swsusp_unmark()` rollback, and repeated hibernate/resume cycles verifying swap slots are freed.
