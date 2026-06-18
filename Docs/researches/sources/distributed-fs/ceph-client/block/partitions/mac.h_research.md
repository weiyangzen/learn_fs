<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.h -->
# sources/distributed-fs/ceph-client/block/partitions/mac.h

## Purpose

`mac.h` defines the Apple Partition Map structures and constants used by `mac.c`. It captures the big-endian on-disk layout for partition entries and driver descriptors.

## Important APIs, Types, And Functions

The header defines `MAC_PARTITION_MAGIC`, `APPLE_AUX_TYPE`, `MAC_STATUS_BOOTABLE`, and `MAC_DRIVER_MAGIC`. `struct mac_partition` contains signature, map count, start block, block count, name, type, data/boot fields, status, boot addresses, checksum, processor, and padding. `struct mac_driver_desc` contains driver descriptor signature, block size, block count, device metadata, and driver count. There are no functions.

## Control Flow

`mac.c` uses `mac_driver_desc.block_size` to determine how to address partition entries and `mac_partition.map_count` to bound the scan. It uses `start_block`, `block_count`, `type`, `status`, `name`, and `processor` to emit partitions and optional boot hints.

## State And Persistence Behavior

These structs model persistent on-disk Apple metadata. They are read directly from sector buffers and interpreted with big-endian accessors. The header itself stores no state.

## Dependencies And Integration Points

It depends on Linux fixed-width integer types already available to includers. It is private to the block partition parser and should remain layout-compatible with the Apple Partition Map disk format.

## Risks And Edge Cases

Because the structures are disk layouts, field size or ordering changes would break parsing. String fields are fixed-width and may lack terminators, so users must compare with bounded string APIs. Numeric fields must be converted from big endian by callers.

## Test Signals

Compile coverage plus `mac.c` parser tests validate this header. Valid images should decode starts and sizes correctly; malformed signatures should not be accepted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/mac.h -->
