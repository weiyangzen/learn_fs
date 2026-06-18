<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/karma.c -->
# sources/distributed-fs/ceph-client/block/partitions/karma.c

## Purpose

`karma.c` recognizes the simple Rio Karma media-player partition label. It is a small partition parser that reads sector 0, checks a `0xAB56` little-endian magic, and publishes up to two firmware-defined data partitions.

## Important APIs, Types, And Functions

The only entry point is `karma_partition(struct parsed_partitions *state)`. It uses a packed local `disklabel` containing two `d_partition` records, each with filesystem type, offset, and size. It calls `read_part_sector()`, `put_partition()`, `seq_buf_puts()`, and `put_dev_sector()`.

## Control Flow

The parser reads sector 0 and returns `-1` on read failure. If `d_magic` is not `KARMA_LABEL_MAGIC`, it releases the sector and returns `0` so other partition parsers may try. When the magic matches, it scans two entries, emits a partition only when `p_fstype == 0x4d` and `p_size` is nonzero, increments the visible slot for each table entry, and stops when reaching `state->limit`.

## State And Persistence Behavior

There is no mutable or persistent kernel state. The persistent format is the Rio Karma on-disk sector-0 label; the parser only fills `parsed_partitions` for the current scan.

## Dependencies And Integration Points

It depends only on `check.h` and core compiler attributes. Its integration point is the block partition parser dispatch that calls `karma_partition()` when the corresponding partition support is configured.

## Risks And Edge Cases

The parser assumes the label layout is packed and sector 0 is readable. It intentionally accepts only type `0x4d`; other entries are ignored even if they have sizes. Slot accounting still advances for ignored entries, preserving physical table position but possibly leaving holes. `state->limit` prevents overflowing the parser result table.

## Test Signals

Tests should cover absent magic, a read failure, two valid partitions, zero-size entries, wrong filesystem types, and a small `state->limit`. Expected signals are return `0` for non-Karma disks, return `1` with a trailing newline for valid labels, and partition offsets/sizes matching little-endian fields exactly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/karma.c -->
