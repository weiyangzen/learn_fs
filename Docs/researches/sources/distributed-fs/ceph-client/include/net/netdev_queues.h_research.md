<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_queues.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_queues.h

## Purpose
`netdev_queues.h` defines queue configuration/statistics APIs, RX queue management operation contracts, and lockless TX queue stop/wake helper macros for drivers.

## Important APIs, types, and functions
Key types are `struct netdev_config`, `struct netdev_queue_config`, RX/TX queue stats structs, `struct netdev_stat_ops`, and `struct netdev_queue_mgmt_ops`. Functions and macros include `netdev_stat_queue_sum`, `netdev_queue_config`, `netif_rxq_has_unreadable_mp`, `netif_txq_try_stop`, `netif_txq_maybe_stop`, `__netif_txq_completed_wake`, subqueue wrappers, `netif_xmit_timeout_ms`, queue DMA-device lookup, create/lease/busy checks.

## Control flow
Stats callbacks gather base and active queue counters under the appropriate device/RTNL lock. Queue management allocates memory while closed, starts/stops queues while open, validates queue configs, and may create virtual queues. TX macros implement a single-producer/single-consumer stop/wake protocol with barriers paired through BQL or explicit memory barriers.

## State and persistence
State includes queue configs, driver per-queue memory, active RX/TX queue stats, BQL accounting, TX queue stopped state, descriptor indexes supplied by drivers, and optional queue leases. The header itself stores no globals.

## Dependencies and integration points
It depends on netdevice, netlink extack through declarations, BQL, jiffies, and netdev ops locking. It integrates modern queue control, stats, and zero-copy queue leasing.

## Risks and test signals
Risks include side effects in macro arguments due to multiple evaluation, wrong descriptor threshold selection, missing producer/consumer barriers, stats fields left undefined in base callbacks, queue config validation drift, and queue leasing lifetime. Tests should cover ring-full/ring-space races, BQL on/off, queue restart, per-queue stats totals, DMA device lookup, and virtual queue creation/lease.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_queues.h` completely for this pass (393 lines, 13526 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_queues.h -->
