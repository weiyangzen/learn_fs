<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mdstypes.h -->
## sources/distributed-fs/ceph/src/mds/mdstypes.h

`mdstypes.h` is the central CephFS MDS type header for identifiers, inode namespace constants, capability string helpers, old inode/xattr containers, directory stats, client/session metadata, dentry keys, table transactions, reconnect structures, dirfrag identities, load vectors, authority pairs, cache object identifiers, replay timing, block diffs, and subvolume metrics.

The header defines private/system inode ranges (`MDS_INO_*`), `mds_role_t`, cap string helpers, `old_inode_t`, `fnode_t`, `old_rstat_t`, `feature_bitset_t`, `metric_spec_t`, `client_metadata_t`, `session_info_t`, `dentry_key_t`, `string_snap_t`, `mds_table_pending_t`, `metareqid_t`, `cap_reconnect_t`, `snaprealm_reconnect_t`, old reconnect compatibility structs, `dirfrag_t`, `inode_load_vec_t`, `dirfrag_load_vec_t`, `mds_load_t`, authority constants, `MDSCacheObjectInfo`, `EstimatedReplayTime`, `BlockDiff`, and `SubvolumeMetric`.

State and persistence behavior is pervasive: nearly every struct has Ceph encode/decode contracts or `DENC`, many with explicit struct versions. `session_info_t` is documented as the durable part of a session; `fnode_t` holds persistent dirfrag accounting, damage, and scrub stamps; reconnect types capture client cap and snaprealm state for MDS recovery; and load vectors are decay-counter snapshots used for balancing rather than strict namespace correctness.

Dependencies include low-level Ceph integer/fs/cap types, `frag_t`, `interval_set`, `utime_t`, `DecayCounter`, entity names, formatter/dump helpers, and STL containers. Integration points include almost every MDS subsystem: MDCache, Locker, SessionMap, Journal, Migrator, Balancer, table services, client reconnect, scrub, and admin dumps.

Risks: macros encode persistent inode ranges and must remain stable; many inline comparators/hashers define map identity; public structs invite inconsistent mutation; old/new allocator templates must match mempool expectations; and version fields must be advanced carefully. Test signals are broad encode/decode generated tests, static assertions around inode ranges, cap formatting tests, reconnect/failover tests, dentry-key parsing, load-vector dumps, and subvolume metric v1/v2 denc compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/mdstypes.h -->
