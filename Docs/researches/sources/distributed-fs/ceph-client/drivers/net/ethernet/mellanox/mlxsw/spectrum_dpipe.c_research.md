<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.c

## Purpose
`spectrum_dpipe.c` exposes parts of the Spectrum routing pipeline through devlink dpipe. It registers metadata headers and four tables: egress RIF (`mlxsw_erif`), IPv4 host (`mlxsw_host4`), IPv6 host (`mlxsw_host6`), and adjacency (`mlxsw_adj`). The tables dump matches, actions, entries, sizes, resources, and optional counters for RIFs, neighbors, and nexthops.

## Important APIs, Types, and Functions
Public functions are `mlxsw_sp_dpipe_init()` and `mlxsw_sp_dpipe_fini()`. Static table ops include ERIF dump/counter/size callbacks, shared host4/host6 entry preparation and enumeration, and adjacency table match/action/entry/counter callbacks. Metadata fields include `erif_port`, `l3_forward`, `l3_drop`, `adj_index`, `adj_size`, and `adj_hash_index`.

## Control Flow
Initialization registers dpipe headers, then registers ERIF, host4, host6, and adjacency tables, assigning KVD resource IDs to host and adjacency tables. ERIF entries iterate all possible RIF indexes under the router mutex, skip missing or device-less RIFs, and paginate devlink entry contexts when netlink messages fill. Host tables iterate RIF neighbor lists, filter by AF_INET or AF_INET6, skip ignored IPv6 neighbors, fill match values for RIF and destination IP, action value for destination MAC, and optional counters. The adjacency table iterates forwarding nexthops that are not IP-in-IP, fills adjacency index/size/hash and destination MAC/eRIF actions, and can enable or disable nexthop counters while updating hardware adjacency entries.

## State and Persistence Behavior
The file does not own long-lived objects beyond devlink dpipe registrations. It observes router, RIF, neighbor, and nexthop state under `mlxsw_sp->router->lock`. Enabling dpipe counters can allocate RIF, neighbor, or nexthop counters and update hardware; disabling releases them. Dump entry allocations are temporary and freed with `devlink_dpipe_entry_clear()`.

## Dependencies and Integration Points
It integrates with devlink dpipe, Spectrum router/RIF/neigh/nexthop APIs, KVD resource identifiers, counter helpers behind router objects, and standard devlink ethernet/IPv4/IPv6 headers. Table names are shared with `spectrum_dpipe.h`.

## Risks and Edge Cases
Dump pagination is stateful; skip counters must remain correct when a message fills midway through a RIF or nexthop iteration. Entry preparation allocates multiple value buffers and depends on `devlink_dpipe_entry_clear()` to release partially allocated state. Counter enable paths are best-effort for ERIF/host tables but adjacency counter enable has rollback for already-enabled nexthops. Router contents may change between paginated dump passes, although the router mutex serializes each full dump.

## Test Signals
Signals include `devlink dpipe table show/dump` for all four tables, resource association for host4/host6/adj, valid ifindex mappings for RIF fields, host table dumps for IPv4 and IPv6 neighbors, adjacency dumps for ECMP/nexthop groups, counter toggling, and clean unregister order on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_dpipe.c -->
