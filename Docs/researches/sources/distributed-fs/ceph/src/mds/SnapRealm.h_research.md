# sources/distributed-fs/ceph/src/mds/SnapRealm.h

Purpose: Defines `SnapRealm`, the MDS cache object that represents a snapshot namespace boundary and derives visible snapshots for inodes beneath it.

Important APIs/types: The class exposes snap existence, parent pruning, snap set/context/info access, trace access, snap name resolution, parent adjustment, split/merge, cap membership tracking, and cache invalidation. Core persistent data is `sr_t srnode`; in-memory topology is `parent`, `open_children`, `inodes_with_caps`, and `client_caps`.

Control flow: Users call accessors such as `get_snaps`, `get_snap_context`, `get_last_created`, or `get_newest_seq`; these funnel through `check_cache()` to rebuild derived state lazily. Cap add/remove functions maintain per-client lists for efficient client snap notifications during realm changes.

State and persistence behavior: `srnode` is journaled as inode metadata. Cached derived fields are mutable so const accessors can rebuild them lazily. `global` distinguishes the global snap realm from ordinary inode-rooted realms. `cached_subvolume_ino`, modified time, and change attr make new snap trace generation sensitive to subvolume and visibility metadata.

Dependencies and integration points: Includes `Capability`, `mdstypes`, `snap.h`, `xlist`, `elist`, and common snap types. Used by `CInode`, `MDCache`, `Server`, `SnapClient`, and stray purge/truncate logic to obtain snap contexts.

Risks: `remove_cap` assumes the cap item is singular when erasing the map entry and asserts map consistency. Cache consumers must call `invalidate_cached_snaps()` after mutating realm relationships or srnode fields. Parent pointers are raw and require lifecycle discipline with inode cache objects.

Test signals: Validate cap list membership, lazy cache refresh, split/merge topology, global realm behavior, and trace buffer stability across repeated reads.
