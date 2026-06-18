# sources/distributed-fs/ceph-client/net/l3mdev/Makefile

## Purpose
The Makefile builds the L3 master device API implementation.

## Important APIs, Types, and Functions
It contains a single object rule, `obj-y += l3mdev.o`, so `l3mdev.c` is built into the networking core when the directory is included by the parent build.

## Control Flow
There is no runtime control flow. The parent networking build and Kconfig determine whether this directory participates, and this file contributes `l3mdev.o`.

## State and Persistence
No state is persisted here. The rule only affects build composition.

## Dependencies and Integration Points
The object exports GPL symbols used by routing, FIB rule, and device-driver code. Because it is `obj-y`, consumers expect the helper symbols to be present whenever the containing build path is enabled.

## Risks and Edge Cases
Changing `obj-y` to conditional or modular output would affect exported-symbol availability and could break built-in callers. The file deliberately has no additional object list.

## Test Signals
Build tests should ensure `l3mdev.o` is linked when `NET_L3_MASTER_DEV` support is configured and that no missing-symbol errors appear for l3mdev consumers.
