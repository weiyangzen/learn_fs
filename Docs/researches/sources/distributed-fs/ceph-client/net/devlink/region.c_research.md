
# sources/distributed-fs/ceph-client/net/devlink/region.c

## Purpose
This file implements devlink regions: named address/data areas that drivers can expose for snapshots or direct reads. It supports device-level and port-level regions, snapshot ID allocation and reference tracking, snapshot create/delete notifications, region listing, and chunked region reads over netlink.

## Important APIs, Types, And Functions
`struct devlink_region` stores owning devlink, optional port, list linkage, ops or port ops, `snapshot_lock`, snapshot list, snapshot limits, current snapshot count, and region size. `struct devlink_snapshot` stores list linkage, region pointer, data pointer, and snapshot ID.

Lookup helpers are `devlink_region_get_by_name()`, `devlink_port_region_get_by_name()`, and `devlink_region_snapshot_get_by_id()`. Snapshot ID internals use `devlink->snapshot_ids` xarray through `__devlink_region_snapshot_id_get()`, `__devlink_snapshot_id_insert()`, `__devlink_snapshot_id_increment()`, and `__devlink_snapshot_id_decrement()`.

Netlink handlers are `devlink_nl_region_get_doit()`, `devlink_nl_region_get_dumpit()`, `devlink_nl_region_new_doit()`, `devlink_nl_region_del_doit()`, and `devlink_nl_region_read_dumpit()`. Driver APIs are `devl_region_create()`, `devlink_region_create()`, `devlink_port_region_create()`, `devl_region_destroy()`, `devlink_region_destroy()`, `devlink_region_snapshot_id_get()`, `devlink_region_snapshot_id_put()`, and `devlink_region_snapshot_create()`.

## Control Flow
Drivers create regions with a name, size, destructor, optional snapshot callback, and optional direct read callback. Creation links the region into either `devlink->region_list` or a port's `region_list` and sends a region-new notification.

Userspace can request an immediate snapshot with `DEVLINK_CMD_REGION_NEW`. The handler resolves the region, checks snapshot support and capacity, obtains a user-specified or allocated snapshot ID, calls the driver snapshot callback to allocate/fill data, and then stores a snapshot under `snapshot_lock`. If the ID was auto-allocated, the handler replies with the chosen ID.

Reads are dump operations. A read can target a stored snapshot or use direct read mode if no snapshot ID is supplied. Data is returned as nested chunks of up to `DEVLINK_REGION_READ_CHUNK_SIZE` bytes, and dump state tracks `start_offset` so multi-part netlink dumps continue from the last emitted offset.

Destroying a region takes the snapshot lock, deletes all snapshots using the registered destructor for each data buffer, removes the region from its list, sends a delete notification, and frees the region.

## State And Persistence
All state is in kernel memory. Region definitions live until driver teardown. Snapshot data persists only until explicitly deleted, region destruction, or devlink teardown. Snapshot IDs are globally tracked per devlink instance in an xarray with reference counts so the same ID can be shared by snapshots taken across multiple regions.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, devlink lock discipline, port lookup from `port.c`, xarray snapshot ID tracking, and driver-provided `devlink_region_ops` or `devlink_port_region_ops`. It integrates with drivers such as DSA switches and NICs that expose register tables or diagnostic dumps through devlink regions.

## Risks And Edge Cases
Port regions store ops in a union, but several paths use `region->ops` for common fields such as name and destructor. This relies on device and port region ops layouts being compatible for those members. Any layout divergence would be dangerous.

`devlink_nl_region_read_dumpit()` checks `region->ops->read` before selecting direct read, even for port regions where the actual callback is `port_ops->read`; this again relies on the unioned ops layout. Direct reads and snapshot reads are mutually exclusive and enforced at runtime.

Chunked reads guard against infinite loops by failing if no progress was made. Offset plus length arithmetic can conceptually overflow before clamping to region size if userspace supplies extreme values; practical netlink u64 handling should still be tested around boundaries.

## Test Signals
Driver-facing examples in this repository include DSA and NIC region setup/teardown and snapshot callbacks. Useful regression tests are snapshot create with explicit and auto IDs, duplicate IDs, max snapshot capacity, deleting shared IDs across multiple regions, direct read versus snapshot read validation, partial dump continuation, and port-region reads. Documentation references in `Documentation/networking/devlink/devlink-region.rst` describe expected userspace behavior.
