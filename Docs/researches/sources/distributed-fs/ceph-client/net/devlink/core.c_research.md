# sources/distributed-fs/ceph-client/net/devlink/core.c

## Purpose

`core.c` owns devlink instance allocation, registration, reference counting, global lookup, namespace exit handling, nested devlink relationships, lock helpers, and tracepoint exports. It is the foundation used by all devlink feature modules and generated netlink handlers.

## Important APIs, Types, and Functions

Global state is `DEFINE_XARRAY_FLAGS(devlinks, XA_FLAGS_ALLOC)` and the private `devlink_rels` xarray. Public helpers include `devlink_priv()`, `priv_to_devlink()`, `devlink_to_dev()`, `devlink_bus_name()`, `devlink_dev_name()`, `devlink_dev_driver_name()`, `devlink_net()`, `devl_lock()`, `devl_trylock()`, `devl_unlock()`, `devlink_try_get()`, `devlink_put()`, `devl_register()`, `devlink_register()`, `devl_unregister()`, `devlink_unregister()`, `devlink_alloc_ns()`, and `devlink_free()`. Relationship APIs are `devlink_rel_nested_in_add()`, `devlink_rel_nested_in_clear()`, `devlink_rel_nested_in_notify()`, and `devlink_rel_devlink_handle_put()`.

## Control Flow

Allocation validates reload ops, allocates a flexible `struct devlink`, assigns a cyclic xarray index, stores either a device reference or synthetic index name, initializes all child collections, sets the network namespace, creates the instance mutex, and initializes refcounting. Registration marks the xarray slot with `DEVLINK_REGISTERED`, sends notifications, and notifies parent relationships. Lookup uses RCU plus `devlink_try_get()` and then callers lock the instance before trusting registration. Unregister clears the registered mark after sending delete notifications and tears down nested relationships. Final free asserts child collections are empty, destroys xarrays, removes the global slot, and drops the last reference, which queues RCU work for memory release.

## State and Persistence Behavior

Devlink instances persist in the global xarray until `devlink_free()`. A reference only guarantees the object can be locked; registration must be checked separately under the devlink lock. Nested relationships persist as `struct devlink_rel` entries with refcounts and delayed work so parent notifications can be sent without assuming parent lock state. Network namespace pre-exit reloads registered devlinks into `init_net` when possible.

## Dependencies and Integration Points

The file registers the devlink generic netlink family, pernet pre-exit hook, and netdevice notifier at `subsys_initcall()`. It relies on `devl_internal.h` definitions and callback functions implemented in other devlink modules for port notification, reload validation, params, resources, rates, and linecards.

## Risks

Registration state, refcounting, and locking are tightly coupled. A caller that treats a reference as proof of registration can race unregister. Relationship delayed work must handle parent lock contention and stale relationship cleanup correctly. `devlink_free()` depends on drivers unregistering all child objects first. Namespace pre-exit reload failures can leave warnings and require driver reload correctness.

## Test Signals

Test allocation/register/unregister/free with child objects present and absent, concurrent netlink lookup during unregister, nested devlink attach/detach notifications, namespace teardown reload, lockdep assertions, and fault injection in xarray allocation or synthetic-name allocation.
