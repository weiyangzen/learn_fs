<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/core_priv.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/core_priv.h

## Purpose

`core_priv.h` is a central internal declaration header for RDMA core. It publishes private cross-file contracts for device registration, net namespace metadata, RoCE netdevice/GID management, netlink, address resolution, MAD/SA initialization, security hooks, cgroup charging, QP/CQ helpers, hardware stats, sysfs/client groups, user mmap tracking, and selected CMA dependencies.

## Important APIs, types, and functions

Important local types include `struct pkey_index_qp_list`, `struct rdma_dev_net`, `struct ib_client_nl_info`, `enum ib_cache_gid_default_mode`, and `struct rdma_umap_priv`. The header declares core globals such as `ib_dev_attr_group`, `ib_devices_shared_netns`, and `rdma_dev_net_id`, plus `rdma_net_to_dev_net()`.

Major declaration groups cover device operations (`ib_device_rename()`, `ib_device_set_dim()`, `ib_device_get_by_index()`), RoCE netdevice enumeration and GID updates, GID cache operations and GID type string parsing, setup/cleanup for cache/MAD/SA/address/netlink subsystems, RDMA cgroup charging stubs or real hooks, InfiniBand security stubs or real hooks, netlink resolve handlers, address L2 helpers, hardware stats setup/release, compatibility device toggling, per-port client sysfs groups, net namespace moves, user mmap private initialization, CQ pool cleanup, and privileged QKey policy.

## Control flow

The header itself is declarative. Runtime flow appears in the C files that include it: initialization code calls the `*_init()` declarations, device registration paths call cache/counter/sysfs/security setup, netlink calls the `nldev` and resolve handlers, CMA calls GID and RoCE helpers, and verbs/CQ code calls QP/CQ/cgroup/security helpers. Conditional compilation provides no-op cgroup and security functions when those kernel features are disabled, keeping call sites simple.

## State and persistence

State represented by this header is runtime kernel state: per-net RDMA metadata, per-port P_Key-to-QP lists, GID cache contents, cgroup charges, security caches, hardware stats, client sysfs groups, mmap tracking entries, and CQ pools. There is no disk persistence. Some state is tied to `struct net`, some to `struct ib_device` and per-port data, and some to resource tracking objects.

## Dependencies and integration points

The header depends on Linux list/spinlock/cgroup/net namespace APIs, RDMA verbs, OPA addressing, MAD internals, resource tracking, and local `mad_priv.h`/`restrack.h`. It is consumed broadly across `drivers/infiniband/core`, including CMA, counters, CQ, device registration, cache, sysfs, netlink, address resolution, MAD, SA, verbs, and security code. Because it is private, it coordinates internal implementation without exposing these contracts to external ULPs.

## Risks

This header has high blast radius. Changing declarations, inline stubs, or shared structs can break many RDMA core modules. Conditional stubs must preserve semantics closely enough that call sites do not need feature-specific branching. Net namespace helpers and global IDs must match registration lifetime. GID cache declarations are used by RoCE and CMA path selection, so type parsing, default GID updates, and netdevice association mistakes can break connection setup. Security and cgroup stubs must not accidentally bypass required enforcement when configs are enabled.

## Test signals

Primary signals are full RDMA core builds across configurations with and without `CONFIG_CGROUP_RDMA`, `CONFIG_SECURITY_INFINIBAND`, IPv6, RoCE, and configfs. Runtime validation should include RDMA device registration/unregistration, net namespace moves, netlink enumeration and resolve responses, GID cache updates on netdevice changes, MAD/SA initialization, security policy enforcement where configured, cgroup charging, CQ pool cleanup during device teardown, and sysfs hardware-stat exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/core_priv.h -->
