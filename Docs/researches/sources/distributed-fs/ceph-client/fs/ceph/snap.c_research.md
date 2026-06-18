# sources/distributed-fs/ceph-client/fs/ceph/snap.c

## Purpose
`snap.c` implements CephFS client snapshot realm tracking, snap context rebuilding, cap-snap queuing, snap notification handling from MDS sessions, and snap-id-to-anonymous-block-device mapping for snapped inodes. It is the client-side consistency layer that decides which writes belong before or after a snapshot.

## Important APIs, Types, And Functions
Public entry points include `ceph_lookup_snap_realm()`, `ceph_get_snap_realm()`, `ceph_put_snap_realm()`, `ceph_update_snap_trace()`, `ceph_change_snap_realm()`, `ceph_handle_snap()`, `__ceph_finish_cap_snap()`, `ceph_get_snapid_map()`, `ceph_put_snapid_map()`, `ceph_trim_snapid_map()`, and `ceph_cleanup_snapid_map()`. The main state types are `struct ceph_snap_realm`, `struct ceph_cap_snap`, `struct ceph_snap_context`, and `struct ceph_snapid_map`.

## Control Flow
MDS snap messages enter through `ceph_handle_snap()`, which decodes the header, handles split operations by moving inodes and child realms, then calls `ceph_update_snap_trace()` under `mdsc->snap_rwsem`. Snap trace decoding creates or looks up realms, adjusts parents, updates sequence and snap arrays, rebuilds cached contexts from parent to child, then queues cap snaps for dirty realms. `flush_snaps()` later drains `mdsc->snap_flush_list` through `ceph_flush_snaps()`. Snapid maps are looked up in an rb-tree, allocated with `get_anon_bdev()` on misses, and retired through an LRU after timeout.

## State, Persistence, And Dependencies
State is in-memory kernel state protected by `snap_rwsem`, `snap_empty_lock`, per-realm inode locks, `snap_flush_lock`, and `snapid_map_lock`. Nothing is persisted locally; authoritative snapshot state comes from MDS snap traces and is propagated to OSD writes through snap contexts. Dependencies include Ceph MDS client sessions, caps, xattr blob building, OSD snap contexts, rb-trees, lists, atomics, and blocklist support.

## Integration Points
This file integrates with cap management (`ceph_flush_snaps`, dirty caps), inode realm membership, MDS message dispatch, quota/xattr metadata snapshots, mount shutdown cleanup, and snapped inode device presentation.

## Risks
The highest-risk areas are refcount/list transitions for empty realms, memory-allocation failures during context rebuilds, split races across MDSs, corrupted snap traces, and cap-snap sequencing while writes or writeback are active. Corrupted traces deliberately fence IO and try to blocklist the client.

## Test Signals
Exercise snapshot create/delete/split, rename across snap realms, dirty write snapshot boundaries, mmap/page writeback snapshots, MDS failover during snap updates, ENOMEM fault injection, malformed snap traces, unmount cleanup, and snapid-map LRU trimming.
