# File Research: sources/block-storage/kvdo/vdo/bio.c

## Purpose

Implements VDO helpers for Linux `struct bio` data movement, allocation, initialization, completion, and statistics accounting.

## Main Responsibilities

- Copies data between bios and linear buffers.
- Allocates and frees VDO-owned bios.
- Counts bios by operation and flags.
- Completes VDO async bios by continuing their owning `vio`.
- Initializes bio fields for VDO I/O.
- Resets a VDO-owned bio around a 4 KiB-aligned buffer, including vmalloc-backed memory.

## Important Functions

- `vdo_bio_copy_data_in()` copies bio segment data into a buffer.
- `vdo_bio_copy_data_out()` copies a buffer into bio segments.
- `vdo_free_bio()` uninitializes and frees a VDO-owned bio.
- `vdo_count_bios()` increments atomic operation counters.
- `vdo_count_completed_bios()` increments completed counters by vio type.
- `vdo_complete_async_bio()` counts completion and continues the owning vio with the bio result.
- `vdo_set_bio_properties()` sets private data, endio callback, op flags, and sector.
- `vdo_reset_bio_with_buffer()` resets and populates bio vectors for a supplied buffer.
- `vdo_create_multi_block_bio()` allocates a bio with inline vec storage.

## Behavior Details

`vdo_count_bios()` treats an empty `REQ_PREFLUSH` bio as both `empty_flush` and `flush`, then returns. Other bios are classified as write, read, or discard and separately counted for preflush/FUA flags.

`vdo_set_bio_properties()` converts VDO physical block numbers to sectors and subtracts `geometry.bio_offset` for normal VIO-backed I/O. The geometry block location sentinel is exempt.

`vdo_reset_bio_with_buffer()` supports kernel API differences around `bio_reset()` through version/RHEL conditionals. It builds page vectors using `vmalloc_to_page()` for vmalloc memory or `virt_to_page()` otherwise.

## Dependencies and Interactions

- Depends on Linux block bio APIs.
- Interacts with `vio`, `vdo`, and `atomic-stats`.
- Used by metadata and data I/O paths to submit and complete work.

## Notable Edge Cases

- Data VIOs are asserted to be single-block.
- Metadata VIOs may span `vio->block_count`.
- If `bio_add_page()` cannot add the requested bytes, returns `VDO_BIO_CREATION_FAILED`.
- Unsupported bio operations assert/log because they should be filtered before this layer.
