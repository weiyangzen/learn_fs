# sources/distributed-fs/juicefs/pkg/meta/tkv_lock.go

## Purpose
`tkv_lock.go` implements advisory BSD flock and POSIX byte-range locks for the KV metadata backend.

## Important APIs, Types, and Functions
Important types and helpers are `lockOwner`, `marshalFlock`, `unmarshalFlock`, `marshalPlock`, and `unmarshalPlock`. Public metadata methods are `Flock`, `Getlk`, `Setlk`, and `ListLocks`.

## Control Flow and State
Flock state is a map from `{sid, owner}` to `R`/`W`/unlock serialized under `F<inode>`. POSIX locks are a map from `{sid, owner}` to serialized `plockRecord` ranges under `P<inode>`. `Flock` and `Setlk` run transactional read/modify/write loops; conflicts return `EAGAIN`, and blocking callers sleep briefly and retry until success or context cancellation. `Getlk` removes the caller's own owner from consideration and returns the first conflicting lock. `ListLocks` decodes both lock families for diagnostics.

## State and Persistence Behavior
Locks are persisted in the metadata KV store and include the JuiceFS session id. Stale-session cleanup in `tkv.go` scans `F` and `P` prefixes and removes lock owners whose `sid` expired. Empty lock maps delete their key.

## Dependencies and Integration Points
It depends on lock constants and range helpers from `utils.go`, transaction/changelog helpers from `tkv.go`, and session cleanup. It implements the lock portions of the `Meta` interface for KV backends.

## Risks and Test Signals
Risks include unfair blocking spin loops, stale lock retention if session cleanup fails, large lock maps per inode, range merge/split bugs in `updateLocks`, and pid visibility only for same-session locks. Tests should cover shared/exclusive conflicts, unlock range splitting, blocking cancellation, stale session cleanup, and `ListLocks` decoding.
