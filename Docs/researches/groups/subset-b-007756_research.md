# Research: subset-b-007756

Grouped research for OpenAFS `src/afs` cache-manager files. Each section preserves the source path and is bounded by reconciliation markers for deterministic per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_analyze.c -->
## sources/distributed-fs/openafs/src/afs/afs_analyze.c

Purpose: Implements the cache manager's central RPC-result analyzer. Callers wrap fileserver or VLDB RPCs in retry loops and call `afs_Analyze` to classify errors, release the connection, update server/volume/request state, and decide whether another server or retry attempt should be tried.

Important APIs and functions: `afs_Analyze` is the exported decision routine. `VLDB_Same` re-queries the VLDB after volume-missing or moved errors and refreshes cached volume server lists. `afs_BlackListOnce` marks a server as skipped only for the current `vrequest`. `afs_ClearStatus` stales cached vnode status after failed mutating RPCs. `afs_PrintServerErrors` reports per-server failures for hard-mount waits, and `afs_kill_pending` suppresses retries when the current task is being killed. Tunables include `afs_BusyWaitPeriod`, `hm_retry_RO`, `hm_retry_RW`, and `hm_retry_int`.

Control flow: `afs_Analyze` first finalizes the request, exits early for pending process death or disconnected mode, and records trace/stat counters. If no connection is available, it handles busy-volume polling, hard-mount retry for the primary cell, path-MTU `RX_MSGSIZE`, and network errors. With a connection, it translates unified-AFS errors, records the last error for the server slot, and branches by error class: success clears busy state; timeouts and `VNOSERVICE` blacklist one server; negative network errors mark servers down and force new connections; `VBUSY`/`VRESTARTING` update volume status; token/rxkad failures mark user tokens bad or retry against another server; access failures set request protection flags; ubik and VLDB errors drive server-down or volume-missing behavior; volume moved/offline errors trigger `VLDB_Same`.

State and persistence: State is volatile but widely shared: `vrequest` error counters and skip arrays, `volume->status`, `VRecheck`/`setupTime`, server down flags, user token states, connection `forceConnectFS`, and performance error buckets. No durable state is written here, but decisions can invalidate vnode status and cached VLDB-derived volume metadata.

Dependencies and integration points: Integrates with RX connection objects, fileserver/VLDB stubs, `afs_conn.c`, cell and volume lookup, server health management, token/user state, vnode cache invalidation, stats/tracing, disconnected mode, and hard-mount policy. It assumes callers pass the connection lock type needed by `afs_PutConn`.

Risks: Retry behavior is subtle and can turn transient failures into long sleeps for hard mounts. Incorrect classification can either hide permanent errors or prematurely mark servers/volumes bad. Some helper paths stale cached vnode status for write RPC failures and require correct operation indexing. `VLDB_Same` performs network work and volume replacement while coordinating multiple locks and old/new VLDB formats.

Test signals: Exercise success, network timeout, `RX_MSGSIZE`, `VBUSY`, `VRESTARTING`, token expiry, rxkad errors with single and multiple replicas, access-denied store failures, VLDB move/offline responses, hard-mount primary-cell retries, disconnected mode, and killed-task early exit. Verify connection refs are released exactly once and request flags match caller expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_analyze.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_axscache.c -->
## sources/distributed-fs/openafs/src/afs/afs_axscache.c

Purpose: Provides allocation, lookup assistance, removal, list-free, and shutdown logic for small per-vnode access-cache entries (`struct axscache`) used to memoize access rights by user id.

Important APIs and functions: `afs_SlowFindAxs` scans a linked list after the fast head check in `afs_FindAxs` misses and moves a found entry to the front. `axs_Alloc` allocates entries from a freelist, bulk-allocating `struct xfreelist` slabs. `afs_RemoveAxs` removes one entry from a parent list and returns it to the freelist. `afs_FreeAllAxs` prepends a whole list to the freelist. `shutdown_xscache` releases all slab allocations.

Control flow: Allocation takes `afs_xaxs`, pops `afs_axsfreelist` when possible, otherwise allocates a slab, initializes each entry with sentinel uid/access values, chains the rest onto the freelist, and returns the first entry. Lookups walk two nodes per loop and use the `axs_Front` macro for LRU-style promotion. Frees take only the global freelist lock; list lookup/removal relies on the caller holding the parent object's lock.

State and persistence: Maintains process/kernel-memory globals `afs_axsfreelist`, `xfreemallocs`, `afs_xaxscnt`, and lock `afs_xaxs`. There is no disk persistence; shutdown frees all slabs and clears globals.

Dependencies and integration points: Depends on allocation primitives, OpenAFS lock macros, and the `struct axscache` contract from `afs_axscache.h`. The data is embedded by higher-level cache objects that own the access-cache list and are responsible for parent-level synchronization.

Risks: The package is optimized for lookup speed and assumes correct external locking around list membership. The remove loop is especially fragile: after checking `j == axsp`, the next unrolled branch assigns `i = j->next` and frees `axsp` without comparing `i` to `axsp`, which is a potential wrong-entry unlink/free path if exercised. Freelist entries are not scrubbed on free beyond later allocation initialization.

Test signals: Allocate more than one slab, find head and non-head entries, verify front promotion, remove head/middle/tail/missing entries, free whole lists with odd/even lengths, run concurrent allocation/free under caller locking assumptions, and validate shutdown releases every slab.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_axscache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_axscache.h -->
## sources/distributed-fs/openafs/src/afs/afs_axscache.h

Purpose: Declares the access-cache entry type and fast macros used by cache-manager structures to cache access bits for recently checked users.

Important APIs and types: `struct axscache` contains `uid`, `axess`, and `next`. `afs_FindAxs(cachep,id)` checks the head entry inline and falls back to `afs_SlowFindAxs`. `axs_Front` moves a found node to the list front. `afs_AddAxs` allocates, fills, and prepends a new entry.

Control flow: The header has no standalone runtime path, but its macros mutate linked-list pointers and may evaluate arguments in ways callers must understand. `afs_FindAxs` explicitly requires a non-null list head and expects the caller to have checked that the cache pointer exists.

State and persistence: State lives in caller-owned linked lists plus the global allocator implemented in `afs_axscache.c`. There is no durable persistence.

Dependencies and integration points: Requires OpenAFS integer types and external implementations of `afs_SlowFindAxs` and `axs_Alloc`. It is integrated with vnode/access checks where parent structures serialize access-cache updates.

Risks: Macros hide allocation and pointer mutation, offer no null safety for `afs_FindAxs`, and rely on caller locks. The field name `axess` is historical and can obscure meaning. Because `afs_AddAxs` is a macro block without `do { } while (0)`, it is sensitive to use in conditional statements.

Test signals: Compile macro use in common conditional contexts, run null-head negative tests at call sites, verify cache-hit access bits are unchanged, and inspect list order after repeated `afs_FindAxs` and `afs_AddAxs` operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_axscache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_buffer.c -->
## sources/distributed-fs/openafs/src/afs/afs_buffer.c

Purpose: Implements the directory-buffer package: a small in-memory cache of 2 KiB directory pages backed by dcache files. Directory code uses it to read, create, dirty, flush, zap, and release directory pages without directly managing cache-file I/O.

Important APIs and functions: `DInit` initializes buffers and hash buckets. `DReadWithErrno`/`DRead` fetch an existing directory page and return a `DirBuffer`. `DNew` creates a new page buffer and extends the dcache chunk if needed. `DRelease` drops a buffer reference and marks dirty. `DVOffset` computes the byte offset of a directory pointer. `DZap`, `DFlushDCache`, and `DFlush` invalidate or write dirty buffers. `shutdown_bufferpackage` flushes and frees buffer storage.

Control flow: Reads validate the dcache chunk, search `phTable[pHash(fid,page)]`, promote hits to the bucket front, and increment `lockers` under the global and per-buffer lock hierarchy. Misses call `afs_newslot`, which selects an unlocked least-recently-used buffer or grows by `NPB` buffers up to `afs_max_buffers`, writes any dirty victim to its stored inode, zeros the page, fills the new header, and rehashes it. `DNew` bypasses disk read and updates `chunkBytes` while the caller still holds the dcache lock, avoiding later lock-order inversions.

State and persistence: Volatile globals include `Buffers`, page backing allocations, `phTable`, `nbuffers`, `timecounter`, and `afs_bufferLock`. Dirty pages persist only when written through `afs_CFileWrite` during eviction or flush. Buffer metadata stores the dcache index and a copied `afs_dcache_id_t` inode so dirty writeback can happen without mapping back through dcache tables.

Dependencies and integration points: Depends on `afs_chunkops.h` cache-file operations, dcache metadata, directory package `DirBuffer`, OpenAFS locking, stats, and OS allocation. It is called from directory manipulation paths and shutdown.

Risks: Lock ordering is central: the code documents `afs_bufferLock -> buffer.lock` and deliberately avoids taking dcache locks during flushes. Bugs can cause deadlocks or dirty directory loss. `DZap` relies on `pHash` internals and scans only page hash variants. Physical I/O errors are collapsed to `EIO` unless callers use `DReadWithErrno`. Timecounter wrap temporarily degrades replacement behavior.

Test signals: Read cache hit/miss, short read and physical-error reporting, dirty release then global and per-dcache flush, eviction of dirty victims, all-buffers-locked growth/failure, `DNew` extending `chunkBytes`, zapping all pages for one dcache, shutdown after multiple growth allocations, and lock-order stress with concurrent directory operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_bypasscache.c -->
## sources/distributed-fs/openafs/src/afs/afs_bypasscache.c

Purpose: Implements optional cache-bypass reads, where file data is fetched directly into VM/user pages instead of being stored in the AFS disk cache. It also handles transitions between cached and bypass states for a vnode.

Important APIs and functions: `afs_alloc_ncr`/`afs_free_ncr` manage `nocache_read_request` packets. `afs_TransitionToBypass` flushes/stales a vnode and marks `FCSBypass`. `afs_TransitionToCaching` clears bypass mode and discards transient pages/cache hints. `afs_ReadNoCache` verifies the vnode and queues a `BOP_FETCH_NOCACHE` background request. `afs_PrefetchNoCache` performs the FetchData RPC. `afs_NoCacheFetchProc` consumes RX data and copies it into page iovecs, releasing pages as they are filled.

Control flow: Transition-to-bypass takes the GLOCK and vnode write lock, optionally stores dirty segments for writers, stales cache status, smushes cache chunks, frees link data, and sets desired/manual state bits. Read dispatch creates a request, verifies vcache status, and retries background queue insertion with short waits. The prefetch worker obtains an AFS connection, starts 64-bit FetchData when supported with fallback to 32-bit, reads the streaming length/data protocol, copies RX iovecs into page mappings, ends the call, runs `afs_Analyze` for retryable failures, and finally applies returned status with `afs_ProcessFS`.

State and persistence: Global policy is `cache_bypass_strategy`, `cache_bypass_threshold`, and `cache_bypass_prefetch`. Per-vcache state uses `cachingStates`, `cachingTransitions`, callback/server pointer, dirty state, and link-data ownership. Bypass reads intentionally avoid populating persistent disk cache chunks; only metadata/status updates remain.

Dependencies and integration points: Compiled under `AFS_CACHE_BYPASS` or `UKERNEL`. Depends on RX, FetchData stubs, background queueing, vnode/cache invalidation, Linux page locking and kmap APIs, `afs_Analyze`, `afs_conn.c`, and `afs_bypasscache.h` policy macros.

Risks: Page lifetime handling is high risk: every error path must unlock and drop page refs exactly once. The copy loop tracks RX iovec and page offsets manually and assumes page/iovec lengths line up with the requested length. Transition paths take the GLOCK internally and can conflict with callers that already hold locks incorrectly. 64-bit fallback and foreign multi-block fetch handling need server-compatibility coverage.

Test signals: Allocate/free requests with zero and many pages, transition both directions with dirty writers and symlink link data, queue saturation returning `EBUSY`, 64-bit and 32-bit FetchData, short RX read, oversized length rejection, foreign multi-block reads, page release on every error path, and status update after successful bypass fetch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_bypasscache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_bypasscache.h -->
## sources/distributed-fs/openafs/src/afs/afs_bypasscache.h

Purpose: Declares the cache-bypass read interface, bypass policy knobs, request carrier structure, and macros used by read paths to toggle bypass mode.

Important APIs and types: `struct nocache_read_request` carries platform-specific direct-read parameters. `enum cache_bypass_strategies` defines always, never, and large-file bypass modes. Exports `cache_bypass_prefetch`, `cache_bypass_strategy`, `cache_bypass_threshold`, allocation/free helpers, transition helpers, `afs_ReadNoCache`, and `afs_PrefetchNoCache`. `variable_cache_strategy` and `trydo_cache_transition` are policy macros for automatic vnode state transitions.

Control flow: The header is active only when `AFS_CACHE_BYPASS` or `UKERNEL` is defined. `trydo_cache_transition` checks whether the strategy is variable, compares the desired bypass flag with `avc->cachingStates`, and calls the appropriate transition routine.

State and persistence: Declares global policy variables and per-vnode state-bit interactions; no durable state is stored directly.

Dependencies and integration points: Pulls in AFS kernel headers, `struct vcache`, credentials, `struct uio`, and platform page-size definitions. It is consumed by fetch/read paths and the background daemon handling no-cache prefetch.

Risks: Macro policy code evaluates vnode state without taking a lock, relying on transition routines to re-check under lock. Platform-specific fields make incorrect structure use easy outside the intended OS branches. `AFS_CACHE_BYPASS_DISABLED` uses `-1` in a size-typed threshold, so comparisons must account for signed/unsigned behavior at callers.

Test signals: Compile with bypass disabled, enabled, and UKERNEL; verify policy transitions for all strategies; validate threshold-disabled behavior; and exercise macro use against vnodes already in the requested state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_bypasscache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_call.c -->
## sources/distributed-fs/openafs/src/afs/afs_call.c

Purpose: Implements the kernel-side AFS syscall/operation dispatcher and daemon lifecycle control. It is the main bridge from `afsd` startup/configuration calls into cache-manager initialization, daemon thread startup, runtime knobs, AFSDB handling, and shutdown.

Important APIs and functions: `afs_syscall_call`/`afs_syscall64_call` dispatch `AFSOP_*` operations. `afs_InitSetup` initializes stats, RX, and resources. Platform-specific `afs_DaemonOp` and `afsd_thread` variants start callback, main AFS, background, truncate, check-server, rxevent, and listener daemons. Optional sockproxy helpers copy packet lists between user space and kernel space. `afs_CheckInit` reports startup readiness, `afs_shutdown` coordinates teardown, and `shutdown_afstest` resets startup flags.

Control flow: Startup is staged by `afs_initState`: RX/resource setup happens before basic cache init; `AFSOP_BASIC_INIT`, cache files, volume/cell info, root volume, and `AFSOP_GO` complete cache-manager readiness. Daemon operations either run in the calling process or spawn kernel threads depending on platform macros. The syscall dispatcher first enforces privileged access except MTU/mask queries, then branches through configuration operations such as add cell, set primary cell, cache init, interface advice, dynroot/fakestat settings, RX packet/MTU/fragment tuning, entropy seeding, volume TTL, and sockproxy handling.

State and persistence: Maintains global startup/shutdown flags (`afs_initState`, `afs_termState`, `afs_cold_shutdown`, `afs_shuttingdown`), daemon-running booleans, cache sizing globals, root volume name, RX bind host, callback interface addresses, and runtime tunables. It initializes persistent cache metadata indirectly through cache, volume, and cell-info init calls, but does not itself own those file formats.

Dependencies and integration points: Integrates almost every cache-manager subsystem: RX, resources, daemons, background queue, callback server, cache init, dynroot, cells, AFSDB, vnode/dcache packages, NFS exporter, ICL logs, OS networking, platform syscall copyin/copyout, and shutdown hooks for all packages.

Risks: This file is heavily platform-conditional and uses user-kernel copy boundaries, so size checks and pointer handling are critical. Startup order is encoded in numeric state transitions and sleeps; missed wakeups or duplicate starts can hang initialization. Shutdown depends on daemon cooperation and correct `afs_termState` progression. Many branches allocate temporary buffers and must free them on all copy/error paths.

Test signals: Exercise full `afsd` startup sequence, duplicate daemon starts, cache initialization idempotence, add-cell/add-cell2/alias/set-thiscell, interface refresh and RX bind behavior, root-volume and cache-file setup, privileged access rejection, MTU/mask queries for unprivileged users, AFSDB handler shutdown code, runtime knob validation, sockproxy copy bounds, cold and warm shutdown ordering, and post-shutdown reinitialization flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_call.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_callback.c -->
## sources/distributed-fs/openafs/src/afs/afs_callback.c

Purpose: Implements the RX callback service exported by the cache manager to fileservers and debugging clients. It breaks callbacks, reports cache/lock/server/cell state, returns xstats and cache configuration, and identifies the client to servers.

Important APIs and functions: Debug RPCs include `SRXAFSCB_GetCE`, `SRXAFSCB_GetCE64`, and `SRXAFSCB_GetLock`. Callback RPCs include `SRXAFSCB_CallBack`, `SRXAFSCB_Probe`, `SRXAFSCB_InitCallBackState`, `SRXAFSCB_InitCallBackState3`, and `SRXAFSCB_ProbeUuid`. Information RPCs include `SRXAFSCB_WhoAreYou`, `SRXAFSCB_TellMeAboutYourself`, `SRXAFSCB_GetServerPrefs`, `SRXAFSCB_GetCellServDB`, `SRXAFSCB_GetLocalCell`, `SRXAFSCB_GetCacheConfig`, and `SRXAFSCB_GetCellByNum`. `ClearCallBack` is the key invalidation helper, and `afs_RXCallBackServer` donates a daemon thread to RX.

Control flow: RPC entry points acquire the AFS GLOCK, gather stats, perform their operation, and release the GLOCK. `SRXAFSCB_CallBack` iterates incoming FIDs and calls `ClearCallBack`, which handles whole-volume callback breaks when vnode is zero or single-FID breaks otherwise. It scans vcache hash chains, clears callback pointers/hints, waits around initializing/dead vnodes, takes vnode references, stales cache flags, and resets volume info for volume breaks. Init-callback-state finds the calling server, stales every vcache callback from it, clears capability knowledge, resets affected volumes, and purges the DNLC.

State and persistence: Updates volatile counters (`afs_allCBs`, odd/even callback/zap counts, `afs_connectBacks`), callback pointers and expiration state in vcaches, server capability flags, volume info, DNLC entries, and interface identity in `afs_cb_interface`. Returned RPC buffers are allocated for the RX stub to free. No durable state is written.

Dependencies and integration points: Depends on generated callback RPC interfaces, RX call/peer APIs, vcache and volume hash tables, server lookup, cell management, interface-address tracking, cache init parameters, stats/xstats, lock tables, and platform vnode reference APIs.

Risks: Hash-chain scans deliberately drop and reacquire locks around vnode refs, so iterator restart logic must remain correct. Debug RPCs expose pointer-derived addresses and lock internals. Several callbacks allocate output buffers while holding global state. `InitCallBackState3` currently delegates to address-based lookup instead of UUID lookup, leaving multi-homed/server-identity ambiguity.

Test signals: Break one file callback, whole-volume callback, callback for initializing/dead vnodes, init callback state from a known and unknown server, probe UUID match/mismatch, xstats collections, cache-config marshalling, server preference enumeration, cell DB/local cell/cell-by-number results, callback server startup wait for `afs_server`, and shutdown counter reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_cbqueue.c -->
## sources/distributed-fs/openafs/src/afs/afs_cbqueue.c

Purpose: Actively manages callback expiration so most cache-manager paths can test callback validity through vnode state bits instead of recomputing expiration times.

Important APIs and functions: `afs_QueueCallback` inserts a vcache into the expiration wheel. `afs_DequeueCallback` removes it. `afs_CheckCallbacks` scans the current bucket for callbacks expiring soon, invalidates or requeues them, and handles RO volume callback expiration. `afs_FlushCBs` drops all callbacks, `afs_FlushServerCBs` drops callbacks for one server, `afs_InitCBQueue` initializes the wheel, and `afs_BumpBase` advances the base bucket as time passes.

Control flow: The wheel has `CBHTSIZE` buckets of `CBHTSLOTLEN` seconds. Queueing offsets the server-provided time by `base` and leaves already queued vcaches in place. Periodic checking scans the base bucket backward under `afs_xcbhash`, compares `cbExpires` with `now + secs`, stales vcaches whose callbacks are about to expire, preserves RO callbacks when the volume callback is still valid, and rehashes entries renewed into a later slot. `BumpBase` advances `base` and concatenates old bucket contents into the new base for continued checking.

State and persistence: Volatile globals are `base`, `basetime`, `cbHashT`, debug pointer `debugvc`, and lock `afs_xcbhash`. Vcache `callsort`, `cbExpires`, callback flags, `dchint`, and volume `expireTime` are the operational state. Nothing is persisted.

Dependencies and integration points: Uses AFS queue macros, vcache/volume state, server down flags, DNLC invalidation flags, stats, and daemon periodic scheduling. It is tightly coupled with callback break handling in `afs_callback.c` and callback assignment in fetch/status paths.

Risks: The code intentionally does not lock each vcache during expiration checks to avoid deadlocks, relying on documented races with `QueueCallback`. Corrupted queues can loop; `CBQ_LIMIT` detects this and flushes all callbacks. Time-wheel assumptions depend on server callback slop and daemon scheduling frequency.

Test signals: Queue/dequeue idempotence, renewed callback rehashing, soon-expiring RW invalidation, RO volume callback preservation, server-down RO behavior, base bump across multiple slots, full flush, per-server flush, corrupted-loop safety counter, and concurrent queue/check stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_cbqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_cbqueue.h -->
## sources/distributed-fs/openafs/src/afs/afs_cbqueue.h

Purpose: Defines the callback-expiration wheel geometry and the queue-entry-to-vcache conversion macro used by `afs_cbqueue.c`.

Important APIs and definitions: `CBHTSLOTLEN` is 128 seconds, `CBHTSIZE` is 128 slots, `CBHash(t)` shifts seconds into slots, and `CBQTOV(e)` computes the containing `struct vcache` from its embedded `callsort` queue entry.

Control flow: No runtime logic exists here; the macros shape the bucket selection and object recovery behavior in queue operations.

State and persistence: No state or persistence. The values define the granularity and range of volatile callback queue state.

Dependencies and integration points: Requires `struct vcache` to contain a `callsort` field matching the pointer arithmetic in `CBQTOV`. Included by callback queue management.

Risks: `CBQTOV` is manual container-of pointer arithmetic and will break if `struct vcache` layout or `callsort` type changes without updating the macro. The slot length is encoded as a shift in `CBHash`, so changing `CBHTSLOTLEN` requires updating the shift assumption.

Test signals: Compile/layout tests for `CBQTOV`, bucket mapping around 127/128/129 seconds, and queue behavior after any callback-wheel constant changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_cbqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_cell.c -->
## sources/distributed-fs/openafs/src/afs/afs_cell.c

Purpose: Manages AFS cell configuration inside the cache manager: AFSDB lookup coordination, persistent cell-name-to-number mapping, aliases, cell LRU lookup, primary-cell state, cell creation/update, and shutdown cleanup.

Important APIs and functions: AFSDB functions are `afs_StopAFSDB`, `afs_AFSDBHandler`, `afs_GetCellHostsAFSDB`, and `afs_LookupAFSDB`. Cell-name persistence uses `afs_cellname_init`, `afs_cellname_write`, and helper lookups. Alias APIs include `afs_GetCellAlias`, `afs_NewCellAlias`, and `afs_CellOrAliasExists`. Cell lookup and lifecycle APIs include `afs_CellInit`, `afs_NewCell`, `afs_GetCellByName`, `afs_GetCell`, `afs_GetCellStale`, `afs_GetCellByIndex`, `afs_GetCellByHandle`, `afs_GetPrimaryCell`, `afs_SetPrimaryCell`, `afs_RemoveCellEntry`, `afs_CellNumValid`, and `shutdown_cell`.

Control flow: AFSDB lookup serializes one kernel request to a user-space handler using `afsdb_client_lock`, `afsdb_req_lock`, `pending`, and `complete`. Cell-name initialization reads records from a cache inode using a magic, cell number, name length, and name bytes; writes persist only used cell names after full initialization. `afs_NewCell` either updates an existing cell or allocates a new one, computes an MD5 cell handle, validates linked-cell requests, marks old VL servers gone, installs new server hosts, sorts them, assigns a stable cell number/index, and invalidates dynroot unless hushed.

State and persistence: Volatile state includes `CellLRU`, `afs_xcell`, `afs_thiscell`, cell objects, aliases, AFSDB request state, and cell indices. Durable state is the optional cell-name mapping file identified by `afs_cellname_inode`; only referenced/used cell names are rewritten. Static non-AFSDB cell entries are protected from being overwritten by later AFSDB timeouts unless they had no servers.

Dependencies and integration points: Integrates with server creation/sorting, dynroot invalidation, cache-file I/O, MD5 handles, AFSDB userspace upcall via `afs_call.c`, volume/VL server selection, callback debug RPCs, and primary-cell hard-mount logic in `afs_analyze.c`.

Risks: AFSDB coordination depends on wakeups and shutdown state; missed transitions can strand lookups. Persistent cell-name parsing stops silently on malformed or duplicate records. `afs_NewCell` mutates existing server host flags and linked-cell backpointers under nested locks. Some getters update LRU/ref-used state but do not visibly refcount cell objects beyond lock protocol, so callers must follow `afs_PutCell` conventions.

Test signals: Initialize with memcache and disk cache, parse/write valid and malformed cell-name files, AFSDB success/failure/alias creation/shutdown, static cell protected from AFSDB overwrite, new and updated cell host lists, linked-cell validation, alias duplicate rejection, primary-cell set/get, lookup by name/id/index/handle, dynroot invalidation, remove server entry, and shutdown memory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_cell.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_chunk.c -->
## sources/distributed-fs/openafs/src/afs/afs_chunk.c

Purpose: Owns the global default chunk-size variables for the cache manager.

Important APIs and variables: Defines `afs_FirstCSize`, `afs_OtherCSize`, and `afs_LogChunk`, initialized to `AFS_DEFAULTCSIZE` and `AFS_DEFAULTLSIZE` from `afs_chunkops.h`.

Control flow: No functions are implemented. Startup code or configuration macros such as `AFS_SETCHUNKSIZE` mutate these globals before cache operations rely on chunk geometry.

State and persistence: The variables are process/kernel-memory configuration state. They are reflected in cache behavior and callback cache-config reporting, but this file does not persist them directly.

Dependencies and integration points: Included with AFS base headers, stats, and `afs_chunkops.h` definitions. Used by dcache indexing, file fetch/store chunk math, and cache initialization.

Risks: If the chunk-size globals are changed after cache data structures are initialized, offset-to-chunk calculations can become inconsistent with existing cache entries. The comments explicitly expect setup before use.

Test signals: Verify defaults, configured chunk sizes through `AFS_SETCHUNKSIZE`, cache-config reporting, and offset/chunk conversion consistency before and after startup configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_chunk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_chunkops.h -->
## sources/distributed-fs/openafs/src/afs/afs_chunkops.h

Purpose: Defines chunk geometry macros and the cache-backend operation vector used to abstract disk, memory, and platform-specific cache storage.

Important APIs and types: Chunk macros include `AFS_CHUNKOFFSET`, `AFS_CHUNK`, `AFS_CHUNKBASE`, `AFS_CHUNKSIZE`, `AFS_CHUNKTOBASE`, `AFS_CHUNKTOSIZE`, and `AFS_SETCHUNKSIZE`. `dslot_state` distinguishes new, unused, and valid dcache slot requests. `struct afs_cacheOps` contains backend callbacks for open/truncate/read/write/close, UIO read/write, dcache slot lookup, volume slot lookup, and link handling. Wrapper macros dispatch through global `afs_cacheType`. Inline helpers copy/reset inode ids and convert an inode id to a trace integer.

Control flow: Runtime behavior is macro-dispatched. Chunk mapping treats chunk zero specially with `afs_FirstCSize`; later chunks use power-of-two `afs_OtherCSize` and `afs_LogChunk`.

State and persistence: The header reads global chunk-size variables and global cache-backend pointer state. It does not persist data itself, but all cache-file I/O and dcache slot retrieval flow through this contract.

Dependencies and integration points: Core dependency for buffer, dcache, memcache, UFS cache, fetch/store, and volume-cache code. Cache backend implementations must fill every function pointer consistently.

Risks: Macros assume chunk sizes are powers of two; invalid values break bitmask and shift calculations. Function-pointer wrappers provide no null checks for `afs_cacheType` or operations. `afs_inode2trace` returns `i->mem`, which is explicitly a tracing hack and may not identify all backend inode forms.

Test signals: Offset-to-chunk boundary tests around first chunk and later chunk boundaries, large-offset tests, configured chunk sizes, every cache backend operation through the wrapper macros, dslot state behavior, and inode copy/reset for each platform inode representation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_chunkops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_conn.c -->
## sources/distributed-fs/openafs/src/afs/afs_conn.c

Purpose: Manages RX client connections from the cache manager to fileservers and VL servers. It selects server addresses, pools connections per server-address/user/port, chooses security objects, handles token changes, and releases/destroys connection vectors.

Important APIs and functions: `afs_Conn` selects a fileserver for a FID's volume. `afs_ConnBySA`, `afs_ConnByHost`, and `afs_ConnByMHosts` create or reuse connections by address, host, or host array. `afs_PutConn` releases a selected connection and RX reference. `afs_ReleaseConns`, `afs_ReleaseConnsUser`, and `ForceNewConnections` tear down or force recreation. Internals include `find_preferred_connection`, `release_conns_user_server`, `release_conns_vector`, and `afs_pickSecurityObject`.

Control flow: `afs_Conn` obtains the volume, chooses the best non-down server address by volume status and server rank while respecting request skip lists, obtains the calling user, and delegates to `afs_ConnBySA`. `afs_ConnBySA` searches existing vectors under `afs_xconn`, creates a vector if allowed, selects a low-utilization slot, handles bad-token downgrade to unauthenticated connections, recreates RX connections when `forceConnectFS` is set, sets hard/idle dead times, configures NAT ping on one filesystem connection, and returns an extra RX ref. `afs_PutConn` decrements both connection and vector refs and drops the RX ref.

State and persistence: Volatile state includes `srvAddr->conns`, `sa_conn_vector` lists, per-slot `afs_conn` refs and RX ids, NAT ping owner, `forceConnectFS`, user token states, `cryptall`, `VNOSERVERS`, and locks `afs_xconn`/`afs_xinterface`. No durable state is stored.

Dependencies and integration points: Integrates with volume/server/cell selection, user/token management, RX and rxkad security classes, server activation/down logic, request retry analysis, replicated volume handling, and NAT keepalive behavior. `afs_Analyze` calls `afs_PutConn` and `ForceNewConnections`.

Risks: Reference-count correctness is critical; imbalance panics in `afs_PutConn`, while vector release skips referenced vectors. Security-object choice mutates `user->viceId` and token-bad handling clears `UHasTokens`. The service-number selection for VL versus fileserver is a historical port comparison. GLOCK drops around RX operations require careful caller context.

Test signals: Connection reuse under `RX_MAXCALLS`, vector creation per user/port/replication flag, server selection with down/busy/offline/skipped hosts, authenticated and unauthenticated security object creation, token expiry forcing new null connections, NAT ping reassignment after destruction, VL hard-dead-time configuration, release while refs are live, user connection release, and `ForceNewConnections` recreation on next use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_consts.h -->
## sources/distributed-fs/openafs/src/afs/afs_consts.h

Purpose: Provides small shared cache-manager constants for host-list and pioctl sizing.

Important APIs and definitions: `AFS_MAXHOSTS` is the maximum hosts per volume, `AFS_OMAXHOSTS` preserves the old eight-host compatibility value, `AFS_MAXCELLHOSTS` is the maximum VLDB servers per cell, and `AFS_PIOCTL_MAXSIZE` caps returned pioctl data.

Control flow: No runtime logic. These constants constrain array sizes and loops throughout volume, cell, connection, analyze, and pioctl code.

State and persistence: No state or persistence.

Dependencies and integration points: Used by cell host arrays, volume server host/status arrays, request skip/error arrays, callback/cell RPC reporting, and pioctl buffer sizing.

Risks: Changing these values is ABI- and structure-sensitive. Arrays in persisted or RPC-facing structures may still assume old limits, especially where `AFS_OMAXHOSTS`, `AFS_MAXHOSTS`, and `AFS_MAXCELLHOSTS` differ.

Test signals: Compile-time structure-size checks, loops over max host counts, compatibility with old VLDB/volume entries, pioctl maximum return tests, and boundary cases for exactly max hosts/cell hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_consts.h -->
