# subset-b-009724 Research Report

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/export_mgr.c -->
# sources/user-network-fs/nfs-ganesha/src/support/export_mgr.c

## Purpose
`export_mgr.c` is the runtime registry and administrative surface for NFS-Ganesha exports. It owns the export-id index, global export list, mount and unexport work queues, export reference lifetime, shutdown pruning, optional DBus export/stat methods, and the asynchronous delegation-transition helper used after export configuration changes. It is the bridge between parsed export configuration, PseudoFS mount/unmount operations, FSAL export lifetime, server statistics, and external management via DBus.

## Important APIs, Types, And Functions
The central state is `static struct export_by_id export_by_id`, which contains `eid_lock`, an AVL tree keyed by `gsh_export.export_id`, and a fixed-size atomic front-end cache. `exportlist`, `mount_work`, and `unexport_work` are global `glist_head` lists. The header exposes `struct gsh_export`, `EXPORT_ADMIN_LOCK`, `EXPORT_ADMIN_UNLOCK`, the advisory `export_admin_counter` seqlock, and `export_ready()`.

Key lifecycle APIs:

- `alloc_export()` allocates an `export_stats` container, initializes embedded `gsh_export` lists and lock, and starts `refcnt` at 1.
- `insert_gsh_export()` inserts into the AVL tree, takes the sentinel reference, updates the cache, and links into `exportlist`.
- `export_revert()` undoes a failed commit after insertion, removes cache/tree/list/work links, removes pNFS data-server state if present, and releases the sentinel through op-context cleanup.
- `_get_gsh_export_ref()` and `_put_gsh_export()` implement atomic reference counting and final cleanup through `free_export_resources()`, `server_stats_free()`, lock destruction, and freeing the `export_stats` container.
- `remove_gsh_export()` removes the export from the cache/tree/list, marks it `EXPORT_STALE`, removes pNFS data-server state, and drops the sentinel reference.

Lookup and iteration APIs:

- `get_gsh_export()` looks up by id through the cache first, then the AVL tree, and returns a referenced export.
- `get_gsh_export_by_path_locked()`, `get_gsh_export_by_pseudo_locked()`, and their unlocked wrappers perform longest-prefix or exact lookup over `exportlist`.
- `get_gsh_export_by_tag()` searches `FS_tag`.
- `foreach_gsh_export()` iterates `exportlist` under `eid_lock` in read or write mode.

Administrative and integration APIs:

- `mount_gsh_export()` and `unmount_gsh_export()` establish an NFSv4 op context and call `pseudo_mount_export()` or `pseudo_unmount_export_tree()`.
- `remove_all_exports()`, `prune_defunct_exports()`, `process_unexports()`, and `remove_one_export()` drive orderly shutdown and config-reread pruning.
- `export_pkginit()` initializes the manager and registers cleanup; `export_mgr_cleanup()` destroys global locks.
- `add_export_id()` and `is_export_id_match()` support config parsing of export-id lists.
- `async_deleg_transition_handler()` submits `queue_deleg_transition_handler()` to a fridge thread for delegation recall after runtime delegation policy changes.
- Under `USE_DBUS`, `dbus_export_init()` registers `org.ganesha.nfsd.exportmgr` and `org.ganesha.nfsd.exportstats` methods for dynamic add/update/remove, display, and statistics.

## Control Flow
Normal export creation starts in `exports.c`, but commits eventually call `insert_gsh_export()`. The inserted export becomes searchable by id and list traversal. Initial exports are queued on `mount_work`; dynamic add paths usually initialize the export root and mount immediately before insertion. Consumers call `get_gsh_export*()` to obtain a referenced export and later release it with `put_gsh_export()`.

Removal is staged. `remove_all_exports()` obtains the pseudo-root export, unmounts the whole PseudoFS tree, queues all exports on `unexport_work`, and drains that queue with `process_unexports()`. Each queued export is referenced, installed in `op_ctx`, and passed to `release_export()`, which eventually calls back into `remove_gsh_export()`. Config reread uses `prune_defunct_exports(generation)` to queue only exports whose `config_gen` is older than the new parse generation.

DBus add/update paths parse a provided config file and expression, collect parser errors into an `open_memstream()`, call `load_config_from_node()` with `add_export_param` or `update_export_param`, and return a string summary or DBus error. DBus remove validates id, rejects export 0 and exports with submounts, initializes an op context, and calls `release_export()`. DBus stats methods look up exports, validate whether the relevant stats block exists, emit status replies, and call the appropriate `server_dbus_*` helpers.

The delegation transition worker first takes and releases `EXPORT_ADMIN_LOCK()` to serialize behind any active export admin operation, builds an op context for the export, walks `exp_state_list`, filters `STATE_TYPE_DELEG`, derives the client address, calls `export_check_access()` for current effective permissions, and recalls read or write delegations whose permissions were disabled.

## State And Persistence Behavior
All state is in memory. Export identity is persisted only through the live AVL/list registry and configuration reload generation. The cache is a process-local acceleration structure and is invalidated on removal/revert when it points at the removed node. The sentinel reference taken during insertion keeps an export alive while it is in the manager; removal drops that sentinel and final freeing waits for all outstanding references.

`export_admin_mutex` serializes high-level add, remove, reread, and shutdown operations. `export_admin_counter` is incremented before and after such operations so other code can detect likely races. `export_by_id.eid_lock` protects the AVL tree, cache coherency, and export list iteration. Individual export contents are protected by `gsh_export.exp_lock` where needed. Path strings use `gsh_refstr` plus RCU access in temporary path helpers.

Stats timestamps (`nfs_stats_time`, `fsal_stats_time`, `v3_full_stats_time`, `v4_full_stats_time`, `auth_stats_time`, and `clnt_allops_stats_time`) track when counters were initialized or enabled. DBus enable/disable methods mutate `nfs_param.core_param` flags at runtime and reset or timestamp stats.

## Dependencies And Integration Points
This file depends on the FSAL layer, MDCACHE/stat helpers, PseudoFS helpers, NFS op-context setup, pNFS data-server cleanup, state/delegation recall, DBus, config parsing, client/IP display helpers, atomics, AVL trees, glists, pthread locks, and RCU-safe refstrings. It is tightly coupled to `exports.c` for config commits and `export_mgr.h` for the `gsh_export` structure and admin lock protocol.

Integration points to watch include `pseudo_mount_export()`, `pseudo_unmount_export_tree()`, `release_export()`, `free_export_resources()`, `server_dbus_*`, `mdcache_dbus_show()`, `fd_usage_summarize_dbus()`, `async_delegrecall_per_state()`, and `general_fridge`.

## Risks And Edge Cases
`get_gsh_export_by_path_locked()` appears to leak a `gsh_refstr` on non-exact prefix matches: it stores `ret_exp` and `len_ret` but does not release `ref_fullpath` before continuing unless it breaks on exact match. The pseudo-path variant has a bottom-of-loop `gsh_refstr_put()`, so path lookup should be reviewed specifically.

The mount and unexport work-list helpers do not take locks themselves; callers must honor the documented export-admin locking discipline. Misuse can corrupt list links because `exp_work` is a single embedded list node.

The DBus stats enable/disable methods accept known strings but do not visibly reject unknown `stat_type` values after parsing; an unknown value can return an OK status with no state change.

`async_deleg_transition_handler()` queues a raw `gsh_export *`. Correctness depends on caller-side lifetime guarantees while the fridge job is pending. The worker serializes against admin updates but does not take its own export reference before queueing.

DBus client display preserves legacy CIDR fields by appending byte fields rather than full byte arrays; callers relying on these fields should be treated as compatibility-sensitive.

## Test Signals
Useful validation includes unit or integration coverage for duplicate export IDs, cache hit and cache invalidation on remove/revert, lookup by path and pseudo with trailing slashes and prefix collisions, all mount/unexport work queue paths, config reread pruning by generation, DBus add/update/remove error reporting, stats enable/disable/status behavior, and delegation recall after disabling read/write delegation options. Leak detection around path lookup and sanitizer runs through dynamic add/update/remove are especially relevant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/export_mgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/exports.c -->
# sources/user-network-fs/nfs-ganesha/src/support/exports.c

## Purpose
`exports.c` parses, validates, commits, updates, logs, initializes, and releases NFS-Ganesha exports. It owns the export configuration grammar for `EXPORT`, `PSEUDOFS`, `EXPORT_DEFAULTS`, and `Client` blocks; computes effective permissions; connects exports to FSAL/MDCACHE; initializes export root objects; handles reread/update pruning; and checks request access/security against export and client policy.

## Important APIs, Types, And Functions
Global defaults are held in `export_opt` and the staging copy `export_opt_cfg`, protected by `export_opt_lock`. `GLOBAL_EXPORT_PERMS_INITIALIZER` sets built-in defaults such as anonymous ids, attr expiry, root squash, no access, default auth/transport inheritance, and no delegations.

Config and commit helpers:

- `StrExportOptions()`, `LogExportClientListEntry()`, `LogExportClients()`, `log_an_export()`, and `log_all_exports()` format export/client permissions.
- `client_init()`, `pseudofs_client_init()`, `client_commit()`, `export_client_allocator()`, `export_client_filler()`, and `client_adder()` build client lists with per-client permissions and HA proxy protocol matching mode.
- `fsal_cfg_commit()` loads/initializes an FSAL, calls `mdcache_fsal_create_export()`, attaches `export->fsal_export`, and clamps read/write sizes to FSAL maxima.
- `fsal_update_cfg_commit()` updates an existing FSAL export through `mdcache_fsal_update_export()` and handles delegation-option transition hooks for Ceph builds.
- `export_commit_common()` is the main validation and insertion/update routine for initial, add, and update commits.
- `pseudofs_fsal_commit()`, `pseudofs_commit()`, `add_export_commit()`, `update_export_commit()`, and `update_pseudofs_commit()` adapt common commit logic for block type.
- `export_defaults_commit()` atomically swaps parsed defaults into `export_opt`.

Runtime APIs:

- `ReadExports()` reads defaults, optional `PSEUDOFS`, all `EXPORT` blocks, creates a default pseudo-root if needed, and logs exports.
- `reread_exports()` serializes under `EXPORT_ADMIN_LOCK()`, reloads defaults/pseudo/exports using update descriptors, prunes defunct exports, and rebuilds PseudoFS.
- `exports_pkginit()` initializes root objects for all manager-registered exports and reverts failed ones.
- `init_export_root()` resolves the FSAL path, sets dynamic IO sizes, stores the root object, and records export-root state in the object junction.
- `nfs_export_get_root_entry()` returns a referenced root object and validates it is a directory.
- `release_export()` unlinks root state, unmounts PseudoFS when not config-only, marks stale, calls FSAL `prepare_unexport()` and `unexport()`, releases state, and removes the export from the manager.
- `free_export_resources()` releases client lists, FSAL exports/modules, QoS state, strings, refstrings, and temporary op context state.
- `export_check_security()`, `get_anonymous_uid()`, `get_anonymous_gid()`, and `export_check_access()` compute request authorization.

## Control Flow
Initial config load starts in `ReadExports()`. It derives default protocol bits from `NFS_options`, loads `EXPORT_DEFAULTS`, loads `PSEUDOFS`, loads each `EXPORT`, and then calls `build_default_root()` if neither export id 0 nor pseudo `/` exists. Each export block allocates a `gsh_export`, processes scalar parameters, processes `Client` blocks, processes the `FSAL` block last, and reaches `export_commit_common()`.

`export_commit_common()` validates pseudo path syntax, export id 0 rules, NFSv4 pseudo requirements, protocol/transport compatibility with core options, `mount_path_pseudo`, duplicate id/tag/pseudo/path rules, and FSAL availability. For new dynamic exports it initializes the export root and mounts into PseudoFS before manager insertion. For initial exports it inserts first and queues later mounting. For updates it fetches the existing export, rejects immutable tag/path/filesystem-id changes, detects pseudo or NFSv4 mountability changes, sets remount/prune flags, copies mutable fields into the existing export, and disposes of the staging export.

Runtime access checks use `export_check_access()`. It starts from no access, optionally matches a specific client entry from the export list or default client list, overlays export permissions, overlays `EXPORT_DEFAULTS`, and finally overlays built-in defaults. `export_check_security()` then validates RPC auth flavor and RPCSEC_GSS service against `op_ctx->export_perms`.

Reread uses a new parse generation. Updated exports receive the current generation. After parsing, `prune_pseudofs_subtree()`, `prune_defunct_exports()`, and `create_pseudofs()` remove older exports and remount changed/new reachable exports.

## State And Persistence Behavior
The file mutates in-memory export structures created from configuration. No on-disk persistence is written. `export_opt_cfg` is a staging object so default updates can be swapped into `export_opt` under `export_opt_lock`. Export fullpath and pseudopath have both config strings and RCU/refcounted `gsh_refstr` values; `copy_gsh_export()` swaps refstrings with `synchronize_rcu()` before releasing old values.

Per-export mutable options are split between atomic scalar fields (`MaxRead`, `MaxWrite`, preferred sizes, offsets, options) and fields protected by `exp_lock` (permissions, client lists, path refstrings, root/junction pointers). FSAL export lifetime is reference-balanced with `fsal_put()` and the FSAL export `release()` op. Root object lifetime is managed through object references, junction locks, `export_root_object_get/put()`, and `exp_root_refcount`.

## Dependencies And Integration Points
Major dependencies include `config_parsing`, `client_mgr` style client matching through `add_client()` and `client_match()`, `ip_utils` for address display and matching support, FSAL module lookup/load/update, MDCACHE FSAL stacking, PseudoFS mount/prune/create functions, pNFS utilities, NFS state cleanup, QoS optional code, HA proxy transport metadata, and global `op_ctx`.

The config descriptors exported from this file are used by DBus dynamic add/update paths in `export_mgr.c`. `ReadExports()` and `reread_exports()` are higher-level startup/reload entry points used by server initialization and SIGHUP/admin reload flows.

## Risks And Edge Cases
`valid_pseudopath()` returns false for `NULL`, and `export_commit_common()` calls it unconditionally before later logic that discusses exports without a pseudo path. If non-NFSv4 exports are still expected to support no `Pseudo`, this ordering makes pseudo path effectively mandatory and should be confirmed against intended behavior.

`export_check_client_options()` walks `exp->clients` without taking `exp->exp_lock` in the visible function. If callers do not already serialize, concurrent export update can race with client-list swapping.

`copy_gsh_export()` deliberately swaps client lists between the live export and staging export so later disposal frees old clients. This is subtle and tests should verify no double-free or stale pointer remains after update failures and successes.

The root object reference choreography in `init_export_root()` and `release_export()` is delicate: lookup references, extra root references, junction list membership, and two `put_ref()` calls must stay balanced across error and config-only cleanup paths.

HA proxy matching relies on `op_ctx->nfs_reqdata->svc.rq_xprt`. Callers invoking `export_check_access()` outside a normal request path must ensure `nfs_reqdata` is valid or that the client matching callback cannot dereference a null request.

## Test Signals
Strong signals include config tests for `EXPORT_DEFAULTS` overlay order, client block parsing, duplicate id/tag/pseudo/path handling, export id 0 constraints, no-pseudo non-v4 exports if supported, dynamic add/update/remount flows, reread generation pruning, FSAL create/update failure cleanup, root object reference cleanup under sanitizer, HA proxy client matching, auth flavor rejection, anonymous uid/gid fallback, and read access check policy formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/exports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/fridgethr.c -->
# sources/user-network-fs/nfs-ganesha/src/support/fridgethr.c

## Purpose
`fridgethr.c` implements Ganesha's "thread fridge": a POSIX-thread based worker/looper pool that can submit jobs, queue or reject overflow, pause, stop, restart, wake loopers, synchronously wait for transitions, and cancel workers during shutdown. It also defines the thread-local `op_ctx` pointer used by NFS operation and support threads.

## Important APIs, Types, And Functions
The companion header defines `struct fridgethr`, `struct fridgethr_entry`, `struct fridgethr_context`, `struct fridgethr_params`, `struct fridgethr_work`, `fridgethr_flavor_t`, `fridgethr_defer_t`, and `fridgethr_comm_t`.

Primary APIs:

- `fridgethr_init()` validates min/max/flavor/deferment/wake settings, initializes detached pthread attributes, locks, lists, command state, and name.
- `fridgethr_destroy()` waits for `frt_mtx` availability, destroys lock/attrs, and frees the fridge object.
- `fridgethr_submit()` dispatches to an idle worker, spawns a new detached worker, queues work, or returns `EWOULDBLOCK`/`EPIPE`.
- `fridgethr_wake()` signals all idle threads.
- `fridgethr_pause()`, `fridgethr_stop()`, and `fridgethr_start()` change command state and arrange completion callbacks.
- `fridgethr_sync_command()` wraps the transition APIs with a private mutex/condition and optional timeout.
- `fridgethr_populate()` starts a fixed number of identical workers for a pre-populated pool.
- `fridgethr_setwait()` and `fridgethr_getwait()` mutate/read runtime wait delay.
- `fridgethr_cancel()` force-cancels all recorded threads during shutdown.
- `general_fridge_init()` and `general_fridge_shutdown()` create and stop the global general-purpose fridge.

Internal functions:

- `fridgethr_start_routine()` is the worker entry point: registers RCU, names the thread, enables cancellation, calls optional initialize/finalize hooks, executes jobs in a loop, runs task cleanup, and freezes or exits.
- `fridgethr_freeze()` is the main state machine for waiting, queue draining, pause completion, timeout shrinkage, and stop exit.
- `fridgethr_dispatch()`, `fridgethr_spawn()`, `fridgethr_queue()`, `fridgethr_getwork()`, and `fridgethr_deferredwork()` implement scheduling mechanics.
- `fridgethr_finish_transition()` invokes transition callbacks and broadcasts completion.

## Control Flow
A submitted worker job enters `fridgethr_submit()`. If the fridge is stopped it fails. If paused or full it follows the configured deferment policy. Otherwise it prefers an idle thread by setting that thread context, marking `fridgethr_flag_dispatched`, and signaling its condition variable. If no idle thread exists and capacity remains, it spawns a detached pthread running `fridgethr_start_routine()`.

Each worker runs `ctx.func(ctx)`, optional `task_cleanup(ctx)`, and then `fridgethr_freeze()`. In worker flavor, freeze first drains queued work unless paused. Otherwise the thread joins `idle_q`, waits on its per-thread condition variable or timed wait, and returns either with dispatched work, queued work, or an instruction to exit. Timed-out idle workers above `thr_min` shrink the pool. Stop transitions decrement `nthreads` and the last exiting thread completes the transition.

Pause sets `command = fridgethr_comm_pause`, marks `transitioning`, stores callback state, and completes immediately if every thread is already idle. Stop wakes idle threads and, if no thread exists but queued work exists, starts one worker to drain cleanup paths. Start switches back to run, wakes idle threads, and may spawn up to a bounded number of workers for deferred jobs.

`fridgethr_sync_command()` issues one of the state transitions and waits until `fridgethr_trivial_syncer()` flips a stack-local `done` flag or until timeout.

## State And Persistence Behavior
All state is process-local. `frt_mtx` protects fridge command state, transition state, thread counts, idle and work queues, callback fields, and delay settings. Each worker also has `fre_mtx` and `fre_cv` for dispatch handoff. Threads are created detached. `thread_info` and `uflags` are deliberately left for caller use.

`op_ctx` is `__thread`, so each fridge worker has its own operation context pointer. Worker startup registers with userspace RCU (`rcu_register_thread()`), and exit unregisters. The global `general_fridge` is a queueing worker fridge with max 32 and no minimum.

## Dependencies And Integration Points
The module depends on pthreads, signals, userspace RCU, Ganesha memory helpers, glists, logging, and `nfs_core.h`. It is used by asynchronous support work such as delegation transitions and recall paths in export management, plus other server worker pools that need pause/stop semantics.

Callers integrate by providing functions of type `void (*)(struct fridgethr_context *)`, optional thread/task hooks, optional looper wake callbacks, and shutdown coordination through sync commands or direct pause/start/stop.

## Risks And Edge Cases
`fridgethr_populate()` adds `fe->thread_link` to `thread_list` without the visible `glist_init()` used by `fridgethr_spawn()`. On `pthread_create()` failure it also returns after destroying sync primitives without removing the list entry, decrementing `nthreads`, or freeing `fe`. This path should be reviewed.

`fridgethr_sync_command()` returns early on transition API errors without destroying its private mutex and condition variable, producing a small resource leak on invalid, busy, or already-in-state calls.

Threads are configured detached, but `fridgethr_cancel()` calls `pthread_join()` after `pthread_cancel()`. Joining detached threads is invalid on POSIX and the code ignores the return. Since this is shutdown-only, the risk is mostly noisy/undefined cleanup rather than normal operation, but it deserves scrutiny.

`fridgethr_start()` lacks the explicit mutex/condition pair validation present in pause/stop. Passing only one of `pmtx` or `cv` can create odd completion semantics.

Asynchronous cancellation is enabled in worker threads. This is intentional for forced shutdown, but it means cancellation can interrupt code while locks or external resources are held.

## Test Signals
Useful tests include submit-to-idle, spawn-up-to-max, queue-on-full, fail-on-full, timed shrink above `thr_min`, pause while jobs run, stop with idle threads, stop while queued and no threads exist, start after pause with queued work, looper wake behavior, sync timeout behavior, populate failure injection, and shutdown cancellation. Thread sanitizer or stress tests around dispatch/freezing are valuable because correctness depends on per-thread flags and two mutex layers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/fridgethr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/ip_utils.c -->
# sources/user-network-fs/nfs-ganesha/src/support/ip_utils.c

## Purpose
`ip_utils.c` provides address and CIDR utilities for Ganesha support code. It hashes, displays, parses, compares, and canonicalizes socket addresses; detects loopback and wildcard addresses; and implements a local replacement for the subset of libcidr behavior used by export/client matching and DBus compatibility.

## Important APIs, Types, And Functions
Socket-address helpers:

- `hash_sockaddr()` hashes IPv4, IPv6, and optionally VSOCK addresses, with optional port exclusion. IPv4 is hashed as IPv4-mapped IPv6 for consistency.
- `display_sockaddr_port()` formats IPv4, IPv6, VSOCK, and local Unix addresses into a `display_buffer`.
- `ip_str_to_sockaddr()` parses IPv4 or IPv6 strings into `sockaddr_t`.
- `sockaddr_cmp()` canonicalizes IPv4 addresses to IPv4-mapped IPv6 before comparing address and optionally port. It also supports VSOCK when compiled.
- `get_port()` extracts IPv4, IPv6, or VSOCK port values.
- `convert_ipv6_to_ipv4()` recognizes IPv4-mapped IPv6 addresses and writes canonical IPv4.
- `ipv4_to_ipv4_mapped_ipv6()` maps IPv4 into IPv6 form.
- `is_loopback()` and `is_inaddrany()` handle IPv4, IPv6, and IPv4-mapped IPv6 forms.

CIDR helpers:

- `cidr_alloc()` and `cidr_free()` allocate/free `CIDR`.
- `cidr_from_str()` parses `address[/mask]`, validates mask bounds, and defaults to /32 or /128.
- `cidr_to_str()` renders address plus prefix length.
- `cidr_contains_ip()` tests whether an address is inside a CIDR network.
- `cidr_from_inaddr()` and `cidr_from_in6addr()` build host CIDRs.
- `cidr_ipaddr_to_chars()` and `cidr_mask_to_chars()` provide legacy 16-byte array forms formerly supplied by libcidr.
- `cidr_family()`, `cidr_proto()`, and `cidr_version()` expose compatibility metadata.
- `cidr_equals()` compares CIDR objects.
- `normalize_v4_mapped_cidr()` converts IPv4-mapped IPv6 CIDRs into canonical IPv4 and adjusts masks.

## Control Flow
Address parsing first tries `inet_pton(AF_INET)`, then `inet_pton(AF_INET6)`. Comparisons map IPv4 inputs to IPv4-mapped IPv6 so mixed IPv4/IPv6 forms sort consistently. Display uses `inet_ntop()` for IP families and writes either `addr` or `addr:port`.

CIDR parsing copies the input into a bounded buffer, splits on `/`, parses the address with `ip_str_to_sockaddr()`, validates a numeric mask if present, or assigns host masks by family. Containment checks require matching address family, then compare full bytes and remaining prefix bits for IPv6 or shifted host-order integers for IPv4. Normalization is explicit; callers must invoke `normalize_v4_mapped_cidr()` before CIDR comparisons if they want mapped IPv6 to behave as IPv4.

## State And Persistence Behavior
The module has almost no mutable global state. `ten_bytes_all_0` is a static zero-filled prefix used to recognize IPv4-mapped IPv6 addresses. All CIDR objects are heap allocated through Ganesha memory helpers and owned by callers. Functions set `errno` to `EINVAL` or `ENAMETOOLONG` on parse/validation failures in CIDR paths and generally return negative comparator or error values for unsupported families.

## Dependencies And Integration Points
The file uses libc networking APIs (`inet_pton`, `inet_ntop`, byte-order helpers), Unix socket structures, optional Linux VSOCK support, Ganesha `display_buffer`, logging, and memory helpers. It integrates with export/client matching, DBus export display compatibility, logging, and any subsystem comparing caller or server socket addresses.

## Risks And Edge Cases
The IPv6 branch in `ip_str_to_sockaddr()` temporarily sets `sp->ss_family = AF_INET` before calling `convert_ipv6_to_ipv4()`, whose conversion check requires `AF_INET6`. As written, IPv4-mapped IPv6 strings may not canonicalize to IPv4 in that path and should be tested.

The `AF_VSOCK` case in `display_sockaddr_port()` uses a string format for `svm_cid` even though the value is numeric. Builds with `RPC_VSOCK` should review this format string.

`cidr_mask_to_chars()` writes `chars[i]` after the full-byte loop even when `mask_bits == 0`. For `/32` IPv4 and `/128` IPv6, `i` can be 16, which is outside the documented 16-byte output buffer.

`cidr_contains_ip()` uses signed `int` for host-order IPv4 values. Networks with the high bit set can be affected by implementation-defined right shifts. `uint32_t` would be safer.

`cidr_equals()` requires exact socket-address equality after family and mask checks. Its comment describes network equivalence, but the implementation does not ignore host bits within the mask. For example, two separately constructed `/24` CIDRs with different host bits will not compare equal.

`cidr_contains_ip()` rejects family mismatches, so callers must normalize IPv4-mapped IPv6 CIDRs and addresses before containment checks when mixed representations are possible.

## Test Signals
High-value tests include IPv4, IPv6, IPv4-mapped IPv6 parsing and normalization; loopback and wildcard detection for native and mapped forms; `sockaddr_cmp()` with and without ports; hash equality expectations for IPv4 versus mapped IPv6; CIDR parsing with invalid masks and long strings; containment for `/0`, `/1`, `/31`, `/32`, `/127`, and `/128`; legacy char-array output bounds under ASAN; VSOCK formatting when enabled; and `cidr_equals()` behavior for same-network but different-host inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/support/ip_utils.c -->
