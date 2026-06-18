# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_create.c

## Purpose

`afs_vnop_create.c` implements file creation and open-with-create behavior, including existing-file handling, server `CreateFile` RPCs, dcache directory updates, disconnected-mode fake fid creation, callback optimism, and local directory consistency through `afs_LocalHero`.

## Important APIs, Types, and Functions

- `afs_create` creates or opens a file in a directory vcache.
- `afs_LocalHero` decides whether a directory dcache can be locally updated after a successful mutating RPC by checking callback freshness and expected data version.

Important internal state includes `OutFidStatus`, `OutDirStatus`, `InStatus`, `newFid`, parent dcache `tdc`, callback counters `afs_evenCBs`/`afs_evenZaps` or foreign-cell equivalents, and disconnected dirty flags.

## Control Flow

`afs_create` validates name length, AFS entry-name legality, and unsupported special file types. It evaluates fakestat, verifies the parent directory, rejects read-only and disconnected-read-only cases, fetches the parent directory dcache, and write-locks the parent. If the name already exists in the dcache, exclusive create returns `EEXIST`; non-exclusive create obtains the existing vcache, checks requested read/write rights, and performs truncation via `afs_setattr` when requested.

If the name does not exist, online mode sends `RXAFS_CreateFile` through `afs_Conn`/`afs_Analyze`; an `EEXIST` race in non-exclusive mode falls back to lookup. Disconnected write mode generates a fake fid. After a successful create, the parent dcache is updated through `afs_dir_Create` when disconnected or `afs_LocalHero` confirms data-version consistency. The new vcache is then found or created under `afs_xvcache`, callback/status is installed if optimistic callback counters still match, and disconnected creates are marked dirty.

`afs_LocalHero` compares server `AFSFetchStatus` data version with the expected dcache version plus an increment. If valid, it marks the dcache entry modified and updates version; otherwise it zaps the dcache and purges directory name lookup cache.

## State and Persistence Behavior

Online creates persist via the fileserver RPC and then opportunistically update local directory dcache. Disconnected creates persist only as local fake-fid vcaches and dirty records until replay. Parent link counts and child status are updated locally when possible. Callback queue state may be installed optimistically or invalidated if races occurred.

## Dependencies and Integration Points

The file depends on access checks, dcache directory functions, vcache hash/creation, callback queue, volume lookup, RX fileserver RPCs, disconnected-mode helpers, mariner logging, and `afs_setattr` for truncation of existing files. `uafs_open_r` calls this path for `O_CREAT`.

## Risks and Edge Cases

Create races are explicitly complex: existing dcache entries with unique zero require lookup, non-exclusive `EEXIST` falls back to lookup, and callback optimism relies on global callback/zap counters. If `afs_GetDCache` returns null, the function returns `EIO` to avoid repeated status calls. Disconnected fake fid handling must avoid collisions and replay conflicts. Existing-file truncation temporarily marks `CCreating`.

## Test Signals

Test exclusive/non-exclusive create, create existing regular file with and without truncate, unsupported special types, invalid names, overlong names, read-only volumes, disconnected read-only, disconnected write fake-fid creation/replay, callback race invalidation, dcache update failure, and create/lookup races returning `EEXIST`.
