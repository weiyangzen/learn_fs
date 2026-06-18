# sources/distributed-fs/ceph-client/include/linux/fcdevice.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/fcdevice.h` declares the Fibre Channel netdevice allocation helper. The source was read as a complete 28-line file for this report.

## Important APIs, Types, and Functions

It includes `linux/if_fc.h` and declares `alloc_fcdev(int sizeof_priv)` for kernel builds.

## Control Flow

There is no local flow. Fibre Channel network drivers call `alloc_fcdev()` to allocate a `net_device` with FC-specific setup and private data.

## State and Persistence Behavior

No state is owned here. State lives in allocated `net_device` instances and driver private areas.

## Dependencies and Integration Points

It integrates with the networking core, `struct net_device`, and Fibre Channel link-layer definitions from `if_fc.h`.

## Risks and Edge Cases

The header is legacy and narrowly scoped; risks are mostly build/API drift with netdevice allocation and FC header definitions.

## Test Signals

Build coverage of FC network drivers and probe/remove tests that allocate and free FC netdevices.
