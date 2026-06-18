# subset-b-009714 research

Grouped research for NFS-Ganesha idmapper cache, 9P/FSAL interface headers, and shared utility headers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_cache.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_cache.c

## Purpose
`idmapper_cache.c` implements the positive ID-mapping cache used by NFS-Ganesha to remember user-name to UID/GID mappings and group-name to GID mappings. It keeps bidirectional AVL indexes, small direct hash hints for ID lookups, FIFO expiry queues, DBus inspection hooks when enabled, and monitoring updates for hit/miss, entry-count, reaped, and evicted-entry metrics.

## Important APIs, types, and functions
- `struct cache_user` stores a `gsh_buffdesc` user name, UID, optional primary GID, two AVL nodes, a UID-tree membership flag used for GSS principals, an insertion `epoch`, and FIFO queue linkage.
- `struct cache_group` stores a group name, GID, name/GID AVL nodes, FIFO linkage, and insertion epoch.
- Global state is split by entity type: `idmapper_user_lock`, `idmapper_group_lock`, `uname_tree`, `uid_tree`, `gname_tree`, `gid_tree`, `uid_cache[]`, `gid_cache[]`, `user_fifo_queue`, and `group_fifo_queue`.
- Comparators `uname_comparator()`, `uid_comparator()`, `gname_comparator()`, and `gid_comparator()` define AVL order by `gsh_buffdesc`, UID, or GID.
- `idmapper_cache_init()`, `idmapper_cache_reap()`, `idmapper_clear_cache()`, and `idmapper_destroy_cache()` manage lifecycle.
- `idmapper_add_user()` and `idmapper_add_group()` insert or replace mappings, reconcile duplicate entries, enforce configured max counts, and update metrics.
- `idmapper_lookup_by_uname()`, `idmapper_lookup_by_uid()`, `idmapper_lookup_by_gname()`, and `idmapper_lookup_by_gid()` are the read-side lookup surface. ID lookups first consult the direct cache slot, then fall back to AVL lookup.
- DBus methods `cachemgr_show_idmapper_users` and `cachemgr_show_idmapper_groups` expose cache contents under `USE_DBUS`.

## Control flow
Initialization creates two rwlocks, initializes four AVL trees, clears direct ID hint arrays, and initializes FIFO queues. Callers are expected to hold the appropriate user or group rwlock in the mode documented by each public function.

Insertion allocates a single object containing the struct and inline name bytes, records the current time, inserts into the name tree, and handles duplicates by removing stale entries before reinserting. User insertion has special merge behavior: if the same non-expired user/UID appears through different idmapping paths, it can retain a previously known GID or UID reverse mapping. Non-GSS users are also inserted into the UID tree and direct `uid_cache` slot. Group insertion always inserts into both name and GID indexes and updates `gid_cache`.

Lookups under read lock search the relevant tree or direct ID cache. A found but expired entry is returned as a miss, leaving actual removal to the reaper or clear path. Reapers take write locks and remove expired FIFO heads until the first non-expired entry, relying on insertion-order queues and fixed validity windows. Clearing takes both user and group write locks, clears direct caches, drains AVL trees, and logs removed counts.

## State and persistence
All state is in process memory. Entry validity and eviction are driven by `nfs_param.directory_services_param` fields such as user/group time validity and max cache counts. The direct ID arrays are best-effort hints and are rebuilt by name lookup or AVL fallback; they are explicitly atomically accessed under read locks. No state is persisted across restart, and the cache content can be observed over DBus when compiled in.

## Dependencies and integration points
The file depends on Ganesha allocator/logging helpers, `gsh_buffdesc_comparator()`, `avltree`, BSD `TAILQ`, pthread rwlocks, idmapper public declarations, global `nfs_param`, atomic pointer helpers, DBus helpers, and `idmapper_monitoring`. It is called by higher-level idmapping code and complements `idmapper_negative_cache.c` for known misses.

## Risks
- Lookup functions can return false for expired entries while stale entries remain allocated until reap or clear; callers must treat false as "resolve externally" rather than "definitely absent from tree".
- The direct UID/GID cache slots are overwritten by modulo hash and cleared on removal; misuse outside the documented locks would risk stale pointers.
- `idmapper_add_user()` assumes caller-held write lock. Missing that contract can corrupt AVL trees or FIFO queues.
- User duplicate merge behavior is subtle for GSS principal versus plain NFS mappings and can regress reverse lookup behavior if simplified.
- DBus string formatting truncates names to 255 bytes for display, so DBus output is diagnostic, not a lossless export.

## Test signals
- Unit or integration tests should cover add/lookup by both directions, duplicate name/ID replacement, GSS principal mappings without UID-tree insertion, and merging of GID or reverse mapping from an existing non-expired entry.
- Cache expiry tests should verify expired lookups count as misses and later reaper calls remove only FIFO-expired heads.
- Capacity tests should exceed user and group max counts and confirm oldest entries are evicted and metrics update.
- Concurrency tests should exercise read-side direct cache fallback under the documented rwlocks.
- DBus builds should verify user/group cache listing shape and timestamped replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_monitoring.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_monitoring.c

## Purpose
`idmapper_monitoring.c` registers and updates monitoring metrics for idmapping behavior. It tracks user group counts, external resolver latency, cache hit/miss counts, resolution outcomes, cache entry totals, reaped entries, evicted-entry cache duration, and max-groups overflow events.

## Important APIs, types, and functions
- Static metric handle arrays are indexed by `idmapping_op_t`, `idmapping_utility_t`, `idmapping_status_t`, `idmapping_cache_t`, and `idmapping_cache_entity_t`.
- `get_status_name()`, `get_op_name()`, `get_utility_name()`, `get_cache_name()`, and `get_cache_entity_name()` translate enum values into stable metric labels and call `LogFatal()` on unsupported values.
- Registration helpers create one metric per label combination: histograms for user group totals, external latency, and evicted cache duration; counters for cache uses, resolutions, reaped entries, and max-groups exceeded; gauges for total cache entries.
- `idmapper_monitoring__init()` registers every metric and flips `is_inited`.
- Update functions include `idmapper_monitoring__cache_usage()`, `idmapper_monitoring__external_request()`, `idmapper_monitoring__resolution()`, `idmapper_monitoring__user_groups()`, `idmapper_monitoring__evicted_cache_entity()`, `idmapper_monitoring__reaped_cache_entity()`, `idmapper_monitoring__cache_entries_total_set()`, and `idmapper_monitoring__max_groups_exceeded_inc()`.

## Control flow
Startup calls `idmapper_monitoring__init()`, which registers all metric families and all enum-label combinations eagerly. Runtime callers can invoke update APIs before initialization; each public update function checks `is_inited` and returns without touching metric handles if registration has not completed. External latency observations compute a nanosecond difference from start/end times and convert to milliseconds.

## State and persistence
Metric handles and the `is_inited` flag are process-local static state. The monitoring backend owns exported samples after registration and updates. No idmapper data is persisted by this file; it only observes counts, durations, and gauges supplied by callers.

## Dependencies and integration points
The file depends on `idmapper_monitoring.h`, `monitoring.h`, `timespec_diff()`, `NS_PER_MSEC`, and Ganesha logging. Positive and negative cache files call cache-entry, cache-use, reaped, and evicted metrics. Resolver paths call external-request and resolution metrics. Group-list lookup code calls the user-group histogram and max-groups counter.

## Risks
- Every enum value must have a string mapping; adding enum members without updating this file can turn metrics registration or updates into fatal process errors.
- Metric cardinality is fixed by nested loops over enum counts. Incorrect enum count values can register too few or too many handles and later index invalid memory.
- `is_inited` is a plain bool and assumes initialization happens before heavy concurrent updates or that benign lost early samples are acceptable.
- Label values are API-facing monitoring names; changing them can break dashboards and alerts.

## Test signals
- Build tests should catch enum declaration drift with missing switch cases when warnings are strict enough.
- Initialization tests should confirm all metric families register with expected names, units, and labels.
- Runtime tests can call update functions before and after init to confirm pre-init calls are no-ops and post-init calls update the backend.
- Enum-expansion tests should intentionally add a temporary enum value and verify tests fail until a label mapping is provided.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_monitoring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_negative_cache.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_negative_cache.c

## Purpose
`idmapper_negative_cache.c` implements a negative cache for idmapping misses. It stores failed user-name, group-name, and UID resolutions so repeated lookups avoid expensive external resolver calls until a configured timeout expires.

## Important APIs, types, and functions
- `negative_cache_entity_type_t` distinguishes `USERNAME`, `GROUP`, and `UID`.
- `negative_cache_entity_t` stores either a name `gsh_buffdesc` or UID, one AVL node, insertion epoch, FIFO queue linkage, and inline name bytes.
- Separate global locks protect each cache: `idmapper_negative_cache_user_lock`, `idmapper_negative_cache_group_lock`, and `idmapper_negative_cache_uid_lock`.
- Separate AVL trees and FIFO queues back name and UID caches: `uname_tree`, `gname_tree`, `uid_tree`, `negative_user_fifo_queue`, `negative_group_fifo_queue`, and `negative_uid_fifo_queue`.
- `idmapper_negative_cache_init()`, `idmapper_negative_cache_reap()`, `idmapper_negative_cache_clear()`, and `idmapper_negative_cache_destroy()` manage lifecycle.
- Add APIs are `idmapper_negative_cache_add_user_by_uid()`, `idmapper_negative_cache_add_user_by_name()`, and `idmapper_negative_cache_add_group_by_name()`.
- Lookup APIs are `idmapper_negative_cache_lookup_user_by_uid()`, `idmapper_negative_cache_lookup_user_by_name()`, and `idmapper_negative_cache_lookup_group_by_name()`.
- DBus methods expose negative users, groups, and UIDs when `USE_DBUS` is enabled.

## Control flow
Initialization creates three rwlocks, initializes three AVL trees with name or UID comparators, and initializes FIFO queues. Add-by-name allocates a struct plus inline name buffer, selects the proper tree, queue, capacity limit, metric entity, and label text, then AVL-inserts it. Duplicate inserts refresh the old entity timestamp and move it to the FIFO tail. New inserts are appended to the tail, and over-capacity caches evict the FIFO head.

Add-by-UID follows the same pattern using the UID tree. Lookups build a stack prototype and search the relevant AVL tree under the caller-held read lock. A present but expired entity returns false and records a miss; physical removal is deferred to the reaper. Reaping runs for users, groups, and UIDs, taking each write lock and removing expired FIFO heads until the first live entity.

## State and persistence
All state is in memory. Validity and capacity are controlled by `nfs_param.directory_services_param.negative_cache_time_validity`, `negative_cache_users_max_count`, and `negative_cache_groups_max_count`; the UID negative cache currently uses the user max-count parameter. Entry totals, reaped entries, evicted durations, and lookup hits/misses are reported to idmapper monitoring.

## Dependencies and integration points
The file depends on `avltree`, `TAILQ`, pthread rwlocks, `gsh_buffdesc_comparator()`, Ganesha allocation/logging, global directory-service configuration, DBus support, and `idmapper_monitoring`. It is used by higher-level idmapper resolution paths to short-circuit repeated not-found lookups and pairs with the positive cache in `idmapper_cache.c`.

## Risks
- Like the positive cache, expired negative entries can remain in AVL trees until reaped. Callers must use the boolean return, not mere tree presence.
- Add and lookup functions rely on caller-held locks as documented; the file itself does not acquire locks for public add/lookup paths.
- UID negative cache capacity uses the user negative-cache max count, which may be intended but should be validated when changing configuration semantics.
- DBus display takes a write lock while only iterating; this is conservative but can block add/reap operations longer than a read lock would.
- Metric calls for name-cache misses happen only after a tree hit or typed switch path; a missing name node returns false without recording a cache-use miss, unlike UID lookup.

## Test signals
- Tests should cover insert, duplicate refresh and FIFO tail movement, lookup hit, expired lookup miss, and reaper removal for all three entity types.
- Capacity tests should exceed user, group, and UID limits and verify oldest-entry eviction and cached-duration metrics.
- Lock-contract tests or thread sanitizers should exercise concurrent readers with serialized writers.
- DBus builds should validate string/epoch output for users, groups, and UIDs.
- Resolver integration tests should verify repeated failed lookups are suppressed until validity expires.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/idmapper_negative_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/pwnam_wrappers.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/pwnam_wrappers.c

## Purpose
`pwnam_wrappers.c` centralizes passwd/group lookup function selection. It lets NFS-Ganesha use either libc NSS switch APIs or SSSD timeout-aware wrappers behind one stable set of `pwnam_wrappers__*` functions.

## Important APIs, types, and functions
- `getgrouplist_wrapper()` normalizes libc `getgrouplist()` by translating `-1` buffer-too-small returns into `errno = ERANGE`.
- Function pointer globals `getgrouplist_func`, `getpwnam_r_func`, `getpwuid_r_func`, `getgrnam_r_func`, and `getgrgid_r_func` hold the active implementation.
- `pwnam_wrappers__set_implementation()` switches between `PWNAM_IMPLEMENTATION__NSSWITCH` and `PWNAM_IMPLEMENTATION__SSSD`, initializing SSSD before installing SSSD function pointers.
- Thin exported wrappers forward calls to the active function pointers.

## Control flow
The file defaults to NSSwitch/libc implementations at load time. Configuration initialization calls `pwnam_wrappers__set_implementation()`. For NSSwitch, it restores all function pointers to libc wrappers and logs success. For SSSD, it calls `sss_nss_idmap__init()`; on success it installs SSSD-backed functions and logs, and on failure it logs a critical error and returns nonzero without switching.

## State and persistence
The only state is the active set of process-global function pointers. There is no persistence across restart and no per-request state. Once switched, all idmapper and uid-to-group helper calls through the wrappers use the selected backend.

## Dependencies and integration points
The file depends on `pwnam_wrappers.h`, `sss_nss_idmap.h`, libc passwd/group APIs, `errno`, and logging. Higher-level callers in `idmapper.c` and `support/uid2grp.c` use these wrappers instead of directly calling libc, so this file is the integration seam for directory-service implementation choice.

## Risks
- Function pointer updates are unsynchronized; implementation selection is expected to happen during initialization, not concurrently with lookups.
- Failed SSSD initialization leaves previous pointers in place, which is safe for default startup but important if runtime reconfiguration is ever added.
- Return conventions differ between libc `getgrouplist()` and SSSD timeout calls; wrapper normalization is essential for callers that interpret `errno`.
- The comment spelling issue is harmless, but callers depend on the documented `ERANGE`, `ENOENT`, and timeout errno behavior.

## Test signals
- Tests should switch to NSSwitch and verify all exported wrappers call libc-compatible functions.
- SSSD tests should mock successful and failed `sss_nss_idmap__init()` and confirm pointer installation or retention.
- `getgrouplist()` buffer-too-small tests should verify `errno` becomes `ERANGE`.
- Startup tests should confirm idmapper initialization logs and handles selected implementation failures predictably.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/pwnam_wrappers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/sss_nss_idmap.c -->
# sources/user-network-fs/nfs-ganesha/src/idmapper/sss_nss_idmap.c

## Purpose
`sss_nss_idmap.c` dynamically loads SSSD's `libsss_nss_idmap.so.0` and adapts its timeout-aware NSS lookup functions to the same signatures used by Ganesha's passwd/group wrapper layer.

## Important APIs, types, and functions
- Function pointer typedefs model SSSD timeout APIs for `getpwnam`, `getpwuid`, `getgrnam`, `getgrgid`, and `getgrouplist`.
- Static state includes `is_inited`, `handle`, `sssd_flags`, and `sssd_timeout`.
- Global resolved symbols include `sss_nss_getpwnam_timeout`, `sss_nss_getpwuid_timeout`, `sss_nss_getgrnam_timeout`, `sss_nss_getgrgid_timeout`, and `sss_nss_getgrouplist_timeout`.
- `sss_nss_idmap__init()` reads directory-service SSSD options, computes flags and timeout in milliseconds, `dlopen()`s the library, resolves required symbols, and marks initialized.
- `sss_nss_idmap__getpwnam()`, `sss_nss_idmap__getpwuid()`, `sss_nss_idmap__getgrnam()`, and `sss_nss_idmap__getgrgid()` forward to the SSSD functions with configured flags and timeout.
- `sss_nss_idmap__getgrouplist()` adapts SSSD's `0` or errno return convention to libc-like `getgrouplist()` behavior by setting `errno` and returning `-1` on failure or `*ngroups` on success.

## Control flow
Initialization first computes runtime options from `nfs_param.directory_services_param`: `sssd_implementation_skip_cache` selects `SSS_NSS_EX_FLAG_NO_CACHE`, and `sssd_implementation_timeout` is converted from seconds to milliseconds. If already initialized, the function returns success after refreshing config-derived fields. If a prior `dlopen()` succeeded but later symbol resolution failed, `handle` remains non-NULL and future init attempts return failure immediately.

On first successful initialization, the file loads `libsss_nss_idmap.so.0` lazily and resolves all required timeout symbols. Public wrapper calls fatal if invoked before successful init, then delegate to the resolved function pointer with `sssd_flags` and `sssd_timeout`.

## State and persistence
State is process-local dynamic-linker state plus cached configuration flags. The library handle is not closed in this file. No lookup data is persisted; SSSD's own cache behavior is controlled by the flags passed to each call.

## Dependencies and integration points
The file depends on `dlopen()`, `dlsym()`, SSSD NSS idmap ABI names, Ganesha logging, and global `nfs_param`. It is selected by `pwnam_wrappers__set_implementation(PWNAM_IMPLEMENTATION__SSSD)` and then services idmapper and uid2grp lookups.

## Risks
- Partial initialization is sticky: after `dlopen()` succeeds but a required `dlsym()` fails, `handle` remains set and later retries return failure without closing/retrying.
- Public calls use `LogFatal()` on missing init; caller ordering must guarantee successful init before function pointer installation.
- The file defines SSSD flag constants locally. If upstream SSSD ABI changes, mismatches may not be caught at compile time.
- Timeout unit conversion assumes the configuration value is in seconds and SSSD wants milliseconds.
- Dynamic loading failures are runtime deployment issues; packages must include the expected shared library when SSSD mode is configured.

## Test signals
- Dynamic-link tests should cover missing library, missing individual symbols, successful symbol resolution, and the sticky partial-failure path.
- Configuration tests should verify skip-cache flag selection and timeout conversion.
- Wrapper tests should ensure `getgrouplist` converts SSSD error codes to `errno` plus `-1`, and success returns the group count.
- Integration tests should verify Ganesha startup refuses or falls back correctly when SSSD mode cannot initialize.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/idmapper/sss_nss_idmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p.h -->
# sources/user-network-fs/nfs-ganesha/src/include/9p.h

## Purpose
`9p.h` is the central public/internal header for NFS-Ganesha's 9P protocol service. It defines 9P protocol constants, message types, wire-format helper macros, connection/fid/request data structures, configuration parameters, utility APIs, flush handling hooks, RDMA conditionals, and every 9P operation entry point.

## Important APIs, types, and functions
- Constants cover preallocation counts, FID limits, message sizes, wire header lengths, block sizes, TCP/RDMA default ports and msize values, and 9P getattr/setattr/lock bitmasks.
- `enum _9p_msg_t` lists 9P2000 and 9P2000.L request/response opcodes used by dispatch.
- `struct _9p_str`, `_9p_qid`, `_9p_user_cred`, `_9p_xattr_desc`, `_9p_fid`, `_9p_conn`, `_9p_request_data`, and `_9p_function_desc` define core runtime objects.
- Serialization macros such as `_9p_getptr`, `_9p_getstr`, `_9p_setptr`, `_9p_setvalue`, `_9p_setqid`, `_9p_setstr`, `_9p_setbuffer`, `_9p_setinitptr`, `_9p_setendptr`, and `_9p_checkbound` advance raw cursors through protocol messages.
- `struct _9p_param`, `_9p_param`, and `_9p_param_blk` define configuration integration.
- Utility APIs include `_9p_init()`, credential ref helpers, op-context setup/release, fid free/clunk/cleanup, UID/name request context setup, FSAL errno/openflag conversion, and share-access conversion.
- Flush APIs `_9p_AddFlushHook()`, `_9p_FlushFlushHook()`, `_9p_LockAndTestFlushHook()`, `_9p_ReleaseFlushHook()`, and `_9p_DiscardFlushHook()` coordinate `TFLUSH` with in-flight request completion.
- Protocol function prototypes expose handlers such as `_9p_attach`, `_9p_walk`, `_9p_read`, `_9p_write`, `_9p_lopen`, `_9p_lcreate`, `_9p_getattr`, `_9p_setattr`, `_9p_lock`, `_9p_xattrwalk`, and `_9p_rerror`.

## Control flow
The header describes a service in which transport-specific decoders create `_9p_request_data` objects tied to a `_9p_conn`, then dispatch through `_9pfuncdesc[]` to opcode handlers. Handlers parse request payloads with cursor macros, initialize operation context from fids and credentials, call FSAL/SAL operations, and serialize replies or errors into caller-provided buffers.

Connections hold transport data, peer/client identity, negotiated `msize`, active fids, socket lock, and per-bucket flush lists. Fids bind protocol FID numbers to exports, user credentials, object handles, state, parent object, names, open count, and optional xattr descriptors. Flush hooks let a `TFLUSH` waiter locate an in-flight request by tag and sequence and wait until original reply send completes before `RFLUSH` is sent.

## State and persistence
The header defines per-connection and per-fid in-memory state only. Persistent filesystem state is accessed through FSAL object handles and state objects referenced by fids. Configurable service state is held in `_9p_param`. Credential and export references are refcounted, while fids are cleaned up on clunk, remove, or connection teardown.

## Dependencies and integration points
It depends on system types, file flags, `9p_types.h`, FSAL/SAL headers, Ganesha client/export types, and optionally Mooshika RDMA types. It integrates the 9P protocol layer with FSAL object operations, NFSv4 share-access constants, Ganesha operation context, transport handlers, request queues, and xattr support.

## Risks
- Wire cursor macros perform raw casts and pointer arithmetic; callers must size-check and account for alignment and endian assumptions.
- `_9p_get_fname()` assumes prior length validation and can overflow if called with unchecked length.
- FID and credential lifetimes are refcount-dependent. Missing clunk/free/release calls can leak exports, object handles, states, or xattr buffers.
- Flush correctness depends on tag/sequence matching and bucket locking; races can cause premature `RFLUSH` or missed cancellation semantics.
- RDMA and TCP paths share core structures but have different buffer lifetime rules under `_USE_9P_RDMA`.

## Test signals
- Protocol tests should cover version negotiation, attach, walk, open/create, read/write, readdir, getattr/setattr, lock, xattr, flush, clunk, remove, and error replies.
- Fuzzing or boundary tests should stress message-size checks, string lengths, buffer lengths, and malformed opcodes.
- Lifetime tests should verify fid cleanup on normal clunk, failed partial allocation, connection teardown, and xattr create/walk paths.
- Concurrency tests should exercise simultaneous requests, flush against active requests, and per-connection socket locking.
- RDMA-enabled builds should compile and run transport callback paths with negotiated RDMA msize and pool settings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_req_queue.h -->
# sources/user-network-fs/nfs-ganesha/src/include/9p_req_queue.h

## Purpose
`9p_req_queue.h` declares the 9P request queue infrastructure used to classify and dispatch incoming 9P requests through producer and consumer queues with cache-line padding and wait-list wakeups.

## Important APIs, types, and functions
- `struct req_q` is a spinlock-protected glist queue with `size`, `max`, and waiter count.
- `struct req_q_pair` separates a decoder-side `producer` queue from an executor-side `consumer` queue, padded with `GSH_CACHE_PAD`.
- `enum req_q_e` currently defines `REQ_Q_LOW_LATENCY` and `N_REQ_QUEUES`.
- `struct req_q_set` groups all queue pairs.
- `struct _9p_req_st` contains global request counters, queue set, aggregate size, a state spinlock, wait list, and waiter count.
- `_9p_rpc_q_init()` initializes a queue list and spinlock; `_9p_rpc_q_destroy()` tears down the spinlock.
- `_9p_queue_awaken()` walks wait-list entries and signals both left and right wait queue condition variables.

## Control flow
Queue users initialize `struct req_q` objects before accepting requests. Producers and consumers coordinate with spinlocks around glist operations in implementation code outside this header. When work becomes available or state changes, `_9p_queue_awaken()` locks the request-state spinlock, iterates waiters, and signals both condition variables in each `wait_q_entry_t`.

## State and persistence
All queue state is in memory and tied to the 9P service runtime. Queue sizes, max counts, counters, and waiters are transient scheduling state; no persistence is involved.

## Dependencies and integration points
The header depends on `gsh_list.h`, `common_utils.h`, `gsh_wait_queue.h`, pthread spinlocks, Ganesha wait-queue entries, and cache-padding macros. It integrates the 9P decoder/executor pipeline with Ganesha's wait queue primitives.

## Risks
- The comment says LIFO for `struct req_q::q`; scheduling behavior depends on implementation code preserving expected order.
- Wakeups signal condition variables while holding the request-state spinlock; waiters must follow compatible locking rules to avoid missed wakeups or lock-order deadlocks.
- Only one queue class is currently declared. Adding classes requires updating queue initialization and dispatch logic outside this header.
- Queue `max` is not initialized by `_9p_rpc_q_init()`, so callers must set or tolerate its default separately.

## Test signals
- Threaded queue tests should cover producer/consumer handoff, waiter wakeups, queue destroy after drain, and repeated awaken with empty wait list.
- Static analysis should verify all queue pairs are initialized and destroyed.
- Performance tests should check cache-line padding keeps hot producer/consumer state from false sharing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_req_queue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_types.h -->
# sources/user-network-fs/nfs-ganesha/src/include/9p_types.h

## Purpose
`9p_types.h` defines short unsigned integer aliases used by the 9P protocol code. It avoids problematic typedef redefinitions by using preprocessor aliases for fixed-width integer types.

## Important APIs, types, and functions
- `u8`, `u16`, `u32`, and `u64` are defined as macros mapping to `uint8_t`, `uint16_t`, `uint32_t`, and `uint64_t`.
- A disabled `#if 0` block documents the avoided typedef form.

## Control flow
There is no runtime control flow. Inclusion of the header makes the aliases available to `9p.h` and protocol implementation files.

## State and persistence
The header has no state. Its only effect is compile-time type spelling.

## Dependencies and integration points
The aliases require `stdint.h` to have been included before or by the includer; `9p.h` includes `<stdint.h>` before this header. The aliases are used heavily in 9P wire-structure constants, fields, and serialization macros.

## Risks
- Macro type aliases can collide with other headers or produce surprising diagnostics compared with typedefs.
- Because this header does not include `<stdint.h>` itself, standalone inclusion depends on include order.
- The copyright line includes an unusual character in the comment; it is harmless to compilation but can affect encoding-sensitive tools.

## Test signals
- Compile 9P code with strict warnings on all supported platforms.
- Include-order tests should verify no source includes `9p_types.h` before fixed-width integer types are defined, or the header should be adjusted if needed.
- Portability checks should compile with headers that already define `u8`-style aliases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/9p_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/Connectathon_config_parsing.h -->
# sources/user-network-fs/nfs-ganesha/src/include/Connectathon_config_parsing.h

## Purpose
`Connectathon_config_parsing.h` declares configuration structures and parser helpers for Connectathon-style test parameters. It is separate from the main Ganesha runtime config and describes test directories, log files, and per-test workload settings.

## Important APIs, types, and functions
- `enum test_number` names test cases `ONE` through `NINE`.
- `struct btest` stores per-basic-test parameters: test numbers, levels, file/dir counts, sizes, block size, path/name strings, and linked-list pointer.
- `struct testparam` stores top-level `dirtest`, `logfile`, and linked `btest` list.
- Lifecycle helpers include `btest_init_defaults()`, `testparam_init_defaults()`, and `free_testparam()`.
- Accessors include `get_test_directory()`, `get_log_file()`, and `get_btest_args()`.
- `readin_config()` reads a config file into a `struct testparam`.

## Control flow
Implementation code initializes defaults, parses a config file into linked `btest` nodes, and returns a `testparam` object. Consumers query the top-level directory/log path and retrieve arguments for a specific numbered test.

## State and persistence
The header defines heap-backed config objects with owned strings and linked nodes. Persistence is external in the config file read by `readin_config()`. `free_testparam()` is responsible for releasing parsed in-memory state.

## Dependencies and integration points
It has no included dependencies beyond C language types. It likely integrates with Connectathon test support code rather than core server runtime.

## Risks
- The include guard name `_CONFIG_PARSING_H` is generic and can collide with the main config parsing header guard.
- Ownership rules for returned strings and `btest` nodes are not documented in the header; misuse can leak or double-free.
- Parser error behavior is not visible from the prototype; callers need implementation knowledge for malformed files.
- SPDX license is marked unknown, which may need cleanup for compliance tooling.

## Test signals
- Parser tests should cover missing fields, defaults, all test numbers, linked-list ordering, and cleanup.
- Include collision tests should build code that includes this header with main config headers.
- Sanitizer runs should verify `free_testparam()` releases all strings and nodes from `readin_config()`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/Connectathon_config_parsing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/access_check.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/access_check.h

## Purpose
`FSAL/access_check.h` declares common FSAL access-check, credential switching, and ACL debug helpers. It is the shared interface for default permission evaluation across FSAL object handles.

## Important APIs, types, and functions
- `fsal_test_access()` checks requested FSAL access flags on an object and can report allowed and denied masks, with an `owner_skip` option.
- `display_fsal_v4mask()` formats an NFSv4 ACE permission mask into a display buffer.
- `fsal_set_credentials()` and `fsal_restore_ganesha_credentials()` are available when Ganesha can host local filesystems.
- `fsal_set_credentials_only_one_user()` and `fsal_save_ganesha_credentials()` support credential-switching policy and saved server credentials.
- `fsal_print_ace_int()` and `fsal_print_acl_int()` implement debug printing, with `fsal_print_ace` and `fsal_print_acl` macros injecting file, line, and function.

## Control flow
FSAL and protocol code call `fsal_test_access()` before operations that require permission checks. Local filesystem FSALs can switch process credentials around POSIX operations, then restore Ganesha credentials. Debug macros pass call-site metadata to ACL/ACE printers.

## State and persistence
The header itself has no state. Credential helpers affect process or thread credential state in their implementation, so callers must pair set/restore operations carefully. Access decisions are derived from object metadata, ACLs, and supplied credentials rather than persisted here.

## Dependencies and integration points
It depends on POSIX stat headers, `config.h`, `fsal_api.h`, log component types, display buffers, `fsal_ace_t`, and `fsal_acl_t`. It integrates FSAL modules with common permission enforcement and diagnostics.

## Risks
- Credential switching is high risk in multithreaded code if implementation scope is process-wide rather than thread-local on a platform.
- Callers that ignore `allowed` or `denied` outputs lose useful diagnostics for NFS access replies.
- `owner_skip` changes semantics and must match NFS owner-permission rules.
- Debug macros cast string literals and predefined macros to `char *`, which relies on callees not modifying them.

## Test signals
- Permission tests should compare mode-bit and ACL access decisions for owner, group, everyone, deny ACEs, and directory-specific masks.
- Credential tests should verify set/restore pairing and behavior when only-one-user restrictions apply.
- Debug output tests should format representative ACE and ACL masks.
- Local-FS builds with and without `GSH_CAN_HOST_LOCAL_FS` should compile cleanly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/access_check.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_commonlib.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_commonlib.h

## Purpose
`FSAL/fsal_commonlib.h` declares common FSAL support routines for module registration, export and object-handle lifecycle, pNFS data-server state, ACL inheritance/conversion, share reservation management, fd lifecycle, verifier handling, referral detection, and export updates.

## Important APIs, types, and functions
- `fsal_registration_entry_t` tracks FSAL modules that need NFS service backend registration.
- Registration APIs include `fsal_registration_try_register()`, `unregister_nfs_service_with_fsal_backend()`, and `register_nfs_service_with_fsal_backend()`.
- Export/object lifecycle APIs include `fsal_attach_export()`, `fsal_detach_export()`, `fsal_export_init()`, `fsal_export_stack()`, `free_export_ops()`, `fsal_default_obj_ops_init()`, `fsal_obj_handle_init()`, and `fsal_obj_handle_fini()`.
- `fsal_obj_handle_is()` is a type-test inline.
- pNFS helpers include `fsal_pnfs_ds_init()`, `fsal_pnfs_ds_fini()`, `encode_fsid()`, and `decode_fsid()`.
- ACL and access helpers include `fsal_inherit_acls()`, `fsal_remove_access()`, `fsal_rename_access()`, `fsal_can_reuse_mode_to_acl()`, `fsal_mode_to_acl()`, and `fsal_acl_to_mode()`.
- Share helpers include `update_share_counters()`, `check_share_conflict()`, `check_share_conflict_and_update()`, locked variants, and `merge_share()`.
- FD helpers include `fsal_close_fd()`, `fsal_reopen_fd()`, `close_fsal_fd()`, `fsal_start_global_io()`, `fsal_start_io()`, `fsal_complete_io()`, `fsal_start_fd_work()`, `fsal_complete_fd_work()`, and FD LRU helpers.
- `init_state()` initializes `state_t` and copies lock owner key data from related state when present.
- Verifier/referral/export APIs include `set_common_verifier()`, `check_verifier_stat()`, `check_verifier_attrlist()`, `fsal_common_is_referral()`, and `update_export()`.

## Control flow
FSAL modules initialize module and export state, attach exports to module lists, initialize object handles with default operation vectors, and use common helpers for operations that span modules. I/O paths use `fsal_start_io()` or `fsal_start_global_io()` to choose or open an fd while honoring share reservations, perform work, then call completion helpers to release fd work state and maintain LRU state. Share-conflict helpers check requested open flags and optionally update counters atomically under object locks.

## State and persistence
The header describes manipulation of persistent runtime objects: `fsal_module`, `fsal_export`, `fsal_obj_handle`, `fsal_share`, `fsal_fd`, `state_t`, and pNFS data-server state. State is in memory, but many helpers mirror or gate persistent filesystem operations. Locked variants mutate share counters under `obj_hdl->obj_lock`.

## Dependencies and integration points
It depends on `fsal_api.h`, `sal_data.h`, and `sal_functions.h`. It is a major integration point between FSAL modules, SAL state, NFS service registration, pNFS, NFSv4 share reservations, object-handle operations, fd caching, ACL mapping, and export reload/update code.

## Risks
- Share-reservation updates must stay atomic with conflict checks. Calling unlocked helpers without external locking can corrupt counters or allow conflicting opens.
- FD lifecycle is subtle: `fsal_start_io()` may reuse state fds, object fds, or temporary fds, and every successful start needs matching completion.
- `fsal_start_fd_work_no_reclaim()` treats failure as fatal; callers must only use it where failure is impossible by invariant.
- ACL mode conversion can lose information unless `fsal_can_reuse_mode_to_acl()` is respected.
- Export stacking and update paths can involve multiple modules; reference and operation-vector ownership must remain clear.

## Test signals
- FSAL common tests should cover object/export initialization/finalization, attach/detach lists, and default ops installation.
- Share tests should cover read/write/deny combinations, bypass behavior, locked and unlocked variants, and merge logic.
- FD tests should exercise open/reopen/close, global fd reuse, state fd reuse, LRU insert/bump/remove, reclaiming, and completion after errors.
- ACL tests should verify inheritance, mode-to-ACL and ACL-to-mode conversion, remove/rename access checks, and verifier truncation behavior.
- Export update tests should cover in-place update and stacked FSAL update cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_commonlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_config.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_config.h

## Purpose
`FSAL/fsal_config.h` declares accessor helpers for `struct fsal_staticfsinfo_t`. These helpers expose configured or module-provided filesystem limits and capability flags through a stable FSAL configuration API.

## Important APIs, types, and functions
- `fsal_supports()` tests an `fsal_fsinfo_options_t` capability.
- Scalar accessors include `fsal_maxfilesize()`, `fsal_maxlink()`, `fsal_maxnamelen()`, `fsal_maxpathlen()`, `fsal_maxread()`, `fsal_maxwrite()`, `fsal_umask()`, and `fsal_expiretimeparent()`.
- Capability/mask accessors include `fsal_acl_support()`, `fsal_supported_attrs()`, and `fsal_readdir_mode()`.

## Control flow
FSAL, export, and protocol code pass a static fsinfo object to these functions instead of reading fields directly. The implementation can apply defaults, option masks, or configured overrides consistently.

## State and persistence
The header has no state. It reads static filesystem info, which is runtime configuration associated with FSAL modules or exports and may reflect persistent export configuration.

## Dependencies and integration points
The header relies on FSAL API types being available to includers. It integrates FSAL module capabilities with protocol responses such as FSINFO, PATHCONF, access limits, readdir behavior, and attribute support.

## Risks
- The header has no include guard and no direct include of FSAL type definitions; it assumes include context.
- Consumers that bypass accessors may observe different behavior from code using normalized helper results.
- Capability option semantics need to stay aligned with `fsal_staticfsinfo_t` field layout.

## Test signals
- Compile tests should include this header through normal FSAL include paths and directly if that is expected.
- Configuration tests should verify every accessor returns correct defaults, overrides, and capability-mask results.
- Protocol integration tests should compare NFS FSINFO/PATHCONF-like replies against FSAL static fsinfo.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_init.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_init.h

## Purpose
`FSAL/fsal_init.h` defines constructor and destructor attribute macros used by FSAL shared modules to register and unregister themselves when dynamically loaded or unloaded.

## Important APIs, types, and functions
- `MODULE_INIT` expands to `__attribute__((constructor))`.
- `MODULE_FINI` expands to `__attribute__((destructor))`.
- Comments document that initializer functions should call `register_fsal` and override default operation vectors, while finalizers must ensure safe unload.

## Control flow
When a FSAL shared object is loaded with `dlopen()`, functions annotated with `MODULE_INIT` run before `dlopen()` returns. On unload, functions annotated with `MODULE_FINI` run to release module-level resources after the core has verified unload safety.

## State and persistence
The macros do not define state. They control module lifecycle hooks that initialize and tear down process-local FSAL module state.

## Dependencies and integration points
The header depends on compiler support for GNU constructor/destructor attributes. It integrates FSAL modules with the dynamic module loader and Ganesha's `register_fsal` flow.

## Risks
- Constructors/destructors are compiler- and platform-specific; non-GNU toolchains may need alternate definitions.
- Constructor order across multiple modules is not generally controllable beyond dynamic load order.
- Finalizers must not run while exports or object handles still reference the module; the comment calls out this invariant but enforcement lives elsewhere.

## Test signals
- Build tests should compile FSAL modules on every supported compiler/platform.
- Dynamic loading tests should verify module registration occurs before use and finalizers run only after safe unload.
- Failure tests should cover constructor registration errors and module unload refusal with active references.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_localfs.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_localfs.h

## Purpose
`FSAL/fsal_localfs.h` declares common support for FSALs that map onto local POSIX filesystems. It tracks discovered filesystems, relationships between filesystems and exports, claims, FSID/device indexes, and cleanup/reindex operations. When local filesystem hosting is unavailable, it provides no-op stubs.

## Important APIs, types, and functions
- Under `!GSH_CAN_HOST_LOCAL_FS`, `release_posix_file_systems()` and optional `dbus_cache_init()` are no-op inline stubs and `struct fsal_filesystem` is forward-declared.
- `struct fsal_filesystem` describes one filesystem: tree/list links, parent/children, owning FSAL, export list, private data, path/device/type, claim callbacks, path/name lengths, AVL nodes for FSID and device indexes, FSID/device values, claim counters, and verifier truncation policy.
- `struct fsal_filesystem_export_map` links a filesystem to an export, supports child maps, and records claim type.
- Core APIs include `populate_posix_file_systems()`, `resolve_posix_filesystem()`, `claim_posix_filesystems()`, `release_posix_file_systems()`, `release_posix_file_system()`, `unclaim_all_export_maps()`, and `get_fs_first_export_ref()`.
- Lookup/reindex APIs include `lookup_fsid_locked()`, `lookup_dev_locked()`, `lookup_fsid()`, `lookup_dev()`, `re_index_fs_fsid()`, `re_index_fs_dev()`, and `change_fsid_type()`.
- `fsal_fs_compare_fsid()` compares FSID type, major, and optionally minor fields.
- `LogFilesystem` formats detailed filesystem topology, export, private data, and claim counters for debug logging.
- `open_dir_by_path_walk()` safely opens a path by walking from a starting directory fd.

## Control flow
Local-FS capable builds populate filesystem records from POSIX paths, resolve which filesystem owns an export path, claim filesystem subtrees for exports, and index filesystems by FSID and device. Export teardown unclaims maps and can release filesystems when no claims remain. Lookup helpers use `fs_lock` externally or internally depending on the locked variant.

## State and persistence
The file declares shared in-memory filesystem topology and indexes protected by external `fs_lock`. It mirrors persistent mounted filesystem facts such as path, device, type, FSID, name length, and statfs-derived attributes. Claim counters record active export relationships and must be balanced during export load/unload.

## Dependencies and integration points
It depends on `fsal_api.h`, AVL trees, Ganesha export/module types, FSAL claim callbacks, DBus optional cache initialization, and POSIX stat/open concepts. It integrates local FSAL modules, export management, FSID/device lookup used by file-handle decoding, and verifier behavior for filesystems with truncated timestamps.

## Risks
- Many-to-many export/filesystem maps and claim counters are easy to leak or unbalance, especially during partial export-load failure.
- Reindexing FSID or device while lookups run requires correct `fs_lock` use.
- `fsal_fs_compare_fsid()` ignores minors for `FSID_MAJOR_64`, so callers must supply consistent types.
- No-op stubs under `!GSH_CAN_HOST_LOCAL_FS` can hide missing feature coverage until runtime configuration asks for local FS behavior.
- Path walking must handle symlinks, races, and permission errors in implementation.

## Test signals
- Local-FS integration tests should claim and unclaim exports rooted at filesystem roots, subtrees, children, and overlapping paths.
- Lookup tests should resolve by FSID and device before and after reindex operations.
- Failure-injection tests should abort export load mid-claim and verify all maps and counters are unwound.
- Builds with `GSH_CAN_HOST_LOCAL_FS` enabled and disabled should compile and run expected stubs or real paths.
- DBus builds should validate filesystem cache initialization and reporting if implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_localfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_atomic.h -->
# sources/user-network-fs/nfs-ganesha/src/include/abstract_atomic.h

## Purpose
`abstract_atomic.h` is Ganesha's inline atomic-operation shim over GCC `__atomic` builtins. It provides named helpers for arithmetic, bit operations, fetch/store, compare-add-unless, and a small number of relaxed counters across common integer, pointer, time, and size types.

## Important APIs, types, and functions
- Pre-operation arithmetic helpers return the value after mutation, for signed and unsigned 8/16/32/64-bit integers and `size_t`: `atomic_add_*`, `atomic_inc_*`, `atomic_sub_*`, and `atomic_dec_*`.
- Post-operation helpers return the value before mutation: `atomic_postadd_*`, `atomic_postinc_*`, `atomic_postsub_*`, and `atomic_postdec_*`.
- Bit helpers for unsigned 8/16/32/64-bit integers include pre and post clear/set operations.
- Fetch/store helpers cover `size_t`, `ptrdiff_t`, `time_t`, `uintptr_t`, `void *`, and integer widths.
- `atomic_add_unless_*()` exists for 32/64-bit signed and unsigned counters and uses a compare-exchange loop.
- `atomic_inc_unless_0_int32_t()` increments a nonzero int32 refcount and returns the new value or zero.
- `atomic_relaxed_add_int32_t()` and `atomic_relaxed_inc_int32_t()` use relaxed ordering for counters that do not need synchronization.

## Control flow
Most helpers are single inline wrappers around `__atomic_*` with `__ATOMIC_SEQ_CST`. The add-unless functions first load the current value, return false if it equals the sentinel, otherwise retry compare-exchange until the mutation succeeds. Relaxed helpers explicitly choose `__ATOMIC_RELAXED`.

## State and persistence
The header has no state. It mutates caller-owned memory atomically and establishes memory-ordering semantics for concurrent runtime state such as refcounts, cache hints, counters, and flags.

## Dependencies and integration points
It depends on `<stddef.h>`, `<stdint.h>`, `<time.h>`, `<stdbool.h>`, and compiler support for GCC/Clang `__atomic` builtins. It is used broadly by cache code, client manager refcounts, state counters, and synchronization utilities such as `atomic_utils.h`.

## Risks
- The file assumes compiler support for `__atomic`; unsupported compilers have no fallback here.
- Nearly all operations are sequentially consistent, which is simple but may be more expensive on hot counters.
- Unsigned add-unless with `-1` arguments relies on unsigned wraparound in callers such as refcount decrement helpers.
- Atomic pointer helpers do not solve object lifetime; callers still need locks or refcounts to keep pointed-to memory valid.
- Type-specific duplication makes it easy for one helper to drift in signature or semantics from the others.

## Test signals
- Compile tests should cover every helper on all supported architectures and detect missing builtins.
- Unit tests should validate pre/post return values, bit set/clear results, fetch/store behavior, add-unless sentinel behavior, and relaxed counter arithmetic.
- Threaded stress tests should exercise refcount-like add-unless loops under contention.
- Static analysis should flag misuse of pointer atomics without lifetime protection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_mem.h -->
# sources/user-network-fs/nfs-ganesha/src/include/abstract_mem.h

## Purpose
`abstract_mem.h` provides Ganesha allocation shims and a minimal object-pool abstraction. It wraps libc allocation functions so allocator behavior can be swapped or instrumented while giving callers a consistent abort-on-OOM contract.

## Important APIs, types, and functions
- `gsh_malloc__()`, `gsh_calloc__()`, `gsh_realloc__()`, and `gsh_malloc_aligned__()` accept call-site metadata and log malloc failures before aborting.
- Simpler `gsh_malloc()`, `gsh_calloc`, `gsh_realloc()`, `gsh_strdup()`, `gsh_memdup()`, `gsh_free()`, and `gsh_free_size()` wrap libc operations with abort-on-failure behavior.
- `gsh_malloc_aligned(a, n)` uses `posix_memalign()` or Apple `valloc()` in the metadata form.
- `gsh_strdupa()` maps to glibc `strdupa()` when available or an `alloca()` plus copy fallback.
- `pool_t` records a pool name and object size.
- `pool_basic_init()`, `pool_destroy()`, `pool_alloc()`, and `pool_free()` implement a simple calloc/free based pool abstraction.
- `gsh_concat()` and `gsh_concat_sep()` allocate concatenated path/string buffers.

## Control flow
Allocation calls immediately abort on OOM rather than returning NULL, except `gsh_realloc()` accepts `n == 0` behavior. Pool creation allocates and names a pool object; `pool_alloc()` zero-allocates one object of the pool's size; `pool_free()` frees it. Callers release all returned memory with `gsh_free()` or the matching pool destroy/free function.

## State and persistence
The header itself has no global state. Pool objects hold name and object size, while allocated objects are ordinary heap memory. No allocations persist across process exit unless intentionally leaked by caller-owned lifecycle.

## Dependencies and integration points
It depends on libc allocation/string APIs, `assert.h`, `alloca()` availability through includers/toolchain, and Ganesha logging for metadata variants. It is included widely by Ganesha code and underlies cache entries, parsed strings, list nodes, and utility allocations.

## Risks
- Abort-on-OOM simplifies callers but prevents graceful degradation under memory pressure.
- Macro forms such as `gsh_calloc`, `gsh_malloc_aligned`, and `pool_alloc` evaluate arguments in expression contexts and may surprise debuggers or non-GNU compilers.
- `gsh_strdupa()` allocates on the stack; large inputs can overflow stack.
- Pool abstraction currently does not track outstanding objects despite comments requiring all objects be returned before destroy.
- `gsh_concat*()` assumes non-NULL inputs and can overflow `size_t` for extreme lengths.

## Test signals
- Allocation tests should cover normal malloc/calloc/realloc/strdup/memdup/free and aligned allocation alignment.
- Failure-injection builds should verify metadata variants log and abort as expected.
- Pool tests should create/destroy pools and ensure allocated objects are zeroed.
- Portability builds should cover glibc, non-glibc, Apple, and C++ include contexts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/abstract_mem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/atomic_utils.h -->
# sources/user-network-fs/nfs-ganesha/src/include/atomic_utils.h

## Purpose
`atomic_utils.h` builds higher-level refcount helpers on top of `abstract_atomic.h`. Its helpers decrement a refcounter and acquire a mutex only for the final-reference path.

## Important APIs, types, and functions
- `PTHREAD_MUTEX_dec_int64_t_and_lock()`
- `PTHREAD_MUTEX_dec_uint64_t_and_lock()`
- `PTHREAD_MUTEX_dec_int32_t_and_lock()`
- `PTHREAD_MUTEX_dec_uint32_t_and_lock()`

Each helper accepts a pointer to a refcounter and a mutex. It returns true when the counter was decremented to zero and the mutex remains locked for caller cleanup.

## Control flow
The helpers first try `atomic_add_unless_*(&refcount, -1, 1)`. If the count was greater than one, the decrement succeeds and no lock is taken. If the count might be one, the helper locks the mutex, decrements under the mutex, and returns true if the result is zero. If another reference appeared, it unlocks and returns false.

## State and persistence
The header mutates caller-owned refcount and mutex state. It has no independent state or persistence.

## Dependencies and integration points
It depends on `common_utils.h` for pthread lock wrappers and `abstract_atomic.h` for add-unless and arithmetic helpers. It is intended for object lifetime code where cleanup must be serialized by a mutex only at the zero-ref transition.

## Risks
- Unsigned variants pass `-1` to unsigned add helpers, relying on wraparound to decrement. This is idiomatic here but easy to misuse.
- Callers must understand that true means the mutex is locked and must be unlocked after destruction/cleanup.
- The pattern assumes references cannot be safely resurrected after the zero path starts without holding the same mutex.
- Passing a zero refcount underflows; caller invariants must prevent double put.

## Test signals
- Unit tests should cover decrement from counts greater than one, exactly one, and concurrent final puts.
- Tests should verify true return leaves the mutex locked and false return leaves it unlocked.
- Sanitizer or assertion tests should catch double-decrement or zero-ref misuse in caller code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/atomic_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/avltree.h -->
# sources/user-network-fs/nfs-ganesha/src/include/avltree.h

## Purpose
`avltree.h` is a vendored libtree header that declares intrusive binary-search tree, red-black tree, AVL tree, and splay tree APIs. NFS-Ganesha heavily uses the AVL portion for caches and indexes.

## Important APIs, types, and functions
- `*_container_of` macros recover parent objects from embedded tree nodes.
- BST declarations include `struct bstree_node`, `struct bstree`, comparator type, first/last/next/prev, lookup, insert, remove, replace, and init.
- Red-black declarations mirror that API with `struct rbtree_node`, `enum rb_color`, and `struct rbtree`.
- AVL declarations include packed/aligned `struct avltree_node`, `get_balance()`, `avltree_cmp_fn_t`, `struct avltree`, inline lookup/insert helpers, first/last accessors, next/prev, size, inf/sup, remove, replace, and init.
- Splay declarations include analogous node/tree and operation prototypes.

## Control flow
Intrusive tree users embed a node in their object and provide a comparator that maps nodes back to containing objects. `avltree_insert()` performs a lookup; if a duplicate is found, it returns the existing node, otherwise it calls `avltree_do_insert()` to rebalance and update metadata. Lookup follows comparator results down the tree. Iteration starts at cached first/last pointers and uses next/prev helpers.

## State and persistence
Tree state is stored in caller-owned `struct *tree` and embedded node fields. The AVL tree tracks root, comparator, height, first/last nodes, and size. There is no persistence beyond the in-memory indexes maintained by callers.

## Dependencies and integration points
It depends on integer and offset types and is implemented by companion source files in the tree library. It is integrated across Ganesha for idmapper caches, client maps, filesystem indexes, and other ordered intrusive collections.

## Risks
- Intrusive nodes can belong to only one tree at a time unless the containing object has multiple node members.
- Comparators must define a strict weak ordering and match the node member used for container lookup; mistakes corrupt tree behavior.
- The packed parent/balance representation depends on pointer alignment and `UINTPTR_MAX`; portability needs coverage.
- Tree operations are not internally synchronized. Callers must provide locks.
- Duplicate insert returns the existing node and does not replace automatically; callers must explicitly handle replacement.

## Test signals
- Tree tests should cover insert, duplicate insert, lookup, remove, replace, first/last, next/prev, inf/sup, and size.
- Stress tests should insert/remove random keys while validating sorted traversal and AVL balance.
- Portability builds should cover 32-bit and 64-bit targets and compilers with/without GNU extensions.
- Caller-specific tests should validate comparators for each embedded-node use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/avltree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/bsd-base64.h -->
# sources/user-network-fs/nfs-ganesha/src/include/bsd-base64.h

## Purpose
`bsd-base64.h` declares BSD/ISC-style base64 encode/decode helpers and a base64url encoder used by Ganesha support code.

## Important APIs, types, and functions
- `b64_ntop()` encodes binary source bytes into base64 text.
- `b64_pton()` decodes base64 text into binary bytes.
- `base64url_encode()` encodes source bytes using URL-safe base64.
- Compatibility macros `__b64_ntop` and `__b64_pton` alias the public names.

## Control flow
Callers provide source pointer/length, target buffer, and target size. Implementations return encoded/decoded lengths or an error code according to the BSD routines' convention.

## State and persistence
The header has no state. Encoded output is written to caller-owned buffers.

## Dependencies and integration points
It depends on `<sys/types.h>` for `u_char`. It integrates with code that needs textual representation of binary tokens, handles, keys, or protocol fields.

## Risks
- Callers must size target buffers correctly and check return values.
- Standard base64 and base64url alphabets are not interchangeable; callers must choose the correct function for protocol context.
- SPDX is marked unknown 0BSD while comments include ISC/IBM permission text; license metadata may require review.
- The include guard closing comment names `_BSD_BINRESVPORT_H`, which is harmless but misleading.

## Test signals
- Known-vector tests should cover empty input, one/two/three-byte groups, padding, invalid characters, target-too-small behavior, and URL-safe output.
- Fuzz tests should decode arbitrary input without overruns.
- License scanning should verify accepted metadata for vendored code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/bsd-base64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/city.h -->
# sources/user-network-fs/nfs-ganesha/src/include/city.h

## Purpose
`city.h` declares the C port of Google's CityHash non-cryptographic hash functions. It provides 64-bit and 128-bit hash APIs for byte arrays with optional seeds.

## Important APIs, types, and functions
- Local aliases `uint8`, `uint32`, and `uint64` map to fixed-width integer types.
- `struct _uint128`/`uint128` stores two 64-bit halves.
- `Uint128Low64()` and `Uint128High64()` macros access the two halves.
- `CityHash64()`, `CityHash64WithSeed()`, and `CityHash64WithSeeds()` compute 64-bit hashes.
- `CityHash128()` and `CityHash128WithSeed()` compute 128-bit hashes.

## Control flow
Callers pass a byte buffer and length, plus optional seed values. Implementations compute deterministic non-cryptographic hashes optimized for little-endian platforms and unaligned reads.

## State and persistence
The header has no state. Hash results may be persisted by callers as indexes or identifiers, but the header itself only declares pure functions.

## Dependencies and integration points
It depends on `<stdlib.h>` and `<stdint.h>`. It can be used by hash tables, fingerprinting, or cache/index code that needs fast non-cryptographic hashing.

## Risks
- Comments explicitly state CityHash is not suitable for cryptography.
- The vendored code warns it has not been tested on big-endian platforms.
- Persisted hash values may change if the implementation is updated or if platform-specific behavior differs.
- Local type aliases can collide with other headers in broad include contexts.

## Test signals
- Known-vector tests should verify 64-bit and 128-bit results for representative inputs and seeds.
- Portability tests should run on architectures with strict alignment and different endianness if supported.
- Security reviews should ensure CityHash is not used for authentication, signatures, or attacker-controlled hash-flood-sensitive tables without mitigation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/city.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/citycrc.h -->
# sources/user-network-fs/nfs-ganesha/src/include/citycrc.h

## Purpose
`citycrc.h` declares CityHash variants that use CRC instructions, including 128-bit and 256-bit hash outputs.

## Important APIs, types, and functions
- `CityHashCrc128()` computes a 128-bit CRC-accelerated CityHash.
- `CityHashCrc128WithSeed()` computes a seeded 128-bit CRC CityHash.
- `CityHashCrc256()` writes four 64-bit words to a caller-provided result array.

## Control flow
Callers pass a byte buffer and length, plus optional seed or output array. Implementations use CRC-capable CPU instructions such as `_mm_crc32_u64()` where available.

## State and persistence
The header has no state. Output buffers are caller-owned.

## Dependencies and integration points
It includes `city.h` for `uint128` and `uint64` types. It integrates with code that wants faster or wider non-cryptographic hashes on CRC-capable platforms.

## Risks
- CRC variants require CPU/compiler support for the needed intrinsics in implementation code.
- These hashes are still non-cryptographic and must not be used as security primitives.
- Runtime dispatch or build flags must prevent illegal-instruction failures on unsupported CPUs.
- `CityHashCrc256()` requires the caller to provide space for four `uint64` values.

## Test signals
- Build tests should cover CRC-enabled and CRC-disabled targets.
- Runtime tests should verify CPU feature gating before calling CRC implementations.
- Known-vector tests should cover seeded and unseeded outputs and the 256-bit four-word result.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/citycrc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/client_mgr.h -->
# sources/user-network-fs/nfs-ganesha/src/include/client_mgr.h

## Purpose
`client_mgr.h` declares Ganesha client-host management APIs and data structures. It tracks connected clients by address, reference counts, per-state statistics, connection-manager state, and export access-list client entries.

## Important APIs, types, and functions
- `struct gsh_client` embeds an AVL node, client rwlock, atomic refcount, last update timestamp, printable host address, socket address, optional QoS class, per-state counters, and `connection_manager__client_t`.
- Inline helpers `inc_gsh_client_refcount()`, `inc_gsh_client_state_stats()`, and `dec_gsh_client_state_stats()` use atomic operations on refcounts and state counters.
- Package and DBus initialization APIs are `client_pkginit()` and optional `dbus_client_init()`.
- Client lookup/lifetime APIs are `get_gsh_client()`, `put_gsh_client()`, and `foreach_gsh_client()`.
- `enum exportlist_client_type` classifies access-list entries: protocol, network, netgroup, wildcard host, GSS principal, match-any, and bad client.
- `struct base_client_entry` stores an access-list item with list linkage, type, CIDR pointer, and string.
- Formatting/logging helpers include `get_base_client_str()`, `StrClient()`, `LogClientListEntry()`, `LogClientList()`, and convenience macros.
- Access-list mutation and matching APIs include `FreeClientList()`, `client_match()`, `add_client()`, `delete_base_client()`, and `haproxy_match()`.

## Control flow
The client package is initialized at server startup. Connection paths call `get_gsh_client()` with a socket address to find or create a client object, increment references while in use, and call `put_gsh_client()` when done. State owners increment/decrement per-state stats as NFS state objects are associated with clients. Export parsing builds lists of `base_client_entry` values; access checks call `client_match()` against a host string/address and optional predicate.

## State and persistence
Client objects are in-memory runtime state keyed by address in an AVL tree managed by implementation code. Refcounts control lifetime. State counters are atomic per client and reflect live server state. Export client lists are configuration-derived in memory and can be rebuilt on export reload.

## Dependencies and integration points
The header depends on pthreads, `avltree`, `gsh_types`, IP/CIDR utilities, SAL state types, connection manager types, optional QoS, DBus, config parser term types, and logging/display buffers. It integrates transport connection handling, export access control, HAProxy proxy matching, per-client state accounting, and management diagnostics.

## Risks
- Client lifetime depends on balanced `get_gsh_client()`/`put_gsh_client()` and atomic refcount correctness.
- AVL-key comparator and address normalization in implementation must handle IPv4/IPv6 and mapped addresses consistently.
- Export-list matching involves multiple client types and optional predicates; order and specificity can affect access decisions.
- State stats are counters only; underflow from unmatched decrement would corrupt diagnostics.
- `base_client_entry` ownership of `cidr` and `str` must be respected by list free/delete functions.

## Test signals
- Client manager tests should cover lookup-only misses, create hits, refcount put/free, foreach traversal, and concurrent lookups.
- Access-list tests should cover protocol, CIDR network, netgroup, wildcard host, GSS principal, match-any, delete, and predicate filtering.
- IPv4/IPv6 tests should verify address string formatting and matching normalization.
- State-counter tests should verify increments/decrements for each state type and guard against underflow.
- HAProxy integration tests should confirm proxied client matching behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/client_mgr.h -->
