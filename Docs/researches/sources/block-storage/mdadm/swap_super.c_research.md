# File Research: sources/block-storage/mdadm/swap_super.c

## Purpose
Standalone utility/test program that endian-swaps a legacy 0.90 md superblock in place on a device.

## Main Responsibilities
- Opens one block device read/write.
- Uses `BLKGETSIZE` to compute the 0.90 tail superblock offset.
- Reads 4096 bytes, swaps every 32-bit word, then separately swaps `events_hi/events_lo` and `cp_events_hi/cp_events_lo`.
- Writes the modified 4096-byte block back.

## Integration
This is not normal mdadm operational code. The file comment explicitly warns not to use it on real arrays and says to use mdadm instead.

## Risks and Edge Cases
- It mutates metadata in place with no checksum repair or validation.
- Uses old `BLKGETSIZE`, so it is only suitable for legacy/manual testing.
