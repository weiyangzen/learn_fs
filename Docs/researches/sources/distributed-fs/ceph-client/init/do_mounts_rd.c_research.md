# sources/distributed-fs/ceph-client/init/do_mounts_rd.c

## Purpose
`do_mounts_rd.c` identifies and loads legacy initial ramdisk images into `/dev/ram`, supporting raw filesystem images and compressed images with configured decompressors.

## Important APIs, Types, and Functions
Important globals are `in_file`, `out_file`, `in_pos`, `out_pos`, `rd_image_start`, `exit_code`, and `decompress_error`. Key functions are `ramdisk_start_setup()`, `identify_ramdisk_image()`, `nr_blocks()`, `rd_load_image()`, `compr_fill()`, `compr_flush()`, `error()`, and `crd_load()`.

## Control Flow
`rd_load_image()` opens `/dev/ram` and `/initrd.image`, identifies the image by checking compression signatures and filesystem magic for romfs, cramfs, squashfs, minix, and ext2, then either invokes decompression callbacks or copies block-sized chunks into the ramdisk. It checks ramdisk capacity and unlinks `/dev/ram` at exit.

## State and Persistence Behavior
State is transient file pointers, offsets, decompressor error flags, and the in-memory ramdisk contents. `rd_image_start` from `ramdisk_start=` selects a starting block and is `__initdata`.

## Dependencies and Integration Points
It depends on kernel file I/O, filesystem magic headers, SquashFS private header, generic decompressor selection, ramdisk block device sizing, and `do_mounts_initrd.c`.

## Risks and Test Signals
Risks include magic detection false positives, unavailable decompressor panics, short reads/writes, oversized images, stale static error flags, and deprecated `ramdisk_start=` use. Test signals include each supported filesystem magic, each compression method enabled/disabled, too-large images, read/write error injection, and successful load followed by root mount from ramdisk.
