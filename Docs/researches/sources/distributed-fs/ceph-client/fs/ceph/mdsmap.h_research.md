<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.h -->
# sources/distributed-fs/ceph-client/fs/ceph/mdsmap.h

## Purpose
`mdsmap.h` defines the kernel client's trimmed representation of a CephFS MDS map and exposes small helper APIs used by the MDS client to inspect rank state, addresses, lagginess, data pools, filesystem status, and availability.

## Important APIs, types, and functions
`struct ceph_mds_info` records per-rank runtime data: daemon global id, messenger address, MDS state, export-target count and array, and laggy flag. `struct ceph_mdsmap` records map epochs, root rank, session timers, file and xattr limits, configured and actual active MDS counts, possible max rank, per-rank info, data pool list, CAS pool, enabled/damaged flags, laggy count, and filesystem name.

Inline helpers are `ceph_mdsmap_get_addr`, `ceph_mdsmap_get_state`, and `ceph_mdsmap_is_laggy`. External functions decode and destroy maps, choose a random MDS, and check cluster availability.

## Control flow
The header itself has no executable control flow beyond simple bounds checks. Callers use `ceph_mdsmap_get_state` to convert out-of-range ranks to `CEPH_MDS_STATE_DNE`, and `ceph_mdsmap_get_addr` returns `NULL` when a rank is outside `possible_max_rank`. These helpers keep call sites simpler when sessions outlive map changes or when maps temporarily contain sparse rank states.

## State and persistence behavior
The structures are in-memory snapshots of monitor-provided MDS maps. The map object is owned by `ceph_mds_client`; per-rank `export_targets`, `m_info`, `m_data_pg_pools`, and `m_fs_name` are dynamically allocated by the decoder and released by `ceph_mdsmap_destroy`. There is no persistent local storage.

## Dependencies and integration points
The header depends on Ceph type definitions and MDS state constants. It is included by `mds_client.h`, `mdsmap.c`, and components that need MDS rank status. Fields are consumed by request selection, session opening/reconnect, metric send filtering, max file size propagation, quota/statfs behavior indirectly through the MDS client, and mount availability checks.

## Risks and test signals
Risks include callers using addresses without checking for `NULL`, assuming ranks are dense, failing to handle `CEPH_MDS_STATE_DNE`, or missing that `possible_max_rank` can exceed both active and configured counts during failover. Test signals include sparse-rank maps, rank removal, export-target arrays, laggy state transitions, maps with zero `m_max_xattr_size`, and use under lockdep to ensure callers read the map under the intended MDS client synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mdsmap.h -->
