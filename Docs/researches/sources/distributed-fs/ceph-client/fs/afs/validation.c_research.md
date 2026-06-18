<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/validation.c -->
# sources/distributed-fs/ceph-client/fs/afs/validation.c

## Purpose
Determines whether cached vnode and volume state is valid, updates callback/VolSync state after operations, and invalidates local cache/pagecache when server state changes.

## Important APIs, Types, And Functions
Exports `afs_check_validity()`, `afs_update_volume_state()`, and `afs_validate()`. Internal helpers compare server exclusion state, update volume creation/update timestamps, detect RO snapshot release or regressions, and zap vnode data through fscache/pagecache invalidation.

## Control Flow
Fast validity checks compare vnode deletion, volume break/check counters, callback promise deadlines, RO snapshot and scrub counters, and zap flags. Blocking validation serializes on `vnode->validate_lock`, optionally locks `volume->cb_check_lock`, fetches status when callbacks expire or counters diverge, updates vnode mirrors of volume counters, and zaps data if scrub/zap state advanced. Operation completion calls `afs_update_volume_state()` to process VolSync and callback promises.

## State And Persistence
Mutates `volume->creation_time`, `update_time`, `cb_v_check`, `cb_ro_snapshot`, `cb_scrub`, `cb_expires_at`, server-entry callback expiry, vnode callback mirror counters, and local cache/pagecache contents. Persistence is remote AFS server state; local cache is invalidated as needed.

## Dependencies And Integration Points
Uses callback break logic, fileserver operation status fetch, volume server-list refresh, fscache/netfs, pagecache invalidation, and rotation success handling.

## Risks And Edge Cases
RO volume release must avoid serving older replicas. Timestamp regression requires cache scrub. Near-expiry callbacks use a 10-second deadline. Parallel operations race through VolSync updates and rely on locks/cmpxchg-style checks to avoid duplicate or missed breaks.

## Test Signals
Callback expiry, CB.InitCallBackState, vnode callback break, RO `vos release`, volume restore/regression, mmap invalidation, deleted vnode status fetch, and concurrent validations are core tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/validation.c -->
