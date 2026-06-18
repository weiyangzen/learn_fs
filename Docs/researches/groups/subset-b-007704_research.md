# subset-b-007704 research

This grouped report covers the OpenAFS Windows cache-manager files assigned to `subset-b-007704`. Each section preserves the original source path in its title and is bounded by the reconciliation markers used to split per-file research outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.h

## Purpose
`cm_nls.h` defines the Windows cache manager's naming and string character model. It maps client-visible strings to UTF-16 (`clientchar_t`), file-server strings to UTF-8 (`fschar_t`), and normalized strings to UTF-16 NFC (`normchar_t`). Most cache-manager code uses the abstract macros in this header instead of directly calling `wcs*`, `str*`, or Windows conversion APIs.

## Important APIs, types, and macros
- `cm_unichar_t`, `cm_normchar_t`, `cm_utf8char_t`, `clientchar_t`, `fschar_t`, and `normchar_t` establish the three implementation encodings and the public aliases used by higher layers.
- Literal helpers `_C`, `_FS`, and `_N` produce client, file-server, and normalized literals.
- Conversion aliases such as `cm_ClientStringToFsStringAlloc`, `cm_FsStringToClientString`, and `cm_FsStringToNormStringAlloc` route callers to UTF-16/UTF-8 conversion and normalization functions.
- Client-string operations map to wide-character or custom Unicode-aware helpers: `cm_ClientStrCmp`, `cm_ClientStrCmpI`, `cm_ClientStrCpy`, `cm_ClientStrPrintfV`, `cm_ClientCharNext`, and related macros.
- File-server string operations map to narrow UTF-8 helpers: `cm_FsStrCmp`, `cm_FsStrCmpI`, `cm_FsStrCpy`, and logging helpers.
- Exported functions cover normalization, UTF-8/UTF-16 conversion, case-insensitive compare, UTF-16 navigation, case folding, and UTF-16 validation.

## Control flow and state behavior
The header has no runtime state, but it strongly shapes control flow by forcing all filename conversion through a narrow set of macros. Allocation-returning routines accept source length and optional destination length out-parameters; non-allocating routines accept explicit destination buffer sizes. The SAL annotations document buffer contracts for static analysis and Windows builds.

## Dependencies and integration points
It depends on Windows wide-character conventions, `MultiByteToWideChar` for OEM/ANSI conversion wrappers, `StringCch*` safe string functions, `towupper`, logging helpers such as `osi_LogSaveStringW`, and implementation functions defined elsewhere in the national-language support code. It is included by cache, directory, redirector, and SMB-facing modules that need consistent path handling.

## Risks and edge cases
- The macro layer hides encoding conversions; misuse can silently compare UTF-8 data as UTF-16 or vice versa if a caller picks the wrong alias.
- `_FS(s)` leaves narrow literals unchanged, so source literals must already be UTF-8-compatible.
- Case-insensitive UTF-8 comparisons are custom and should be tested for non-ASCII behavior, not assumed equivalent to locale-specific Windows comparisons.
- `lengthof(a)` only works for arrays, not pointers.

## Test signals
Useful tests include UTF-16 validation failures, surrogate-pair navigation via `char_next_utf16` and `char_prev_utf16`, UTF-8 round trips, NFC normalization equivalence, ASCII and non-ASCII case-insensitive comparisons, OEM/ANSI conversion behavior, and buffer-size failure paths for the non-allocating conversion APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_nls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.c

## Purpose
`cm_performance.c` implements an optional performance-tuning collector for the Windows cache manager. It builds a FID-keyed statistics table from scache, volume, and buffer state, then appends aggregate cache usage summaries to `afsd_performance.log` under `%TEMP%` or the Windows directory.

## Important APIs and functions
- `nearest_prime()` chooses a hash-table size near the requested value using a simple sieve.
- `cm_PerformanceGetNew()` allocates `cm_fid_stats_t` objects from never-freed 32 KiB blocks.
- `cm_PerformanceInsertToHashTable()` inserts a FID-stat object by `fid.hash`.
- `cm_PerformanceAddSCache()` snapshots one non-deleted `cm_scache_t` into a stats entry, including file length/type, read-only flags, and callback state.
- `cm_PerformanceTuningInit()` allocates the stats hash table, scans all scache entries, all volumes, and all valid buffers, and prints the first report.
- `cm_PerformanceTuningCheck()` refreshes existing stats state, discovers new scache/volume entries, recounts valid buffers, and prints a report.
- `cm_PerformancePrintReport()` computes aggregate counts by volume class, scache/volume/buffer presence, callback presence, file type, and file-size bucket.

## Control flow
Initialization sizes the hash table from `cm_data.stats / 3`, walks `cm_data.scacheHashTablep`, then `cm_data.allVolumesp`, then `cm_data.buf_allp`. During scans it drops global locks before taking per-object locks or calling lookup helpers, then reacquires the global lock. Buffer accounting validates a buffer with `cm_FindSCache()` and `cm_HaveBuffer()` before incrementing the FID's `buffers` count. Each run ends by printing a single appended text block.

## State and persistence behavior
The module owns static `fidStatsHashTablep` and `fidStatsHashTableSize`. Individual `cm_fid_stats_t` records are intentionally never freed. Persistent output is only the appended performance log; no cache-manager state is saved from these statistics. Refreshes clear transient flags and counts while preserving RO/PURERO classification.

## Dependencies and integration points
It depends on `cm_data`, `cm_scacheLock`, `cm_volumeLock`, `buf_globalLock`, `cm_FindSCache`, `cm_HaveBuffer`, `cm_HaveCallback`, `cm_SetFid`, `cm_FidCmp`, `cm_ReleaseSCache`, and Windows file APIs (`GetEnvironmentVariable`, `CreateFile`, `WriteFile`). It is diagnostic and tuning-oriented rather than part of core cache correctness.

## Risks and edge cases
- `cm_PerformanceTuningCheck()` hashes `scp->fid` but compares `cm_FidCmp(&fid, &statp->fid)` in the scache loop; `fid` is not initialized in that path. This can prevent existing stat records from matching and create duplicate or incorrect entries.
- `nearest_prime()` loops until `malloc` succeeds and never handles permanent allocation failure.
- `cm_PerformanceGetNew()` is explicitly not thread-safe and assumes only one caller thread.
- The log file can grow without bounds.
- The hash table size can be zero if `cm_data.stats` is very small and allocation fallback is not reached safely.

## Test signals
Tests should inspect report buckets after controlled creation of RW/RO/BACK volume roots, scache entries with/without callbacks, deleted scaches, valid and invalid buffers, and large file lengths. Regression coverage should specifically exercise `cm_PerformanceTuningCheck()` with an existing scache stats record to catch the uninitialized-FID comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.h

## Purpose
`cm_performance.h` exposes the data structure and public entry points for the optional cache-manager performance collector implemented in `cm_performance.c`.

## Important APIs and types
- `cm_fid_stats_t` records one FID, its file type, file length, summary flags, valid buffer count, and hash-chain link.
- `CM_FIDSTATS_FLAG_HAVE_SCACHE`, `CM_FIDSTATS_FLAG_HAVE_VOLUME`, `CM_FIDSTATS_FLAG_RO`, `CM_FIDSTATS_FLAG_PURERO`, and `CM_FIDSTATS_FLAG_CALLBACK` describe the observed cache/volume/callback state.
- `cm_PerformanceTuningInit()`, `cm_PerformanceTuningCheck()`, and `cm_PerformancePrintReport()` are the externally visible lifecycle and reporting functions.

## Control flow and state behavior
The header defines no state by itself. Its struct is intentionally compact and hash-chain-friendly, and its flags are used as denormalized observations collected from scache, volume, and buffer scans. The header assumes `cm_fid_t` and `osi_hyper_t` are already visible through the surrounding cache-manager include graph.

## Dependencies and integration points
It is tightly coupled to `cm_scache.h` for `cm_fid_t` and file type constants, and to cache-manager global accounting in `cm_data`. Consumers should include it only in the Windows afsd cache-manager context.

## Risks and edge cases
The struct lacks ownership fields or allocation metadata because implementation records are never freed. Any future attempt to support unloading, reset, or concurrent collection would need an explicit allocator and locking model.

## Test signals
Compile-time tests should ensure the header is included in contexts where `cm_fid_t` and `osi_hyper_t` are defined. Runtime tests belong with `cm_performance.c`: flag combinations, buffer counts, and reporting paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_performance.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_rdr.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_rdr.h

## Purpose
`cm_rdr.h` is a bridge header between the user-mode Windows cache manager and the AFS redirector interface. It centralizes inclusion of redirector user definitions, structures, and prototypes.

## Important APIs and types
The file does not define new APIs. It includes:
- `..\afsrdr\common\AFSUserDefines.h`
- `..\afsrdr\common\AFSUserStructs.h`
- `..\afsrdr\common\AFSUserPrototypes.h`

## Control flow and state behavior
There is no executable code or state. The header only controls visibility of redirector contracts to cache-manager code.

## Dependencies and integration points
It depends on the Windows redirector common headers. Modules such as `cm_scache.c` integrate with redirector invalidation and buffer ownership (`RDR_InvalidateObject`, redirector cache state, and request-source flags) through these shared definitions.

## Risks and edge cases
- The relative include paths are Windows-build-specific and can be fragile for non-standard build roots.
- This header hides a large external contract behind a small wrapper; changes in the redirector common headers can affect cache-manager modules without local changes here.

## Test signals
Primary signals are build and ABI compatibility tests: user-mode afsd must compile against the redirector common headers, and redirector invalidation/request structures must remain binary-compatible with kernel-side consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_rdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.c

## Purpose
`cm_rpc.c` implements the Windows RPC side channel used to transfer AFS session keys between client applications and the AFS service without sending keys in cleartext through pioctl data. A pioctl supplies a UUID, and the RPC call supplies the matching UUID plus session key under RPC packet privacy/authentication.

## Important APIs and functions
- `tokenEvent_t` stores a one-use UUID, DES session key, optional caller SID string, and list link.
- `cm_RegisterNewTokenEvent()` pushes a new token event into the global list under `tokenEventLock`.
- `cm_FindTokenEvent()` finds and removes the matching UUID, returns the session key, and either returns or frees the SID string.
- `AFSRPC_SetToken()` is an RPC manager entry point that impersonates the caller, extracts token statistics and SID, converts the SID to a string, and registers the event.
- `AFSRPC_GetToken()` is an RPC manager entry point that consumes a registered event by UUID.
- `midl_user_allocate()` and `midl_user_free()` provide MIDL allocation hooks.
- `RpcListen()` registers the RPC interface, auth info, and endpoint, then listens until stopped.
- `RpcInit()` initializes the mutex/event and starts the listener thread.
- `RpcShutdown()` stops listening and waits for listener cleanup.

## Control flow
The normal token handoff has two paths converging on `tokenEvents`: `AFSRPC_SetToken()` records a UUID/session-key pair, while the pioctl side later calls `cm_FindTokenEvent()` to consume it. Entries are single-use and removed on successful lookup. The server startup path creates a listener thread, registers `afsrpc_v1_0_s_ifspec`, registers WinNT authentication, registers the endpoint, and calls `RpcServerListen`. Shutdown stops listening and waits on `rpc_ShutdownEvent`, which the listener sets during cleanup.

## State and persistence behavior
Global mutable state consists of `tokenEvents`, `tokenEventLock`, and `rpc_ShutdownEvent`. Token events live only in memory and are not persisted. The SID string is owned by the event until the consumer takes it or lookup frees it. The RPC shutdown event is a named Windows event (`afsd_rpc_ShutdownEvent`).

## Dependencies and integration points
It depends on Windows RPC, SDDL/SID APIs, thread token APIs, the MIDL-generated `afsrpc` interface, OpenAFS threading/event wrappers, `smb_GetUserSID`, and rxkad token structures. It integrates with pioctl token-management code through UUID matching and with SMB/user identity handling through SID capture.

## Risks and edge cases
- `cm_RegisterNewTokenEvent()` does not check `malloc` failure.
- Token events have no timeout or cap; abandoned events can accumulate if the pioctl side never consumes them.
- `AFSRPC_SetToken()` registers an event even if impersonation or SID extraction fails, in which case the SID may be NULL but the session key still enters the list.
- `RpcInit()` calls `CloseHandle(listenThread)` without guarding against `CreateThread` failure; if `listenThread` is NULL, Windows behavior should be checked.
- `RpcListen()` can log `task` after failure only if each failure path assigned it; current assignments cover visible failure jumps.

## Test signals
Tests should cover one-use UUID consumption, missing UUID failure, SID return versus SID free paths, concurrent registration and lookup under lock, RPC listener start/stop, caller impersonation failure, and stale event accumulation under failed or interrupted token setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.h

## Purpose
`cm_rpc.h` declares the afsd RPC token side-channel interface used by the Windows cache manager and includes the MIDL-generated RPC declarations.

## Important APIs
- `cm_RegisterNewTokenEvent(afs_uuid_t uuid, char sessionKey[8], clientchar_t *)` registers a pending session-key handoff.
- `cm_FindTokenEvent(afs_uuid_t uuid, char sessionKey[8], clientchar_t **)` consumes a pending handoff.
- `RpcInit()` starts the RPC server.
- `RpcShutdown()` stops it.

## Control flow and state behavior
This header only declares functions. Runtime state is implemented in `cm_rpc.c` as a global token-event list protected by a mutex and a listener shutdown event.

## Dependencies and integration points
It includes `afsrpc.h`, which must provide the RPC interface, UUID type, and generated server/client declarations. It also depends on `clientchar_t` from the cache-manager string layer.

## Risks and edge cases
The API exposes raw 8-byte session-key buffers and pointer ownership for SID strings; callers must follow the implementation's ownership convention exactly. No length is passed for the session key because the protocol fixes it at 8 bytes.

## Test signals
Compile and RPC IDL compatibility tests should verify declarations match the generated interface. Runtime behavior is covered by `cm_rpc.c` tests for registration, lookup, and server lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.c

## Purpose
`cm_scache.c` implements the Windows cache manager's stat-cache lifecycle and synchronization core. It owns allocation/recycling of `cm_scache_t` objects, FID hash lookup, LRU management, callback/status invalidation, fetch/store synchronization, status merging, refcounting, validation, shutdown, and diagnostics.

## Important APIs and functions
- Global state: `cm_scacheLock`, `cm_allFileLocks`, `cm_freeFileLocks`, `cm_lockRefreshCycle`, `cm_fakeSCache`, and the free waiter list.
- `cm_RootSCachep()` obtains status/callback on the root scache before returning it.
- `cm_AdjustScacheLRU()`, `cm_RemoveSCacheFromHashTable()`, and `cm_RecycleSCache()` manage hash/LRU membership and object reset.
- `cm_GetNewSCache()` recycles an unused LRU entry or allocates from the preallocated scache arena.
- `cm_SetFid()` and `cm_FidCmp()` are the canonical FID construction/comparison helpers.
- `cm_InitSCache()`, `cm_ShutdownSCache()`, and `cm_SuspendSCache()` initialize locks/lists, release callbacks/resources, and handle suspend callback expiry.
- `cm_FindSCache()` and `cm_GetSCache()` provide held scache lookup/create paths, including freelance-root handling.
- `cm_SyncOp()` and `cm_SyncOpDone()` serialize status, data, callback, access-rights, lock, async-store, and bulk-read operations against a scache and optional buffer.
- `cm_MergeStatus()` merges `AFSFetchStatus` and `AFSVolSync` results into an scache, updates ACL/access caches, invalidates stale buffers, updates volume online state, and notifies the redirector.
- `cm_DiscardSCache()`, refcount helpers, `cm_FindFileType()`, `cm_ValidateSCache()`, and `cm_DumpSCache()` support invalidation, lifecycle safety, and diagnostics.

## Control flow
Lookup starts with a hash-table scan under `cm_scacheLock`. On miss, `cm_GetSCache()` obtains a new/recycled scache, resolves the cell and volume, rechecks the hash under write lock to avoid duplicate insertion, initializes RO/dotdot/parent state, inserts into the hash table, and returns a held reference. Freelance root and mountpoint entries bypass normal server status and synthesize local metadata.

Recycling walks the LRU tail, temporarily drops the global lock to inspect dirty or redirector-held buffers, tries the scache write lock, verifies LRU position did not change, removes hash membership, clears callbacks, ACLs, DNLC entries, mountpoint state, file locks, B+ directory state, flags, and FID fields, and optionally notifies the redirector of callback expiry.

`cm_SyncOp()` is the main concurrency gate. It requires the scache write lock, tests requested sync flags against current scache and buffer flags, obtains callbacks and access rights when requested, and sleeps via a per-scache waiter queue if the operation conflicts. On success it marks scache flags and buffer I/O queues. `cm_SyncOpDone()` clears those marks, removes buffer queue entries, releases held buffers, and wakes waiters.

`cm_MergeStatus()` validates status, handles server-side error status, rejects stale non-RO data versions unless forced, updates file metadata and ACL caches, removes stale unreferenced clean buffers from hash tables, maintains `bufDataVersionLow`, sends redirector data-version invalidations when needed, marks fetch-status complete, and marks the backing volume online.

## State and persistence behavior
Stat-cache state is in-memory only, backed by the mapped `cm_data` arena and hash/LRU lists. Each scache stores FID, status fields, data-version ranges, callback server/expiry, access cache links, file-lock counters, buffer I/O queues, redirector buffer queues, wait queues, and B+ directory state. No scache state is persisted by this file, but it preserves dirty buffer state by avoiding recycle when dirty buffers exist and by not discarding dirty data on status invalidation.

## Dependencies and integration points
This file is central to the afsd subsystem. It depends on volume/cell lookup, callback management, DNLC, ACL cache, buffer cache, redirector invalidation, freelance root support, B+ directory trees, server refs, request flags, OpenAFS fetch-status structures, and OSI locks/queues. Its public functions are used by fetch/store, directory, SMB, redirector, callback, and daemon paths.

## Risks and edge cases
- Lock ordering is complex: the code intentionally drops global locks around per-object locks, redirector invalidation, volume lookup, buffer checks, and callback operations. Regressions can deadlock.
- `cm_SyncOp()` can sleep with interactions between scache locks and buffer mutexes; missed `cm_SyncOpDone()` calls leave waiters dependent on the error wakeup path.
- Recycle decisions are race-sensitive and rely on LRU neighbor snapshots plus refcount/buffer checks.
- `cm_MergeStatus()` assumes valid `reqp` in redirector-invalidation checks; callers should not pass NULL if redirector support is active.
- Data-version arithmetic uses wrap-aware `dv_diff()` and active-RPC counts; incorrect flags can invalidate too much or too little cached data.
- Several diagnostic paths use fixed-size `sprintf` buffers with rich state strings.

## Test signals
High-value tests include duplicate lookup races, LRU recycle with dirty/redirector buffers, callback discard, redirector invalidation on data-version change, concurrent fetch/store/read/write conflicts, waiter wake ordering, `NOWAIT` behavior, stale data-version merges on RW versus RO files, ACL cache updates on access errors, directory B+ reset, suspend/shutdown callback release, and validation of hash/LRU/DNLC invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.h

## Purpose
`cm_scache.h` defines the stat-cache object model for the Windows AFS cache manager. It describes FIDs, byte-range locks, cached file status, callback state, access cache links, buffer/redirector state, synchronization flags, file-type constants, and the public scache API.

## Important APIs and types
- `cm_fid_t` identifies AFS objects by cell, volume, vnode, unique, and cached hash.
- `cm_key_t`, `cm_range_t`, and `cm_file_lock_t` model per-client byte-range locks.
- `cm_prefetch_t` tracks the last prefetch scan range.
- `cm_scache_t` is the central cached-vnode object, containing LRU/hash links, locks, refcount, file status, volume/callback data, ACL cache, file-lock state, directory B+ tree state, open counts, sync wait queue, redirector buffer queue, and active RPC count.
- File-type constants map AFS file status to cache-manager categories, including mount points, symlinks, DFS links, and invalid entries.
- `CM_SCACHEFLAG_*`, `CM_SCACHESYNC_*`, and `CM_MERGEFLAG_*` define persistent scache state, operation synchronization requests, and status-merge context.
- Public APIs include initialization, lookup/create, synchronization, status merge, refcounting, recycle, hash removal, directory reset, root lookup, validation, dump, suspend, and shutdown.

## Control flow and state behavior
The header defines the flags that drive `cm_scache.c` control flow. `CM_SCACHEFLAG_*` bits record in-progress RPCs, callback state, read-only state, quota/space errors, local modifications, redirector use, and watcher state. `CM_SCACHESYNC_*` flags request synchronization for one operation and map to those state bits. `CM_MERGEFLAG_*` tells `cm_MergeStatus()` why status is being merged so it can interpret data-version changes correctly.

## Dependencies and integration points
It includes Jenkins hash support via `opr/jhash.h`, then later includes `cm_conn.h` and `cm_buf.h` because scache synchronization touches connections and buffers. It exposes global locks and lists used across the cache manager. Redirector, SMB, callback, volume, ACL, directory, and daemon code all depend on this header's struct layout and flag meanings.

## Risks and edge cases
- `CM_FID_GEN_HASH` hashes volume/vnode/unique but intentionally excludes cell, so comparisons must still use `cm_FidCmp()` and callback-revocation paths must understand possible cross-cell hash collisions.
- Many fields are protected by different locks (`cm_scacheLock`, `scp->rw`, `redirMx`, `dirlock`, atomics), making the comments part of the correctness contract.
- `cm_scache_t` is large and shared broadly; layout changes can affect persisted memory-map assumptions or debugger tooling.
- Flag overlap between RPC sync flags and local sync flags requires careful use of masks.

## Test signals
Compile-time and runtime tests should verify FID hash/comparison behavior, lock count accounting, sync flag to scache flag transitions, file type mapping, read-only flag propagation, redirector queue protection, B+ directory invalidation, and refcount/list invariant validation through `cm_ValidateSCache()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_scache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.c

## Purpose
`cm_server.c` manages known VLDB and file servers for the Windows cache manager. It tracks server identity, reachability, capabilities, ranking/preference, per-server volume references, server-reference lists used by cells/volumes, network-interface ranking inputs, and diagnostic dumps.

## Important APIs and functions
- Global locks/state: `cm_serverLock`, `cm_syscfgLock`, `cm_serversAllFirstp`, `cm_serversAllLastp`, `cm_numFileServers`, `cm_numVldbServers`, interface arrays, and `cm_LanAdapterChangeDetected`.
- `cm_NewServer()`, `cm_FindServer()`, `cm_FindServerByIP()`, and `cm_FindServerByUuid()` create or find server objects.
- `cm_GetServer()`, `cm_PutServer()`, and no-lock variants maintain server refcounts.
- `cm_PingServer()`, `cm_CheckServersSingular()`, `cm_CheckServersMulti()`, and `cm_CheckServers()` probe reachability and capabilities.
- `cm_RankServer()`, `cm_RankUpServers()`, and `cm_SetServerIPRank()` compute active server rank from admin preference, local network proximity, random jitter, and RX performance statistics.
- `cm_NewServerRef()`, `cm_InsertServerList()`, `cm_ChangeRankServer()`, `cm_RandomizeServer()`, `cm_FreeServerList()`, and `cm_AppendServerList()` maintain sorted server reference lists.
- `cm_MarkServerDown()`, `cm_ForceNewConnectionsAllServers()`, `cm_ServerClearRPCStats()`, and capability flag setters update connection and server state.
- `cm_DumpServers()` and `cm_ServerEqual()` support diagnostics and identity comparisons.

## Control flow
Server creation first searches for an existing server by address/type, attaches UUID/cell metadata if missing, or allocates a new server and links it into the global list. Unless probing is suppressed, new servers are initially marked down, ranked, and pinged.

Pinging obtains an unauthenticated connection when networking is available, performs the VLDB or file-server probe, updates up/down state, capabilities, volume online/offline status, connection state, and rank. Multi-check mode batches file-server `RXAFS_GetCapabilities` probes and VLDB `VL_ProbeServer` probes using `multi_Rx`, while singular mode pings each selected server individually. Registry value `MultiCheckServers` selects the mode.

Ranking updates local IP rank from interface/subnet comparisons, incorporates admin rank if present, folds in RX peer RPC timing and congestion-window data, adds jitter, and then reorders volume or cell server lists if the rank changes enough.

## State and persistence behavior
Server state is in memory and protected by `cm_serverLock`, per-server `mx`, and `cm_syscfgLock`. It records address, type, connection list, flags, capabilities, cell pointer, refcount, ping concurrency, ranks, served volume IDs, down time, and UUID. Persistence is indirect: admin preferences and multi-check behavior may come from registry/DNS/user commands, but this file itself does not write persistent state.

## Dependencies and integration points
It depends on RX connections and peer stats, VLDB/file-server RPC probes, cell and volume modules (`cm_ChangeRankVolume`, `cm_ChangeRankCellVLServer`, `cm_FindVolumeByID`, `cm_UpdateVolumeStatus`), connection garbage collection, Windows registry access, network interface discovery via `syscfg_GetIFInfo`, and OSI locks/queues. It is the server-selection backbone for volume and connection code.

## Risks and edge cases
- `cm_CheckServersMulti()` allocates several arrays without checking each allocation before use.
- `cm_DumpServers()` calls `ctime(&tsp->downTime)` and trims the returned string even when the server is up; if `ctime` returns NULL this would fail.
- `cm_NewServer()` logs a two-cell association path that dereferences `tsp->cellp` and `cellp`; malformed calls with NULL can be unsafe in that branch.
- Ranking uses floating point/log and random jitter; tests need tolerances rather than exact ranks.
- The list-free paths deliberately drop `cm_serverLock` in `cm_FreeServer()` to obey lock hierarchy, so refcount races must be covered.
- Background probe creation passes `cm_PingServer` to `pthread_create`; signature compatibility depends on platform typedefs/build settings.

## Test signals
Tests should cover server creation deduplication by IP/port/type/UUID, cell attachment, up/down transitions, capability update, multi-check and singular probe paths, network-interface ranking, admin rank precedence, sorted insertion and reranking of server refs, deletion with nonzero refs, volume-ID tracking, no-network behavior, and server equality with and without UUID support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.h

## Purpose
`cm_server.h` declares the Windows cache manager's server model: server objects, server-reference list nodes, server ranking constants, state flags, probe flags, global locks, and public server-management APIs.

## Important APIs and types
- `cm_server_vols_t` stores pages of volume IDs known to reside on a server.
- `cm_server_t` records global-list membership, socket address, type, connection list, flags, wait/ping counts, capabilities, cell pointer, refcount, ranks, volume list, down time, and UUID.
- `cm_serverRef_t` links volumes/cells to servers with per-reference status, refcount, and volume ID.
- `enum repstate` distinguishes not-busy, busy, offline, and deleted server refs.
- Constants define server types (`CM_SERVER_VLDB`, `CM_SERVER_FILE`), flags (`DOWN`, `PREF_SET`, `NO64BIT`, `NOINLINEBULK`, `UUID`), check masks, and IP rank buckets.
- Public functions cover creation/find, refs, ranking, probing, list operations, capability flags, interface updates, dumping, equality, and RPC stats clearing.

## Control flow and state behavior
The header's protection comments define lock ownership: global lists and server refs are protected by `cm_serverLock`; per-server address/type/flags/waits/capabilities/ranks/vols/down time/UUID are protected by `serverp->mx`; interface arrays are protected by `cm_syscfgLock`. Server-reference lists are sorted by active rank and can retain deleted nodes until refcounts drop.

## Dependencies and integration points
It includes Winsock and OSI lock types and forward-references cell/connection structures. It is consumed by volume, cell, connection, callback, and diagnostics modules that need server identity, ordering, and reachability information.

## Risks and edge cases
- `NUM_SERVER_VOLS` is derived from pointer size and should be treated as layout-sensitive.
- Several APIs accept `locked` flags; callers must pass the right value to avoid double-locking or unlocked mutation.
- Server objects can be pointed to by cells and volumes without holds, so global lock discipline is part of memory safety.

## Test signals
Tests should validate server-ref refcount behavior under locked/unlocked calls, list ordering by rank, deleted reference cleanup, IP rank constants, capability flag setters, and lock-protected interface array updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.c

## Purpose
`cm_user.c` implements cache-manager user objects and per-cell token records. It initializes the root user, creates users, creates/finds per-cell credential slots, maintains user and virtual-circuit reference counts, and periodically expires Kerberos/rxkad tokens associated with SMB users.

## Important APIs and functions
- `cm_InitUser()` initializes `cm_userLock` once and creates `cm_rootUserp`.
- `cm_NewUser()` allocates and initializes a `cm_user_t` with refcount one and a mutex.
- `cm_GetUCell()` finds or creates the `cm_ucell_t` record for a user/cell; root-user records receive `CM_UCELLFLAG_ROOTUSER`.
- `cm_FindUCell()` returns the best cell-info iterator entry for token-list enumeration.
- `cm_HoldUser()` and `cm_ReleaseUser()` maintain object lifetime under `cm_userLock`.
- `cm_HoldUserVCRef()` and `cm_ReleaseUserVCRef()` maintain virtual-circuit references under the user mutex.
- `cm_CheckTokenCache()` walks SMB VCs/users, expires rxkad tokens, frees tickets, clears flags, increments generation, and resets ACL cache for the affected cell/user.

## Control flow
Initialization is once-only for the lock but creates the root user whenever `cm_InitUser()` runs. Per-cell info is lazily inserted at the list head, with iterators increasing from the prior head. Token expiration scans `smb_allVCsp` under `smb_rctLock`, locks each user, checks `CM_UCELLFLAG_RXKAD` records against `now`, frees expired ticket material, clears rxkad state, increments `gen`, temporarily drops the user lock to reset ACL cache, and resumes scanning.

## State and persistence behavior
User/token state is in memory only. `cm_user_t` holds refcount, cell info list, mutex, VC refs, flags, and redirector auth group. `cm_ucell_t` holds ticket bytes, session key, kvno, expiration, generation, flags, and username. Ticket buffers are freed on expiration and user destruction.

## Dependencies and integration points
It depends on OSI locks, Windows atomics, SMB VC/user lists, rx/rxkad types, cell structures, `cm_ResetACLCache`, and global `cm_rootUserp`. Connection objects hold user references, and SMB/redirector authentication code consumes these users.

## Risks and edge cases
- `cm_NewUser()` does not handle `malloc` failure.
- `cm_ReleaseUser()` finalizes `userp->mx` while holding `cm_userLock`; callers must not race with outstanding user mutex users after refcount reaches zero.
- `cm_FindUCell()` relies on iterator ordering from head insertion; changes to insertion order would affect token enumeration.
- Token expiration currently handles rxkad flags; rxgk/root token behavior is only represented in flags/stub code.
- `bExpired` is declared but unused.

## Test signals
Tests should cover root-user initialization, per-cell lazy creation, iterator lookup ordering, refcount underflow assertions, VC ref underflow assertions, ticket free and flag clearing on expiration, ACL cache reset after expiration, and no-op behavior for users without tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.h

## Purpose
`cm_user.h` defines the Windows cache manager user and per-cell credential structures, credential flags, user flags, root-user global, and public user lifecycle/token APIs.

## Important APIs and types
- `cm_ucell_t` stores per-cell credentials: cell pointer, ticket buffer/length, session key, kvno, expiration, generation, iterator, flags, username, and optional AFS ID.
- `CM_UCELLFLAG_HASTIX`, `RXKAD`, `BADTIX`, `RXGK`, and `ROOTUSER` classify credential state.
- `cm_user_t` stores refcount, cell-info list, mutex, virtual-circuit refs, flags, and redirector auth group GUID.
- `CM_USERFLAG_DELETE` marks delete-on-last-reference behavior.
- Declared functions cover initialization, user creation, ucell lookup, reference management, token-cache checking, and token presence.

## Control flow and state behavior
The header defines lock ownership: user refcount is protected by `cm_userLock`, while most fields inside `cm_user_t` and `cm_ucell_t` are protected by `userp->mx`. There are no free references outside the all-users list contract described in comments; connection objects hold references.

## Dependencies and integration points
It includes OSI primitives and rxkad key definitions. It forward-references cell structures and is used by connection, token, SMB, redirector, ACL, and cache synchronization code.

## Risks and edge cases
Callers must distinguish held user references from VC references. Credential buffers are raw pointers and require exact ownership handling. Future rxgk support must preserve existing rxkad assumptions in token expiration and connection setup.

## Test signals
Tests should verify struct flag transitions for token setup/expiration, root-user ucell creation, user ref/VC ref behavior, and `cm_HaveToken()` behavior for cells with and without usable tickets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.c -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.c

## Purpose
`cm_utils.c` provides miscellaneous Windows cache-manager utilities: global utility initialization, RPC/error-code mapping, reusable scratch-space allocation, 8.3 short-name generation and wildcard matching, hook DLL loading, OS file-version probing, SMB redirector capability detection, thread-priority adjustment for long requests, Windows/Unix/DOS time conversions, and a power-of-two helper.

## Important APIs and functions
- `cm_utilsInit()` and `cm_utilsCleanup()` initialize/finalize `cm_utilsLock` and the TLS request-start slot.
- `init_et_to_sys_error()` and `et_to_sys_error()` map unified AFS error-table values to errno values.
- `cm_MapRPCError()`, `cm_MapRPCErrorRmdir()`, and `cm_MapVLRPCError()` translate RX, Unix, volume, and VLDB errors to cache-manager error codes, honoring saved request errors on timeout.
- `cm_GetSpace()` and `cm_FreeSpace()` manage a freelist of `cm_space_t` scratch buffers.
- `cm_Is8Dot3()`, `cm_Gen8Dot3NameInt()`, `cm_Gen8Dot3NameIntW()`, and `cm_Gen8Dot3VolNameW()` validate and synthesize DOS 8.3 names.
- `cm_MatchMask()` and `szWildCardMatchFileName()` implement Windows-style wildcard matching with optional case folding and 8.3 restriction.
- `cm_TargetPerceivedAsDirectory()`, `cm_LoadAfsdHookLib()`, `cm_GetOSFileVersion()`, and `msftSMBRedirectorSupportsExtendedTimeouts()` provide Windows integration helpers.
- `cm_SetRequestStartTime()`, `cm_UpdateServerPriority()`, and `cm_ResetServerPriority()` adjust thread priority based on request duration using TLS state.
- Time helpers convert Unix time to/from Windows `FILETIME` and DOS search time.
- `cm_NextHighestPowerOf2()` rounds a 32-bit value upward to a power of two.

## Control flow
Utility initialization is lazy via `osi_Once`; `cm_GetSpace()` calls it before using the scratch-space freelist. Error mapping first resolves AFS error-table values to errno, then maps transport/server/application failures into `CM_ERROR_*` values. Wildcard matching normalizes some Windows wildcard metacharacters, compresses redundant wildcard sequences, optionally folds case, then recursively matches `*` and `?`. SMB redirector timeout detection checks OS version/service pack, possibly disables WoW64 filesystem redirection, reads `mrxsmb.sys` version, and caches the result.

## State and persistence behavior
State is limited to process memory: `cm_utilsOnce`, `cm_utilsLock`, `cm_spaceListp`, `et2sys`, and `cm_TlsRequestSlot`. Scratch spaces are recycled but never globally drained here. Timeout support detection is cached in static local variables. No persistent files are written.

## Dependencies and integration points
It depends on Windows APIs (`TlsAlloc`, file-version APIs, path helpers, module loading, thread priority, OS version, WoW64 redirection), RX error codes, OpenAFS unified error tables, cache-manager request structs, string macros from `cm_nls.h`, directory FID structures, registry/build constants, and OSI locks/time.

## Risks and edge cases
- `init_et_to_sys_error()` must be called before error-table mappings are expected; otherwise table entries remain zero.
- `cm_GetSpace()` does not check `malloc` failure before `memset`.
- `cm_FreeSpace()` accepts any pointer and does not validate it came from `cm_GetSpace()`.
- `cm_MatchMask()` allocates a new mask without NULL checking.
- `msftSMBRedirectorSupportsExtendedTimeouts()` appears to use `if (cm_GetOSFileVersion(...) || (fvFile >= min))`, which can mark support true when version retrieval succeeds even if the version is below the threshold; the likely intended condition is success and version >= minimum.
- `GetVersionEx` behavior depends on application manifesting on newer Windows versions.
- `cm_NextHighestPowerOf2(0)` returns 0 through unsigned wrap; callers must decide if that is acceptable.

## Test signals
Tests should cover RX timeout saved-error precedence, VLDB no-entry mapping, rmdir `ENOTEMPTY` variants, scratch freelist reuse, 8.3 validation/generation including high-bit and illegal characters, wildcard metacharacter normalization, case-folded matching, hook DLL path construction, SMB redirector version-threshold behavior, TLS priority reset, all time round trips, and power-of-two edge values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.h

## Purpose
`cm_utils.h` declares miscellaneous utility structures, VLDB error-code constants, error mapping APIs, scratch-space allocation, 8.3 and wildcard helpers, Windows integration helpers, time conversion helpers, interlocked bitwise helpers, and power-of-two rounding for the Windows cache manager.

## Important APIs and types
- `cm_space_t` is an 8192-character scratch buffer that can hold either client UTF-16 data or narrow data and link into a freelist.
- `VL_*` constants provide local VLDB error-code definitions used by mapping paths.
- Error APIs: `cm_MapRPCError`, `cm_MapRPCErrorRmdir`, `cm_MapVLRPCError`, and `init_et_to_sys_error`.
- Filename APIs: `cm_Is8Dot3`, `cm_Gen8Dot3Name`, `cm_Gen8Dot3NameInt`, `cm_Gen8Dot3NameIntW`, `cm_Gen8Dot3VolNameW`, and `cm_MatchMask`.
- Windows helpers: `cm_TargetPerceivedAsDirectory`, `cm_LoadAfsdHookLib`, `cm_GetOSFileVersion`, `msftSMBRedirectorSupportsExtendedTimeouts`.
- Request-priority APIs: `cm_UpdateServerPriority`, `cm_SetRequestStartTime`, and `cm_ResetServerPriority`.
- Time helpers convert between Unix, Windows search/FILETIME, and DOS search time encodings.
- Inline `cm_InterlockedAnd` and `cm_InterlockedOr` implement compare-exchange loops for debug x86 builds.
- `cm_NextHighestPowerOf2()` rounds up a 32-bit integer.

## Control flow and state behavior
The header declares the utility module's public behavior but owns no runtime state. Its inline interlocked helpers perform lock-free read-modify-write loops and are conditionally aliased to `_InterlockedOr`/`_InterlockedAnd` for debug x86 builds.

## Dependencies and integration points
It depends on `clientchar_t`, `cm_req_t`, directory FID types, Windows `HANDLE`, `FILETIME`, `LARGE_INTEGER`, and cache-manager flags such as `CM_FLAG_8DOT3` and `CM_FLAG_CASEFOLD` from surrounding includes. It is used broadly by RPC callers, directory enumeration, SMB/redirector code, and daemon/request priority paths.

## Risks and edge cases
The VLDB constants duplicate external error meanings; they must stay consistent with the VLDB protocol. The `cm_Gen8Dot3Name` macro rewrites to `cm_Gen8Dot3NameInt`, so debuggers and static analyzers should account for the macro indirection. Inline interlocked helpers assume `LONG` operands and Windows compare-exchange semantics.

## Test signals
Tests should validate macro expansion for short-name generation, VLDB error mapping constants, interlocked helper behavior under concurrent bit updates, time conversion declarations across 32-bit and 64-bit `time_t`, and compatibility with modules that include this header before or after other cache-manager headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.h -->
