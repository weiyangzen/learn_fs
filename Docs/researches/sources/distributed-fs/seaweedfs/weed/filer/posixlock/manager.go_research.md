# sources/distributed-fs/seaweedfs/weed/filer/posixlock/manager.go

## Purpose

`posixlock/manager.go` implements the concurrent, per-filer authority for POSIX advisory locks across inode keys. It wraps per-inode `Set` objects with a mutex, tracks which sessions hold locks on which keys, and reaps stale leased sessions efficiently.

## Important APIs, Types, and Functions

`Manager` holds `byKey`, `bySid`, and `lastSeen`. Public methods include `NewManager`, `Renew`, `ReapExpired`, `TryLock`, `Track`, `Snapshot`, `Reassert`, `Unlock`, `GetLk`, `ReleasePosixOwner`, `ReleaseFlockOwner`, and `ReleaseSession`. Internal helpers maintain the session index.

## Control Flow

`TryLock` creates a set on demand, calls `Set.Acquire`, indexes the session on success, and returns conflicts on failure. `Track` inserts already-granted locks without arbitration for client-side mirrors. `Reassert` renews a session lease, removes that session's current locks on the key, tries to reacquire asserted locks against other sessions, records conflicts, and prunes empty sets/index entries. Release methods delegate to `Set` then call `afterRelease`.

`ReapExpired` scans only sessions that have called `Renew`, releases their locks across indexed keys when the last heartbeat is older than the TTL, and removes lease/index state.

## State and Persistence Behavior

All lock state is transient in memory and intentionally not replicated through metadata logs. `bySid` is an index for O(locks-held) cleanup, while `lastSeen` determines which sessions are lease-managed. Restarting a filer loses authoritative lock state unless clients reassert.

## Dependencies and Integration Points

The manager depends on the pure `Set` algorithm in `posixlock.go`. It integrates with FUSE/mount lock RPCs, owner-filer routing by path or hardlink key, mount keepalives, and reassertion after owner changes.

## Risks and Edge Cases

Sessions that never renew are never reaped, preserving backward compatibility but risking stale locks if keepalives are absent. Reassertion can conflict with locks acquired during an owner migration gap and reports those conflicts without double-granting. The manager serializes all keys with one mutex, which is simple but can become contended under high lock churn.

## Test Signals

Tests should cover conflict/grant, index pruning, partial unlock, GETLK, namespace-specific owner releases, session-wide release, stale leased reaping, concurrent flock mutual exclusion, reassert rebuild/idempotence/conflict, and lease renewal.
