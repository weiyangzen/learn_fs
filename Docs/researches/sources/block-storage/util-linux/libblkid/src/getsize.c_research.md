# File Research: sources/block-storage/util-linux/libblkid/src/getsize.c

## Purpose
Small public helper for returning a block device or regular file size in bytes.

## Main Components
- `blkid_get_dev_size(int fd)` calls `blkdev_get_size()`.
- Returns the byte count on success.
- Returns `0` if size retrieval fails.

## Dependencies and Interactions
Uses util-linux block-device helper `blkdev_get_size()` through `blkidP.h`. Declared in the public header as `blkid_get_dev_size()`.

## Research Notes
The function collapses all errors to `0`, so callers cannot distinguish an error from a genuinely empty object through this API alone.
