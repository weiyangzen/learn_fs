# sources/distributed-fs/ceph-client/include/linux/kobject.h

## Purpose

`kobject.h` defines the generic kernel object infrastructure used by sysfs, ksets, uevents, and reference-counted kernel object lifetime management. The source was read as a complete 222-line file.

## Important APIs, Types, and Functions

Core types include `struct kobject`, `struct kobj_type`, `struct kobj_uevent_env`, `struct kset_uevent_ops`, `struct kobj_attribute`, and `struct kset`. APIs include `kobject_set_name()`, `kobject_init()`, `kobject_add()`, `kobject_init_and_add()`, `kobject_del()`, `kobject_create_and_add()`, `kobject_rename()`, `kobject_move()`, `kobject_get()`, `kobject_get_unless_zero()`, `kobject_put()`, `kobject_namespace()`, `kobject_get_ownership()`, `kobject_get_path()`, `kset_init()`, `kset_register()`, `kset_unregister()`, `kset_create_and_add()`, `kset_find_obj()`, `kobject_uevent()`, `kobject_uevent_env()`, `kobject_synth_uevent()`, and `add_uevent_var()`.

## Control Flow

Objects are initialized with a type, named, added under a parent or kset, exposed in sysfs, and refcounted with `kobject_get()`/`kobject_put()`. Uevents are emitted for lifecycle changes. Release is delegated to the type's `release()` callback when the final reference drops.

## State and Persistence Behavior

`struct kobject` stores name, parent, kset, type, sysfs `kernfs_node`, refcount, and lifecycle flags. Ksets hold a list of member objects plus their own embedded kobject. State persists in memory and sysfs until deletion and reference release complete.

## Dependencies and Integration Points

It integrates with sysfs/kernfs, krefs, namespaces, wait/workqueue debug release, uevent helper/netlink handling, UID/GID ownership, and global `/sys/kernel`, `/sys/kernel/mm`, `/sys/hypervisor`, `/sys/power`, and `/sys/firmware` roots.

## Risks and Edge Cases

Kobject lifetime bugs are high risk: every type needs a valid release callback, and objects must not be freed before final `kobject_put()`. Uevent action strings are constrained by driver-core policy. Namespace and ownership callbacks must match sysfs expectations.

## Test Signals

Driver-core tests, sysfs add/remove/rename/move tests, kobject refcount leak/UAF tests, uevent environment tests, namespace sysfs tests, and `CONFIG_DEBUG_KOBJECT_RELEASE` coverage are useful.
