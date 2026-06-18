# sources/distributed-fs/ceph-client/net/devres.c

## Purpose
This small file provides devres-managed helpers for network devices. It lets drivers allocate Ethernet `struct net_device` instances and register them so cleanup is tied to the lifetime of a parent `struct device`.

## Important APIs, Types, And Functions
`struct net_device_devres` stores the managed `struct net_device *`. `devm_alloc_etherdev_mqs()` wraps `alloc_etherdev_mqs()`, records the resulting device in devres, and exports the helper. `devm_register_netdev()` validates that the netdev was already allocated through the same device's devres, registers it with `register_netdev()`, and adds a second devres action that calls `unregister_netdev()`. `netdev_devres_match()` is the matcher used to prove the same netdev is managed.

## Control Flow
Allocation first allocates a devres record, then allocates the Ethernet netdev, then adds the record to the managing device. Registration refuses unmanaged netdevs with `WARN_ON()` and `-EINVAL`, allocates an unregister devres record, calls `register_netdev()`, and only after success installs the unregister action on `ndev->dev.parent`.

## State And Persistence
The state is a pair of devres records: one freeing the netdev and one unregistering it. Ordering is controlled by devres release order during device detach; the netdev exists until the managed free action runs.

## Dependencies And Integration Points
This integrates with the Linux driver-core devres mechanism, `<linux/etherdevice.h>`, and normal netdev registration. It is intended for device drivers whose netdev allocation and registration should unwind automatically when the parent device goes away.

## Risks And Edge Cases
`devm_register_netdev()` requires the netdev to be managed by the same device and currently assumes the only managed allocator is `devm_alloc_etherdev_mqs()`. Passing a netdev allocated elsewhere returns `-EINVAL`. The unregister devres record is added to `ndev->dev.parent`, so parent assignment must be correct by registration time.

## Test Signals
Tests should cover successful managed allocation/registration, registration failure cleanup, rejection of unmanaged netdevs, and detach-time ordering that unregisters before freeing the netdev.
