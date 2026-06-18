# sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_nic.c

## Purpose
This file manages NIC hardware offload tables for UDP tunnel destination ports. It tracks tunnel port reference counts, queues add/delete operations, synchronizes them to drivers, supports shared hardware tables, handles replay after overflow, exposes dump helpers for ethtool netlink, and reacts to netdevice lifecycle events.

## Important APIs, Types, and Functions
Important types are `struct udp_tunnel_nic`, `struct udp_tunnel_nic_table_entry`, `struct udp_tunnel_nic_info`, `struct udp_tunnel_nic_table_info`, and `struct udp_tunnel_info`. Key functions include `__udp_tunnel_nic_add_port()`, `__udp_tunnel_nic_del_port()`, `udp_tunnel_nic_device_sync_work()`, `udp_tunnel_nic_register()`, `udp_tunnel_nic_unregister()`, `udp_tunnel_nic_flush()`, `udp_tunnel_nic_replay()`, dump helpers, and the exported ops table assigned to `udp_tunnel_nic_ops`.

## Control Flow
On netdevice register, the module validates driver capabilities, allocates per-table entries or joins shared state, stores `dev->udp_tunnel_nic`, and asks tunnel drivers to replay existing ports unless offloads are open-only. Add-port checks device state, static VXLAN special cases, tunnel type/family capability, and port/type collisions; it adjusts an existing entry or allocates a free one, marks add/delete flags, and schedules ordered work. Work runs under RTNL and the device mutex, calls driver `set_port`/`unset_port` or `sync_table`, records failures, and may request replay when missed tables get space. Unregister flushes hardware state and defers freeing while work is pending.

## State and Persistence Behavior
Persistent state is attached to each netdevice in `dev->udp_tunnel_nic` or shared through `udp_tunnel_nic_shared`. Entries store port, tunnel type, flags, use count, and driver-private hardware value. `missed`, `need_sync`, `need_replay`, and `work_pending` encode deferred reconciliation with hardware.

## Dependencies and Integration Points
The file depends on netdevice notifiers, RTNL, an ordered workqueue, ethtool tunnel dump attributes, tunnel driver replay callbacks, driver-provided UDP tunnel NIC info, and the global `udp_tunnel_nic_ops` pointer from the stub.

## Risks
Risks include shared-table lifetime, unregister while async work still references device state, failed hardware operations leaving dodgy entries, port collisions between tunnel types, replay deadlocks if called from notification context, and use-count overflow or underflow. Open-only devices require correct NETDEV_UP/GOING_DOWN flushing.

## Test Signals
Test register validation, add/delete reference counting, sync-by-port and sync-by-table drivers, hardware failure retry, missed-table replay, shared tables across devices, static IANA VXLAN handling, ethtool dump output, NETDEV_UP/GOING_DOWN behavior, and unregister with pending work.
