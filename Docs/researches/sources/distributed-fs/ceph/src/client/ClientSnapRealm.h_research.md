# sources/distributed-fs/ceph/src/client/ClientSnapRealm.h

## Purpose
`ClientSnapRealm.h` defines `SnapRealm`, the client cache record for a snapshot realm. It tracks realm identity, parentage, snapshot membership, child realms, change attributes, snapdir visibility, and inodes whose caps are attached to the realm.

## Important APIs, Types, and Functions
The main type is `SnapRealm`. Fields include `ino`, `nref`, `created`, `seq`, `parent`, `parent_since`, `prior_parent_snaps`, `my_snaps`, `pparent`, `pchildren`, `last_modified`, `change_attr`, `is_snapdir_visible`, and `inodes_with_caps`. `get_snap_context()` lazily returns a cached `SnapContext`; `build_snap_context()` and `dump()` are implemented in the cc file. `operator<<` prints compact debug state.

## Control Flow
Client snap handling obtains or creates realms, links them into a parent/child tree, invalidates caches on updates, and asks `get_snap_context()` when cap snapshots or file IO need the effective snap context. The cached context is rebuilt only when its sequence is zero.

## State and Persistence Behavior
All state is volatile client metadata cache derived from MDS snap traces. The authoritative snapshot tree is not persisted here. `nref` and `inodes_with_caps` support local lifetime and cap flush interactions; parent/child pointers express the current client view of the realm tree.

## Dependencies and Integration Points
It depends on Ceph `types.h`, `snap_types.h`, `xlist`, and `Inode` forward declarations. `Client` owns the map of realms and updates, while `Inode` references a `SnapRealm` and links into `inodes_with_caps`.

## Risks and Edge Cases
The raw pointer parent/child graph requires disciplined unlinking. Cached context invalidation must propagate to children when inherited snapshots change. `is_snapdir_visible` affects user-visible namespace behavior and should track MDS policy exactly.

## Test Signals
Tests should inspect snap context cache rebuild, parent switches, child invalidation, snapdir visibility propagation, and no dangling `inodes_with_caps` links on inode release.
