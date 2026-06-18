<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/affs_hardblocks.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/affs_hardblocks.h

## Purpose
Defines Amiga Rigid Disk Block and partition block layouts used by AFFS-related partition/disk parsing.

## Important APIs, Types, And Functions
`struct RigidDiskBlock` describes RDB metadata, geometry, linked-list block pointers, and vendor/product strings. `struct PartitionBlock` describes partition block metadata and environment arrays. `IDNAME_RIGIDDISK`, `IDNAME_PARTITION`, and `RDB_ALLOCATION_LIMIT` are exported constants.

## Control Flow
Disk scanning code looks for the big-endian `RDSK` identifier, validates checksum/summed longs, follows partition and filesystem-header block lists, and decodes partition environment values.

## State And Persistence
The structs are persistent on-disk big-endian records. Kernel/userspace code uses them as ABI descriptions of Amiga disk metadata.

## Dependencies And Integration Points
Depends on Linux integer/endian types. Integrates with AFFS, partition scanners, Amiga disk image tools, and block-device probing.

## Risks And Edge Cases
Big-endian fields on little-endian hosts, untrusted linked block lists, checksum validation, and fixed vendor string lengths are the main hazards.

## Test Signals
Use known RDB disk images, verify identifier/checksum handling, partition list traversal bounds, endian conversion, and rejection of malformed list pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/affs_hardblocks.h -->
