# sources/distributed-fs/ceph-client/include/uapi/linux/netdev.h

## Purpose
Defines the auto-generated generic netlink ABI for netdev introspection and control: XDP features, page pools, NAPI, queues, qstats, dmabuf binding, queue leases, and netdev multicast groups.

## Important APIs, Types, And Functions
Exports `NETDEV_FAMILY_NAME`, `NETDEV_FAMILY_VERSION`, feature enums `netdev_xdp_act`, `netdev_xdp_rx_metadata`, `netdev_xsk_flags`, queue/qstats/NAPI enums, many `NETDEV_A_*` attribute families, `NETDEV_CMD_*`, and multicast groups `NETDEV_MCGRP_MGMT`/`PAGE_POOL`.

## Control Flow
Userspace sends generic netlink get/set/bind/create requests and receives device, page-pool, queue, NAPI, qstats, lease, and dmabuf attributes. Notifications report device and page-pool add/delete/change events.

## State, Persistence, And Dependencies
State is live netdevice, NAPI, queue, page-pool, AF_XDP, dmabuf, and lease state in the kernel. The header is generated from `netdev.yaml`.

## Integration Points
Used by YNL tools, network diagnostics, AF_XDP setup, page-pool observability, and advanced queue binding.

## Risks
Generated numeric attributes are ABI. Some enums are bitmasks while others are ordinal. Empty enum families exist as generated placeholders and should be tolerated by clients.

## Test Signals
Validate YNL schema conformance, dev get/dump, page-pool stats, NAPI set/get, queue/qstats get, dmabuf bind, RX/TX bind, queue create, multicast notifications, and feature bit decoding.
