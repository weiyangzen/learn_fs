# File Research: sources/cow-pools/openzfs/module/os/linux/zfs/trace.c

## Purpose

Defines ZFS tracepoints exactly once for kernel builds.

## Contents

The file includes core ZFS headers needed by tracepoint definitions, then under `_KERNEL` defines `CREATE_TRACE_POINTS` and includes trace headers for:

- ACL
- ARC
- debug messages
- dbuf
- DMU
- dnode
- multilist
- rrwlock
- txg
- vdev
- ZIL
- ZIO
- zrlock

## Notes

There is no runtime control flow. This is a compilation unit whose purpose is tracepoint ownership and link-time definition.
