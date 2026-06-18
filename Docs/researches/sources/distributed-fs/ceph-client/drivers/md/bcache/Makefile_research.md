# sources/distributed-fs/ceph-client/drivers/md/bcache/Makefile

## Purpose
The bcache Makefile builds the monolithic `bcache.o` module from its component objects.

## Important APIs, Types, and Functions
`bcache-y` includes allocation, bset, btree, debug, extents, IO, journal, moving GC, request, stats, superblock, sysfs, trace, util, writeback, and feature objects.

## Control Flow, State, and Persistence
There is no runtime flow. Object composition matters because many files share internal symbols and initialize global workqueues, sysfs types, and metadata handlers inside one module.

## Dependencies and Integration Points
It is controlled by `CONFIG_BCACHE` from Kconfig and integrates bcache into `drivers/md/Makefile` through `obj-$(CONFIG_BCACHE) += bcache/`.

## Risks and Test Signals
Risks include missing new objects from `bcache-y`, link failures from conditional debug code, and trace object dependencies. Test signals are `BCACHE=m` and `BCACHE=y` builds with debug and async registration toggled.
