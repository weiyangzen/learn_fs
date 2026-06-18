# File Research: sources/block-storage/util-linux/libblkid/src/topology/sysfs.c

## Scope

Provides primary Linux topology probing through `/sys/dev/block`.

## Behavior

- Reads sysfs attributes for alignment offset, minimum I/O size, optimal I/O size, physical block size, DAX, and disk sequence.
- For partitions, falls back to parent whole-disk attributes through the sysfs path context.
- Counts successfully exported values and returns success if any topology value was set.

## Dependencies And Risks

- Preferred topology source on modern Linux.
- Depends on util-linux sysfs path helpers and kernel ABI attribute names.
- Setter functions ignore zero values, so successful reads of zero may not count as exported topology.
