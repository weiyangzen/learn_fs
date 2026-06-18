# sources/distributed-fs/ceph-client/net/openvswitch/dp_notify.c

## Purpose

This file handles netdevice unregister notifications for Open vSwitch vports backed by ordinary netdevices. When an external device disappears, it schedules OVS work to detach the corresponding vport and multicast a vport deletion notification.

## Important APIs, Types, and Functions

The exported object is `ovs_dp_device_notifier`. Its callback `dp_device_event()` reacts to `NETDEV_UNREGISTER`. The workqueue function `ovs_dp_notify_wq()` scans all datapaths in the net namespace and detaches vports whose devices are no longer OVS ports. `dp_detach_port_notify()` builds the deletion netlink message with `ovs_vport_cmd_build_info()`, detaches the port, and multicasts on `dp_vport_genl_family`.

## Control Flow

On netdevice events, internal OVS devices are ignored. For non-internal devices, the callback looks up the associated vport. If the event is unregister, it immediately calls `ovs_netdev_detach_dev()` to unlink upper device state and decrement promiscuity, then queues `dp_notify_work` on `system_percpu_wq`.

The work function takes `ovs_mutex`, walks all datapaths and vport hash buckets, skips internal vports, identifies vports whose device no longer reports `netif_is_ovs_port()`, and detaches/notifies each one.

## State and Persistence

No independent durable state is owned here. It uses per-net `ovs_net->dp_notify_work`, datapath vport tables, and vport device association. Detach operations mutate datapath port membership.

## Dependencies and Integration Points

It depends on Linux netdevice notifier infrastructure, generic netlink multicast, OVS datapath helpers, internal-device helpers, and netdev vport helpers. It is registered and unregistered by `datapath.c` module lifecycle.

## Risks and Edge Cases

Detach is deferred because notifier context is not the right place to destroy the vport fully. If notification allocation fails, the port is still detached and netlink error is set for listeners. The scanner must hold `ovs_mutex` while walking and modifying vport hash lists.

## Test Signals

Tests should unregister a netdev-backed OVS port and verify immediate netdev detach, later vport deletion, multicast notification, no action for internal ports, correct behavior when notification allocation fails, and safe operation during concurrent datapath deletion.
