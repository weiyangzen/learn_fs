# File Research: sources/block-storage/util-linux/libblkid/samples/partitions.c

## Purpose
Sample program that reads and prints partition-table information through libblkid’s binary partition API.

## Main Components
- Creates a filename-backed probe.
- Calls `blkid_probe_get_partitions()` directly.
- Retrieves the root partition table with `blkid_partlist_get_table()`.
- Prints device size, sector size, root table type, table offset, and table ID.
- Iterates partitions with `blkid_partlist_numof_partitions()` and `blkid_partlist_get_partition()`.
- Prints partition number, start, size, numeric type, nested table type when applicable, name, UUID, and type string.

## Behavior
The sample reports failure if no known partition table exists. For nested partition tables, it identifies partitions whose owning table differs from the root table.

## Dependencies and Interactions
Demonstrates the binary API implemented mainly by `src/partitions/partitions.c` and populated by format-specific probers.

## Research Notes
The sample shows that libblkid’s binary partition API is independent of the NAME=value API used by `blkid_do_fullprobe()`.
