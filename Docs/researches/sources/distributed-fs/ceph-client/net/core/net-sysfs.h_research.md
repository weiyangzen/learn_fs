# sources/distributed-fs/ceph-client/net/core/net-sysfs.h

## Purpose

`net-sysfs.h` is the internal header for network device sysfs integration. It declares the kobject lifecycle and queue-update helpers implemented by `net-sysfs.c` and shared with core netdevice code.

## Important APIs, Types, And Functions

The header declares `netdev_kobject_init()`, `netdev_register_kobject()`, `netdev_unregister_kobject()`, `net_rx_queue_update_kobjects()`, `netdev_queue_update_kobjects()`, and `netdev_change_owner()`. It also exposes `rps_default_mask_mutex` and declares the `skb_defer_disable_key` static key.

## Control Flow

Callers initialize the net class once through `netdev_kobject_init()`. Individual devices call `netdev_register_kobject()` during registration and `netdev_unregister_kobject()` during teardown. Queue count changes call the RX/TX update helpers. Namespace moves call `netdev_change_owner()` to adjust sysfs ownership.

## State And Persistence Behavior

The header owns no state. It exposes synchronization and static-key symbols owned elsewhere. The functions it declares mutate sysfs/device-core state and queue kobject state.

## Dependencies And Integration Points

It depends on `struct net_device`, `struct net`, `struct mutex`, and jump-label static-key infrastructure. The declarations are part of the boundary between netdevice registration code and sysfs implementation.

## Risks

Because these functions participate in registration, unregister, namespace moves, and queue resizing, misuse can leak kobjects, leave stale sysfs files, or expose wrong user namespace ownership. Callers must already satisfy the locking rules expected by `net-sysfs.c`.

## Test Signals

Compile coverage is the main direct signal. Behavioral coverage comes from netdevice registration/unregistration, queue resize, namespace move, and sysfs ownership tests.
