<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/of.c -->
# sources/distributed-fs/ceph-client/block/partitions/of.c

## Purpose

`of.c` implements partition discovery from Open Firmware device-tree nodes. It scans child nodes of the block device's Open Firmware node, validates `partition-*` nodes, reads their `reg` ranges, and publishes them as Linux partitions.

## Important APIs, Types, And Functions

The entry point is `of_partition(struct parsed_partitions *state)`. `validate_of_partition()` checks node names and slot ranges. `add_of_partition()` reads properties and calls `put_partition()`. It uses Open Firmware helpers such as `disk_to_dev()`, `dev_of_node()`, `for_each_child_of_node()`, `of_node_name_eq()`, `of_property_read_u32()`, and `of_property_read_reg()`.

## Control Flow

`of_partition()` obtains the disk device node and returns `0` when no OF node exists. For each child, `validate_of_partition()` requires a `partition-` prefix and a valid numeric suffix, then rejects slot `0` or slots beyond `state->limit`. `add_of_partition()` reads a 64-bit start and size from `reg`, emits the partition, optionally fills `volname` from `label`, and optionally marks the slot read-only from the `read-only` property.

## State And Persistence Behavior

The parser does not write persistent state. Device-tree properties are the persistent firmware-provided source. It fills `state->parts[slot]`, including metadata and flags, for the current scan.

## Dependencies And Integration Points

It depends on the driver core and Open Firmware APIs plus `check.h`. It integrates with platforms that describe fixed partitions in firmware rather than on the block media itself.

## Risks And Edge Cases

Node naming is strict; malformed `partition-*` suffixes are ignored. Slot `0` is rejected because it represents the whole disk. Missing or invalid `reg` causes the node to be skipped. Labels are copied with `strscpy()`, avoiding unterminated strings. Firmware data can conflict with on-disk partition tables, so parser ordering determines final behavior.

## Test Signals

Tests should include no OF node, valid partition child nodes, malformed names, slot zero, slots beyond limit, missing `reg`, labels, and read-only properties. Expected signals are ` [of]` output on at least one valid partition, correct slot placement, `has_info` for labels, and `ADDPART_FLAG_READONLY` when requested.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/partitions/of.c -->
