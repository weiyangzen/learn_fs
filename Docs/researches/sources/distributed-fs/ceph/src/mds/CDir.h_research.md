# sources/distributed-fs/ceph/src/mds/CDir.h

## Purpose
`CDir.h` declares `CDir`, the MDS cache object for one directory fragment. A `CDir` is owned by a `CInode`, keyed by `dirfrag_t`, and stores cached dentries plus the per-fragment `fnode_t` statistics that are committed to metadata objects. It is the boundary object for directory authority, import/export, freezing, fetch/commit, scrub, bloom-filter lookup hints, and fragment split/merge.

## Important APIs, Types, And State
The class inherits `MDSCacheObject` and `Counter<CDir>`, so it participates in common cache object state, waiters, authority, pins, and dumping. Important nested types are `dentry_key_map`, `dentry_key_set`, `fnode_ptr`, `dentry_commit_item`, `freeze_tree_state_t`, and `scrub_info_t`. `dentry_commit_item` is the commit staging structure for null, remote, and primary dentries; it carries key, snap range, inode data, xattrs, old inode map, snaprealm data, symlink text, features, damage flags, and alternate names.

Major public APIs include `lookup`, `add_null_dentry`, `add_primary_dentry`, `add_remote_dentry`, `link_*_inode`, `unlink_inode`, `remove_dentry`, `split`, `merge`, `fetch`, `fetch_keys`, `commit`, `mark_complete`, `mark_dirty`, `mark_clean`, `encode_export`, `decode_import`, `freeze_tree`, `freeze_dir`, `unfreeze_tree`, `unfreeze_dir`, and scrub methods. Accessors expose the owning inode, frag id, auth state, fnode versions, dentry counts, and stats.

State is represented by many explicit bits. Important bits include completeness, frozen/freezing tree and dir states, committing, fetching, creating, import/export bounds, active importing/exporting, fragmenting, sticky pinning, dirty dirfragtree, bad fragment, open-file-table tracking, and auxiliary subtree. Masks define which bits survive export/import/fragment operations.

## Control Flow And Persistence
The normal data path is: a `CInode` opens or locates a `CDir`; dentries are inserted, linked, unlinked, or loaded; mutations project an `fnode_t`; journal callbacks pop projected fnode state; dirty fragments are committed via OMAP operations. Fetch methods load full fragments or selected keys from backing metadata objects. Commit helpers encode fnode headers, dentry records, stale removals, and primary inode payloads.

`fnode` is held through shared immutable pointers, with `project_fnode` creating mutable copies for mutations. This mirrors `CInode` projected metadata and lets log events share stable snapshots. `pre_dirty`, `_mark_dirty`, `mark_dirty`, and `mark_clean` coordinate versioning, log segment membership, and dirty pins. `_encode_base` and `_decode_base` serialize first snap, fnode, replication mode, and replica list data for import/export or metadata movement.

## Dependencies And Integration Points
`CDir` depends tightly on `CInode`, `CDentry`, `MDCache`, `MDSContext`, `Mutation`, `LogSegmentRef`, `MDSCacheObject`, `snap.h`, and Ceph buffer encoding. It is a friend of migrator, discovery, balancer, cache, and commit/fetch context classes. `CInode` uses `CDir` for dirfrag ownership, scatter-stat accounting, auth-pin propagation, export pinning, freezing checks, and path construction. `Locker` and `MDCache` integrate with `lock_caches_with_auth_pins`, dir auth pins, waiters, and subtree authority.

## Risks
The highest-risk behavior is state coupling: fragment dirtyness, auth pins, freeze states, projected fnode queues, and import/export masks must stay synchronized. Losing or double-clearing pins can deadlock migration or trim active metadata. Bloom filters are intentionally not serialized, so callers that enable them must maintain accuracy until `mark_complete` deletes them. Split/merge and subtree auth transitions must preserve dentry waiters and stat accounting. Bad-fragment paths must register damage consistently so scrub and recovery do not trust corrupted metadata.

## Test Signals
Useful test signals include directory fetch/commit round trips, split and merge under active waiters, auth import/export with dirty and boundary fragments, scrub detecting local stat mismatch, damage injection on dentry/header decode, freeze/unfreeze with nested auth pins, and replica rejoin with preserved exported mask bits. Assertions around ref counts, dirty counters, projected fnode emptiness, and dirfrag leaf membership are also important runtime guards.
