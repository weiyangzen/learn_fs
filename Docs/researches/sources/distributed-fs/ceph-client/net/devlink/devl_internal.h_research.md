# sources/distributed-fs/ceph-client/net/devlink/devl_internal.h

## Purpose

`devl_internal.h` is the private header tying the devlink implementation together. It defines the internal `struct devlink`, shared state structures, lock and registration assertions, netlink dump state, notification helpers, and cross-module prototypes.

## Important APIs, Types, and Functions

The central type is `struct devlink`, containing the global index, child object collections, ops pointers, namespace, mutex, refcount, RCU work, nested relationship state, reload stats, and private driver storage. Other important definitions are `struct devlink_dev_stats`, `DEVLINK_REGISTERED`, `DEVLINK_RELOAD_STATS_ARRAY_SIZE`, `devlinks_xa_for_each_registered_get`, `devl_dev_lock()`, `devl_dev_unlock()`, `struct devlink_nl_dump_state`, `devlink_nl_put_handle()`, `devlink_nl_put_u64()`, `struct devlink_obj_desc`, and notification send helpers.

## Control Flow

This header supplies inline helpers used by generated netlink handlers and feature modules. Pre-doit code resolves and locks a devlink, handlers use `info->user_ptr`, fill replies with `devlink_nl_put_handle()`, and notifications use `devlink_nl_obj_desc_init()` plus multicast filtering. Assertions encode the lifecycle split: before registration drivers initialize without userspace concurrency; after registration the devlink lock serializes userspace and driver access.

## State and Persistence Behavior

The header itself stores no state, but it defines the persistent fields that every devlink instance carries. Dump state persists across multipart netlink dump callbacks through `netlink_callback::ctx`, tracking instance index, subobject index, region offsets, health dump timestamps, and resource port context.

## Dependencies and Integration Points

It includes device, netdevice, net namespace, rtnetlink, RDMA verbs, public devlink API, and generated netlink definitions. All devlink C files in this subset depend on it for shared declarations and invariants.

## Risks

Changing `struct devlink` layout or lock semantics affects every devlink module. Dump-state union reuse requires each dump handler to reset fields correctly when moving between instances. Inline notification filters rely on object descriptors containing enough stable identity to filter multicast messages safely.

## Test Signals

Build coverage is the primary signal for prototype drift. Runtime tests should exercise all dump handlers across multiple devlinks and ports, lockdep assertions for registered versus unregistered phases, and multicast filtering by bus, device, index, and port.
