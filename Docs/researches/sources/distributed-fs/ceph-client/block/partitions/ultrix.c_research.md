<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ultrix.c -->
# sources/distributed-fs/ceph-client/block/partitions/ultrix.c

## Purpose

`ultrix.c` parses Ultrix partition tables. It checks for Ultrix magic and validity flags in sector 0 and publishes the fixed set of partition entries.

## Important APIs, Types, And Functions

The entry point is `ultrix_partition(struct parsed_partitions *state)`. It defines `PT_MAGIC` and `PT_VALID`, uses local disklabel structures, and calls `read_part_sector()`, `put_partition()`, and `put_dev_sector()`.

## Control Flow

The parser reads sector 0. If the magic or valid flag is absent, it returns `0`. For valid labels, it scans the table, skips zero-size entries, emits partitions up to `state->limit`, appends a newline, and returns `1`.

## State And Persistence Behavior

There is no long-lived state. The on-disk Ultrix table is persistent input, while `parsed_partitions` is the transient output of the scan.

## Dependencies And Integration Points

It depends on `check.h` and standard kernel integer helpers. It integrates through the block partition parser list.

## Risks And Edge Cases

The parser is intentionally simple and trusts the label once magic/valid checks pass. It does not do deep capacity validation. Read failures must release no invalid sectors and return `-1`.

## Test Signals

Tests should cover wrong magic, invalid flag, sparse entries, full entry count, and partition-table limits. Expected signals are return `0` for non-Ultrix disks and correct partition emission for valid labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/ultrix.c -->
