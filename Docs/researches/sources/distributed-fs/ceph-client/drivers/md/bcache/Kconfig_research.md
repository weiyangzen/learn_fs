# sources/distributed-fs/ceph-client/drivers/md/bcache/Kconfig

## Purpose
This Kconfig file declares bcache configuration options.

## Important APIs, Types, and Functions
It defines `BCACHE`, `BCACHE_DEBUG`, and `BCACHE_ASYNC_REGISTRATION`. `BCACHE` selects `CRC64` and `CLOSURES` and optionally deprecated block holder support with sysfs.

## Control Flow, State, and Persistence
There is no runtime flow. The config controls whether bcache is built and whether debug checks or asynchronous sysfs registration behavior are included.

## Dependencies and Integration Points
It is sourced from `drivers/md/Kconfig` and paired with `drivers/md/bcache/Makefile`. Help text points users to the admin guide.

## Risks and Test Signals
Risks include missing selects for required libraries, debug-only code compile drift, and sysfs async registration behavior being enabled without tests. Test signals are builds with `BCACHE=m/y`, `BCACHE_DEBUG=y`, and `BCACHE_ASYNC_REGISTRATION=y`.
