<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/aix.c -->
# sources/distributed-fs/ceph-client/block/partitions/aix.c

## Purpose
`aix.c` recognizes a simple AIX LVM layout and exposes contiguous logical volumes as Linux partitions. It supports only the simple case where logical volumes occupy contiguous physical partitions.

## Important APIs, Types, and Functions
- Parser entry point: `aix_partition()`.
- Disk-reading helpers: `read_lba()`, `alloc_pvd()`, and `alloc_lvn()`.
- On-disk structs: `lvm_rec`, `vgda`, `lvd`, `lvname`, `ppe`, and `pvd`.
- Internal `lv_info` tracks expected physical partitions per logical volume, discovered count, and contiguity.

## Control Flow
The parser reads sector 7 and checks the LVM record version. Version 1 yields physical-partition size, VGDA length, and VGDA sector. It reads VGDA metadata to discover logical-volume count, reads logical-volume descriptors and names, then reads a physical-volume descriptor. It scans physical partition entries, tracking contiguous logical partition indices for each LV. When the final expected LP for an LV is seen in order, it publishes one partition covering the contiguous extent and prints the LV name. Non-contiguous LVs are warned and skipped.

## State and Persistence Behavior
The parser creates transient allocations for LV names, PVD, and `lv_info`; it writes only `parsed_partitions`. It does not mutate AIX metadata. The resulting partition numbers are LV index plus one, bounded by `state->limit`.

## Dependencies and Integration Points
It depends on `check.h`, big-endian field conversion, generic sector reads, and partition core probing. It is enabled by `CONFIG_AIX_PARTITION`.

## Risks and Edge Cases
Only LVM version 1 is supported; other versions produce informational output and no partitions. Large shifts from `pp_size` need sane on-disk data. The parser assumes VGDA/PVD offsets used by supported simple layouts. Non-contiguous logical volumes are intentionally not exposed, avoiding misleading block-device ranges.

## Test Signals
Test with simple contiguous AIX LVM images, non-contiguous LV images, unsupported LVM version, truncated VGDA/PVD/name tables, large physical partition sizes, and allocation-failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/aix.c -->
