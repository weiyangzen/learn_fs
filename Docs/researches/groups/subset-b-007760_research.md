# Research: subset-b-007760

This grouped report covers the OpenAFS Cache Manager sources requested for `subset-b-007760`. Each file section is wrapped with the required reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_server.c -->
# sources/distributed-fs/openafs/src/afs/afs_server.c

## Purpose

`afs_server.c` owns Cache Manager server and server-address records: liveness state, multihomed address lists, address preference ranking, connection refresh, and server-related performance counters. The file maintains the global server hash table `afs_servers[NSERVERS]`, the server-address hash table `afs_srvAddrs[NSERVERS]`, and allocation/debug counters such as `afs_totalServers` and `afs_totalSrvAddrs`. It is a core integration layer between VLDB/file-server discovery, Rx connections, callback state, volume/cache invalidation, and `afs_stats_cmperf` server up/down accounting.

## Important APIs, Types, and Functions

Important exported routines include `afs_MarkServerUpOrDown`, `afs_ServerDown`, `afs_CountServers`, `ForceAllNewConnections`, `afs_CheckServers`, `afs_LoopServers`, `afs_FindServer`, `afs_random`, `afs_randomMod15`, `afs_randomMod127`, `afs_SortOneServer`, `afs_SortServers`, `afsi_SetServerIPRank`, `afs_GetCapabilities`, `afs_GetServer`, `afs_ActivateServer`, `afs_RemoveAllConns`, and `afs_MarkAllServersUp`. The main data structures come from `afsincludes.h`: `struct server`, `struct srvAddr`, `struct cell`, `struct afs_conn`, `struct unixuser`, `struct volume`, and callback/cache structures. `GetUpDownStats` selects the correct `afs_stats_cmperf.fs_UpDown` or `vl_UpDown` bucket, split by same-cell versus different-cell and by file-server versus VL-server port.

## Control Flow and State

Server-down handling starts in `afs_ServerDown`, which short-circuits if either the logical server or address is already down, calls `afs_MarkServerUpOrDown`, and logs file-server or VL-server loss through `print_internet_address`. `afs_MarkServerUpOrDown` updates `SRVADDR_ISDOWN` on a specific address and `SRVR_ISDOWN` only when all addresses of a multihomed server are down; on recovery, any up address marks the server up, but aggregate uptime stats are updated only when all addresses share the same state. It records downtime start/end, incident counts, duration buckets, and never-down counts.

Periodic probing flows through `afs_CheckServers`, which delegates to `afs_LoopServers` with `CkSrv_GetCaps`. `afs_LoopServers` snapshots `afs_srvAddrs` under `afs_xserver`/`afs_xsrvAddr`, creates Rx connections for eligible addresses, shortens dead time for down servers, and invokes callback functions over arrays of `afs_conn` and `rx_connection`. VL servers are probed separately by `CheckVLServer` using `VL_ProbeServer`; file servers are checked through `RXAFS_GetCapabilities` in `CkSrv_GetCaps`. `CkSrv_MarkUpDown` converts RPC results into server-up/server-down transitions and wakes waiters when needed.

Server lookup and creation are centered on `afs_GetServer`. It first checks existing non-multihomed or UUID/multihomed records under shared locking. If updates are needed, it respects the lock order `afs_xvcb` before `afs_xserver`, obtains `afs_xsrvAddr`, allocates or reuses `struct server` and `struct srvAddr` instances, moves addresses between server records, creates orphan server records for removed multihomed addresses, recomputes address ranks, sorts address lists, updates global stats, optionally fetches capabilities, and returns the canonical server. Address changes trigger `afs_FlushServer`, which resets affected volumes, flushes callbacks, frees callback records, and removes empty server records.

## Dependencies and Integration Points

This file depends on Rx multi-call support (`rx/rx_multi.h`), file-server RPCs (`RXAFS_GetCapabilities`), VLDB RPCs (`VL_ProbeServer`), cell and user lookup (`afs_GetCellStale`, `afs_GetUser`, `afs_PutUser`), connection management (`afs_ConnBySA`, `afs_ConnByHost`, `afs_PutConn`, `ForceNewConnections`), callback/vcache state (`afs_vhashT`, `afs_FlushServerCBs`, `afs_HaveCallBacksFrom`), and volume reset code (`afs_ResetVolumes`). Platform-specific ranking inspects interface tables or user-space interface data, with separate Solaris, Darwin, FreeBSD, OpenBSD, NetBSD, SGI, and generic paths.

## Persistence and Side Effects

No on-disk records are written here directly, but long-lived kernel state is mutated heavily: server/address hash tables, connection vectors, callback records, volume state, address rankings, and performance statistics. Server activation records timestamps and contributes to `afs_stats_cmperf`; server removal frees kernel memory only when address lists are detached. Logs are emitted through `afs_warnall` via `print_internet_address`.

## Risks and Test Signals

The main risks are lock-order regressions, stale server/address aliases during multihomed updates, races between snapshots and connection use, incorrect address ranking on platform-specific network stacks, and stats under/over-counting when partial multihomed outages occur. `afs_GetServer` is especially sensitive because it moves `srvAddr` records, flushes volumes/callbacks, and may call `afs_GetCapabilities` while manipulating locks. Useful tests include simulated VLDB address changes, multihomed partial-failure recovery, server-down/up probes with Rx failures, address ranking with multiple local interfaces, capability fallback on `RXGEN_OPCODE`, and stress tests that run server checks while volume/callback caches are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_server.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_stat.c -->
# sources/distributed-fs/openafs/src/afs/afs_stat.c

## Purpose

`afs_stat.c` defines and initializes the Cache Manager statistics globals. It is the concrete storage for the structures declared in `afs_stats.h`: `afs_cmstats`, `afs_stats_cmperf`, `afs_stats_cmfullperf`, and `afs_stats_XferSumBytes`. Its only function, `afs_InitStats`, prepares call counters, performance counters, timing minima, transfer minima, server bucket metadata, and cache-entry size fields during Cache Manager startup.

## Important APIs, Types, and Functions

The primary API is `afs_InitStats(void)`. It works with `struct afs_CMStats`, `struct afs_stats_CMPerf`, `struct afs_stats_CMFullPerf`, `struct afs_stats_opTimingData`, and `struct afs_stats_xferData`. It also records size information for `struct vcache` and platform vnode structures. On Darwin, `AFS_SIZEOF_VNODE` is pinned to a known vnode zone size because `struct vnode` is opaque to the shipped SDK headers; other platforms use `sizeof(struct vnode)`.

## Control Flow and State

Initialization zeroes the three global stats structures, sets `srvNumBuckets` to `NSERVERS`, initializes every file-server and cache-manager RPC timing `minTime.tv_sec` to `999999`, initializes file-server transfer `minTime.tv_sec` and `minBytes`, and then records cache/stat object size metadata. `stat_entry_size` is `sizeof(struct vcache)` plus `sizeof(struct vnode)` unless the build embeds the vnode in the vcache.

## Dependencies and Integration Points

The file depends on `afsincludes.h` for Cache Manager structures and `afs_stats.h` for stats layouts and constants. Runtime consumers include xstat callbacks, server/user stats code, RPC instrumentation macros, cache accounting, and call-counter macros across the AFS client. The initialization values in this file establish sentinel minima expected by `XSTATS_END_TIME` and transfer-stat update code elsewhere.

## Persistence and Side Effects

All state is in-memory and scoped to the current Cache Manager instance. The values become externally observable through xstat collection interfaces and debugging tools, but there is no direct disk persistence. Reinitializing after live use would destroy counters, so the function is intended to run once at startup.

## Risks and Test Signals

Risks include ABI drift in Darwin vnode sizing, missing initialization for new stats arrays added to `afs_stats.h`, and incorrect minima if new timing/transfer buckets are introduced without updating this loop. Test signals include xstat output immediately after startup, minimum RPC/transfer times remaining sane after first successful operation, and build checks for platforms with opaque vnode definitions or embedded vnode configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_stats.h -->
# sources/distributed-fs/openafs/src/afs/afs_stats.h

## Purpose

`afs_stats.h` defines the Cache Manager statistics ABI and the macros used to collect call counts, RPC timings, transfer sizes, authentication/PAG stats, server uptime stats, access stats, and authorship stats. It is intentionally conservative because `struct afs_CMCallStats` is exported as an unversioned binary blob for xstat clients; the header explicitly warns that fields must only be appended, never removed, reordered, or made conditional.

## Important APIs, Types, and Macros

The most widely used macro is `AFS_STATCNT(name)`, which increments the corresponding `C_name` member in `afs_cmstats.callInfo`. `AFS_CM_CALL_STATS` is the master call-counter list spanning many Cache Manager source files. Timing macros include `XSTATS_DECLS`, `XSTATS_START_TIME`, `XSTATS_START_CMTIME`, and `XSTATS_END_TIME`; helper macros include `afs_stats_TimeLessThan`, `afs_stats_TimeGreaterThan`, `afs_stats_GetDiff`, `afs_stats_AddTo`, `afs_stats_TimeAssign`, and `afs_stats_SquareAddTo`.

Key structures are `afs_CMStats`, `afs_CMCallStats`, `afs_stats_SrvUpDownInfo`, `afs_stats_CMPerf`, `afs_stats_opTimingData`, `afs_stats_xferData`, `afs_stats_RPCErrors`, `afs_stats_RPCOpInfo`, `afs_stats_AuthentInfo`, `afs_stats_AccessInfo`, `afs_stats_AuthorInfo`, `afs_stats_CMFullPerf`, and `afs_CTD_stats`. The header also declares `extern struct afs_CMStats afs_cmstats`, with the concrete definitions supplied by `afs_stat.c`.

## Control Flow and State

The timing macros assume a local variable named `code` indicates operation result. `XSTATS_START_TIME` or `XSTATS_START_CMTIME` picks the relevant timing record and captures `opStartTime`; `XSTATS_END_TIME` captures stop time, increments operation count, and, on success, updates success count, elapsed-time sum, square sum, min, and max. Transfer stats are structured similarly but updated elsewhere. Server stats are divided into file-server and VL-server arrays, each with same-cell and different-cell slots; they record current up/down counts, total records, record ages, downtime incidents, duration buckets, and incident-count buckets.

## Dependencies and Integration Points

The header depends on `afs/param.h` and provides a user/kernel-compatible `osi_timeval32_t` definition outside kernel builds. It is included throughout Cache Manager code for lightweight counters and by xstat-related callback interfaces for binary data layout. `afs_server.c` updates `afs_stats_SrvUpDownInfo`; `afs_user.c` updates `afs_stats_AuthentInfo`; RPC wrappers and callback code use the XSTATS macros; `afs_stat.c` initializes the exported global instances.

## Persistence and ABI Behavior

All data is in-memory for a Cache Manager runtime, but the layout is externally consumed by monitoring clients. The call-counter list is therefore persistent as an ABI contract even when individual functions become unused. Spare fields in `afs_stats_CMPerf` exist for future expansion without breaking consumers.

## Risks and Test Signals

The main risks are ABI breakage from reordering/removing fields, adding conditional members, adding call counters anywhere except the end, or using timing macros without a valid `code` variable. Arithmetic macros use integer timeval math and can overflow if very large durations or sums accumulate. Test signals include xstat client compatibility across kernel/user builds, structure-size checks, RPC timing sanity after success and failure paths, and call-counter changes after representative vnode, pioctl, server, and token operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_syscall.c -->
# sources/distributed-fs/openafs/src/afs/afs_syscall.c

## Purpose

`afs_syscall.c` implements the platform-specific AFS system-call entry layer. It translates user-mode syscall arguments into kernel Cache Manager calls, handles 32-bit compatibility layouts on 64-bit kernels, dispatches AFS syscall numbers such as `AFSCALL_CALL`, `AFSCALL_SETPAG`, `AFSCALL_PIOCTL`, inode-server calls, and `AFSCALL_ICL`, and normalizes platform return conventions. It is primarily glue, but it is security-sensitive because it copies user pointers and bridges user requests into privileged kernel state.

## Important APIs, Types, and Functions

Shared helpers include `copyin_afs_ioctl`, which imports `struct afs_ioctl` or `struct afs_ioctl32`, and `copyin_iparam`, which imports inode-call parameters through `struct iparam` or `struct iparam32`. Conversion helpers `afs_ioctl32_to_afs_ioctl` and `iparam32_to_iparam` preserve pointer values through platform-appropriate casts. Entry points vary by platform: AIX has `syscall`, `lsetpag`, and `lpioctl`; SGI has `Afs_syscall(struct afsargs *, rval_t *)`; Solaris, Darwin, BSD, Linux, UKERNEL, and generic Unix builds each expose `Afs_syscall`, `afs3_syscall`, or `afs_syscall` with local argument structures.

## Control Flow and Dispatch

The generic dispatcher increments `AFS_STATCNT(afs_syscall)` and switches on the syscall number. `AFSCALL_CALL` delegates to `afs_syscall_call` or `afs_syscall64_call`; `AFSCALL_SETPAG` enters `AFS_GLOCK`, calls `afs_setpag`, and releases the lock; `AFSCALL_PIOCTL` similarly calls `afs_syscall_pioctl` with platform credentials and return-value handles; inode operations call `afs_syscall_icreate`, `afs_syscall_iopen`, or `afs_syscall_iincdec`; `AFSCALL_ICL` calls `Afscall_icl` or `Afscall64_icl`. Linux has only five syscall arguments, so `AFSCALL_ICL` and `AFSCALL_CALL` unpack folded parameters from a user array; SPARC64 has additional 32-bit argument cleanup.

## Dependencies and Integration Points

This file integrates with pioctl handling, PAG management, inode file-server support, fstrace/ICL tracing, kernel credential APIs, user-copy macros (`AFS_COPYIN`), Rx globals, and platform process/context helpers. It also includes network interface headers for platform builds that need shared AFS kernel definitions. The code uses `AFS_GLOCK` around Cache Manager operations that require global serialization, while some inode operations run outside it depending on platform conventions.

## Persistence and Side Effects

The file does not own persistent data structures, but every dispatched operation may mutate Cache Manager state: PAG credentials, tokens, pioctl-controlled configuration, inode cache state, or trace buffers. Failed user copies return errors before dispatch. Some platforms store errors in `uerror` or return negative Linux errno values; Darwin may pass negative `AFSCALL_CALL` results back as syscall return values with `code` reset to zero.

## Risks and Test Signals

Risks include pointer truncation in compat paths, incorrect credential passing, missing `AFS_GLOCK` coverage, mismatched platform return semantics, and unsafe user-copy lengths. `copyin_afs_ioctl` and `copyin_iparam` must stay in sync because both encode user pointer compatibility policy. Test signals include 32-bit userland on 64-bit kernels, Linux folded-argument syscalls, pioctl/setpag smoke tests, invalid pointer copyin failures, ICL return-value behavior, and platform-specific syscall registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_sysname.c -->
# sources/distributed-fs/openafs/src/afs/afs_sysname.c

## Purpose

`afs_sysname.c` owns the global `@sys` expansion name list used by the AFS client. It initializes a fixed-size list of system names, defaults the first entry to `SYS_NAME`, exposes generation state through `afs_sysnamegen`, and controls behavior through `afs_atsys_type`, which defaults to `AFS_ATSYS_INTERNAL`.

## Important APIs, Types, and Functions

Global state includes `afs_global_sysnames`, `afs_sysnamegen`, `afs_sysname_lock`, and `afs_atsys_type`. The public lifecycle functions are `afs_sysname_init(void)` and `afs_sysname_shutdown(void)`. Internal helpers `sysnamelist_init` and `sysnamelist_destroy` allocate and free each `MAXSYSNAME` buffer in the `struct afs_sysnames` array, set `namecount`, and clear the structure on teardown.

## Control Flow and State

Initialization is guarded by a static `init_done`. On first call, the file initializes `afs_sysname_lock`, allocates `MAXNUMSYSNAMES` name buffers in a static `global_sysnames` object, copies `SYS_NAME` into slot zero with `strlcpy`, sets `namecount` to one, assigns `afs_global_sysnames`, increments `afs_sysnamegen`, and returns success. If allocation or default-copy fails, it calls `afs_sysname_shutdown` to clean partial state. Shutdown frees all allocated name buffers, zeros the list, clears the global pointer, and destroys the mutex.

## Dependencies and Integration Points

Consumers of `@sys` path expansion and pioctl sysname setters/readers use `afs_global_sysnames` and `afs_sysnamegen`. The file documents an important lock order: hold `afs_sysname_lock` when reading or writing the sysname list, and acquire `afs_sysname_lock` before `GLOCK` if both are required. The mutex is deliberately not an `afs_rwlock_t`, so it can be used outside `GLOCK`.

## Persistence and Side Effects

The sysname list is memory-resident kernel state. It survives for the Cache Manager runtime and can be changed by other sysname-management code, but this file only creates the default list and destroys it at shutdown. The generation counter lets consumers detect list updates.

## Risks and Test Signals

Risks include use after shutdown if consumers do not check `afs_global_sysnames`, allocation leaks on partial initialization, lock-order inversions with `GLOCK`, and truncation failures if `SYS_NAME` exceeds `MAXSYSNAME`. Test signals include startup default sysname, repeated `afs_sysname_init` idempotence, clean shutdown under leak checking, and pioctl/sysname expansion behavior after list updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_sysname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_tokens.c -->
# sources/distributed-fs/openafs/src/afs/afs_tokens.c

## Purpose

`afs_tokens.c` implements the in-kernel token jar abstraction used to store, query, serialize, and securely free authentication tokens. It currently supports rxkad (`RX_SECIDX_KAD`) tokens and bridges between internal token storage and new-style pioctl token structures encoded with XDR.

## Important APIs, Types, and Functions

Core APIs include `afs_FindToken`, `afs_FreeTokens`, `afs_AddToken`, `afs_DiscardExpiredTokens`, `afs_HasUsableTokens`, `afs_HasValidTokens`, `afs_AddRxkadToken`, `afs_AddTokenFromPioctl`, `afs_ExtractTokensForPioctl`, `afs_free_ktc_tokenUnion`, and `afs_free_ktc_setTokenData`. Important internal helpers are `afs_FreeFirstToken`, `afs_IsTokenExpired`, `afs_IsTokenUsable`, `countValidTokens`, `afs_AddRxkadTokenFromPioctl`, `rxkad_extractTokenForPioctl`, and `extractPioctlToken`. Data structures include `struct tokenJar`, `union tokenUnion`, `struct rxkadToken`, `struct ClearToken`, `struct ktc_tokenUnion`, `struct ktc_setTokenData`, and `struct token_opaque`.

## Control Flow and State

Tokens are stored as a singly linked list. `afs_AddToken` allocates a zeroed jar node, sets its security type, pushes it onto the front, and returns the union payload. `afs_AddRxkadToken` allocates and copies the opaque rxkad ticket and copies the clear token. Lookups scan by security index and return the first matching token. Expiration is type-specific: rxkad tokens are expired when `EndTimestamp < now - NOTOKTIMEOUT`; unknown token types are considered non-expired but unusable. `afs_DiscardExpiredTokens` walks with a pointer-to-pointer so it can unlink and securely free expired nodes in place.

Pioctl import converts `struct ktc_tokenUnion` rxkad fields into a `ClearToken` and ticket copy. Export first counts valid tokens, allocates an XDR token array, converts each internal token to a pioctl token, computes its encoded length with `xdrlen_create`, allocates the opaque buffer, and XDR-encodes into it. Secure free wrappers zero keys, tickets, opaque encoded buffers, and top-level structures before delegating to XDR free routines.

## Dependencies and Integration Points

This file depends on `token.h`, XDR helpers, kernel allocation wrappers (`afs_osi_Alloc`, `osi_Alloc`, `xdr_alloc`), and rxkad token definitions. `afs_user.c` calls token functions to garbage collect expired credentials, determine whether users have usable tokens, free user token jars, and reset access state. Pioctl handlers call the import/export helpers for SetTokens/GetTokens style operations.

## Persistence and Side Effects

Token state is in-memory per user/PAG record. Ticket buffers and keys are sensitive; the file attempts to zero them before freeing, though comments acknowledge compilers may optimize dead stores. Adding tokens changes authentication behavior for future Rx connections; discarding/freeing tokens may cause user records and access caches to be treated as unauthenticated.

## Risks and Test Signals

Risks include incomplete secure clearing, XDR allocation/free mismatches, token count/export races if callers do not hold user locks, treating unknown token types as valid but unusable, and error cleanup leaks in partial export failure paths. Test signals include rxkad import/export round trips, expired-token discard, multiple-token jar ordering, unsupported token type rejection on import, allocation-failure cleanup in XDR export, and verification that user GC drops records once no usable tokens remain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_tokens.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_user.c -->
# sources/distributed-fs/openafs/src/afs/afs_user.c

## Purpose

`afs_user.c` manages Cache Manager `unixuser` records keyed by uid/PAG and cell. It owns the `afs_users[NUSERS]` hash table, reference counting, per-user locking, token garbage collection, access-cache invalidation, connection reset after token changes, PAG statistics, primary-user selection, and optional PAG garbage collection by walking the process table.

## Important APIs, Types, and Functions

Global state includes `afs_xuser` and `afs_users`. Core APIs are `afs_GCUserData`, `afs_FindUser`, `afs_GetUser`, `afs_LockUser`, `afs_PutUser`, `afs_ComputePAGStats`, `afs_SetPrimary`, `afs_NotifyUser`, and `afs_MarkUserExpired`. When `AFS_PAG_MANAGER` is not defined, the file also provides `afs_CheckTokenCache`, `afs_ResetAccessCache`, and `afs_ResetUserConns`. With `AFS_GCPAGS`, it adds `afs_GCPAGs_perproc_func` and `afs_GCPAGs`. Important state flags include `UHasTokens`, `UTokensBad`, `UNeedsReset`, `UPAGCounted`, `UPrimary`, and `TMP_UPAGNotReferenced`.

## Control Flow and State

`afs_GetUser` hashes by uid, keeps each bucket sorted by uid, reuses an existing record when uid and cell match, fills in a previously unknown cell when appropriate, or allocates a new zeroed `unixuser` with an initialized lock, `UNDEFVID`, `refCount = 1`, and current `tokenTime`. Remote/exported users propagate exporter references when creating additional cell-specific records. `afs_FindUser` is a lookup-only path that increments `refCount` and returns the user with the requested lock. `afs_PutUser` releases the requested lock and decrements `refCount`.

`afs_GCUserData` obtains locks in the documented order, scans all users, discards expired tokens, and deletes unreferenced records when no usable token remains or unauthenticated timeout has elapsed. Deletion releases user connections, frees tokens, releases exporter references, and frees the record. `afs_CheckTokenCache` marks users whose tokens have become unusable as `UTokensBad | UNeedsReset`, scans vcaches to remove matching access-cache entries, frees removed access entries, and clears reset flags. `afs_ResetUserConns` marks every connection vector for the user with `forceConnectFS` so future RPCs use new tokens, then resets access-cache entries for that uid/cell.

`afs_ComputePAGStats` walks user buckets to calculate current PAG count, record count, authenticated/unauthenticated record count, max records per PAG, longest chain, and high-water marks. It uses `UPAGCounted` as a temporary mark while grouping records with the same uid in a bucket. `afs_SetPrimary` ensures that only one record for a uid has `UPrimary`, while preserving an existing primary until it has unlogged. Optional `afs_GCPAGs` marks all user records as not referenced, asks OS-specific process traversal to clear live PAGs, disables PAG GC if traversal appears broken, and expires unreferenced non-exported records for later removal.

## Dependencies and Integration Points

This file depends on token management from `afs_tokens.c`, connection and server locks (`afs_xsrvAddr`, `afs_xconn`, `afs_ReleaseConnsUser`), vcache/access-cache structures (`afs_vhashT`, `struct axscache`, `afs_FindAxs`, `afs_RemoveAxs`, `afs_FreeAllAxs`), exporter reference hooks, OS credential/PAG helpers, and `afs_stats_cmfullperf.authent`. It is used by connection setup, pioctl token operations, request initialization, server checks, access checks, and background daemons.

## Persistence and Side Effects

User records and token jars are memory-resident but long-lived. Token changes and expiration directly affect authorization, Rx connection reuse, and cached access decisions. GC can free records and connections; access-cache resets remove per-vcache authorization results. Stats high-water marks persist for the process lifetime.

## Risks and Test Signals

Risks include refcount/lock mismatches, access-cache removal while using only read locks due to hierarchy constraints, token-expiration races, sorted-bucket insertion mistakes, and PAG GC expiring all tokens if process traversal fails. The code contains explicit safeguards for traversal failure, but platform credential walkers remain high risk. Test signals include token set/unlog/expiration flows, user lookup by uid/cell including `cell == -1`, connection refresh after token replacement, access-cache invalidation after bad tokens, PAG stats correctness with multiple cells per PAG, exporter user handling, and PAG GC behavior when process traversal returns zero processes or zero credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_util.c -->
# sources/distributed-fs/openafs/src/afs/afs_util.c

## Purpose

`afs_util.c` provides miscellaneous Cache Manager utility routines for numeric/string conversion, portable string helpers, warning output for server addresses, vnode noop/bad operations, pointer-to-int truncation, and AFS inode-number calculation. These helpers are small, but several are widely used by vnode operations, server logging, cache identity generation, and portability layers.

## Important APIs, Types, and Functions

Exports include `afs_cv2string`, `afs_strtoi_r`, `afs_strcasecmp`, `afs_strcat`, `afs_strcpy` on selected OpenBSD builds, `afs_strchr`, `afs_strrchr`, `afs_strdup`, `print_internet_address`, `afs_noop`, `afs_badop`, `afs_data_pointer_to_int32`, and `afs_calc_inum`. Internal helper `afs_calc_inum_md5` optionally generates inode numbers from an MD5 digest when `afs_md5inum` is nonzero. Global `afs_md5inum` controls whether MD5-based inode calculation is attempted.

## Control Flow and State

`afs_cv2string` writes an unsigned decimal string backwards into a caller-provided buffer and returns the start pointer. `afs_strtoi_r` parses only unsigned decimal digits into an `afs_uint32`, stops at the first nondigit, reports overflow-like conditions, and updates `endptr`; it is documented as a portable parser for volume/vnode/uniq values, not a general `strtoul`. The string helper fallbacks are compiled only when platform macros do not provide equivalents.

`print_internet_address` formats a `srvAddr` IPv4 address, server cell, postamble, and error code through `afs_warnall`; for multihomed servers it adds context describing whether all addresses are down or only one interface changed. When logging a down event with an Rx connection, it asks Rx for network error origin/type/code/message and emits a second diagnostic if available. `afs_noop` returns `EINVAL`; `afs_badop` panics for invalid vnode operations.

`afs_data_pointer_to_int32` uses a union and runtime endian check to return the least significant `afs_int32` portion of a pointer without triggering truncation warnings. `afs_calc_inum` first asks `afs_calc_inum_md5` for a nonzero/non-one positive 31-bit inode derived from cell, volume, and vnode; if unavailable, it falls back to `(volume << 16) + vnode` and masks to 31 bits.

## Dependencies and Integration Points

The file depends on AFS kernel includes, `afs_stats.h` counters, Rx network-error reporting, `struct srvAddr`/`struct server`, warning output (`afs_warnall`), and `hcrypto/md5.h`. `print_internet_address` is called by server liveness code in `afs_server.c`. Inode calculation is used by vnode/cache identity code to produce stable-ish inode values for AFS objects exposed to the OS.

## Persistence and Side Effects

Most helpers are stateless. `afs_md5inum` is a runtime knob affecting inode-number generation. `print_internet_address` emits user-visible/kernel-visible warnings. `afs_badop` intentionally terminates via panic. `afs_strdup` allocates memory that callers must free with AFS allocation routines.

## Risks and Test Signals

Risks include buffer misuse by callers of `afs_cv2string`/`afs_strcat`, `afs_strtoi_r` accepting empty strings as zero with `endptr` unchanged, IPv4-only logging assumptions, inode-number collisions in both MD5 and fallback modes, and pointer truncation being intentionally lossy. Test signals include parsing boundary values around `4294967295`, server-down logging with and without Rx network errors, MD5 inode generation avoiding 0 and 1, fallback inode stability, and platform builds where fallback string functions are compiled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_util.h -->
# sources/distributed-fs/openafs/src/afs/afs_util.h

## Purpose

`afs_util.h` is the small public header for `afs_util.c`. In this snapshot it only provides an include guard and the `CVBS` constant, the maximum helper buffer size used for converting an `afs_int32`-sized integer to decimal text.

## Important APIs, Types, and Functions

The only exported symbol is `CVBS`, defined as `12`. The comment explains the sizing assumption: a maximum `afs_int32` decimal representation is around `4 * 10^9`, with space for a NUL terminator and margin. Function prototypes for `afs_util.c` are provided through broader AFS headers, not this file.

## Control Flow, State, and Dependencies

There is no executable control flow or mutable state. The header depends only on conventional preprocessing and can be included wherever the conversion-buffer constant is needed.

## Integration Points, Risks, and Test Signals

`CVBS` is relevant to callers of decimal conversion helpers such as `afs_cv2string`. Risks are limited to callers assuming it is suitable for wider integer types or signed formatting with extra prefixes. Test signals are compile-time: users of `CVBS` should allocate buffers large enough for the numeric type they pass to conversion routines, and future widening of AFS integer formats should revisit this constant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/afs_util.h -->
