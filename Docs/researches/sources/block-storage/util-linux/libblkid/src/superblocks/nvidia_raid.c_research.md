# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/nvidia_raid.c

## Scope

Detects NVIDIA RAID member metadata.

## Behavior

- Reads a fixed-size metadata block two sectors from the end of a whole disk or regular file.
- Validates vendor signature, metadata size, and additive checksum.
- Exports RAID member version and records the signature as the magic.

## Dependencies And Risks

- Skips partitions/non-whole-disk block devices to avoid false positives.
- Depends on `pr->size` sector arithmetic; minimum size is enforced by idinfo.
- Checksum count is bounded by the buffer size before iteration.
