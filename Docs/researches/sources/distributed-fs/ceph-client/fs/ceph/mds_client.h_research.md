<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mds_client.h -->
# sources/distributed-fs/ceph-client/fs/ceph/mds_client.h

## Purpose
`mds_client.h` defines the public interface and central runtime data structures for the CephFS MDS client. It is included by most CephFS client subsystems that need to create MDS requests, inspect sessions, queue cap releases, handle MDS maps, enforce MDS cap auth rules, wait for async creates, or share MDS-managed metadata state.

## Important APIs, types, and functions
The header defines CephFS feature bits in `enum ceph_feature_type` and the supported feature vector `CEPHFS_FEATURES_CLIENT_SUPPORTED`. These feature bits gate reply encoding, lazy cap wanted behavior, multi reconnect, delegated inodes, metric collection, alternate names, session-state notification, getvxattr, 32-bit retry/forward counters, owner uid/gid support, MDS auth caps checks, and subvolume metrics.

Core wire-parsed reply containers are `ceph_mds_reply_info_in`, `ceph_mds_reply_dir_entry`, `ceph_mds_reply_xattr`, and `ceph_mds_reply_info_parsed`. They hold pointers into MDS reply messages plus allocated fscrypt blobs and readdir buffers. `ceph_mds_session` captures per-rank session state, including connection/auth state, cap generation/TTL, cap lists, dirty/flushing cap lists, wait and unsafe request lists, delegated inode xarray, and refcounting. `ceph_mds_request` captures one in-flight metadata operation, including VFS objects, explicit paths, operation args, flags, credentials, idmap, request/reply messages, reply parse state, timing, unsafe tracking, forwarding/retry state, and cap reservations.

`ceph_mds_client` is the mount-level controller. It holds the active MDS map, sessions, request tree, wait queues, stopping state, dirty folio counters, quota realm cache, snap realm trees/lists, cap delay/flush/reclaim state, cap reservation pool, dentry leases, global metrics, subvolume metrics send tracking, snapid and pool permission caches, MDS cap auth rules, and nodename metadata.

Public functions cover lifecycle (`ceph_mdsc_init`, `ceph_mdsc_destroy`, `ceph_mdsc_close_sessions`, `ceph_mdsc_force_umount`), request handling (`ceph_mdsc_create_request`, `ceph_mdsc_submit_request`, `ceph_mdsc_wait_request`, `ceph_mdsc_do_request`, `ceph_mdsc_release_request`), cap handling (`ceph_flush_session_cap_releases`, `__ceph_queue_cap_release`, `ceph_trim_caps`, `ceph_iterate_session_caps`), path and lease helpers, MDS map handlers, export-target session opening, access checks, and delegated inode helpers.

## Control flow
The header documents the primary lock layering: `session->s_mutex`, then `mdsc->mutex`, then `mdsc->snap_rwsem`, then inode cap locks and snap/cap delay locks. Callers allocate and populate `ceph_mds_request`, submit it to the MDS client, wait or receive callbacks, then drop the kref through `ceph_mdsc_put_request`. Session references use `ceph_get_mds_session` and `ceph_put_mds_session`. Request flags record important lifecycle transitions such as aborted, got unsafe, got safe, got result, parent locked, async, and fscrypt file marshalling.

## State and persistence behavior
The structures describe in-memory state only. Session and request state is persistent for the lifetime of the mount or operation, not across remounts or reboot. The MDS client uses RB trees and lists for deterministic runtime lookup and ordering: request TIDs, quota realm inodes, snap realms, snapid maps, pool permissions, cap queues, unsafe operations, and dentry leases. Durability-related fields such as unsafe request lists, safe completions, cap flush TIDs, and oldest client TID reflect protocol persistence on the MDS side rather than local storage.

## Dependencies and integration points
The header depends on Linux kernel synchronization, krefs/refcounts, rbtree/list/xarray users via included structures, Ceph messenger/auth/types, `mdsmap.h`, `metric.h`, `subvolume_metrics.h`, and `super.h`. It is the shared contract for implementation files such as `mds_client.c`, `caps.c`, `inode.c`, `dir.c`, `file.c`, `quota.c`, `metric.c`, `snap.c`, and debugfs support.

## Risks and test signals
Risks include ABI drift between feature vectors and session-open encoding, misuse of request flags, incorrect kref/session ref pairing, lock-order violations by call sites, stale comments relative to actual lock behavior, and memory ownership mistakes for path buffers, fscrypt blobs, pagelists, credentials, idmaps, dentries, and inodes. Test signals include build coverage across `CONFIG_DEBUG_FS` and fscrypt options, sparse/lockdep runs, request allocation/free fault injection, MDS feature negotiation, multi-MDS session array growth, and lifecycle tests for async requests, cap release queues, quota realm cleanup, and mount shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ceph/mds_client.h -->
