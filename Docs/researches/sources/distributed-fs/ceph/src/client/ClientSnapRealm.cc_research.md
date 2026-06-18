# sources/distributed-fs/ceph/src/client/ClientSnapRealm.cc

## Purpose
`ClientSnapRealm.cc` implements the client-side snapshot realm helpers declared in `ClientSnapRealm.h`. A `SnapRealm` collects the snapshots that affect a subtree by combining local snapshots, prior parent snapshots, and current parent realm snapshots.

## Important APIs, Types, and Functions
`SnapRealm::build_snap_context()` builds `cached_snap_context` from `prior_parent_snaps`, parent `SnapContext` entries newer than `parent_since`, and `my_snaps`, selecting the maximum sequence from the realm and parent. `SnapRealm::dump()` emits realm identity, refs, parentage, snapshot lists, and child realm IDs to a `Formatter`.

## Control Flow
The build path starts with a sorted `set<snapid_t>`, inserts prior parent snaps, optionally asks `pparent->get_snap_context()` for inherited snaps, filters inherited snaps by `parent_since`, inserts local snaps, then writes the output vector in descending order. `get_snap_context()` in the header calls this lazily when the cached sequence is zero.

## State and Persistence Behavior
The implementation only maintains transient client cache. Snapshot authority and realm update messages come from the MDS; this code materializes the currently known effective context for cap snapshots and data IO. Cache invalidation is explicit through `invalidate_cache()` in the header.

## Dependencies and Integration Points
It depends on `SnapContext` from common snapshot types and `Formatter` for diagnostics. `Client` snapshot update code owns parent/child relationships and invalidation; `Inode` cap-snap logic consumes the resulting contexts.

## Risks and Edge Cases
Missing invalidation after parent changes would leave stale inherited snapshots. Parent recursion depends on a valid realm tree without cycles. The descending snapshot order is deliberate; callers expecting Ceph snap context order would break if changed. Filtering by `parent_since` is the key correctness boundary for moved realms.

## Test Signals
Exercise parent realm changes, realm-local snapshots, prior parent snapshots, cache invalidation, dump output, and snap context ordering after MDS snap trace updates.
