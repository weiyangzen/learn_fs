# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/ngbe/ngbe_ethtool.h

## Purpose
`ngbe_ethtool.h` exposes the `ngbe` PF ethtool setup hook.

## Important APIs, Types, and Functions
It declares `ngbe_set_ethtool_ops(struct net_device *netdev)`.

## Control Flow
There is no runtime flow in the header. Probe code calls the declared function before registering the netdev.

## State and Persistence Behavior
No state is stored here. The implementation assigns the netdev's ethtool operation table.

## Dependencies and Integration Points
It requires `struct net_device` to be declared by including translation units and links `ngbe_main.c` to `ngbe_ethtool.c`.

## Risks and Edge Cases
The header must stay synchronized with the implementation. Missing inclusion in probe would leave the device without driver-specific ethtool operations.

## Test Signals
Build `ngbe` and verify `ethtool` operations are available after probe.
