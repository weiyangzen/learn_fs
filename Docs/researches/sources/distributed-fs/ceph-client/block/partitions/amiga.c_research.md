<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/amiga.c -->
# sources/distributed-fs/ceph-client/block/partitions/amiga.c

## Purpose
`amiga.c` detects Amiga Rigid Disk Block partition tables and maps valid `PartitionBlock` entries to Linux partitions.

## Important APIs, Types, and Functions
- Entry point: `amiga_partition()`.
- Helper: `checksum_block()` sums big-endian words and expects zero for valid blocks.
- Uses Amiga AFFS hardblock structures `RigidDiskBlock` and `PartitionBlock`.

## Control Flow
The parser scans sectors from zero to `RDB_ALLOCATION_LIMIT` looking for an `IDNAME_RIGIDDISK` block with a valid checksum. It retries checksum validation after zeroing a known Windows-corrupted word range. Once an RDB is found, it derives the logical block-size multiplier and follows the RDB partition-list chain. For each partition block it validates ID and checksum, calculates cylinder blocks from heads and sectors, normalizes by RDB block size, derives start and size from low/high cylinders, checks overflow, then calls `put_partition()`. It prints DOS type and selected environment parameters for mounting diagnostics.

## State and Persistence Behavior
The parser only reads Amiga RDB metadata and writes transient parsed partition records. It emits warnings for invalid checksums, overflow, and 64-bit needs but does not repair metadata.

## Dependencies and Integration Points
It depends on AFFS hardblock definitions, overflow helpers, `check.h`, generic sector reads, and `CONFIG_AMIGA_PARTITION`. It is called from the partition core after several more common parser types.

## Risks and Edge Cases
RDB permits very large 32-bit fields whose products can overflow, so checked arithmetic is central. Logical block sizes other than 512 bytes require normalization. Partition-list block numbers are in the RDB block-size domain and are converted to 512-byte sectors in-place. Bad metadata can create long or invalid chains; the loop bounds partition count to 16.

## Test Signals
Use valid RDB images, corrupted checksum images including the Windows word workaround, oversized arithmetic cases, non-512 RDB block sizes, invalid partition IDs, zero-length partitions, and KASAN/folio leak testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/amiga.c -->
