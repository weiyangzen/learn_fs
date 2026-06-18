# sources/distributed-fs/ceph-client/drivers/net/netdevsim/bus.c

## Purpose
This file implements the synthetic bus used to create and manage `netdevsim` devices from sysfs. It provides bus attributes to add/delete simulated devices and link/unlink netdevsim peers, per-device attributes to configure SR-IOV-like VFs and ports, and module lifecycle for bus and driver registration.

## Important APIs, Types, and Functions
Global state includes an IDA for device ids, `nsim_bus_dev_list`, `nsim_bus_dev_list_lock`, `nsim_bus_enable`, a refcount of bus devices, and a completion for teardown. Per-device sysfs attributes are `sriov_numvfs`, `new_port`, and `del_port`. Bus attributes are `new_device`, `del_device`, `link_device`, and `unlink_device`. Probe/remove bridge to `nsim_drv_probe()` and `nsim_drv_remove()`. Public lifecycle functions are `nsim_bus_init()` and `nsim_bus_exit()`.

## Control Flow
Writing `new_device` parses `id [port_count [num_queues]]`, checks the bus enable flag under the list mutex, allocates/registers a `struct nsim_bus_dev`, increments the device refcount, marks the device initialized with release semantics, and adds it to the global list. Device registration triggers bus probe, which creates the devlink/netdevsim instance in `dev.c`. Writing `del_device` finds the id under the list lock, removes it from the list, and unregisters the device. Per-device `new_port` parses a PF port id plus optional MAC address, validates initialization and MAC format, and calls `nsim_drv_port_add()`. `del_port` removes a PF port. `sriov_numvfs` calls `nsim_drv_configure_vfs()` while the device lock is held. Link/unlink look up net namespaces by fd, find netdevs by ifindex under RTNL, validate both are netdevsim devices, then assign or clear reciprocal RCU peer pointers and carrier state.

## State and Persistence
State is in-memory synthetic device state plus sysfs-visible attributes. `init` and `nsim_bus_enable` use acquire/release ordering to prevent sysfs operations from racing uninitialized or exiting objects. Device ids are reserved in the IDA until device deletion. Peer links are RCU pointers and are cleared with `synchronize_net()` on unlink before waking queues.

## Dependencies and Integration Points
This file integrates with Linux driver core bus/device APIs, sysfs attributes, net namespace fd lookup, RTNL, netdevsim core creation/destruction in `dev.c`, and SR-IOV-style netdevsim configuration. It registers a `bus_type` named `DRV_NAME` and a matching `device_driver`.

## Risks and Edge Cases
Input parsing is strict and reports format errors. `unlink_device_store()` parses `netnsfd` as unsigned despite storing in an `int`, which can make negative fd inputs fail format expectations differently from `link_device_store()`. Link creation refuses already-linked devices and self-links. Bus exit disables new operations, unregisters all remaining devices, waits for release completion, then unregisters driver and bus; correctness depends on refcounting every created `nsim_bus_dev`. Device deletion while sysfs operations run is guarded by list/device locks and init flags but remains concurrency-sensitive.

## Test Signals
Tests should write sysfs `new_device`/`del_device`, create/delete PF ports with and without MAC addresses, change `sriov_numvfs`, link and unlink devices across namespaces, verify carrier behavior when linked devices are up, and unload the module with devices present. Expected signals include created bus devices, netdevsim netdevs and devlink instances, reciprocal peer pointers, and no leaks or use-after-free warnings on exit.
