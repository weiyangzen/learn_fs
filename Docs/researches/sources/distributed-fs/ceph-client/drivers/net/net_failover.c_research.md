# sources/distributed-fs/ceph-client/drivers/net/net_failover.c

## Purpose
This file implements the `net_failover` upper netdev used by paravirtualized drivers to present a stable interface backed by a standby paravirtual device and an optional primary direct-attached VF. It provides active-backup transmit behavior, lower device registration hooks for the generic failover core, statistics folding across lower devices, VLAN and multicast synchronization, and public create/destroy APIs.

## Important APIs, Types, and Functions
The central private state is `struct net_failover_info` from `<net/net_failover.h>`, containing RCU-protected `primary_dev` and `standby_dev` pointers, stats snapshots, and a stats lock. Exported APIs are `net_failover_create()` and `net_failover_destroy()`. Netdev operations include open/close, start xmit, select queue, get stats, change MTU, set RX mode, VLAN add/del, address validation, and feature checks. Failover integration uses `struct failover_ops net_failover_ops` with slave pre-register/register/unregister/link/name-change and RX handler callbacks.

## Control Flow
Create allocates an Ethernet upper with 16 queues, copies the standby MAC and MTU bounds, sets failover features/flags, registers the upper netdev, then registers with the generic failover core. Opening the upper opens primary then standby lowers and enables carrier/queues if either lower is ready. Transmit first tries the primary lower if running and carrier-up, falls back to standby, and drops if neither can transmit. Queue selection delegates to the primary when present, stores the original queue mapping for later restoration, and folds the selected queue into the upper queue range. Slave registration aligns MTU, holds the lower device, opens it if needed, syncs unicast/multicast lists and VLANs, assigns it to primary or standby based on parent device identity, snapshots stats, recomputes features, and emits `NETDEV_JOIN`. Unregistration reverses VLAN/address sync, closes and drops the lower, clears the RCU pointer, recomputes features, and preserves accumulated stats.

## State and Persistence
State is runtime-only: RCU pointers to lower devices, cached stats snapshots, accumulated failover stats, upper netdev flags/features, lower VLAN/address lists, and carrier/queue state. No data survives module unload or device destruction. RCU is used for fast transmit/RX paths, RTNL for structural changes, and `stats_lock` for stats folding.

## Dependencies and Integration Points
The file depends on netdevice core, etherdevice helpers, ethtool, VLAN helpers, PCI device checks, netpoll headers, RTNL, scheduler queue metadata, and the generic failover infrastructure. Paravirtual drivers call `net_failover_create()` with their standby device and later call `net_failover_destroy()`. The generic failover core discovers and binds compatible primary VF devices by MAC and invokes these operations.

## Risks and Edge Cases
Primary eligibility is approximated by requiring a PCI parent because there is no generic VF test. If standby VLAN synchronization fails after primary VLAN setup, the code rolls back the primary VLAN add. MTU changes roll back primary MTU if standby fails, but lower devices may have side effects. RX handler drops standby-origin frames with `RX_HANDLER_EXACT` while primary exists, enforcing primary preference but making standby receive inactive until failover. Stats folding filters negative deltas and handles apparent 32-bit counters, but lower driver stat resets can still make accounting approximate. Destroy assumes proper failover core serialization under RTNL.

## Test Signals
Tests should create/destroy failover devices, attach/detach standby and PCI primary lowers, verify transmit preference and fallback, check carrier transitions on lower link changes, exercise MTU and VLAN rollback paths, confirm multicast/unicast list propagation, validate RX handler behavior, and inspect folded stats across lower removal/re-add. Live migration scenarios should show traffic moving from VF to standby when the VF unregisters.
