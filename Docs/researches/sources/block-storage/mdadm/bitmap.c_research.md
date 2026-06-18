# File Research: sources/block-storage/mdadm/bitmap.c

## Purpose
`bitmap.c` reads, displays, creates, and updates md bitmap files or internal bitmap areas.

## Main Flow
`bitmap_file_open()` opens a block device or member device with `O_DIRECT`, guesses metadata if needed, and uses metadata `locate_bitmap()` to seek to a bitmap for a selected cluster node.

`bitmap_fd_read()` reads the bitmap superblock with aligned buffers, converts fields from little endian, and, unless brief mode is requested, counts total and dirty bits across the bitmap area.

`ExamineBitmap()` prints bitmap metadata, UUID, event counters, chunk size, write mode, sync size, dirty-bit percentage, and clustered node details. `IsBitmapDirty()` checks all clustered bitmap nodes and returns dirty/clean/error. `CreateBitmap()` writes a bitmap superblock and initializes all bits dirty. `bitmap_update_uuid()` rewrites the bitmap UUID in place.

## Key Behavior
- Bitmap state strings map only known clean/out-of-date values, with unknown fallback.
- Dirty-bit counting treats truncated bitmap files as warnings and counts only readable bits.
- Clustered bitmaps iterate `nodes` and reopen the bitmap at each node slot.
- Default bitmap chunk size grows until the number of chunks stays near the intended limit.
- Created bitmap payload is initialized to `0xff`, marking chunks dirty until synced.

## Integration Notes
The file uses `bitmap_super_t` from `bitmap.h`, metadata-specific bitmap location hooks, mdadm UUID formatting/swapping rules, and common size formatting helpers.

## Risks
`bitmap_fd_read()` must handle `O_DIRECT` alignment correctly. Clustered-node iteration reuses file descriptors and metadata guesses carefully. `CreateBitmap()` writes regular files, while `bitmap_file_open()` only supports block devices for examination.
