# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/fsmount.sh

## Purpose
This generator emits mount attribute flag arrays for `fsmount.c`.

## Important APIs, Types, And Functions
It reads `mount.h` from an optional/default UAPI linux header directory and emits `static const char *fsmount_attr_flags[]`.

## Control Flow
The script filters `MOUNT_ATTR_` hex defines whose suffix starts with an alphanumeric character, excludes `MOUNT_ATTR_RELATIME` because it is zero-valued, strips the prefix, and indexes names by `ilog2(value) + 1`.

## State, Dependencies, And Integration
It writes generated C to stdout for inclusion by `fsmount.c`. It assumes one-bit hex flag values except for deliberately excluded/special mask values.

## Risks And Test Signals
Mask constants and zero constants need C-side handling rather than generated bit-array entries. Build generation plus `perf trace` formatting tests for mount attributes are the relevant signals.
