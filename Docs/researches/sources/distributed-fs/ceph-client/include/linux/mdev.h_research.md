<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdev.h -->
# sources/distributed-fs/ceph-client/include/linux/mdev.h

## Purpose
This header defines the mediated device (mdev) bus interfaces used by parent drivers to expose partitioned virtual devices and by mdev drivers to bind to those instances.

## Important APIs, types, and functions
`struct mdev_device` wraps a Linux device, UUID, type pointer, list node, and active flag. `struct mdev_type` describes a parent-provided type with sysfs and display names plus core-populated kobjects. `struct mdev_parent` ties a physical parent device, mdev driver, type set, unregister semaphore, and instance counter. `struct mdev_driver` declares `device_api`, optional `max_instances`, `probe`, `remove`, availability, and description callbacks. APIs include `mdev_register_parent`, `mdev_unregister_parent`, `mdev_register_driver`, `mdev_unregister_driver`, `to_mdev_device`, and `mdev_dev`.

## Control flow
Parent drivers register supported mdev types. Userspace creates mediated devices via sysfs, causing mdev device creation and driver probe. Unregistration synchronizes against creation/removal with `unreg_sem`; active instances are removed through driver callbacks.

## State and persistence
Runtime state includes UUIDs, active devices, type kobjects, available instance counts, and parent/type relationships. Persistent configuration is typically userspace-managed, not stored by the header.

## Dependencies and integration points
It depends on Linux device model, UUIDs, kobjects/ksets, lists, rw semaphores, atomics, and sysfs. It integrates with VFIO and parent drivers for GPUs, accelerators, and other partitionable devices.

## Risks and test signals
Risks include UUID collisions, available-instance accounting errors, parent unregistration races, stale kobjects, and mismatched `device_api`. Test create/remove under concurrency, unregister with active children, max-instance limits, type descriptions, and driver bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdev.h -->
