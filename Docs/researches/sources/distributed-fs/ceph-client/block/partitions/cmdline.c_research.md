<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/cmdline.c -->
# sources/distributed-fs/ceph-client/block/partitions/cmdline.c

## Purpose
`cmdline.c` implements partition definitions supplied through the kernel command line `blkdevparts=` parameter, primarily for embedded fixed block devices without on-disk partition tables.

## Important APIs, Types, and Functions
- Runtime structs: `cmdline_subpart` for one named range and `cmdline_parts` for one block device’s partition list.
- Parser helpers: `parse_subpart()`, `parse_parts()`, `cmdline_parts_parse()`, `cmdline_parts_find()`.
- Runtime application: `cmdline_partition()`, `cmdline_parts_set()`, `add_part()`, `cmdline_parts_verifier()`.
- Boot parameter hook: `__setup("blkdevparts=", cmdline_parts_setup)`.

## Control Flow
The setup hook stores the raw command line. On first `cmdline_partition()` call, the raw string is parsed into a linked list of device definitions separated by `;`, with subpartitions separated by `,`. Each subpartition can specify size, optional start after `@`, optional name in parentheses, and flags `ro` and `lk`. The parser finds the matching `state->disk->disk_name`, fills missing starts sequentially, clamps oversize partitions to disk end, adds partitions by byte-to-sector conversion, stores names in `partition_meta_info`, and warns about overlaps.

## State and Persistence Behavior
`cmdline` is a one-shot pointer to boot argument text. Parsed `bdev_parts` is global runtime state retained for later device scans and freed/replaced if a new raw string is parsed. Published partition metadata becomes kernel-visible state; no on-disk metadata is written.

## Dependencies and Integration Points
It depends on `memparse()`, boot `__setup`, generic parser core, partition metadata, block device names, and `CONFIG_CMDLINE_PARTITION`. It has higher probe priority than OF partitioning in `core.c`.

## Risks and Edge Cases
The parser mutates `subpart->from` and `subpart->size` while applying to a disk, so repeated rescans use adjusted values. `PF_POWERUP_LOCK` is parsed but not applied in `add_part()`. Overlapping partitions are allowed but warned. Invalid size below `PAGE_SIZE` rejects a subpartition. `-` size means consume remainder.

## Test Signals
Boot tests with multiple devices, named/unnamed partitions, explicit and implicit starts, remainder sizes, read-only flags, overlaps, invalid syntax, no matching device, repeated rescans, and byte-sector conversion boundary cases are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/cmdline.c -->
