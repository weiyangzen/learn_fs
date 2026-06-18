# sources/distributed-fs/ceph-client/fs/udf/lowlevel.c

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/lowlevel.c` provides low-level block-device and CD-ROM queries used during UDF mounting, especially multisession optical media handling and last-written-block discovery. The source was read as a complete 62-line implementation.

## Important APIs, Types, and Functions

The public functions are `udf_get_last_session` and `udf_get_last_block`.

## Control Flow

`udf_get_last_session` obtains a `cdrom_device_info` from the superblock block device disk, requests multisession information in LBA format, and returns the session start LBA only when the CD-ROM layer reports an XA multisession address. Otherwise it returns zero. `udf_get_last_block` asks the CD-ROM layer for the last written block; if unavailable, failing, or zero, it falls back to `sb_bdev_nr_blocks`. It returns the last valid block number (`lblock - 1`) or zero if no usable value exists.

## State and Persistence Behavior

The file does not mutate filesystem state. It derives mount-time geometry hints from the underlying block device and CD-ROM subsystem. Returned values influence where superblock and volume descriptors are searched.

## Dependencies and Integration Points

The file depends on Linux block device, CD-ROM, and UDF superblock declarations. It integrates with mount/superblock discovery code that needs the last session start and end-of-media block for optical or removable media.

## Risks and Edge Cases

Non-CD block devices have no `cdrom_device_info` and fall back to zero or block-device size. Bogus CD-ROM layer results are handled by falling back to device size in `udf_get_last_block`. Very large block devices that exceed `udf_pblk_t` return zero to avoid truncation. Returning zero can mean either a legitimate first block or unavailable geometry, so callers must interpret it carefully.

## Test Signals

Tests should cover non-CD block devices, CD devices with and without multisession XA flags, failing `cdrom_get_last_written`, zero last-written values, oversized block-device counts, and mount discovery on single-session and multisession UDF images.
