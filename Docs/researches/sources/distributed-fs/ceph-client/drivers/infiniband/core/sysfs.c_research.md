# sources/distributed-fs/ceph-client/drivers/infiniband/core/sysfs.c

## Purpose
`sysfs.c` builds the RDMA core sysfs representation for devices and ports. It exposes device identity, port state, GID/PKey tables, PMA counters, driver hardware counters, and legacy client port groups under the RDMA device kobject tree.

## Important APIs, types, and functions
- Port setup/teardown: `ib_setup_port_attrs()` and `ib_free_port_attrs()`.
- Device hw stats: `ib_setup_device_attrs()` and `ib_device_release_hw_stats()`.
- Port hw stats access: `ib_get_hw_stats_port()`.
- Legacy client groups: `ib_port_register_client_groups()` and `ib_port_unregister_client_groups()`.
- Attribute show/store helpers cover port state, LID/LMC/SM LID/SL, capability mask, rate, physical state, link layer, GIDs, GID attributes, PKeys, PMA counters, hardware counters, lifespan, node type/GUIDs/description, and firmware version.

## Control flow and behavior
Device setup allocates optional hardware counter attributes from driver-provided descriptors, performs an initial `get_hw_stats()` read, skips optional counters, adds a writable `lifespan` attribute, and installs the group into the device’s group array. Port setup creates a `ports` kobject, queries each port, allocates a per-port kobject with `gids` and optional `pkeys` tables, optional per-port hardware counters, optional PMA counter group based on class-port-info capability, driver port groups, and a nested `gid_attrs` kobject with `ndevs` and `types` tables.

Attribute reads query live device state where appropriate. GID reads preserve userspace compatibility by returning a zero GID for invalid table entries rather than failing. Hardware counter reads are rate-limited by `stats->lifespan`, guarded by a mutex, and add dynamic RDMA counter values to driver stats. Teardown removes groups, kobjects, allocated attribute arrays, and hardware stats structures in reverse order.

## State, persistence, and dependencies
Persistent sysfs state includes `struct ib_port`, `struct gid_attr_group`, dynamic attribute arrays, `hw_stats_device_data`, `hw_stats_port_data`, kobject entries in `coredev->port_list`, and pointers from `ibdev->port_data[port].sysfs`. Hardware stats persist timestamps, lifespans, descriptors, values, and mutexes.

## Integration points
The file integrates with RDMA device registration, driver ops (`query_port`, `process_mad`, `alloc_hw_*_stats`, `get_hw_stats`, `modify_device`, `port_groups`), GID cache, PKey query APIs, PMA MAD processing, RDMA counters, kobject/sysfs core, and userspace tooling that reads `/sys/class/infiniband`.

## Risks and test signals
Risks include memory leaks on partial setup failure, stale `port_data[].sysfs` pointers, userspace ABI regressions in attribute names or invalid GID handling, hardware counter descriptor/order mismatches, PMA MAD failures, and concurrent stats reads with lifespan writes. Test signals include sysfs tree shape for multi-port devices, invalid GID slots returning zero, PKey/GID table bounds, hw counter lifespan behavior, device node description writes, PMA counter group selection, driver port groups, and fault injection through allocation and kobject creation failures.
