# subset-b-007759 research

Grouped research for OpenAFS cache-manager pioctl, prototype, and segment-management sources. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_pioctl.c -->
# sources/distributed-fs/openafs/src/afs/afs_pioctl.c

## Purpose

`afs_pioctl.c` implements the Unix/OpenAFS cache manager's path ioctl and vnode ioctl control plane. It is the kernel-facing backend for many `fs` command operations: ACL fetch/store, token set/get/unlog, cache and callback flushes, cell and alias management, volume status changes, server preference tuning, RX statistics toggles, disconnected-mode transitions, callback address changes, NFS translator credential handling, and FID/status inspection. It also provides small buffer-cursor helpers (`struct afs_pdata`) that make the varied pioctl payload formats less fragile than open-coded pointer arithmetic.

## Important APIs, types, and functions

- `struct afs_pdata` tracks a moving pointer and remaining byte count for pioctl input/output buffers. Helpers include `afs_pd_alloc`, `afs_pd_free`, `afs_pd_getBytes`, `afs_pd_getInt`, `afs_pd_getStringPtr`, `afs_pd_putBytes`, `afs_pd_putString`, `afs_pd_inline`, and XDR wrappers `afs_pd_xdrStart`/`afs_pd_xdrEnd`.
- `DECL_PIOCTL(name)` defines the common internal pioctl handler signature: `(struct vcache *avc, int afun, struct vrequest *areq, struct afs_pdata *ain, struct afs_pdata *aout, afs_ucred_t **acred)`.
- `VpioctlSw`, `CpioctlSw`, and `OpioctlSw` map pioctl device/function numbers to handlers. Device `'V'` carries original Venus pioctls, `'C'` newer coordinated/common operations, and `'O'` OpenAFS/private operations.
- `HandleIoctl` handles vnode ioctl commands on an already-open AFS vnode. It is much smaller than the pioctl path and supports safe-store, file-cell lookup, and cache-manager init parameter retrieval.
- `afs_xioctl` has multiple platform-specific implementations for AIX, SGI, Solaris, Linux, Darwin/BSD, and UKERNEL. Each detects AFS vnodes, copies in `struct afs_ioctl`, enters the AFS global lock where needed, and routes to `HandleIoctl`; non-AFS calls are passed through or rejected.
- `afs_syscall_pioctl` is the main syscall entry: it copies in the `afs_ioctl` descriptor, optionally applies NFS translator client context, handles the prefetch special case, resolves the path to a vnode, and dispatches to `afs_HandlePioctl`.
- `afs_HandlePioctl` creates a `vrequest`, evaluates fakestat, validates device/function and buffer sizes, copies user input into kernel memory, allocates output space, calls the selected handler, copies output to user space, and finalizes request/error handling.
- High-value handlers include `PSetAcl`, `PGetAcl`, `PSetTokens`, `PSetTokens2`, `PGetTokens`, `PGetTokens2`, `PUnlog`, `PGetVolumeStatus`, `PSetVolumeStatus`, `PFlush`, `PRemoveCallBack`, `PNewCell`, `PNewAlias`, `PListCells`, `PRemoveMount`, `PFlushVolumeData`, `PFlushAllVolumeData`, `PSetSysName`, `PSetSPrefs`, `PGetSPrefs`, `PExportAfs`, `PGetRxkcrypt`, `PSetRxkcrypt`, `PDiscon`, `PCallBackAddr`, `PNFSNukeCreds`, and `PGetLiteralFID`.

## Control flow

There are two main entry families. The vnode ioctl family starts with platform-specific `afs_xioctl` or AIX `afs_ioctl` wrappers. These inspect the file descriptor/vnode, confirm it is an AFS vnode, copy the small `struct afs_ioctl` descriptor from userspace, then call `HandleIoctl`. `HandleIoctl` switches on the low command byte and performs a few legacy ioctl operations without the full path-lookup/pioctl machinery.

The path pioctl family enters through `afs_syscall_pioctl` (or `afs_syscall64_pioctl` on modern Darwin). The function normalizes `follow`, copies in the user `struct afs_ioctl`, and checks for `PSetClientContext`, which allows an NFS translator process to supply remote client credentials. It special-cases VIOC prefetch so the whole pathname evaluation can run in a background helper. Otherwise it resolves `path` to a vnode with platform lookup helpers, optionally unwraps Solaris real vnodes, and only proceeds when the target is absent or an AFS vnode. It then calls `afs_HandlePioctl` with the vnode, command, descriptor, follow flag, and active credentials. Finally it restores any temporary foreign credentials, releases the vnode/dentry, frees referenced credentials, and returns a checked errno.

`afs_HandlePioctl` performs the common dispatch. It creates an `afs_vrequest`, evaluates fakestat for mount-point fakery, selects a switch table based on command device byte, validates input/output lengths and token payload maxima, copies user input into an `afs_pdata`, allocates a bounded output buffer, calls the selected handler with copied cursors, computes the output length from pointer movement, and copies successful output back to userspace. It then zeros/frees input/output buffers, releases fakestat state, maps filesystem/RX errors through `afs_CheckCode`, and destroys the request.

Individual handlers follow repeated patterns: validate `avc` and input buffer, check init state or superuser privileges, acquire local cache/user/cell/server locks, call cache-manager helpers or fileserver RX RPCs, retry RPCs through `afs_Analyze`, update local state, and return errno-style codes. ACL and volume operations use `afs_Conn`, `RXAFS_*` calls, XSTATS timing, and RX/AFS global-lock drop/reacquire blocks. Cache-flush operations walk vcache/dcache/volume tables under locks. Token operations parse legacy binary or XDR token payloads and update `unixuser` token jars.

## State and persistence behavior

This file mutates extensive cache-manager runtime state. Global state includes `afs_rootFid`, message gag flags (`afs_showflags`), disconnected-mode state (`afs_is_disconnected`, `afs_is_discon_rw`, `afs_in_sync`), default store-behind asynchrony, NFS exporter policy (`afs_NFSRootOnly`), RX encryption setting (`cryptall` from another module), RX tunables, probe interval, cache size counters, callback interface addresses/UUID, sysname generation, server rankings, and token/user structures.

Token state is stored in `struct unixuser` entries keyed by PAG/uid and cell. `PSetTokens` replaces legacy rxkad tokens, `PSetTokens2` replaces a token jar from XDR-encoded token unions, `PGetTokens` and `PGetTokens2` export tokens, and `PUnlog`/`PNFSNukeCreds` clear tokens and reset user connections. Sensitive pioctl buffers are zeroed before being returned to the allocator, though `afs_pd_free` only zeros the bytes still represented by `remaining`, not necessarily the original allocation span after cursor movement.

Cache state is changed by flush and sizing commands. `PFlush` resets a single vcache. `FlushVolumeData` invalidates vcaches in a volume or all volumes, flushes eligible dcaches, resets volume metadata, and purges the DNLC. `PSetCacheSize` changes `afs_cacheBlocks`, recomputes cache parameters, wakes the truncate daemon, and waits briefly for shrink progress.

Fileserver-persistent state can be changed by `PSetAcl`, `PSetVolumeStatus`, and `PRemoveMount`, which issue RXAFS RPCs to servers. `PDiscon` persists locally modified disconnected files back to the server when switching online through `afs_ResyncDisconFiles`, or discards them when forced.

## Dependencies and integration points

`afs_pioctl.c` integrates with nearly every cache-manager subsystem. It depends on vcache lookup and validation (`afs_GetVCache`, `afs_VerifyVCache`, `afs_ResetVCache`, fakestat helpers), dcache access (`afs_GetDCache`, `afs_FlushDCache`), cell and volume management (`afs_GetCell*`, `afs_NewCell`, `afs_GetVolume`, `afs_ResetVolumeInfo`), user/token management (`afs_GetUser`, `afs_FindUser`, token-jar helpers), server/ranking state (`afs_srvAddrs`, `afs_servers`, `afs_GetServer`, `afs_SortServers`), RX/RXAFS RPCs, directory helpers (`afs_dir_Lookup`, `afs_dir_Delete`), DNLC functions, background daemon queues, OS-specific vnode/file-descriptor lookup, credential/PAG helpers, NFS exporter hooks, sysname support, disconnected-mode resync, and cache bypass support when enabled.

The public declarations in `afs_prototypes.h` expose `afs_syscall_pioctl`, `afs_xioctl`, and `HandleIoctl`, while userland ABI details come from `struct afs_ioctl`, pioctl command numbers, token XDR types, and related `fs` command payload structures.

## Risks and edge cases

- This is a security-sensitive syscall surface. Many handlers correctly require `afs_osi_suser`, but the command set is broad and mixed with NFS translator credential substitution. Authorization regressions can expose cell, cache, token, or RX state.
- Several handlers intentionally depend on variable-length C structs or "writing past the end of arrays" conventions (`PSetSPrefs`, `PGetSPrefs`, `PGetCPrefs`, `PSetCPrefs`). The new `afs_pdata` helpers reduce risk but do not fully eliminate ABI fragility.
- String extraction helpers use `strlen(apd->ptr)` before explicitly proving a NUL byte exists inside `remaining`. `afs_pd_alloc` adds a guard NUL after copied input, so many cases are protected, but malformed embedded layouts can still make a logical field consume the guard rather than a caller-provided terminator.
- `afs_pd_free` zeroes from the current cursor for `remaining` bytes. If a buffer contained tokens and the cursor advanced, consumed bytes may not be scrubbed by this helper. Some local structs are separately cleared, but this is a sensitive-memory review point.
- `afs_HandlePioctl` computes switch-table size using `sizeof(table)` but compares `function >= pioctlSwSize / sizeof(char *)`; this assumes function pointer size equals `char *` size. That is true on normal supported ABIs but brittle style.
- `PCheckServers` peeks at `*(afs_int32 *)ain->ptr` before alignment-safe copying. Kernel alignment requirements vary by architecture.
- `FlushVolumeData` skips dirty or referenced dcaches and loops around vcaches in transitional states. It is best-effort and can return `EIO` on dslot read failure; flush semantics are not a hard guarantee for actively used data.
- `PDiscon` mode values are hard-coded to match userland `fs.c`, so ABI drift breaks offline/online behavior.

## Test signals

Useful validation includes pioctl ABI tests for every populated `V`, `C`, and `O` switch entry; malformed size/string/XDR inputs; token set/get/unlog round trips for legacy and XDR token formats; root vs non-root authorization checks; NFS translator client-context scenarios; ACL and volume status operations against test fileservers; cache flush and cache-size behavior with dirty and referenced chunks; server preference pagination; sysname get/set including invalid names; disconnected offline/online/force flows; and platform wrapper tests that non-AFS ioctls pass through while AFS vnodes route to the cache manager. Kernel memory instrumentation should specifically watch pioctl buffer bounds, credential reference lifetimes, token memory scrubbing, and lock ordering around vnode/dentry release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_pioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/afs_prototypes.h

## Purpose

`afs_prototypes.h` is the main internal prototype aggregation header for the non-Windows OpenAFS cache manager. It does not implement behavior; it publishes cross-file globals, function declarations, platform-specific syscall/vnode signatures, helper macros, and a few small type/flag definitions so the cache-manager modules can call each other consistently across Unix kernels and UKERNEL builds.

## Important APIs, types, and functions

The header is organized by source module. Major groups include:

- Analysis and request/error handling: `afs_Analyze`, `afs_CheckCode`, `afs_FinalizeReq`, `afs_CopyError`.
- Initialization and shutdown: `afs_CacheInit`, `afs_ResourceInit`, `shutdown_AFS`, per-subsystem shutdown functions.
- Cell, volume, server, and connection management: `afs_NewCell`, `afs_GetCell*`, `afs_GetVolume*`, `afs_CheckVolumeNames`, `afs_Conn*`, `afs_PutConn`, `afs_GetServer`, `afs_SortServers`, `afs_CheckServers`.
- Dcache and fetch/store interfaces: `afs_GetDCache`, `afs_FindDCache`, `afs_ObtainDCacheForWriting`, `afs_CacheStoreVCache`, `afs_CacheFetchProc`, `afs_FlushDCache`, dcache hash/table globals, and cache type globals.
- Segment interfaces: `afs_StoreAllSegments`, `afs_InvalidateAllSegments`, `afs_InvalidateAllSegments_once`, `afs_ExtendSegments`, and `afs_TruncateAllSegments`.
- Pioctl interfaces: globals such as `afs_rootFid`, `afs_waitForever`, `afs_showflags`, `afs_defaultAsynchrony`, plus `afs_syscall_pioctl`, `afs_syscall64_pioctl` where applicable, platform-specific `afs_xioctl`, and `HandleIoctl`.
- Credential/PAG/token support: `afs_setpag`, `setpag`, `AddPag`, `afs_CreateReq`, `afs_DestroyReq`, PAG encoding helpers, token-jar add/free/extract helpers, and pioctl token cleanup helpers.
- Vcache and vnode operation APIs: vcache lookup/lifetime, stale-callback helpers, status processing, remote lookup, access/attrs/create/lookup/read/write/readdir/remove/rename/symlink/fsync vnode operations.
- OSI abstraction declarations: allocation, sleep/wakeup, file I/O, VM operations, process credentials, random reads, inode syscalls, and platform-specific VFS roots.

It also defines `enum afs_shutdown_type` and `afs_stalevc_flags_t` plus `AFS_STALEVC_*` flags that tune vcache invalidation behavior.

## Control flow

As a header, runtime control flow is indirect. Its practical control-flow role is compile-time wiring: modules include it through `afsincludes.h`/related include chains, then the compiler can type-check calls across subsystem boundaries. Conditional blocks select signatures based on platform macros such as `AFS_SUN5_ENV`, `AFS_LINUX_ENV`, `AFS_DARWIN_ENV`, `AFS_XBSD_ENV`, `AFS_AIX_ENV`, `AFS_SGI_ENV`, `AFS_FBSD_ENV`, `AFS_NBSD_ENV`, and `UKERNEL`.

The declarations mirror the cache manager's high-level runtime flow: syscalls and vnode ops create requests and credentials, pioctls/vnode ops validate vcaches, dcache/fetchstore code moves file data, RX connection/server/volume code contacts fileservers, callbacks and DNLC maintain cache coherency, and shutdown paths unwind initialized modules.

## State and persistence behavior

The header exposes many process/kernel-lifetime globals. Examples include cache sizing and dcache tables (`afs_cacheBlocks`, `afs_blocksUsed`, `afs_indexFlags`, `afs_dvhashTbl`, `cacheDiskType`), cell/server/volume hash tables and locks, callback counters and interface address state, user/token tables, vcache LRU/hash lists, system-name state, PAG counters, mariner monitor state, stats structures, and global VFS/root vnode pointers.

Persistent on-disk state is not managed in this header, but several declarations refer to cache metadata files and inodes (`cacheInode`, `volumeInode`, `vcacheMetaInode`, cache-info/cell-info/volume-info init/write functions) and to operations that write filesystem-visible state through fileserver RPCs or local cache files. Because these globals are declared here, any signature or type mismatch can propagate into persistent cache layout, token lifetime, or server-side mutation paths.

## Dependencies and integration points

`afs_prototypes.h` depends on prior inclusion of OpenAFS core type definitions for `struct vcache`, `struct dcache`, `struct vrequest`, `struct cell`, `struct volume`, `struct server`, `struct unixuser`, `struct afs_conn`, `afs_int32`, `afs_size_t`, locks, vnode/credential types, RX types, AFS RPC structs, and platform ABI types. It finishes by including `osi_prototypes.h` for supported kernel/user-kernel environments, extending the platform abstraction layer.

The file is an integration map for the subset's other sources. It declares the `afs_pioctl.c` syscall/ioctl entry points and the `afs_segments.c` segment-store/truncate/invalidate functions. It also exposes the fetchstore, dcache, vcache, VM, server, volume, token, and request APIs that those implementations call.

## Risks and edge cases

- This header is very broad. A small signature mismatch can break multiple platforms or silently select the wrong ABI under conditional compilation.
- Several declarations are platform-specific and use old kernel ABI types (`rval_t`, `register_t`, `user_addr_t`, `struct ioctl_args`, `struct inode`, `struct file`, `cred_t`). Build coverage must span the supported platforms, not just Linux.
- There is a likely typo in one conditional: `AFS_DAWRIN_ENV` appears in the `afs_xioctl` declaration branch, while the surrounding code uses `AFS_DARWIN_ENV`. If active, that branch would not compile as intended.
- The file exposes writable globals freely. This matches the historic C cache-manager style but makes invariants difficult to enforce across modules.
- Duplicate declarations appear in a few places, such as repeated shutdown or helper prototypes. They are mostly harmless when identical, but they increase maintenance risk.
- Many declarations depend on macros defining `extern` replacements or platform-specific function-like macros. Missing include ordering can produce confusing compile failures.

## Test signals

The strongest tests are cross-platform compile and sparse/static-analysis runs that include every supported conditional branch. Module-level tests should verify that `afs_pioctl.c` and `afs_segments.c` implementations match the prototypes exactly, especially around credential pointer mutability, vnode/syscall signatures, and `afs_size_t` vs `int` truncation. ABI review should cover exported pioctl/syscall entry points, vnode op declarations, token XDR declarations, and stale-vcache flags. Header hygiene checks should flag duplicate prototypes, misspelled platform macros, and declarations of globals without a single owning definition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_segments.c -->
# sources/distributed-fs/openafs/src/afs/afs_segments.c

## Purpose

`afs_segments.c` manages the cache manager's per-file data segments: storing dirty dcaches back to fileservers, issuing minimal truncation/extension stores, invalidating cached chunks, extending local cache chunks with zeroes, and truncating local cached chunks. It is the bridge between vnode-level file size changes, VM page flushing, local dcache metadata, and RXAFS store RPCs.

## Important APIs, types, and functions

- `afs_StoreMini(struct vcache *avc, struct vrequest *areq)` is a private helper that sends a zero-length data store/truncation request to the fileserver when the client has only changed length metadata or needs to extend the server-side length.
- `afs_StoreAllSegments(struct vcache *avc, struct vrequest *areq, int sync)` stores all dirty dcache chunks for a vcache, updates data versions, clears dirty state when safe, and handles post-error invalidation.
- `afs_InvalidateAllSegments_once(struct vcache *avc)` performs a single attempt to invalidate all dcache chunks for a vcache.
- `afs_InvalidateAllSegments(struct vcache *avc)` wraps the single attempt and retries indefinitely via background daemon requests if invalidation fails after a fatal store error.
- `afs_ExtendSegments(struct vcache *avc, afs_size_t alen, struct vrequest *areq)` grows local cache chunks to a target file length by writing zero pages.
- `afs_TruncateAllSegments(struct vcache *avc, afs_size_t alen, struct vrequest *areq, afs_ucred_t *acred)` truncates local cache and VM state to a new length, or marks a pure extension for later store.
- Globals include `afs_stampValue`, `NCHUNKSATONCE` (64 normally, 3 on HPUX), and `afs_dvhack`.

## Control flow

`afs_StoreAllSegments` is called with the vcache write-locked. It allocates a dcache pointer list, traces the store, and flushes dirty VM pages unless the sync flags/platform/cache type say not to. If disconnected and not in sync mode, it returns `ENETDOWN`. It snapshots the starting data version and callback count, downgrades the vcache lock to shared, and repeatedly scans the dcache DV hash chain for chunks marked `IFDataMod` matching the vcache FID. It collects at most `NCHUNKSATONCE` contiguous chunk slots starting at `minj`, then calls `afs_CacheStoreVCache` to perform the actual store RPCs and dcache state updates.

After all dirty chunks are stored, the function upgrades the vcache lock back to write mode. If no data store extended the fileserver to the current client length, or if `truncPos` is set, it calls `afs_StoreMini`; a successful mini-store increments the expected new data version. It then makes a second pass over matching dcaches to relabel eligible chunk `versionNo` values, set `DFEntryMod`, and clear `DWriting`. The relabel only happens when the cache manager can prove no intervening callback/data-version change invalidated the local view: either the vcache data version equals `newDV`, or the `afs_dvhack`/foreign path has not observed a global callback-count change.

If a store failed permanently or the vcache is a core file, dirty local data is invalidated to avoid later serving bytes that were not stored on the server. Finally the function may clear `CDirty` and advance `mapDV` when VM pages and data versions line up. Temporary write errors are suppressed unless the request has a permanent write error or `AFS_LASTSTORE` is set.

`afs_StoreMini` builds an `AFSStoreStatus` with client mod time, computes the shorter of current length and `truncPos`, clears truncation/extension markers, obtains a fileserver connection, and starts `StoreData64` when possible. If the server rejects 64-bit opcodes, it marks that server as no-64-bit and retries the 32-bit RPC when lengths fit. On success it calls `afs_ProcessFS` with the returned status.

`afs_InvalidateAllSegments_once` asserts the vcache write lock, clears truncation/extension/dirty indicators, optionally releases Solaris VM pages, counts matching dcaches under `afs_xdcache`, stores references in an allocated array, clears dirty/page index flags, then zaps each dcache under its own lock. Directory dcaches also call `DZap`. On dslot errors it releases held references and returns `EIO`.

`afs_InvalidateAllSegments` calls the single-shot invalidator. If it fails, it warns, then loops forever: wait ten seconds, queue `BOP_INVALIDATE_SEGMENTS` to a background daemon while retaining the vcache write lock, wait for completion, and retry until success. The comments explain this is required to avoid serving failed-store data indefinitely.

`afs_ExtendSegments` allocates one zero page, obtains writable dcaches chunk by chunk, opens each cache file, writes zero-filled pages until `validPos` reaches the extended range, adjusts dcache size, advances `avc->f.m.Length`, and releases each dcache. `afs_TruncateAllSegments` handles extension as a cheap `CExtendedFile` length update. For shrink, it performs VM pre-truncate/truncate work, updates `truncPos`, gathers all matching dcaches, and truncates or zero-sizes cache files and validity metadata beyond the new length.

## State and persistence behavior

The file mutates both local cache metadata and fileserver-persistent state. Server persistence happens through `RXAFS_StoreData`/`StoreData64` in `afs_StoreMini` and through `afs_CacheStoreVCache` in the full-store path. Local persistent cache state includes dcache file sizes, `chunkBytes`, `validPos`, dirty flags, `DWriting`, `DFEntryMod`, dcache data versions, and dcache index flags such as `IFDataMod` and `IFAnyPages`.

Vcache state changed here includes `f.m.Length`, `f.m.Date`, `f.truncPos`, `CExtendedFile`, `CDirty`, `mapDV`, and stale/dirty flags. `afs_TruncateAllSegments` records truncations so a later store can tell the fileserver about the shorter length even if no dirty chunk is stored. `afs_ExtendSegments` writes zeroes into local cache files so reads from newly extended sparse ranges are backed by explicit zero data in the cache.

The invalidation retry loop is intentionally persistent in behavior even though it writes no durable marker: it holds the caller in a retry path until bad local chunks are zapped, because returning while invalidation failed could leave incorrect data in the disk cache.

## Dependencies and integration points

This file depends on dcache hash/index state (`afs_dvhashTbl`, `afs_dvnextTbl`, `afs_indexFlags`, `afs_indexUnique`, `afs_GetValidDSlot`, `afs_PutDCache`, `afs_AdjustSize`, `ZapDCE`, `DZap`), fetchstore (`afs_CacheStoreVCache`), vcache status processing (`afs_ProcessFS`, `afs_StaleVCacheFlags`), RXAFS RPC stubs, connection analysis (`afs_Conn`, `afs_Analyze`), VM integration (`osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_Truncate`, `osi_VM_PreTruncate`, `osi_ReleaseVM`), local cache file operations (`afs_CFileOpen`, `afs_CFileWrite`, `afs_CFileTruncate`, `afs_CFileClose`), background daemon queues (`afs_BQueue`, `afs_BRelease`), tracing/statistics, and disconnected-mode globals.

Its public functions are declared in `afs_prototypes.h` and are called from vnode write, setattr/truncate, close/fsync/inactive, error-recovery, and background daemon paths.

## Risks and edge cases

- Lock ordering is delicate. The implementation intentionally downgrades/upgrades `avc->lock`, scans `afs_xdcache`, and avoids taking `tdc->lock` in some places because of ordering constraints. Changes must preserve those constraints.
- `afs_StoreAllSegments` relies on sorted/contiguous chunk batches and repeats hash scans from the beginning to avoid races. Incorrect changes can skip dirty chunks or double-handle dcaches.
- Data-version relabeling is conservative but subtle. Mislabeling a stale dcache with the current DV would let the client serve old bytes as fresh.
- `afs_StoreMini` clears `truncPos` and `CExtendedFile` before the RPC path completes. Callers rely on later error handling and invalidation paths to recover from failed stores.
- The 32-bit fallback checks large lengths and returns `EFBIG` if they cannot be represented. Large-file tests must cover servers without 64-bit StoreData support.
- `afs_InvalidateAllSegments` can wait indefinitely when local cache I/O keeps failing. This is intentional for correctness but can appear as an AFS hang.
- `afs_ExtendSegments` advances `validPos` after each write without checking each `afs_CFileWrite` return before continuing; write-error handling deserves close review.
- `afs_TruncateAllSegments` asserts `afs_CFileOpen` succeeds in the truncation loop. Cache-file open failures in production kernels could become panics depending on assertion behavior.

## Test signals

Important coverage includes dirty multi-chunk file stores, sparse extension followed by StoreMini, truncate-without-dirty-data, truncation across chunk boundaries, server 64-bit and 32-bit StoreData paths, temporary vs permanent store errors, disconnected-mode `ENETDOWN`, ccore invalidation, dcache version relabeling after intervening callback/data-version changes, VM sync/invalidation flags on supported platforms, directory dcache invalidation, cache I/O failure injection for invalidation retry behavior, and large-file edge cases near 2 GiB for old servers. Instrumentation should watch `IFDataMod`, `DWriting`, `DFEntryMod`, `CDirty`, `CExtendedFile`, `truncPos`, `mapDV`, and `validPos` transitions before and after store/truncate/extend calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_segments.c -->
