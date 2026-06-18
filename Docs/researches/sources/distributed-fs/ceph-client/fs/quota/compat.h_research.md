# sources/distributed-fs/ceph-client/fs/quota/compat.h

## Purpose
`compat.h` defines 32-bit userspace compatibility layouts for quota ioctl data structures.

## Important APIs, types, and functions
It declares `struct compat_if_dqblk`, `struct compat_fs_qfilestat`, and `struct compat_fs_quota_stat` using `compat_*` fixed ABI types.

## Control flow
There are no functions; quota compat ioctl handlers include these definitions when translating between 32-bit userspace structures and native kernel quota structures.

## State and persistence
The header has no runtime state. It preserves ABI layout compatibility for quota state exchanged with userspace.

## Dependencies and integration points
It depends on `linux/compat.h` and integrates with quota ioctl compatibility code and filesystem quota stat reporting.

## Risks and test signals
Risks include field layout drift from userspace ABI, signedness/width mismatches, and missing fields compared with native structures. Test signals include 32-bit quotactl tests on a 64-bit kernel, structure size/layout checks, and quota stat/block limit round trips with large values.
