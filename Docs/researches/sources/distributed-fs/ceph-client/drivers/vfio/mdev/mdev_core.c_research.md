# sources/distributed-fs/ceph-client/drivers/vfio/mdev/mdev_core.c

## Purpose

`mdev_core.c` implements the mediated device core lifecycle. It lets a parent device register supported mdev types, lets userspace create/remove mdev instances through sysfs, attaches the selected mdev driver explicitly, and removes all children during parent unregister.

## Important APIs, Types, and Functions

Exported APIs are `mdev_register_parent()`, `mdev_unregister_parent()`, `mdev_device_create()`, and `mdev_device_remove()`. Global state includes `mdev_list`, `mdev_list_lock`, and a compatibility class. Internal helpers are `mdev_device_remove_common()`, `mdev_device_remove_cb()`, and `mdev_device_release()`.

## Control Flow

Parent registration initializes `unreg_sem`, stores the parent device, mdev driver, type array, and available instance count, creates sysfs type files, creates a class compatibility link, logs registration, and emits a `KOBJ_CHANGE` uevent. Creation parses through sysfs in `mdev_sysfs.c`, checks duplicate UUIDs under `mdev_list_lock`, reserves an available instance when no dynamic `get_available` callback exists, allocates and initializes an `mdev_device`, takes a type kobject reference, adds it to the global list, names it by UUID, obtains a read lock on the parent unregister semaphore, adds the device, explicitly attaches the parent's mdev driver, creates mdev sysfs links, marks it active, and releases the semaphore.

Removal verifies the device is in the global list and active, marks it inactive, obtains the unregister semaphore read lock, removes sysfs links, deletes the device, and drops the initialization reference. Parent unregister takes the write lock, removes the compatibility link, removes every mdev child with the callback, removes parent sysfs, releases the lock, and emits an unregister uevent.

## State and Persistence Behavior

Mdev instances persist as kernel devices named by UUID until removed or until the parent unregisters. Instance accounting is either dynamic through driver `get_available()` or atomic `available_instances`. The global list enforces UUID uniqueness across all mdevs. There is no file-backed persistence.

## Dependencies and Integration Points

The file depends on the mdev bus from `mdev_driver.c`, sysfs helpers from `mdev_sysfs.c`, class compatibility links, kobject uevents, UUIDs, and parent-driver callbacks.

## Risks and Edge Cases

The parent unregister semaphore prevents creation/removal races with parent teardown. A failed `device_driver_attach()` or sysfs link creation must delete the device and eventually restore instance counts through release. `mdev_device_remove()` returns `-EAGAIN` if another removal already marked the device inactive. Global UUID uniqueness can reject duplicates across different parents.

## Test Signals

Test parent registration/unregistration, sysfs type creation failure unwind, duplicate UUID rejection, available-instance exhaustion/restoration, creation during unregister, attach failure unwind, sysfs link failure unwind, remove idempotence, parent unregister removing active children, uevents, and module init/exit bus/class registration.
