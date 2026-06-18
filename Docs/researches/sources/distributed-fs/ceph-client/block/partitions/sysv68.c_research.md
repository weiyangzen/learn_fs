<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sysv68.c -->
# sources/distributed-fs/ceph-client/block/partitions/sysv68.c

## Purpose

`sysv68.c` parses Motorola/System V/68 disk labels. It reads the volume id, disk configuration, and slice table from sector 0 and publishes valid slices.

## Important APIs, Types, And Functions

The entry point is `sysv68_partition(struct parsed_partitions *state)`. Local structures `volumeid`, `dkconfig`, `dkblk0`, and `slice` describe the disk-resident label. The parser uses `read_part_sector()`, endian/access helpers, and `put_partition()`.

## Control Flow

The parser reads sector 0, validates the expected volume id and configuration magic/checksum fields, then scans the fixed slice table. Valid slices are emitted until `state->limit` is reached. It prints a label marker on success and releases the sector on all paths.

## State And Persistence Behavior

No state persists in the kernel. The persistent state is the SysV68 disk label and slice table; emitted `parsed_partitions` entries are transient.

## Dependencies And Integration Points

It depends on `check.h` and kernel integer/endian APIs. It integrates only with the generic partition parser framework.

## Risks And Edge Cases

Because this is a legacy format with fixed structs, layout and endian interpretation are the main risks. Bad checksum/magic should cause return `0`, while read failure returns `-1`. Slice starts and sizes are trusted after label validation.

## Test Signals

Tests should include invalid volume ids, invalid configuration/checksum, empty slices, maximum slices, and valid labels. Expected signals are no output for rejected labels and correctly emitted slice starts/sizes for accepted images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/sysv68.c -->
