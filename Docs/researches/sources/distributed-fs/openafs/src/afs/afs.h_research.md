# sources/distributed-fs/openafs/src/afs/afs.h

## Purpose
Defines core OpenAFS cache-manager constants, state bits, structures, queues, cache metadata, vnode/dcache contracts, background operation opcodes, and helper macros shared by the VNOPS implementation.

## Important APIs, Types, and Functions
Key types include `struct VenusFid`, `struct vrequest`, `struct cell`, `struct unixuser`, `struct afs_conn`, `struct server`, `struct volume`, `struct fvcache`, `struct vcache`, `struct fcache`, `struct dcache`, `struct brequest`, `struct afs_fakestat_state`, `struct storeOps`, and `struct fetchOps`. Important macros include queue operations `QAdd`, `QRemove`, `QTOV`; fid comparisons `FidCmp` and `FidMatches`; store flags `AFS_SYNC`, `AFS_LASTSTORE`, `AFS_NOVMSYNC`; background opcodes `BOP_FETCH`, `BOP_STORE`, `BOP_PARTIAL_STORE`; vcache state bits such as `CStatd`, `CDirty`, `CMValid`, `CUnlinked`, `CBulkStat`, `CBulkFetching`; disconnected flags such as `VDisconRemove`, `VDisconCreate`, `VDisconRename`, `VDisconWriteClose`; dcache flags `DFFetching`, `DFFetchReq`, `DFNextStarted`; and read/write wrappers `afs_rdwr` and `afs_nlrdwr`.

## Control Flow and State
This header has no standalone runtime flow, but its macros define how vnode paths select read versus write functions, how fake-open/fake-close increments writer counters and defers last-writer storeback with `CCore`, how vcache verification fast-paths `CStatd`, how queue entries are converted to containing structures, and how cache-full thresholds are computed.

`struct fvcache` captures persistent vnode metadata such as FID, length, data version, owner, mode, link count, parent, truncation position, state bits, disconnected dirty flags, shadow vnode, and old parent. `struct vcache` layers runtime locks, callback state, access cache, open/writer counts, mountpoint/root/silly-name union, link data, readdir hints, dirty queues, and platform vnode state on top. `struct fcache` is stored in dcache entries and records chunk identity, data version, cache inode, chunk size, and flags. `struct dcache` tracks locks, valid bytes, refcounts, data flags, and meta flags.

## Dependencies and Integration Points
Includes AFS syscall constants and parameter headers, depends heavily on platform compile-time environment macros, and is included by cache, callback, vnode, pioctl, daemon, fetch/store, and OS integration code. It exposes global tables such as `afs_indexTable`, `afs_indexUnique`, `afs_vhashT`, `afs_brs`, cache sizing counters, root FID, and callback statistics.

## Risks and Test Signals
Many macros mutate state without type or lock enforcement; callers must already hold the documented locks. `QRemove` assumes queue membership. `afs_FakeClose` stores credentials in `linkData` while `CCore` is active, creating implicit ownership coupling. `struct vcache` uses a union for silly unlink names, mountpoint target roots, and root parent FIDs, so `mvstat` and state bits must match the active field. Platform conditionals change structure layout and vnode reference semantics.

Test all supported platform configurations, validate vcache/dcache lock invariants, exercise fake-open/fake-close with last and non-last writer, cache-full threshold behavior, queue add/remove consistency, disconnected dirty flag replay, dcache fetch/write flags, bulk stat state bits, FID matching with zero unique/CUnique, and cache header migration or invalidation when persistent formats change.
