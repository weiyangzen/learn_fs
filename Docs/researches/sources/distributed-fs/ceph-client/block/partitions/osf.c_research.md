<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/osf.c -->
# sources/distributed-fs/ceph-client/block/partitions/osf.c

## Purpose

`osf.c` parses OSF/1 disklabels. It reads the disklabel from sector 0, verifies the OSF magic, and publishes up to 18 partitions from the embedded table.

## Important APIs, Types, And Functions

The entry point is `osf_partition(struct parsed_partitions *state)`. It defines `MAX_OSF_PARTITIONS` and `DISKLABELMAGIC`, uses a local packed view of the disklabel, and calls `read_part_sector()`, `put_partition()`, and `put_dev_sector()`.

## Control Flow

The parser reads sector 0, checks `d_magic`, then scans `d_partitions` until either the configured maximum or `state->limit - 1` is reached. Entries with zero size are skipped. Nonzero entries are emitted with little-endian start and size.

## State And Persistence Behavior

There is no persistent kernel state. The persistent state is the OSF disklabel. The parser only populates `parsed_partitions` for the current scan.

## Dependencies And Integration Points

It depends on `check.h` and endian helpers. Its integration is the generic partition parser dispatch for OSF disklabel support.

## Risks And Edge Cases

Malformed sector reads return `-1`; wrong magic returns `0`. The parser trusts the fixed label layout and does not validate checksums or parent bounds. `state->limit` prevents writing past available partition slots.

## Test Signals

Test wrong magic, valid labels with sparse entries, maximum partition count, and read failures. Signals are return codes, emitted slot count, and exact little-endian starts/sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/osf.c -->
