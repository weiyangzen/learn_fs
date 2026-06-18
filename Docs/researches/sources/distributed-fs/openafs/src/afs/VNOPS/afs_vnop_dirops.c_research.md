# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_dirops.c

## Purpose

`afs_vnop_dirops.c` implements directory creation and removal for OpenAFS vnode operations, including online fileserver RPCs, disconnected write-mode local directories, parent dcache edits, link count updates, and dnlc invalidation.

## Important APIs, Types, and Functions

- `afs_mkdir` creates a directory under a parent vcache.
- `afs_rmdir` removes a directory entry from a parent vcache.

Both functions use `struct vrequest`, `struct dcache`, `struct vcache`, `AFSStoreStatus`, `AFSFetchStatus`, fakestat state, RX connections, and disconnected-mode dirty helpers.

## Control Flow

`afs_mkdir` validates name length and legality, evaluates fakestat, verifies the parent, rejects read-only and disconnected-read-only operation, builds an `InStatus`, obtains the parent dcache, and locks the parent. Online mode sends `RXAFS_MakeDir`; disconnected write mode generates a fake fid. The parent dcache is updated via `afs_dir_Create` if disconnected or if `afs_LocalHero` validates the server status. Online mode then fetches the new directory vcache; disconnected mode creates a new vcache, generates status, creates an empty `.`/`..` dcache via `afs_dir_MakeDir`, updates length, and marks it `VDisconCreate`.

`afs_rmdir` validates name length, evaluates fakestat and parent freshness, rejects read-only and disconnected-read-only cases, obtains the parent dcache, optionally finds the target vcache, and online sends `RXAFS_RemoveDir`. Disconnected mode requires local dcache and target vcache, rejects non-empty directories by link count, creates a shadow parent dir if needed, and decrements parent link count. It then deletes the parent dcache entry, purges dnlc state, marks or removes disconnected dirty records, and clears `CUnique` on the removed vcache.

## State and Persistence Behavior

Online mkdir/rmdir persist through fileserver RPCs and update parent dcache/link count when local freshness allows. Disconnected writes persist as local dcache/vcache changes plus dirty operation records for later replay. Directory dcache contents and link counts are mutated under locks.

## Dependencies and Integration Points

This file depends on `afs_LocalHero` from create, directory package functions `afs_dir_Create`, `afs_dir_Delete`, and `afs_dir_MakeDir`, RX RPCs `MakeDir`/`RemoveDir`, dcache/vcache lookup, fakestat, disconnected helpers, dnlc purge/remove, and `afs_CheckCode`.

## Risks and Edge Cases

Disconnected `rmdir` relies on link count to decide emptiness, which can be stale if local state is inconsistent. Mountpoint-directory comments indicate incomplete disconnected handling for mountpoints. Parent dcache absence in disconnected mode results in `ENETDOWN`. Dcache update surprises zap directory caches, so callers must tolerate subsequent refetches.

## Test Signals

Test mkdir/rmdir online success, invalid and overlong names, read-only volumes, disconnected read-only rejection, disconnected write create/remove/replay, local empty directory construction, non-empty directory rejection, shadow directory creation, dnlc purge, and failures in parent dcache acquisition or new dcache creation.
