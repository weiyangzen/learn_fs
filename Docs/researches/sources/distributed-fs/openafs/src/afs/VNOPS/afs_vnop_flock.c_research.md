# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_flock.c

## Purpose

`afs_vnop_flock.c` implements AFS whole-file locking and maps local `fcntl` lock requests to fileserver lock RPCs. It tracks local simple locks, handles shared/exclusive lock compatibility, exposes get-lock queries, and deliberately degrades byte-range locks to warnings/success.

## Important APIs, Types, and Functions

- `lockIdSet` stores the current process identity into an `AFS_FLOCK` or `SimpleLocks`, with platform-specific pid/sysid handling and UKERNEL using `get_user_struct()->u_procp->p_pid`.
- `lockIdcmp2` checks whether a flock identity differs from a simple lock or all locks on a vcache.
- `HandleFlock` performs whole-file lock, unlock, upgrade, downgrade, retry, and server RPC logic.
- `afs_lockctl` is the vnode lock-control entry point for `F_GETLK`, `F_SETLK`, and `F_SETLKW`.
- `HandleGetLock` reports whether a requested lock would be blocked.
- `GetFlockCount` asks the fileserver for lock count through `RXAFS_FetchStatus`.
- `DoLockWarning` rate-limits warnings for ignored byte-range locks.

## Control Flow

`afs_lockctl` creates a request, evaluates fakestat, handles `F_GETLK` through `HandleGetLock`, rejects write locks on read-only volumes, normalizes Java's maximum `l_len` to whole-file, warns and succeeds for true byte-range locks, maps `F_RDLCK`/`F_WRLCK`/`F_UNLCK` to `LOCK_SH`/`LOCK_EX`/`LOCK_UN`, applies nonblocking flags, and calls `HandleFlock`.

`HandleFlock` write-locks the vcache. Unlock removes matching local simple locks and releases the server lock with `RXAFS_ReleaseLock` when local count reaches zero; exclusive unlock first stores dirty segments synchronously and retries checks because store can drop locks. Lock acquisition handles local compatibility, same-process exclusive regrabs, shared/exclusive upgrade/downgrade, server `RXAFS_SetLock` for first local lock, wait/retry for blocking requests, and local simple-lock record insertion.

`HandleGetLock` answers from local `flockCount`/`slocks` when possible and calls `GetFlockCount` when server state is needed. `GetFlockCount` uses a nonblocking request flag and treats RPC failures as unlocked.

## State and Persistence Behavior

Lock state lives in `avc->flockCount`, `avc->slocks`, and platform-specific owner fields such as AIX `ownslock`. Server-visible locks persist in fileserver state until released or timed out. Unlock of exclusive locks flushes dirty file segments to the server before releasing.

## Dependencies and Integration Points

It depends on vcache locks, RX fileserver RPCs `SetLock`, `ReleaseLock`, and `FetchStatus`, request creation, fakestat, disconnected-mode flags, `afs_StoreAllSegments`, process identity macros, and warning/logging helpers. `Afs_vnodeops.vn_lockctl` points here in UKERNEL.

## Risks and Edge Cases

Byte-range locks are not enforced across machines and are reported as success after warning. Disconnected lock acquisition pretends success, while release can return `ENETDOWN`, which can mask cross-client conflicts. `HandleGetLock` contains duplicated write-lock decision blocks, increasing maintenance risk. RPC failure in `GetFlockCount` lies that the file is unlocked. Lock upgrades are intentionally limited and process-identity comparisons vary by platform.

## Test Signals

Test shared and exclusive locks, nonblocking conflicts, blocking retry/interruption, same-process reentrant exclusive lock, shared-to-exclusive upgrade, exclusive-to-shared downgrade, unlock by child/parent rules, read-only volume behavior, byte-range warning rate limiting, disconnected locking, and dirty segment store before exclusive unlock.
