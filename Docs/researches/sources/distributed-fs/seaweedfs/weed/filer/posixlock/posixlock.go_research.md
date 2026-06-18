# sources/distributed-fs/seaweedfs/weed/filer/posixlock/posixlock.go

## Purpose

`posixlock/posixlock.go` implements the pure byte-range advisory lock algorithm for one inode. It handles fcntl and flock namespaces, read/write conflict rules, same-owner upgrades/downgrades, range coalescing, splitting, and owner/session release.

## Important APIs, Types, and Functions

Constants `Read`, `Write`, and `Unlock` define platform-independent lock types. `Range` describes inclusive `[Start,End]` locks with session, owner, pid, and flock namespace. `Set` stores sorted held locks. Public methods are `Conflict`, `Acquire`, `Grant`, `Release`, `ReleaseOwner`, `ReleaseFlockOwner`, `ReleasePosixOwner`, `ReleaseSession`, `HasPosix`, `Locks`, and `Empty`.

## Control Flow

`Conflict` scans held locks and returns the first overlapping lock in the same namespace from a different owner where at least one side is a write. `Acquire` calls `Conflict`, then inserts if clear. `insert` removes/adjusts same-owner overlaps: same-type ranges are widened/coalesced, different-type overlaps are split around the new range, and adjacent same-type ranges merge without overflowing at `MaxUint64`. `remove` drops or splits matching locks across a range, supporting unlock and owner/session cleanup.

## State and Persistence Behavior

`Set` is in-memory and has no internal synchronization; callers must serialize. The stored slice is sorted by start offset and aliases internal state when returned by `Locks`. Lock end offsets are inclusive; `math.MaxUint64` represents EOF.

## Dependencies and Integration Points

The file depends only on `math` and `sort`. It is used by `Manager` for server-side lock authority and by client-side mirrors for reassertion.

## Risks and Edge Cases

Same owner identity includes `(Sid, Owner)` for conflicts but `sameOwner` ignores `IsFlock`; namespace checks are performed separately by callers in conflict/insert paths. Off-by-one errors around inclusive ranges and `MaxUint64` adjacency are safety-critical. `Locks` exposes mutable internal slice content by contract, so callers must not mutate it.

## Test Signals

Tests should cover read/read sharing, write conflicts, same-owner type replacement, coalescing, splitting, whole-file locks, namespace separation, session identity, owner/session releases, and max-end overflow avoidance.
