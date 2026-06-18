# sources/distributed-fs/ceph/src/mds/SnapRealm.cc

Purpose: Implements snapshot realm inheritance, cache rebuilding, snap context/trace generation, snap name resolution, realm split/merge, and parent adjustment.

Important APIs/functions: `build_snap_set`, `check_cache`, `get_snaps`, `get_snap_context`, `get_snap_info`, `get_snapname`, `resolve_snapname`, `adjust_parent`, `split_at`, `merge_to`, `get_snap_trace`, `get_snap_trace_new`, `build_snap_trace`, and `prune_past_parent_snaps`.

Control flow: `check_cache()` recomputes cached state when local sequence, global last-destroyed, last-modified, or change-attr moves forward. `build_snap_set()` combines local snaps, filtered past-parent snaps, and current parent snaps since `current_parent_since`. `build_snap_trace()` emits old and new trace formats, appending parent traces for inheritance. Split/merge operations move child realms and inodes-with-caps across realm boundaries.

State and persistence behavior: Persistent realm data lives in `srnode` on the inode. Cached fields (`cached_seq`, `cached_snaps`, `cached_snap_context`, trace bufferlists, subvolume ino, modified/change attrs) are derived and invalidated via `invalidate_cached_snaps` or sequence checks. Split/merge updates in-memory realm topology and cap ownership; durable changes come from journaling the inode's projected srnode through `EMetaBlob`.

Dependencies and integration points: Integrates with `MDCache`, `MDSRank::snapclient`, `CInode`, `CDentry`, `CDir`, `Capability`, `SnapInfo`, `SnapRealmInfo`, and `SnapRealmInfoNew`. `Server` uses traces for client snap notifications.

Risks: Parent inheritance is subtle for global realms, past parents, snapdir visibility, and long snapshot names. Split traversal reserves based on `CDir::count()` and relies on `is_ancestor_of`; stale topology can misplace caps. Cache invalidation must include destruction sequence and change attrs, not only creation.

Test signals: Cover local/global realm cache builds, parent changes, past-parent pruning, old/new trace encoding, long-name resolution, split/merge with open children and caps, subvolume inheritance, and snapshots deleted while realms still reference past parents.
