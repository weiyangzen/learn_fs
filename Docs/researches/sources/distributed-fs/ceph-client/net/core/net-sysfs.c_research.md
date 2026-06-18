# sources/distributed-fs/ceph-client/net/core/net-sysfs.c

## Purpose

`net-sysfs.c` implements the `net` device class and its sysfs ABI. It exposes net_device attributes, statistics, physical-port metadata, RX queue controls, TX queue controls, BQL/XPS/RPS settings, namespace ownership, uevents, OpenFirmware lookup helpers, and netdev kobject registration/unregistration.

## Important APIs, Types, And Functions

Public functions include `netdev_kobject_init()`, `netdev_register_kobject()`, `netdev_unregister_kobject()`, `net_rx_queue_update_kobjects()`, `netdev_queue_update_kobjects()`, `netdev_change_owner()`, `netdev_class_create_file_ns()`, `netdev_class_remove_file_ns()`, `rps_cpumask_housekeeping()`, and `of_find_net_device_by_node()` when OF is enabled.

The file defines `net_class`, `net_ns_type_operations`, RX queue and TX queue kobject types, sysfs ops wrappers for queue attributes, and large attribute groups for netdev fields, statistics, physical-port fields, wireless placeholder directories, RX queue RPS attributes, TX queue XPS/maxrate/traffic-class attributes, and BQL attributes.

## Control Flow

`netdev_register_kobject()` initializes the embedded `struct device`, binds it to `net_class`, attaches default and device-specific groups, calls `device_add()`, creates the `queues` kset, then adds RX and TX queue kobjects. `netdev_unregister_kobject()` suppresses uevents for dead namespaces, holds a kobject reference, removes queue kobjects, disables memalloc-noio runtime PM behavior, and calls `device_del()`. Final memory release happens in `netdev_release()` after the device kobject refcount reaches zero.

Attribute reads generally use `netdev_show()` with RCU and `dev_isalive()`. Writes use `netdev_store()` for RTNL-protected changes or `netdev_lock_store()` for netdev-lock-protected changes after `CAP_NET_ADMIN` checks. `sysfs_rtnl_lock()` is a key deadlock-avoidance helper: it takes a temporary device reference, breaks kernfs active protection, obtains RTNL interruptibly, checks the device is still alive, then restores active protection.

RX queue setup creates `rx-N` kobjects, optional RPS attributes, optional driver queue groups, and default RPS masks. TX queue setup creates `tx-N` kobjects, default queue groups, optional BQL groups, and XPS/maxrate attributes. Queue update functions add kobjects for new queue counts and remove groups/kobjects for shrinking counts, suppressing uevents when the namespace is already dying.

## State And Persistence Behavior

State is mostly live kernel object state projected into sysfs. Some writes mutate net_device fields or driver state: MTU, flags, carrier, tx queue length, alias, group, protocol-down state, GRO flush timeout, deferred hard IRQs, threaded NAPI, RPS maps, RPS flow tables, XPS maps, TX maxrate, and BQL tunables. Queue kobject release callbacks clear kobject memory so queues can be re-registered later and drop device references. Ownership changes are persisted in sysfs inode ownership until the device moves again or is removed.

## Dependencies And Integration Points

This file integrates with sysfs/kernfs, device core, net namespaces, user namespaces, RTNL, netdev locking, ethtool link settings, linkwatch, RPS/XPS internals, BQL/DQL, runtime PM, OpenFirmware, namespace kobject operations, and driver `netdev_ops`. User space depends on `/sys/class/net/<ifname>/` and `/sys/class/net/<ifname>/queues/{rx,tx}-N/`.

## Risks

The major risk is lock ordering with sysfs active references and RTNL during unregister; `sysfs_rtnl_lock()` exists specifically to avoid an ABBA deadlock. Queue kobject re-addition can race with pending sysfs operations; the code detects initialized kobjects and returns `-EAGAIN`. Bitmap parsing for RPS/XPS must respect housekeeping CPUs and queue counts. Owner changes across namespaces must update device and queue groups consistently. Many attributes are ABI-stable, so names, permissions, and formatting are hard to change.

## Test Signals

Test with interface registration/unregistration under concurrent sysfs reads/writes, namespace moves with different owning user namespaces, queue count changes, RPS/XPS bitmap writes, BQL sysfs writes, carrier/MTU/flags changes, and driver paths with/without optional operations. Lockdep and KASAN are important for unregister races; user-space ABI tests should compare `/sys/class/net` layout and permissions.
