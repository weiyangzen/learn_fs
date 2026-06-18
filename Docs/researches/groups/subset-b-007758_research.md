# subset-b-007758 OpenAFS afs source research

Grouped research report for the source files assigned to `subset-b-007758`. Each section is delimited for reconciliation into a source-tree-aligned per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_fetchstore.c -->
# sources/distributed-fs/openafs/src/afs/afs_fetchstore.c

## Purpose
`afs_fetchstore.c` implements the Cache Manager's FetchData and StoreData transfer machinery between local cache chunks and the AFS fileserver. It abstracts UFS-backed disk cache and memory-cache data paths behind `storeOps` and `fetchOps`, handles 32-bit versus 64-bit fileserver RPC entry points, updates transfer statistics, and coordinates dcache/vcache state after successful stores and fetches.

## Important APIs, types, and functions
The store path centers on `struct storeOps`, `struct rxfs_storeVariables`, `rxfs_storeInit`, `afs_GenericStoreProc`, `afs_CacheStoreDCaches`, and the exported `afs_CacheStoreVCache`. UFS operations allocate a large transfer buffer and call `afs_osi_Read` plus `rx_Write`; memory-cache operations allocate Rx iovecs via `rx_WritevAlloc`, read from `afs_MemReadvBlk`, and write with `rx_Writev`. `rxfs_storeClose` ends `StoreData` or `StoreData64`, and `rxfs_storeDestroy` always closes the Rx call and frees buffers.

The fetch path centers on `struct fetchOps`, `struct rxfs_fetchVariables`, `rxfs_fetchInit`, `rxfs_fetchMore`, and exported `afs_CacheFetchProc`. UFS fetch reads from Rx into a large buffer and writes via `afs_osi_Write`; memory-cache fetch reads with `rx_Readv` and writes via `afs_MemWritevBlk`. `rxfs_fetchClose` obtains returned fetch status, callback, and volume sync before ending the Rx call.

`FillStoreStats` is shared by fetch and store despite the name; it updates `afs_stats_cmfullperf.rpc.fsXferTimes`, byte buckets, min/max byte counts, and elapsed-time aggregates.

## Control flow
Stores are initiated by `afs_CacheStoreVCache`, which scans a dcache list, groups contiguous locked chunks, computes the RPC base offset, byte count, and file length, then repeatedly obtains an AFS connection through `afs_Conn`. It starts a store with `rxfs_storeInit`, streams each dcache through `afs_CacheStoreDCaches`, invokes `afs_Analyze` for retryable failures, and falls back from `StoreData64` to `StoreData` on `RXGEN_OPCODE` when needed. On success it clears dirty dcache flags, releases dcache references, processes returned file status with `afs_ProcessFS`, and records maximum stored length for later mini-store extension decisions.

Fetches are initiated by `afs_CacheFetchProc`, which starts the RPC in `rxfs_fetchInit`, validates the server-reported length, streams data into the cache file or memory cache, advances `adc->validPos`, wakes waiters on valid data arrival, and closes the RPC to collect status/callback metadata. For foreign files, `rxfs_fetchMore` supports the AFS/DFS translator extension where the high bit announces additional length-prefixed data blocks.

## State and persistence behavior
This file mutates persistent cache chunk content through `afs_CFileOpen`, `afs_osi_Read`, `afs_osi_Write`, memory-cache block writes, and dcache flags such as `DWriting`, `DFEntryMod`, `IFDataMod`, `IFDirtyPages`, and `IFAnyPages`. Stores update server-side file contents and data versions; successful returned status is reconciled into the vcache with `afs_ProcessFS`. Fetches update `validPos` so readers can consume partial data as it arrives. Transfer statistics are retained in global in-memory stats structures.

## Dependencies and integration points
The module depends on Rx calls (`rx_NewCall`, `rx_Read`, `rx_Readv`, `rx_Write`, `rx_Writev`, `rx_EndCall`), fileserver stubs (`StartRXAFS_FetchData`, `StartRXAFS_FetchData64`, `EndRXAFS_*`), cache file APIs, memory-cache APIs, connection analysis/retry (`afs_Analyze`), dcache/vcache locks, and ICL tracing. It is part of the storeback/fetch pipeline used by higher-level cache manager code.

## Risks and edge cases
Key risks are protocol length validation, partial transfers, 64-bit fallback correctness, dcache lock/release balance, and dirty-flag consistency after failed stores. The code explicitly rejects server fetch lengths larger than requested or too large for signed 32-bit local handling. Older fileservers returning negative lengths are treated as zero. Store padding for short chunks is required when storing multi-chunk ranges. Memory-cache iovec allocation must be pinned/heap-backed for kernel Rx safety. `storeallmissing` records missing dcache anomalies that currently warn and continue.

## Test signals
Useful signals include FetchData/StoreData success and retry paths against 32-bit and 64-bit servers, memory cache versus UFS cache modes, partial fetch wakeups through `validPos`, dirty flag clearing after store, fallback on `RXGEN_OPCODE`, rejected oversized server responses, short-read/write error handling, and xstats/ICL transfer event counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_fetchstore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_icl.c -->
# sources/distributed-fs/openafs/src/afs/afs_icl.c

## Purpose
`afs_icl.c` implements the kernel in-core logging facility used by the AFS Cache Manager. It owns trace logs, trace sets, event append paths, privileged control operations, copyout to user space, log resizing, activation/deactivation, and shutdown cleanup. The default Cache Manager logs are created as `cmfx`, `cm`, and `cmlongterm`.

## Important APIs, types, and functions
Top-level globals include `afs_iclSetp`, `afs_iclLongTermSetp`, `afs_icl_allLogs`, `afs_icl_allSets`, `afs_icl_lock`, and `afs_icl_inited`. Initialization uses `afs_icl_InitLogs`, `afs_icl_CreateLog`, and `afs_icl_CreateSetWithFlags`; teardown uses `shutdown_icl`, `afs_icl_LogFree`, and `afs_icl_SetFree`.

Runtime tracing enters through `afs_icl_Event0` through `afs_icl_Event4`, which all funnel into `afs_icl_Event4` and then `afs_icl_AppendRecord`. Append helpers include `afs_icl_GetLogSpace`, `afs_icl_AppendString`, `ICL_APPENDINT32`, `ICL_APPENDLONG`, and `afs_icl_AppendOne`.

Privileged user control goes through `Afscall_icl` or Darwin's `Afscall64_icl`. Supported operations include copyout, copyout-and-clear, enumerate logs, enumerate logs by set, clear log, clear set, clear all, enumerate sets, set set status, set all set statuses, set log size, and query log/set state.

## Control flow
Trace emission first checks whether the set is active, holds the set, decodes the log mask from `lAndT`, checks per-event enable bits, and appends a record to each selected log. `afs_icl_AppendRecord` samples time, inserts a timestamp record when the low timestamp window rolls, computes record size from parameter types, evicts oldest records until enough ring-buffer space exists, and writes a compact record header, event id, thread id, timestamp, and encoded arguments.

Copyout starts from a caller-supplied cookie. `afs_icl_CopyOut` maps that cookie into the circular buffer, marks `ICL_COPYOUTF_MISSEDSOME` if the requested data has already been overwritten, copies at most the requested word count across one or two ring spans, optionally clears the log after reaching the end, and can wait for more data when requested.

Set activation with `ICL_OP_SS_ACTIVATE` reasserts log use if the set had been freed, while `ICL_OP_SS_FREE` is rejected for active sets and otherwise decrements log use counts so backing buffers can be freed.

## State and persistence behavior
All ICL data is in memory. Logs keep circular buffer fields `datap`, `logSize`, `firstUsed`, `firstFree`, `logElements`, `baseCookie`, `lastTS`, `setCount`, `refCount`, and state flags such as persistent/deleted/waiting. Sets keep their name, reference count, state flags, event enable bitmap, and up to `ICL_LOGSPERSET` log references. Log storage is allocated lazily on first real set use and can be freed while the log structure remains named. Persistent logs/sets are protected from bulk clear/status changes.

## Dependencies and integration points
The module depends on AFS locks, OSI allocation, optional kernel pinning, copyin/copyout wrappers from `afs_osi.h`, Rx lock wrappers for syscall paths, thread id/time helpers, and global AFS superuser checks. It is used by many Cache Manager files through `afs_Trace*` macros, including lock tracing, fetch/store tracing, memory cache tracing, DNLC tracing, NFS translator tracing, and cache initialization events.

## Risks and edge cases
The logging path is performance-sensitive and can run while holding the global AFS lock. Record size is capped at 255 words by the encoded high byte; oversized records are silently dropped. String arguments are copied by walking kernel memory, so callers must pass stable strings. Refcount and deleted-state handling is subtle because logs and sets can be found, held, freed, and zapped under different locks. The `ICL_COPYOUTF_WAITIO` path sleeps on the log lock address but append does not obviously wake waiters in this file, so wait semantics depend on surrounding ICL conventions.

## Test signals
Test by enabling and disabling trace sets, copying logs out with cookies across wrap boundaries, resizing logs while inactive and active, freeing and reactivating sets, validating persistent log behavior, exercising 32-bit and Darwin 64-bit syscall argument paths, and checking that lock tracing avoids recursive ICL locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_icl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_init.c -->
# sources/distributed-fs/openafs/src/afs/afs_init.c

## Purpose
`afs_init.c` initializes and tears down the main AFS Cache Manager resources. It establishes cache parameters, cache metadata files, volume and dcache/vcache pools, core locks, callback services, cell/server/user tables, sysname state, DNLC state, and platform-specific cache device handles.

## Important APIs, types, and functions
Key exported state includes `cacheDev`, `cacheInfoModTime`, `afs_cacheVfsp` or platform equivalents, `Initialafs_freeVolList`, `afs_memvolumes`, `afs_discon_lock`, `cm_initParams`, `afs_cacheinit_flag`, and `afs_resourceinit_flag`. Major functions are `afs_CacheInit`, `afs_ComputeCacheParms`, `afs_LookupInodeByPath`, `afs_InitCellInfo`, `afs_InitVolumeInfo`, `afs_InitFHeader`, `afs_InitCacheInfo`, `afs_ResourceInit`, `shutdown_cache`, `shutdown_vnodeops`, `shutdown_AFS`, plus private `shutdown_server`, `shutdown_volume`, and AIX `afs_procsize_init`.

## Control flow
`afs_CacheInit` records the Cache Manager epoch, applies dynamic-vcache settings, prevents double initialization, initializes global locks and disconnection queues, initializes DNLC, allocates the volume free list, sets cache counts, initializes vcache and dcache layers, optionally saves Linux credentials for future cache-file access, records VM mapping limits, optionally probes AIX proc size, and stores a `cm_initParams` snapshot for pioctl queries.

`afs_InitCacheInfo` is UFS-cache specific. It locates the cache info file, discovers filesystem fragment size, captures device/vnode identity, opens the cache metadata file, validates or rewrites the `afs_fheader`, truncates invalid contents, and leaves the file open in `afs_cacheInodep` for later slot operations. `afs_InitVolumeInfo` locates and truncates the volume metadata file; BSD variants hold the vnode to avoid lock recursion through vnode reclamation.

`afs_ResourceInit` initializes global locks, cell and callback queues, file-server callback tables, sysname state, Rx server security, and Rx services for callbacks and stats. Shutdown reverses much of this state, freeing volumes, users, tokens, exporters, servers, server addresses, Rx services/events, sysnames, and cache metadata.

## State and persistence behavior
The file configures both persistent cache metadata and in-memory resource pools. Persistent state includes cache info file headers, volume info file contents, cache inode/device identity, and filesystem fragment sizing used in cache accounting. In-memory state includes volume arrays, user/server hash tables, dcache/vcache pools, locks, disconnection queues, sysname data, PAG epoch/counter reset on cache shutdown, and saved Linux cache credentials.

## Dependencies and integration points
Dependencies include OS lookup/statfs/vnode APIs, cache file operations, dcache/vcache initialization, DNLC, cell/server/user modules, callback queue, Rx/RxStats services, sysname initialization, memory cache flags, and platform-specific vnode/device helpers. It is invoked by afsd/kernel module startup and shutdown paths and provides the foundation expected by fetch/store, pioctl, NFS translator, and callback code.

## Risks and edge cases
Initialization order is explicitly critical. Calling cache init twice is intentionally ignored after the first pass, but partially failed dcache initialization leaves earlier allocations in place. UFS cache metadata validation must match chunk sizes and version or the cache file is rewritten. Platform branches hold vnodes or saved credentials to avoid reclaim/security failures. Shutdown assumes write-through of dcache slots succeeds and has comments noting memcache volume allocations may not all be recoverable.

## Test signals
Signals include successful cold start with UFS and memory cache, invalid cache info header rewrite, correct `cm_initParams`, Linux security-module cache-file access using saved credentials, BSD vnode hold/release on shutdown, Rx callback/stat service startup, and clean teardown without leaked users, volumes, server addresses, or DNLC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_lock.c -->
# sources/distributed-fs/openafs/src/afs/afs_lock.c

## Purpose
`afs_lock.c` provides the generic AFS lock implementation used by Cache Manager structures. It supports read, write, shared, and boosted write lock acquisition, lock release policies biased toward readers or writers, wait-time accounting, and optional ICL tracing of lock operations.

## Important APIs, types, and functions
`Lock_Init` initializes `struct afs_lock` counters and ownership/debug fields. `Afs_Lock_Obtain` implements acquisition for `READ_LOCK`, `WRITE_LOCK`, `SHARED_LOCK`, and `BOOSTED_LOCK`. `Afs_Lock_ReleaseR` and `Afs_Lock_ReleaseW` choose which waiter class to wake. `Afs_Lock_Trace` emits lock trace records when `afs_trclock` is enabled while avoiding recursive tracing of ICL locks.

## Control flow
Acquisition records a start timestamp, increments `num_waiting`, sets a wait-state bit, sleeps on either `readers_reading` or `excl_locked`, and loops until the requested condition is satisfied. Read locks wait only for a write lock. Write locks wait for both exclusive state and readers. Shared locks wait for no exclusive state and then set `excl_locked` to `SHARED_LOCK`. Boosted locks wait for readers to drain and then become write locks. After acquisition, elapsed wait time is accumulated into the lock object and optionally traced.

Release paths inspect `wait_states`, clear the selected class, and wake the corresponding sleep address. `Afs_Lock_ReleaseR` prefers queued readers; `Afs_Lock_ReleaseW` prefers queued exclusive locks.

## State and persistence behavior
The lock state is entirely in memory: counts of readers, exclusive lock kind, waiter bitmask, number waiting, last reader/writer pid fields, source indicator, and cumulative `time_waiting`. No state is persisted beyond runtime diagnostics.

## Dependencies and integration points
The implementation depends on OSI sleep/wakeup primitives, time helpers, AFS stats macros, and ICL tracing globals. Lock macros elsewhere in the tree wrap these functions, so changes affect cache, vcache, dcache, ICL, DNLC, NFS translator, and PAG code.

## Risks and edge cases
Correctness depends on callers holding the expected global synchronization around lock operations. Wakeup policy can affect fairness. `BOOSTED_LOCK` skips waiting on existing exclusive state and only waits for readers, so it must only be used in contexts matching that convention. Lock tracing must avoid tracing ICL internal locks or it can recurse.

## Test signals
Exercise concurrent read/write/shared acquisition, boosted lock transitions, reader- and writer-preferred releases, cumulative wait-time accounting, and lock tracing with non-ICL locks while ICL logging is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_mariner.c -->
# sources/distributed-fs/openafs/src/afs/afs_mariner.c

## Purpose
`afs_mariner.c` implements the legacy Mariner fetch/store monitoring facility. It keeps a small ring of vcache-to-name associations and sends one-line UDP status messages to a configured Mariner host.

## Important APIs, types, and functions
Exported state includes `afs_server`, `afs_mariner`, and `afs_marinerHost`. `afs_AddMarinerName` records a name and vcache pointer in a 10-entry ring. `afs_GetMariner` resolves a vcache back to the last recorded short name. `afs_MarinerLogFetch` logs a fetch message. `afs_MarinerLog` formats and sends the UDP packet. `shutdown_mariner` clears the ring and disables Mariner state.

## Control flow
Callers associate file names with vcaches through `afs_AddMarinerName`. Fetch logging calls `afs_MarinerLogFetch`, which delegates to `afs_MarinerLog` with a fixed `fetch$Fetching` prefix. `afs_MarinerLog` builds a sockaddr for port 2106 on `afs_marinerHost`, allocates a small buffer, concatenates the message, optional file name, and newline with bounds checks, releases the AFS global lock, sends through `rxi_NetSend` on `afs_server->socket`, reacquires the lock, and frees the buffer.

## State and persistence behavior
The only state is in memory: ten names, ten vcache pointers, a ring pointer, and the current Mariner host/enabled flag. It does not persist messages and intentionally ignores send failures.

## Dependencies and integration points
It depends on Rx's kernel socket send path, OSI small-space allocation, global lock macros, and vcache pointers supplied by lookup/fetch code. It is initialized and shut down as part of vnode/cache manager teardown paths and relies on `afs_server` having a valid socket.

## Risks and edge cases
Names are truncated to 19 bytes plus terminator. Ring entries are not reference-counted, so stale vcache pointers are possible until overwritten; callers only use them for equality lookup and logging text. UDP send errors are ignored by design. Buffer concatenation guards prevent overflow but silently drop overlong messages.

## Test signals
Test enabling Mariner host logging, name truncation, ring wraparound, fetch log packet formatting, operation with null vcache, and shutdown clearing vcache slots and flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_mariner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_memcache.c -->
# sources/distributed-fs/openafs/src/afs/afs_memcache.c

## Purpose
`afs_memcache.c` implements the in-memory cache-file backend used when the Cache Manager runs with memory cache instead of UFS cache files. It simulates open/read/write/truncate operations over an array of `struct memCacheEntry` blocks with per-entry locks.

## Important APIs, types, and functions
Core globals are `memCache`, `memCacheBlkSize`, and `memMaxBlkNumber`. `afs_InitMemCache` allocates entries and their initial buffers, initializes per-entry locks, and creates cache file slots. `afs_MemCacheOpen` maps a memory inode number to an entry. Read APIs include `afs_MemReadBlk`, `afs_MemReadvBlk`, and `afs_MemReadUIO`. Write APIs include `afs_MemWriteBlk`, `afs_MemWritevBlk`, and `afs_MemWriteUIO`. `_afs_MemExtendEntry` grows buffers. `afs_MemCacheTruncate` shrinks logical size and can return oversized zero-length buffers to the default block size. `shutdown_memcache` frees data and entries.

## Control flow
Initialization allocates a table of entries and one data buffer per entry, then calls `afs_InitCacheFile` for each logical cache file. Reads take a read lock, clamp requested bytes to available logical size, copy to the destination or iovecs while dropping the AFS global lock around `memcpy`, and return the byte count. Writes take a write lock, grow the data buffer if needed, zero-fill holes between old size and new offset, copy user/iovec data, and extend the logical size to the final offset. UIO paths perform equivalent operations through `AFS_UIOMOVE`.

## State and persistence behavior
Memory cache content is volatile. Each entry tracks logical `size`, allocated `dataSize`, data pointer, and lock. On shutdown, all entry buffers and the entry table are freed only if `cacheDiskType == AFS_FCACHE_TYPE_MEM`.

## Dependencies and integration points
The module depends on OSI allocation/free, AFS locking macros, UIO wrappers from `afs_osi.h`, ICL tracing, cache initialization (`afs_InitCacheFile`), and fetch/store memory-cache paths in `afs_fetchstore.c`.

## Risks and edge cases
`afs_MemCacheOpen` panics on invalid memory block numbers; the range check uses `> memMaxBlkNumber`, so the exact upper boundary deserves attention. Large directory support allows arbitrary entry growth, so memory pressure is a real failure mode. Allocation failure paths must preserve old buffers. Hole zeroing and offset arithmetic must avoid negative or overflowed lengths. Shutdown reinitializes locks just before freeing entries, which is harmless but unusual.

## Test signals
Exercise memory-cache initialization failure cleanup, read/write/readv/writev behavior, sparse writes with zero-filled gaps, UIO read/write offset and resid updates, truncation of oversized zero-length entries, fetch/store through memory cache, and shutdown in both memory and non-memory cache modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_memcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_nfsclnt.c -->
# sources/distributed-fs/openafs/src/afs/afs_nfsclnt.c

## Purpose
`afs_nfsclnt.c` manages AFS identities for the NFS translator/exporter path. It maps remote NFS clients by host and uid/PAG into `nfsclientpag` exporter records, handles request credential transformation, optionally fetches remote credentials and sysnames through PAG callback RPCs, and garbage-collects translator entries.

## Important APIs, types, and functions
The file defines `nfs_exportops`, `afs_nfspags`, `afs_xnfspag`, `afs_nfsexported`, and `init_nfsexporter`. Key functions are `afs_nfsclient_init`, `afs_nfsclient_reqhandler`, `afs_GetNfsClientPag`, `afs_FindNfsClientPag`, `afs_PutNfsClientPag`, `afs_nfsclient_hold`, `afs_nfsclient_getcreds`, `afs_nfsclient_sysname`, `afs_nfsclient_GC`, `afs_nfsclient_checkhost`, `afs_nfsclient_gethost`, `afs_nfsclient_stats`, and AIX IA UTH hooks when enabled.

## Control flow
`afs_nfsclient_init` registers exporter operations with the kernel exporter layer once. Each NFS request enters `afs_nfsclient_reqhandler`, which verifies the exporter is enabled, extracts uid and any PAG from credentials, tags the credential as an NFS translator call, verifies claimed PAGs against known `unixuser` records, finds or creates a host/uid `nfsclientpag`, calls `setpag` as needed to install the local translator PAG, associates the exporter with the corresponding `unixuser`, optionally refreshes tokens through `afs_nfsclient_getcreds`, and returns the PAG and exporter pointer to the caller.

`afs_nfsclient_getcreds` creates an Rx connection to the remote host's PAG callback service, fetches sysnames if absent, fetches credential blobs, maps cell names to local cells, creates or updates `unixuser` token sets for each cell, marks tokens primary/valid, and resets user connections. `afs_nfsclient_sysname` sets or reports sysname lists and can apply changes to all PAGs for a host. `afs_nfsclient_GC` frees entries with no references after timeout, matching a specific PAG, or all entries on shutdown.

## State and persistence behavior
State is in memory: hash buckets of `nfsclientpag` structures keyed by host, uid, and PAG; reference counts; last-call timestamps; sysname strings; exporter stats; and links from `unixuser->exporter` back to translator entries. Tokens installed into `unixuser` records are runtime credentials and are cleared/freed through normal token lifecycle.

## Dependencies and integration points
This module is wired into Solaris/AIX NFS dispatchers, the exporter abstraction, PAG/group credential routines, `unixuser` token management, Rx, PAGCB RPCs, cell lookup, and pioctl `exportafs` state. It is excluded when `AFS_NONFSTRANS` is defined except for selected AIX IA UTH cases.

## Risks and edge cases
Security depends on rejecting stale or forged remote PAGs, treating translator reboot as invalidating old remote PAGs, and correctly handling `EXP_CLIPAGS` remote-PAG mode. Reference counts must match exporter/user holds or GC can free live entries. `afs_nfsclient_getcreds` handles secret ticket material and must zero or free rejected tokens. The AIX IA UTH block appears syntactically suspect in this snapshot, so platform build coverage matters.

## Test signals
Test NFS export disabled rejection, first request creating a translator PAG, subsequent request reusing it, invalid remote PAG fallback, remote-PAG mode, callback credential import for multiple cells, sysname propagation, GC by timeout/PAG/shutdown, and exporter reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_nfsclnt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_nfsdisp.c -->
# sources/distributed-fs/openafs/src/afs/afs_nfsdisp.c

## Purpose
`afs_nfsdisp.c` is the Solaris NFS translator dispatch interposer. It hooks NFSv2, NFSv3, and ACL dispatch tables, detects AFS file handles, invokes the AFS NFS-client credential handler before delegating to the original NFS implementation, and rewrites selected returned file handles to compact AFS `SmallFid` handles for root-only export mode.

## Important APIs, types, and functions
The file is compiled for `AFS_SUN5_ENV` when NFS translation is enabled. It defines local dispatch table descriptors, `afs_rfs_disp_tbl`, `afs_acl_disp_tbl`, `afs_rfs3_disp_tbl`, and `afs_acl3_disp_tbl`. Entry points `afs_xlatorinit_v2` and `afs_xlatorinit_v3` replace kernel dispatch procedures with AFS wrappers while retaining original procedure pointers.

Detection helpers are `is_afs_fh`, `is_afs_fh3`, `nfs2_to_afs_call`, `acl2_to_afs_call`, `nfs3_to_afs_call`, and `acl3_to_afs_call`. Credential dispatchers are `afs_nfs2_dispatcher` and `afs_nfs3_dispatcher`. Response helpers are `afs_nfs2_noaccess`, `afs_nfs3_noaccess`, `afs_nfs3_notsupp`, `afs_nfs2_smallfidder`, and `afs_nfs3_smallfidder`.

## Control flow
Initialization walks the kernel NFS and ACL dispatch tables, stores each original procedure in the AFS table, and installs AFS wrapper functions. Each wrapper temporarily sets `curthread->t_cred` to the request credential, calls the relevant dispatcher, denies access if the dispatcher reports rejection, otherwise calls the original kernel NFS/ACL procedure, then restores the saved thread credential.

The dispatchers identify the remote IPv4 client from the RPC transport, parse the operation-specific arguments to find one or two file handles, and check for the AFS VFS magic. For AFS calls, they trace the incoming `SmallFid`, capture the anonymous uid from exportinfo once, call `afs_nfsclient_reqhandler`, release the returned exporter, and use `call` return codes to indicate no AFS handling, normal AFS handling, or access denial.

For lookup/create/mkdir/symlink/mknod responses in `afs_NFSRootOnly` mode, smallfidder routines translate transient vnode-style handles into stable `SmallFid` data containing volume, cell index, unique, and vnode, then release the vnode reference.

## State and persistence behavior
The module mutates kernel dispatch tables in memory and records one-time initialization flags. It does not persist data. It temporarily mutates the current thread credential during wrapper execution and relies on `afs_nfsclient_reqhandler` for PAG/exporter state.

## Dependencies and integration points
Dependencies include Solaris NFS/NFS ACL kernel headers, exporter state, `afs_nfsclient_reqhandler`, vcache/vnode conversion, cell lookup, `SmallFid` layout, ICL tracing, and `afs_NFSRootOnly` policy. It directly complements `afs_nfsclnt.c` and `afs_osi_vget.c`.

## Risks and edge cases
Hooking kernel dispatch tables is ABI-sensitive. Every operation wrapper must preserve credentials and call the correct original procedure. File-handle parsing is operation-specific; missing a second-handle operation can bypass translator setup. `READDIRPLUS` is explicitly not supported for AFS calls under NFSv3. SmallFid conversion assumes returned handles are vnode-pointer handles marked with `AFS_XLATOR_MAGIC` and releases vnode refs based on `vrefCount`.

## Test signals
Test NFSv2/v3 operations with AFS and non-AFS handles, ACL get/set paths, access-denied behavior when export is disabled, thread credential restoration, root-only smallfid conversion on successful object-creating lookups, and `READDIRPLUS` returning not-supported for AFS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_nfsdisp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi.c -->
# sources/distributed-fs/openafs/src/afs/afs_osi.c

## Purpose
`afs_osi.c` provides common operating-system-interface initialization and process/credential helpers for the Cache Manager. It sets up global locks, initializes the long-lived AFS kernel credential, masks or unmasks signals for kernel threads, marks AFS threads as system/invisible where supported, and cleans OSI sleep resources on shutdown.

## Important APIs, types, and functions
Globals include `afs_ftf`, `afs_osi_credp`, and platform-specific global-lock variables for Solaris, SGI, Darwin, BSD, FreeBSD, and AIX. Main functions are `osi_Init`, `afs_osi_MaskSignals`, `afs_osi_UnmaskRxkSignals`, `afs_osi_MaskUserLoop`, `afs_osi_RxkRegister`, `afs_osi_Invisible`, `afs_osi_Visible`, `shutdown_osi`, `shutdown_osisleep`, and `afs_osi_suser`.

## Control flow
`osi_Init` is guarded by a static one-time flag. It initializes the global AFS lock, hcrypto kernel mutex, and if needed creates or references `afs_osi_credp` according to platform conventions: BSD duplicates current credentials, Solaris uses `kcred`, Darwin allocates and initializes a credential object, Linux initializes group info for the static credential, and other platforms zero and hold `afs_osi_cred`. It also initializes error-code translation and SGI lock-owner data.

Signal helpers defer to Linux-specific masks or Darwin invisible/full-mask behavior. Visibility helpers set or clear system process flags where the platform exposes them. `shutdown_osi` releases Darwin context state, tears down OSI sleep hashes on non-Linux/non-Darwin platforms, and reinitializes `afs_ftf` on cold shutdown.

## State and persistence behavior
All state is in memory and tied to kernel module lifetime: global lock primitives, static credentials, Darwin context references, event sleep hash entries, and process flags. There is no on-disk persistence.

## Dependencies and integration points
The file depends on `osi_machdep` platform code, OS credential APIs, sleep/event hash definitions, AFS global lock initialization, hcrypto initialization, and error mapping. Many other AFS files assume `afs_osi_credp` exists for anonymous/internal requests and that OSI sleep/wakeup resources are initialized.

## Risks and edge cases
Credential lifetime differs significantly by platform. Incorrect reference ownership can leak or free kernel credentials too early. Marking processes invisible/system is platform-specific and may be a no-op on newer kernels. `shutdown_osisleep` warns on nonzero event refcounts, signaling potential sleeping waiters during shutdown.

## Test signals
Verify one-time init, platform credential setup, Linux signal masking, Darwin context release, system flag toggling where supported, sleep hash cleanup, and superuser checks through `afs_osi_suser`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi.h -->
# sources/distributed-fs/openafs/src/afs/afs_osi.h

## Purpose
`afs_osi.h` is the common OSI contract header for AFS kernel code. It defines portable types, file/device/socket abstractions, vnode/vcache hooks, global lock and copy wrappers, UIO access macros, PAG group layout constants, and default vnode/refcount behavior that platform-specific `osi_machdep.h` can override.

## Important APIs, types, and macros
Important types include `struct osi_socket`, `struct osi_stat`, `struct osi_file`, `struct osi_dev`, `struct afs_osi_WaitHandle`, and fixed-size `osi_timeval32_t`. File macros include `osi_SetFileProc`, `osi_SetFileRock`, `osi_GetFileProc`, and `osi_GetFileRock`. Vnode hooks include `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_PostPopulateVCache`, `osi_AttachVnode`, `osi_ResetVCache`, and `osi_vnhold`.

The header defines `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `RX_AFS_GLOCK`, `AFS_RELE`, `AFS_FAST_RELE`, `AFS_COPYIN`, `AFS_COPYINSTR`, `AFS_COPYOUT`, `AFS_UIOMOVE`, `AFS_UIO_OFFSET`, `AFS_UIO_RESID`, `AFS_UIO_SETOFFSET`, `AFS_UIO_SETRESID`, and default vnode/vfs argument conversion macros.

## Control flow and contracts
The most important behavioral contract is that user/kernel copy and UIO moves may drop the AFS global lock before operations that can fault or block, then reacquire it. This is conditional on `AFS_GLOBAL_SUNLOCK`. UIO signatures are normalized across Darwin, BSD, and older Unix variants. Vnode reference macros wrap platform `VN_RELE` and deliberately drop the global lock for non-UKERNEL builds.

Platform-specific behavior is layered by defining defaults first, then including `osi_machdep.h`, allowing the platform header to redefine vnode types, global lock behavior, UIO details, and credential access.

## State and persistence behavior
The header itself stores no state, but its structures define runtime state shapes used throughout the Cache Manager. `struct osi_file` begins with `size` and stores platform file/vnode handles, offset, optional write callback, rock pointer, and UKERNEL fd. `struct osi_dev` stores platform-specific device or mount identity.

## Dependencies and integration points
Every source in this subset includes or indirectly depends on this header. It integrates kernel headers, Linux dummy inode-info shields, Coda/XFS include conflict avoidance, vnode operations, credential globals, PAG group count, and optional Linux delayed remove/unlink behavior.

## Risks and edge cases
Because this header normalizes many kernel ABIs, macro mistakes have broad blast radius. Copy/Uiomove wrappers must not leave the global lock in the wrong state. Darwin user-address casting is version-gated to avoid 32/64-bit userspace issues. `AFS_FAST_RELE` intentionally bypasses full inactive behavior on some platforms and must only be used under its assumptions.

## Test signals
Build coverage across Linux, Solaris, Darwin, BSD, AIX, and UKERNEL is the primary signal. Runtime signals include copyin/copyout while holding/not holding the global lock, UIO moves on Darwin and BSD variants, vnode release behavior, `osi_vnhold` failure handling, and PAG group count behavior under one-group and two-group builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_alloc.c -->
# sources/distributed-fs/openafs/src/afs/afs_osi_alloc.c

## Purpose
`afs_osi_alloc.c` implements common OSI memory allocation helpers and the reusable small/large network buffer pools used by Rx and cache-manager code. It also updates memory-use statistics and performs pool cleanup at shutdown.

## Important APIs, types, and functions
Important globals are `osi_fsplock`, `osi_flplock`, `freePacketList`, `freeSmallList`, and the zero-length allocation sentinel `memZero`. General allocation APIs are `afs_osi_Alloc`, `afs_osi_Free`, and `afs_osi_FreeStr`. Pool APIs are `osi_AllocLargeSpace`, `osi_FreeLargeSpace`, `osi_AllocSmallSpace`, `osi_FreeSmallSpace`, and `shutdown_osinet`.

## Control flow
`afs_osi_Alloc` returns a non-null sentinel for zero-byte allocations, updates outstanding allocation counters, and calls Linux or generic kernel allocation. `afs_osi_Free` ignores null and the sentinel, updates counters, and frees through platform-specific APIs.

Large and small pool allocation first validate size against `AFS_LRALLOCSIZ` or `AFS_SMALLOCSIZ`. If no free-list item exists, they allocate a new fixed-size block and optionally pin it. Otherwise they pop a block under the corresponding lock. Freeing pushes a block back onto the free list under the lock and decrements active counters. `shutdown_osinet` drains both free lists, unpins where needed, reinitializes locks on cold shutdown, and warns if active block counts are nonzero.

## State and persistence behavior
All allocation state is runtime-only. The pool keeps only free fixed-size blocks; active blocks are tracked by counters but not by a list. Allocation statistics contribute to `afs_stats_cmperf`.

## Dependencies and integration points
The module depends on OSI allocation macros, Linux allocation wrappers, optional kernel pinning, AFS global-lock assertions, AFS locks, and stats. It is used heavily by ICL, Rx send/receive paths, fetch/store buffers, pioctl marshalling, UIO copies, and request allocation.

## Risks and edge cases
Pool free/alloc functions require the global lock on builds where `AFS_ASSERT_GLOCK` is meaningful. Size violations panic instead of returning errors. Active block leaks are only warned during shutdown. Zero-size allocation sentinel requires callers to free with the same size discipline but prevents false null allocation failures.

## Test signals
Test zero-byte allocation/free, large/small pool reuse, size-limit panics in debug builds, active counter accounting, shutdown warnings for leaked active blocks, pin/unpin coverage, and behavior when `AFS_PRIVATE_OSI_ALLOCSPACES` supplies private implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_pag.c -->
# sources/distributed-fs/openafs/src/afs/afs_osi_pag.c

## Purpose
`afs_osi_pag.c` implements Process Authentication Group generation, group encoding/decoding, credential installation, and request initialization. PAGs provide an authentication-token handle that is more specific than Unix uid, reducing token sharing between unrelated sessions with the same uid.

## Important APIs, types, and functions
Global PAG state is `pag_epoch`, `pagCounter`, `afs_pag_sleepcnt`, and `afs_pag_timewarn`. PAG generation APIs include `afs_genpag`, internal `genpagval`, `getpag`, `afs_pag_sleep`, and `afs_pag_wait`. Credential APIs include platform-specific `afs_setpag`, UKERNEL `afs_setpag_val`, `AddPag`, `PagInCred`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, and `afs_IsPagId`. Request helpers are `afs_InitReq`, `afs_CreateReq`, and `afs_DestroyReq`.

## Control flow
Kernel PAG values normally encode an ASCII `A` in the high byte and a 24-bit counter, with Linux adding `pag_epoch` so PAGs remain unique after module reloads for roughly the wrap window. `afs_pag_wait` throttles non-superuser PAG creation if elapsed time since epoch is less than the counter, enforcing an average one PAG per second to reduce wraparound risk. `afs_setpag` generates a PAG and delegates to platform `AddPag`/`setpag` logic to clone and update credentials.

PAGs are represented in Unix group lists by one or two special groups near `0x3f00`. `afs_get_groups_from_pag` encodes a PAG into group ids, and `afs_get_pag_from_groups` reverses it, validating kernel PAG ids outside UKERNEL. `PagInCred` extracts the PAG from Linux keyrings, AIX kernel credential PAGs, or encoded groups depending on platform.

`afs_InitReq` initializes a `vrequest`, aborts during shutdown, lets Linux NFS translator code override request setup, sets `av->uid` to the PAG if present, otherwise uses a real uid or nobody fallback. `afs_CreateReq` allocates a small-space request and `afs_DestroyReq` frees it.

## State and persistence behavior
PAG state is runtime-only and resets with cache shutdown or module reload. Credentials carry encoded PAG groups or keyring/AIX PAG metadata. `vrequest` objects are transient per operation.

## Dependencies and integration points
The file depends on platform credential cloning/group APIs, Linux keyring helpers, NFS translator request handling, user/token tables via `vrequest->uid`, OSI wait/sleep, and small-space allocation. It is central to pioctl, NFS translator, token lookup, and request authorization.

## Risks and edge cases
PAG wraparound is security-sensitive; throttling protects non-superusers but clock rollback disables throttling with a warning. Group-list layouts differ by platform and one-group builds. Some platforms cannot infer PAGs on newer Darwin variants. `PagInCred` returns `NOPAG` for the global AFS credential and null credentials. Request allocation requires a non-null credential and can fail with `EINVAL` or `ENOMEM`.

## Test signals
Test PAG creation throttling, clock rollback behavior, group encode/decode round trips, Linux keyring fallback, request uid selection with and without PAGs, shutdown rejection, UKERNEL explicit PAG set/get, and NFS translator request initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_pag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_uio.c -->
# sources/distributed-fs/openafs/src/afs/afs_osi_uio.c

## Purpose
`afs_osi_uio.c` provides portable helper routines for copying, trimming, partially copying, freeing, and advancing `struct uio` objects used by AFS read/write paths.

## Important APIs, types, and functions
For non-Darwin80 builds, `afsio_copy` copies a uio and its iovec array into caller-provided storage, `afsio_trim` clamps a uio to a target byte size, `afsio_partialcopy` allocates a small-space block containing a copied uio and up to `AFS_MAXIOVCNT` iovecs, and `afsio_free` frees that allocation. `afsio_skip` advances an existing uio by a byte count and is available for all builds, using `uio_update` on Darwin80.

## Control flow
`afsio_copy` rejects iovec counts above `AFS_MAXIOVCNT`, shallow-copies the uio structure, redirects the output uio to the output iovec array, and copies each input iovec. `afsio_trim` sets resid to the target size and walks iovecs until the target is covered, truncating the final iovec or shortening the iovec count. `afsio_partialcopy` allocates a combined uio/iovec buffer, zeroes it, copies the source uio, trims it, and returns the new uio. `afsio_skip` repeatedly advances the current iovec base/length, resid, and offset until the skip count is consumed or the uio is empty.

## State and persistence behavior
There is no persistent state. The helpers mutate supplied uio structures or allocate transient small-space copies.

## Dependencies and integration points
The file depends on OSI small-space allocation, `AFS_MAXIOVCNT`, platform uio field aliases from headers, and AFS stats. It is used by cache read/write paths that need to split or advance user IO without losing the original vector.

## Risks and edge cases
Multiple-iovec behavior is noted as not thoroughly tested in comments. `afsio_partialcopy` assumes small-space blocks are large enough for one uio plus `AFS_MAXIOVCNT` iovecs. `afsio_skip` silently stops when resid reaches zero and skips zero-length iovecs by advancing the vector pointer.

## Test signals
Test copying at max and over-max iovec counts, trimming exact/partial/zero lengths, partialcopy allocation layout, skip across empty and multiple iovecs, offset/resid consistency, and Darwin80 `uio_update` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_uio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_vget.c -->
# sources/distributed-fs/openafs/src/afs/afs_osi_vget.c

## Purpose
`afs_osi_vget.c` implements the common, system-independent part of VFS `vget` for platforms other than Linux and Darwin80. It maps compact AFS NFS translator file handles back to vcaches.

## Important APIs, types, and functions
The sole exported function is `afs_osi_vget(struct vcache **avcpp, struct fid *afidp, struct vrequest *areqp)`. It uses `struct SmallFid`, `struct VenusFid`, cell lookup by index, `afs_NFSFindVCache`, `afs_CreateReq`, `afs_GetVCache`, and `afs_DestroyReq`.

## Control flow
The function copies `SmallFid` bytes out of the VFS fid, extracts the cell index from the high byte of `CellAndUnique`, resolves that index to an AFS cell, builds a full `VenusFid`, and first searches for an existing vcache using NFS wildcard semantics. If more than one vcache matches it returns `ENOENT`; if none matches it creates an anonymous/internal request with `afs_osi_credp`, calls `afs_GetVCache` to fetch or construct the vcache, and destroys the request. A null final vcache is reported as `ENOENT`.

## State and persistence behavior
No state is persisted. The function may create or reference a vcache, which affects normal vcache cache state and reference counts.

## Dependencies and integration points
It complements `afs_nfsdisp.c` smallfid generation and NFS translator exports. It depends on cell index mappings, vcache lookup/fetch, request allocation from PAG code, and platform VFS fid layout.

## Risks and edge cases
The compact fid stores only a cell index and low 24 bits of unique plus a 16-bit vnode field, so ambiguity is possible and is explicitly rejected if wildcard lookup finds multiple matches. Missing cell-index mappings return `ENOENT`. Anonymous request allocation can fail during shutdown or memory pressure.

## Test signals
Test vget for cached vcaches, uncached but fetchable vcaches, missing cells, ambiguous wildcard matches, invalid fids, and interaction with NFS root-only smallfid handles generated by Solaris dispatch code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_vget.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/afs_osi_vm.c

## Purpose
`afs_osi_vm.c` provides common virtual-memory/cache coordination logic around vcaches. It detects active mapped/open files, flushes stale VM pages after remote changes, flushes text mappings on older text-cache platforms, and releases VM pages during invalidation.

## Important APIs, types, and functions
Main functions are `osi_Active`, `osi_FlushPages`, optional `osi_FlushText_really`, and `osi_ReleaseVM`. Important vcache fields are `opens`, `f.states`, `mapDV`, `flushDV`, `execsOrWriters`, `f.m.DataVersion`, and `f.m.Length`.

## Control flow
`osi_Active` checks open counts and mapped/text flags using platform-specific mechanisms. `osi_FlushPages` ignores directories, performs a read-locked fast check to see whether the current data version has already been purged or whether local writers have dirty pages, then repeats under write lock. If flushing is needed, it records the original data version, traces the event, drops the vcache lock and global lock, calls platform `osi_VM_FlushPages`, reacquires locks, and sets `mapDV` to the original version so later calls know that version was purged.

`osi_FlushText_really` handles text-cache invalidation under `AFS_TEXT_ENV`, with platform-specific comments around avoiding Sun/HP-UX text object deadlocks. `osi_ReleaseVM` truncates VM state to zero; Solaris keeps the vcache lock held while other platforms release and reacquire it around `osi_VM_Truncate`.

## State and persistence behavior
No state is persisted. Runtime state changes include `mapDV`, `flushDV`, VM/page cache contents, and possible text-cache purge state.

## Dependencies and integration points
The file depends on platform VM hooks (`osi_VM_FlushPages`, `osi_VM_Truncate`, `afs_DirtyPages`), vnode type macros, global lock macros, vcache locks, and ICL tracing. It is used when callbacks, stores, invalidations, or remote updates require page-cache consistency.

## Risks and edge cases
The main risk is flushing pages that contain local dirty data, losing writes. The double-check under read then write lock is designed to avoid that. Another risk is skipping empty-file flushes; the code deliberately still flushes because some kernels cache zero pages for empty files. Lock drop/reacquire behavior differs by platform and can race if platform VM truncation requires locks not modeled here.

## Test signals
Test remote invalidation of mapped files, local writer dirty-page protection, directory no-op behavior, repeated flushes against `mapDV`, empty-file zero-page flushes, Solaris versus non-Solaris `osi_ReleaseVM` locking, and text flush behavior where `AFS_TEXT_ENV` still builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osi_vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osidnlc.c -->
# sources/distributed-fs/openafs/src/afs/afs_osidnlc.c

## Purpose
`afs_osidnlc.c` implements the OSI directory name lookup cache, an in-memory name-to-vcache cache for frequently accessed directory entries. It avoids repeated disk-cache directory scans for short names.

## Important APIs, types, and functions
Global state includes `afs_xdnlc`, `dnlcstats`, `ncfreelist`, fixed `nameCache[NCSIZE]`, `nameHash[NHSIZE]`, `afs_usednlc`, and debug trace arrays. Public functions are `osi_dnlc_enter`, `osi_dnlc_lookup`, `osi_dnlc_remove`, `osi_dnlc_purgedp`, `osi_dnlc_purgevp`, `osi_dnlc_purge`, `osi_dnlc_purgevol`, `osi_dnlc_init`, and `osi_dnlc_shutdown`. Internal helpers are `GetMeAnEntry`, `InsertEntry`, and `RemoveEntry`.

## Control flow
`osi_dnlc_init` initializes the lock, stats, hash table, fixed cache array, and freelist. `osi_dnlc_enter` hashes a short name, rejects names too long for `AFSNCNAMESIZE`, verifies the directory vcache is statted and still at the directory data version used for lookup, de-duplicates an existing entry if present, otherwise obtains an entry from the freelist or scavenges the oldest entry from a hash bucket, fills `dirp`, `vp`, key, and name, and inserts it at the bucket head.

`osi_dnlc_lookup` hashes the name, searches the bucket under DNLC and vcache read locks, rejects initializing/dead vcaches, obtains a vnode/vcache reference with Darwin or generic APIs, removes entries that fail to ref, and returns the held vcache. Remove and purge functions null matching entries first and opportunistically unlink them under a nonblocking write lock, falling back to eventual scavenging when busy.

## State and persistence behavior
The cache is fixed-size and volatile. Each `struct nc` stores key, circular hash links, directory vcache, target vcache, and short name. Stats count enters, lookups, misses, removes, purge types, cycles, and lookup races.

## Dependencies and integration points
It depends on vcache locks (`afs_xvcache`), vcache state flags, vnode reference APIs, Darwin name cache purge calls, AFS locks, and `afs_osidnlc.h`. Lookup, directory update, callback invalidation, and volume purge paths use it to cache or invalidate name mappings.

## Risks and edge cases
Long names are not cached. Hash buckets are circular lists; cycle detection warns, increments stats, and purges the whole cache. Nonblocking removal can leave invalidated entries in buckets with null pointers until scavenged. Entry validity depends on matching the directory data version at insertion, so stale directory data should not be cached. Linux disables this cache by default in this file.

## Test signals
Test enter/lookup hit/miss behavior, long-name rejection, duplicate update, stale directory version rejection, ref-acquisition failure removal, purgedp/purgevp/purgevol invalidation, full-cache scavenging, cycle recovery, and Darwin cache-purge integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osidnlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osidnlc.h -->
# sources/distributed-fs/openafs/src/afs/afs_osidnlc.h

## Purpose
`afs_osidnlc.h` defines the data structures and constants for the OSI directory name lookup cache implemented by `afs_osidnlc.c`.

## Important APIs, types, and functions
The header defines `AFSNCNAMESIZE` as 36 bytes, `struct nc`, and `dnlcstats_t`. `struct nc` contains a hash key, next/previous circular-list pointers, directory and target vcache pointers, and the cached name bytes. `dnlcstats_t` contains counters for enters, lookups, misses, removes, directory purges, vnode purges, volume purges, full purges, cycles, and lookup races.

## Control flow
There is no executable control flow in this header, but the fixed name size and structure layout directly shape DNLC behavior: only names shorter than `AFSNCNAMESIZE` are cached, hash membership is tracked with `prev != NULL`, and entries can be moved between circular hash buckets and the freelist.

## State and persistence behavior
The structures define volatile in-memory cache entries and counters. No data is persisted.

## Dependencies and integration points
The header assumes `struct vcache` is visible or forward-declared by including sources. It is included by DNLC implementation and several PAG/NFS-related sources that need DNLC declarations indirectly through broader AFS includes.

## Risks and edge cases
The name array comment notes possible null-byte waste; actual implementation copies names including the terminator and rejects names that would not fit. Changing `AFSNCNAMESIZE` affects memory footprint and lookup cache hit rate. Structure layout changes affect fixed `nameCache` memory use.

## Test signals
Validate build compatibility for all includers, DNLC name-size boundary behavior, stats counter reads, and no accidental ABI assumptions in debugging tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_osidnlc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_pag_call.c -->
# sources/distributed-fs/openafs/src/afs/afs_pag_call.c

## Purpose
`afs_pag_call.c` implements the PAG/NFS translator helper runtime used in PAG-only or translator contexts. It starts Rx services for remote stats and PAG callbacks, manages shutdown sequencing for Rx server/event/listener threads, converts selected pioctl payloads between host and network byte order, forwards pioctls to a remote system-control service, and restricts generic syscall calls.

## Important APIs, types, and functions
Global state includes `afs_termState`, `afs_gcpags`, `afs_shuttingdown`, `afs_cold_shutdown`, `afs_resourceinit_flag`, `afs_nfs_server_addr`, `afs_cb_interface`, `AFS_WaitHandler`, `srv_secobj`, `clt_secobj`, `stats_svc`, `pagcb_svc`, and `rmtsys_conn`. Key functions are `afs_Daemon`, `afspag_Init`, `afspag_Shutdown`, `token_conversion`, `FetchVolumeStatus_conversion`, `inparam_conversion`, `outparam_conversion`, `afs_syscall_pioctl`, and `afs_syscall_call`.

## Control flow
`afspag_Init` creates a callback UUID, initializes stats and PAG-specific locks, sets resource state and NFS server address, initializes sysnames, creates Rx stats and PAG callback services on port 7001, starts Rx server/listener/event/PAG daemon threads, initializes ICL logs, creates a remote `rmtsys` connection to port 7009, and sends a pioctl request asking the translator to drop cached credentials.

`afs_Daemon` periodically runs packet checks, user-data GC every 10 minutes, PAG GC every 60 minutes, waits, and participates in staged shutdown by moving `afs_termState` toward Rx event/listener shutdown. `afspag_Shutdown` sets `AFS_SHUTDOWN`, wakes Rx server procs, waits for state transitions, cancels daemon waits, and stops the Rx listener where present.

`afs_syscall_pioctl` copies in an `afs_ioctl`, handles local token/unlog/sysname pioctls first, builds `clientcred` from uid and PAG groups, canonicalizes path, allocates and converts input/output buffers, forwards the pioctl to `RMTSYS_Pioctl`, converts output payloads back, copies to user space, frees buffers, and returns remote or local errors.

## State and persistence behavior
Runtime state includes Rx services/connections, thread shutdown state, global shutdown mode, sysname and user/PAG data, and remote translator connection state. No persistent on-disk state is managed here.

## Dependencies and integration points
The file depends on Rx/RxStats, PAGCB and RMTSYS RPC definitions, pioctl command layouts, token and volume status structures, credential group encoding from PAG code, sysname/token handlers in `afs_pag_cred.c`, ICL, and OSI wait/copy/allocation APIs.

## Risks and edge cases
Pioctl marshalling is size-sensitive and only converts known commands. Buffer sizes are capped by `MAXBUFFERLEN`, with large buffers allocated differently from fixed large-space buffers. Secret token conversion must avoid reading past malformed lengths. Shutdown is state-machine based; missed wakeups or wrong state transitions can hang. `afs_syscall_call` only permits superuser shutdown and denies everything else.

## Test signals
Test translator startup service registration, remote credential flush pioctl, shutdown sequencing with and without Rx kernel listener, pioctl forwarding for token, unlog, sysname, volume status, cache parms, oversized input/output rejection, byte-order conversion round trips, and non-shutdown syscall denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_pag_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_pag_cred.c -->
# sources/distributed-fs/openafs/src/afs/afs_pag_cred.c

## Purpose
`afs_pag_cred.c` manages local PAG token and sysname state for the PAG callback/translator runtime. It stores a local mapping of cell names to synthetic cell numbers, sets/unsets tokens from pioctl payloads, serves credentials and sysnames to the NFS translator over PAGCB RPCs, and updates global sysname state.

## Important APIs, types, and functions
The file defines `struct afspag_cell`, `afs_xpagcell`, `afs_xpagsys`, `lastcell`, `cells`, and `primary_cell`. Cell helpers are `afspag_GetCell`, `afspag_GetPrimaryCell`, and `afspag_SetPrimaryCell`. Token pioctl handlers are `afspag_PUnlog` and `afspag_PSetTokens`. PAGCB service handlers are `SPAGCB_GetCreds` and `SPAGCB_GetSysName`. Sysname pioctl handling is in `afspag_PSetSysName`.

## Control flow
`afspag_GetCell` locks the cell list, returns an existing named cell, or allocates a new `afspag_cell`, duplicates the cell name, assigns the next synthetic cell number, links it into the list, and initializes the primary cell if absent. `afspag_PUnlog` finds all `unixuser` entries for the current PAG or uid and clears token state, vice id, and token storage.

`afspag_PSetTokens` parses a pioctl payload containing ticket length, ticket bytes, clear token length, clear token, optional primary flag, and optional cell name. It can request setting the parent PAG, resolves the target cell, identifies the current PAG or uid, obtains a write-locked `unixuser`, replaces tokens with a new rxkad token, updates auth stats, marks token state valid, sets primary state, and records token time.

`SPAGCB_GetCreds` accepts calls only from the configured NFS server host and port, counts matching `unixuser` records, allocates a `CredInfos` array, copies valid rxkad token material and cell names into RPC-owned allocations, and handles cleanup on allocation failure. `afspag_PSetSysName` validates superuser-supplied sysnames, rejects dangerous `.` and `..`, updates `afs_global_sysnames`, bumps `afs_sysnamegen`, and marks the forwarded command so the server applies it to all PAGs. `SPAGCB_GetSysName` copies current sysnames into a PAGCB response.

## State and persistence behavior
State is in memory: synthetic cell list, primary cell pointer, global sysname list/generation, and token state in `unixuser` records. Tokens are sensitive runtime credentials and are freed or copied into RPC responses as needed.

## Dependencies and integration points
Dependencies include `unixuser` hash tables and token APIs, rxkad token structures, PAG extraction, pioctl payload layouts, PAGCB XDR types, Rx peer/host checks, sysname locks, OSI allocation/string duplication, and the translator init state from `afs_pag_call.c`.

## Risks and edge cases
Security depends on `SPAGCB_GetCreds` restricting callers to `afs_nfs_server_addr:7001`, superuser checks for sysname mutation, and correct PAG/uid selection when no PAG exists. Payload parsing in `afspag_PSetTokens` must match pioctl marshalling exactly. Allocation failures in RPC response construction require careful partial cleanup. The `set_parent_pag` path warns and mutates process PAGs, which is sensitive.

## Test signals
Test token set/unlog for uid and PAG users, default primary cell behavior, explicit cell creation, primary token flag handling, parent-PAG request warning, PAGCB credential export only from the configured host, multi-cell credential responses, sysname validation and propagation, and allocation-failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_pag_cred.c -->
