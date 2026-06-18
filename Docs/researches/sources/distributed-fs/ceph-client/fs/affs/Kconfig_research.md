# sources/distributed-fs/ceph-client/fs/affs/Kconfig

## Purpose
This Kconfig entry exposes Amiga Fast File System support as `AFFS_FS`.

## Important APIs, types, and functions
It is declarative build configuration. `AFFS_FS` is a tristate depending on `BLOCK`, selecting `BUFFER_HEAD` and `LEGACY_DIRECT_IO`. Help text documents read/write support for Amiga FFS partitions and loop-mounted emulator disk images.

## Control flow
When enabled as built-in or module, kbuild descends through the AFFS Makefile and builds `affs.o`; otherwise no AFFS code is compiled.

## State and persistence
The only state is `.config` selection. Runtime state is in the compiled filesystem driver.

## Dependencies and integration points
The dependency on block devices and selected buffer-head/direct-I/O helpers matches AFFS's buffer_head-based metadata and direct-I/O implementation in `file.c`.

## Risks and test signals
Risks are stale dependency declarations or missing helper selections causing randconfig build failures. Test signals include `AFFS_FS=y`, `AFFS_FS=m`, `BLOCK=n`, and configs with or without legacy direct I/O support.
