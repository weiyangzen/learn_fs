<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_failover.h -->
# sources/distributed-fs/ceph-client/include/net/net_failover.h

## Purpose
`net_failover.h` defines the generic net failover private state and feature masks used to pair a standby virtual netdevice with a primary device of the same MAC.

## Important APIs, types, and functions
It defines `struct net_failover_info`, `net_failover_create`, `net_failover_destroy`, `FAILOVER_VLAN_FEATURES`, and `FAILOVER_ENC_FEATURES`.

## Control flow
A standby device creates a failover instance; the failover core tracks RCU primary and standby devices, aggregates stats, and migrates traffic/features as devices appear or disappear.

## State and persistence
Runtime state includes RCU primary/standby netdevice pointers, separate and aggregated rtnl stats, and a spinlock protecting stats updates.

## Dependencies and integration points
It depends on the generic failover framework and netdevice feature flags. It integrates virtio/netvsc-style failover devices with the network stack.

## Risks and test signals
Risks include RCU device lifetime, stats aggregation races, inconsistent feature masks, and MAC matching assumptions. Tests should cover primary add/remove, standby teardown, stats reads under traffic, VLAN/encap feature propagation, and failover during carrier changes.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_failover.h` completely for this pass (40 lines, 1023 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_failover.h -->
