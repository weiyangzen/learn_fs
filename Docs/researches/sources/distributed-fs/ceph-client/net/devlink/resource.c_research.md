
# sources/distributed-fs/ceph-client/net/devlink/resource.c

## Purpose
This file implements devlink resources: hierarchical, driver-declared capacity objects with sizes, pending new sizes, validation constraints, optional occupancy callbacks, and device or port scope. Userspace can inspect resource trees and request new sizes, while drivers later consume pending sizes during reload or reconfiguration.

## Important APIs, Types, And Functions
`struct devlink_resource` contains name, ID, committed size, pending `size_new`, subtree validity, parent pointer, size constraints, child list, occupancy callback, and callback private data.

Recursive lookup uses `__devlink_resource_find()` and `devlink_resource_find()`. Size validity helpers are `devlink_resource_validate_size()` for min/max/granularity checks and `devlink_resource_validate_children()` for ensuring child pending sizes do not exceed parent pending size.

Netlink handlers are `devlink_nl_resource_set_doit()`, `devlink_nl_resource_dump_doit()`, and `devlink_nl_resource_dump_dumpit()`. Serialization is recursive through `devlink_resource_put()`, emitting name, size, ID, pending size when different, occupancy, size params, child list, and `DEVLINK_ATTR_RESOURCE_SIZE_VALID` for resources with children.

Driver APIs include `devl_resource_register()`, `devl_resources_unregister()`, `devlink_resources_unregister()`, `devl_resource_size_get()`, `devl_resource_occ_get_register()`, `devl_resource_occ_get_unregister()`, `devl_port_resource_register()`, and `devl_port_resources_unregister()`.

## Control Flow
Drivers register top-level resources or children under an existing parent ID while holding the devlink lock. Registration rejects duplicate IDs in the selected tree, verifies parents for non-top resources, initializes current and pending sizes to the same value, copies sizing params, and links the resource into the proper list.

Userspace size changes resolve a resource by ID, validate the requested size against min/max/granularity, update `size_new`, then recompute the child-sum validity flag for the resource and its parent. The actual committed size changes when a driver calls `devl_resource_size_get()`, which returns `size_new` and updates `size`.

Dump paths support both single request/reply style and generic netlink dump iteration. They can emit device resources, port resources, or both, controlled by optional `DEVLINK_ATTR_RESOURCE_SCOPE_MASK`. Dump state tracks the current resource index and port index across callbacks.

## State And Persistence
Resource state is in memory in `devlink->resource_list` and each `devlink_port->resource_list`. `size_new` persists as pending runtime state until a driver consumes it or resources are unregistered. Occupancy is not stored; it is sampled by calling the registered callback during dump.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, devlink lock discipline, port resources initialized by `devlink_port_init()`, generic netlink helpers, and driver-provided occupancy callbacks. Drivers use resource size getters during reload or reinitialization to apply pending allocations. DSA and NIC drivers in this tree register resources for VLAN/FDB/ATU/SF counts and similar capacities.

## Risks And Edge Cases
Only the changed resource and its immediate parent are revalidated on set. Because a parent's validity can affect higher ancestors, deeply nested trees may leave ancestor `size_valid` stale if grandchildren are resized in ways that change aggregate validity beyond one level.

`devlink_resource_fill()` assumes the selected resource list is non-empty before taking `list_first_entry()`, and callers enforce that for normal dump-doit. Any future caller must preserve that precondition.

`devlink_resource_validate_size()` divides by `size_granularity`; invalid zero granularity in driver-provided params would be a serious driver bug. Occupancy callbacks run during dump and should be fast and safe under devlink locking expectations.

## Test Signals
Relevant local selftests include mlxsw devlink resource scripts under `tools/testing/selftests/drivers/net/mlxsw/spectrum/devlink_resources.sh`. Useful tests cover size min/max/granularity failures, pending size reporting, parent/child aggregate validity, scoped dump selection for device versus port resources, occupancy callback registration/unregistration, and driver reload consumption via `devl_resource_size_get()`.
