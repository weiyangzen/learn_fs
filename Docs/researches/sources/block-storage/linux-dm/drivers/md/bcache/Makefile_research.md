# File Research: sources/block-storage/linux-dm/drivers/md/bcache/Makefile

## Purpose
Builds the bcache module or built-in object from its component implementation files.

## Main Contents
`obj-$(CONFIG_BCACHE) += bcache.o` and `bcache-y` aggregates allocation, bset, btree, closure, debug, extents, IO, journal, moving GC, request, stats, superblock/sysfs, trace, util, writeback, and features code.

## Integration Points
The object list is the compilation boundary for the single bcache driver. Files in this research group provide key metadata, allocation, btree, and helper portions of that aggregate.

## Risks And Review Focus
- New bcache compilation units must be added here or they will not be linked.
- Ordering is less explicit than the parent Makefile, but missing core helpers produce link-time failures across the monolithic `bcache.o`.
