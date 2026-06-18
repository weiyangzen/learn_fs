# Research Report: subset-b-005735

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.c

Purpose: implements OCFS2 DLM lock conversion, both when the local node masters the lock resource and when the request must be forwarded to a remote master. It changes a granted lock from one mode to another, preserves DLM queue ordering, carries lock value block (LVB) get/put semantics, and exposes the network handler for `DLM_CONVERT_LOCK_MSG`.

Important APIs and functions: `dlmconvert_master()` is the local-master entry used by `dlmlock()` for `LKM_CONVERT`; it serializes on `res->spinlock`, reserves an AST slot, marks `DLM_LOCK_RES_IN_PROGRESS`, delegates to `__dlmconvert_master()`, and then queues the AST or releases the reservation. `__dlmconvert_master()` is the core queue transition routine. `dlm_revert_pending_convert()` moves a failed conversion back to the granted list and clears conversion/LVB flags. `dlmconvert_remote()` performs the secondary-node path and records `convert_pending` while waiting for the remote response. `dlm_send_remote_convert_request()` builds `struct dlm_convert_lock`, optionally sends an LVB kvec, and maps network errors to DLM status. `dlm_convert_lock_handler()` is the master-side o2net callback that validates the message, finds the remote lock by node/cookie, applies LVB flags, and runs the same master conversion logic.

Control flow: local conversion starts with `dlmconvert_master()`: wait for the lockres, reserve AST capacity, set `IN_PROGRESS`, run `__dlmconvert_master()`, clear `IN_PROGRESS`, wake waiters, and then queue an AST only when conversion was granted immediately. In `__dlmconvert_master()`, the lock must not already have `ml.convert_type` set and must be on `res->granted`. Downconverts (`type <= current type`) are granted in place. Upconverts scan both granted and converting queues for compatibility; if compatible, the lock mode is changed immediately and the lock is moved to the tail of granted; otherwise `LKM_NOQUEUE` returns `DLM_NOTQUEUED`, while normal requests set `ml.convert_type` and move the lock to the converting queue. Remote conversion mirrors this locally by moving the secondary lock to converting before sending the message, then reverts if the master refuses or recovery intervenes.

State and persistence behavior: all state is volatile kernel DLM state. Conversion mutates `struct dlm_lock` fields (`ml.type`, `ml.convert_type`, `convert_pending`, LKSB status/flags) and `struct dlm_lock_resource` queues (`granted`, `converting`) under `res->spinlock` and `lock->spinlock`. LVB state is copied from `lock->lksb->lvb` into `res->lvb` on EX-mode PUT conversions and fetched later through AST completion when GET is requested. `DLM_LOCK_RES_IN_PROGRESS` and `res->wq` serialize competing local operations and recovery/migration state transitions.

Dependencies and integration points: depends on `dlmcommon.h` queue helpers, lock compatibility, AST reservation/queueing, `dlm_kick_thread()`, lockres state-to-status conversion, and lock/debug printing. It integrates with `dlmlock.c` for public conversion entry, `dlmdomain.c` network handler registration, `dlmmaster.c` recovery/migration state, and o2net for `DLM_CONVERT_LOCK_MSG`. It also relies on OCFS2 cluster heartbeat status via `dlm_is_host_down()` and `dlm_wait_for_node_death()`.

Risks: the file is sensitive to lock ordering: only `__dlmconvert_master()` expects `res->spinlock` held on entry and returns with it held. Failing to clear LVB flags on rejected paths can cause stale value block operations. A remote master can die after accepting a conversion but before AST delivery, so the `convert_pending` check intentionally returns `DLM_RECOVERING` to force retry. Incorrect compatibility scans can starve older conversions or grant incompatible modes. The handler assumes lock cookies and node ids uniquely identify the granted lock; stale secondary state returns `DLM_IVLOCKID`.

Test signals: exercise local downconvert and upconvert, incompatible upconvert queueing, `LKM_NOQUEUE` rejection, repeated conversion denial, EX-mode `LKM_VALBLK` PUT, PR/NL GET-LVB conversion, remote convert success, remote `DLM_RECOVERING`/`DLM_MIGRATING` retry, master-side invalid name/flags/cookie handling, and recovery during accepted-but-not-ASTed conversions. Lockdep, KASAN, and DLM debug output should show balanced AST reservations and correct granted/converting list membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.h

Purpose: declares the two conversion entry points used outside `dlmconvert.c`: one for resources mastered locally and one for resources mastered by another node.

Important APIs and types: `dlmconvert_master(struct dlm_ctxt *dlm, struct dlm_lock_resource *res, struct dlm_lock *lock, int flags, int type)` performs conversion against a locally mastered lock resource. `dlmconvert_remote(...)` performs the secondary-node path and sends a network conversion request to the current owner. The declarations rely on DLM core types and `enum dlm_status` from the included DLM common/API headers in callers.

Control flow: this header has no executable control flow. It defines the compile-time contract consumed mainly by `dlmlock.c`, allowing `dlmlock()` to dispatch `LKM_CONVERT` based on `res->owner == dlm->node_num`.

State and persistence behavior: no state is stored in the header. The functions it exposes mutate runtime lock and lock-resource queue state only in memory.

Dependencies and integration points: included by `dlmlock.c` and implemented by `dlmconvert.c`. It is part of the internal OCFS2 DLM interface, not a public exported symbol interface.

Risks: prototypes must stay consistent with the implementation and with `dlmlock()` dispatch assumptions. Since conversion status is returned as `enum dlm_status`, callers must preserve DLM-specific retry semantics such as `DLM_RECOVERING`, `DLM_MIGRATING`, `DLM_FORWARD`, and `DLM_NOTQUEUED`.

Test signals: build coverage with OCFS2 DLM enabled is the primary signal. Conversion tests in `dlmlock()` should cover both declared paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmconvert.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.c

Purpose: provides diagnostic printing and debugfs views for OCFS2 DLM domains, lock resources, locks, master-list entries (MLEs), purge lists, and DLM state. It also maps `enum dlm_status` values to stable strings for callers.

Important APIs and functions: exported helpers are `dlm_print_one_lock()`, `dlm_errname()`, and the debugfs lifecycle routines declared in `dlmdebug.h`. `dlm_print_one_lock_resource()` and `__dlm_print_one_lock_resource()` dump owner/state, refmap, queue contents, AST/BAST state, and lock cookies. `dump_mle()` and `dlm_print_one_mle()` render MLE type, current/new master, heartbeat attachment, refcount, and node maps. Under `CONFIG_DEBUG_FS`, `dlm_debug_init()` creates per-domain files `dlm_state`, `locking_state`, `mle_state`, and `purge_list`; `dlm_create_debugfs_root()` creates the global `o2dlm` root.

Control flow: print helpers take the relevant spinlocks, stringify lock names, and walk queue/list structures. The debugfs single-page files (`dlm_state`, `mle_state`, `purge_list`) allocate one page at open time, snapshot current state into it, set inode size, and serve it through `simple_read_from_buffer()`. `locking_state` uses seq_file state in `struct debug_lockres` to iterate one tracked lock resource at a time; each `seq_start` advances through `dlm->tracking_list`, takes a reference to the selected lockres, dumps it under `res->spinlock`, and drops the previous reference.

State and persistence behavior: the module does not persist DLM state; it snapshots in-memory structures into temporary pages or seq buffers. `dlm_errnames[]` is static read-only mapping data. Debugfs dentries live for the module/domain lifetime. `debug_lockres` pins a `dlm_ctxt` with `dlm_grab()` and pins the current lockres while a seq file is open, releasing both on close.

Dependencies and integration points: integrates with Linux debugfs, seq_file, simple read helpers, OCFS2 mask logging, DLM lock/resource/MLE structures, and DLM domain tracking lists. `dlmmaster.c` and error paths call `dlm_print_one_mle()` and lock-resource printers to explain invariant failures. `dlmdomain.c` invokes the debugfs init/destroy hooks at module and domain creation/destruction.

Risks: debug code runs while holding spinlocks and must not sleep in those regions. Single-page debugfs snapshots can truncate large domains, so output is useful but not exhaustive under heavy load. `stringify_lockname()` embeds OCFS2 lock-name format knowledge and may misrepresent future formats. The seq iterator only emits one lockres per read iteration via a custom tracking cursor; reference accounting around `dl_res` is critical to avoid use-after-free when resources are purged while debugfs is open.

Test signals: mount with `CONFIG_DEBUG_FS=y`, inspect `/sys/kernel/debug/o2dlm/<domain>/dlm_state`, `locking_state`, `mle_state`, and `purge_list` during idle, active lock traffic, conversion, migration, and recovery. Validate disabled-debugfs builds use stubs. Exercise `dlm_errname()` for valid and out-of-range statuses and check lockdep under concurrent resource purge plus debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.h

Purpose: declares the OCFS2 DLM debugging interface and provides no-op debugfs hooks when debugfs support is disabled.

Important APIs and types: `dlm_print_one_mle()` is always declared for diagnostic paths in mastering/recovery code. When `CONFIG_DEBUG_FS` is enabled, `struct debug_lockres` stores seq-file iteration state (`dl_len`, `dl_buf`, pinned `dl_ctxt`, and current `dl_res`) and the header declares `dlm_debug_init()`, `dlm_create_debugfs_subroot()`, `dlm_destroy_debugfs_subroot()`, `dlm_create_debugfs_root()`, and `dlm_destroy_debugfs_root()`. When debugfs is disabled, those lifecycle hooks compile to empty inline functions.

Control flow: no runtime control flow beyond the inline stubs. The header lets domain setup and teardown call debugfs hooks unconditionally, with build-time selection deciding whether files are created.

State and persistence behavior: only `struct debug_lockres` describes state, and that state exists per open debugfs seq file. The disabled path stores no state.

Dependencies and integration points: implemented by `dlmdebug.c`, consumed by `dlmdomain.c` for debugfs lifecycle and by `dlmmaster.c` for MLE diagnostics. It depends on DLM core type declarations being visible before inclusion.

Risks: any changes to `struct debug_lockres` must stay synchronized with the seq operations in `dlmdebug.c`. Stub behavior must remain side-effect free so domain lifecycle code is identical across debugfs and non-debugfs builds.

Test signals: compile both `CONFIG_DEBUG_FS=y` and `CONFIG_DEBUG_FS=n`; with debugfs enabled, verify per-domain files appear and disappear as domains are registered/unregistered; with it disabled, verify domain lifecycle links without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.c

Purpose: owns OCFS2 DLM domain lifecycle: module initialization, global join-message handlers, per-domain context allocation, join negotiation, heartbeat/node-info validation, per-domain network handler registration, graceful leave, lock migration before shutdown, and eviction callback registration.

Important APIs and functions: public/exported APIs are `dlm_register_domain()`, `dlm_unregister_domain()`, `dlm_setup_eviction_cb()`, `dlm_register_eviction_cb()`, `dlm_unregister_eviction_cb()`, and `dlm_fire_domain_eviction_callbacks()`. Lockres lookup helpers include `__dlm_insert_lockres()`, `__dlm_unhash_lockres()`, `__dlm_lookup_lockres_full()`, `__dlm_lookup_lockres()`, and `dlm_lookup_lockres()`. Context lifetime helpers include `dlm_grab()`, `dlm_put()`, and `dlm_domain_fully_joined()`. Join protocol functions include `dlm_query_join_handler()`, `dlm_request_join()`, `dlm_try_to_join_domain()`, `dlm_assert_joined_handler()`, `dlm_cancel_join_handler()`, `dlm_send_nodeinfo()`, and `dlm_send_regions()`. Shutdown functions include `dlm_begin_exit_domain()`, `dlm_leave_domain()`, `dlm_migrate_all_locks()`, and `dlm_complete_dlm_shutdown()`.

Control flow: module init creates MLE, lockres, and lock caches, registers global join handlers keyed by `DLM_MOD_KEY`, and creates the debugfs root. `dlm_register_domain()` either reuses an already joined context with compatible filesystem locking protocol or allocates a new `dlm_ctxt`, inserts it in `dlm_domains`, registers per-domain handlers, launches DLM/recovery threads, creates a workqueue/debugfs subroot, and repeatedly calls `dlm_try_to_join_domain()`. Joining snapshots heartbeat live nodes, sends `DLM_QUERY_JOIN_MSG` to peers, negotiates DLM and filesystem protocol minor versions, validates node configuration and heartbeat regions for protocol >= 1.1, sends join assertions, and marks the context `DLM_CTXT_JOINED`. If join fails after peers responded, cancel messages clear their `joining_node` state.

State and persistence behavior: state is in memory under `struct dlm_ctxt`: domain name/key, negotiated protocol versions, node number, `domain_map`, `live_nodes_map`, `recovery_map`, `exit_domain_map`, lockres/master hash page vectors, lists for dirty/purge/recovery/tracking/work, worker/recovery threads, join state, counters, and eviction callbacks. `dlm_domain_lock` protects the global domain list and context state transitions, while `dlm->spinlock` protects domain maps and join/recovery fields. No on-disk state is persisted; peers reconstruct membership and lock ownership through messages and recovery.

Dependencies and integration points: depends on o2net for all DLM network message registration and send paths, o2hb heartbeat callbacks and region queries, o2nm node configuration, DLM lock/master/recovery/AST subsystems registered as per-domain handlers, debugfs hooks, Linux workqueues, module init/exit, and OCFS2 filesystem protocol negotiation. The file registers message handlers implemented in `dlmlock.c`, `dlmconvert.c`, `dlmunlock.c`, `dlmast.c`, `dlmmaster.c`, and recovery modules.

Risks: join serialization is delicate. Parallel joins are blocked with `joining_node`, domain maps must match peer live maps, and protocol minor negotiation must downgrade consistently. Error paths during join must unregister handlers, stop threads, destroy workqueues, and send cancel messages without leaving peers stuck. Shutdown must mark `IN_SHUTDOWN`, inform peers, migrate or purge all lock resources, reject new joins at the right phase, and force-free remaining MLEs only after the domain map is empty. Lock ordering is documented explicitly and violations can deadlock (`dlm_domain_lock`, `dlm->spinlock`, lockres, `master_lock`, `ast_lock`, MLE, lock). Debugfs and context freeing must handle partially joined domains.

Test signals: multi-node domain join, simultaneous join races, protocol minor downgrade and mismatch rejection, global heartbeat region mismatch, node IP/port mismatch, join cancellation on failure, `DLM_BEGIN_EXIT_DOMAIN_MSG` behavior with protocol 1.2+, graceful unregister with remote locks requiring migration, repeated register/unregister of same domain, signal interruption during join backoff, debugfs root/subroot lifecycle, module init unwind failures, and eviction callback ordering before recovery completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.h -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.h

Purpose: exposes minimal domain-state helpers and global domain list symbols for OCFS2 DLM internals.

Important APIs and types: declares `dlm_domain_lock` and `dlm_domains`, defines inline `dlm_joined()` and `dlm_shutting_down()` predicates, and declares `dlm_fire_domain_eviction_callbacks()`. `dlm_joined()` tests `DLM_CTXT_JOINED`; `dlm_shutting_down()` tests `DLM_CTXT_IN_SHUTDOWN`; both take `dlm_domain_lock`.

Control flow: only the two inline predicates execute code. They acquire the global domain lock, inspect `dlm->dlm_state`, and release the lock.

State and persistence behavior: no state is owned by the header; it exposes the global domain lock/list defined in `dlmdomain.c` and reads volatile `dlm_ctxt` state.

Dependencies and integration points: used by DLM modules that need to test domain membership or shutdown state without duplicating locking rules. The eviction callback declaration lets recovery/domain code notify filesystem consumers of node eviction.

Risks: these helpers intentionally expose coarse state checks; callers needing `DLM_CTXT_IN_SHUTDOWN` to count as fully usable should use `dlm_domain_fully_joined()` instead. The global symbols should only be manipulated according to the lock ordering documented in `dlmdomain.c`.

Test signals: compile coverage and behavior checks around join/shutdown transitions, especially paths that should reject new operations in shutdown but still accept certain network messages while leaving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmlock.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmlock.c

Purpose: implements OCFS2 DLM lock creation and the exported `dlmlock()` API. It allocates locks, assigns cookies, finds or masters lock resources, grants or queues locks on the master, sends remote create-lock requests on secondaries, and handles incoming `DLM_CREATE_LOCK_MSG` messages.

Important APIs and functions: `dlm_init_lock_cache()`/`dlm_destroy_lock_cache()` manage the `o2dlm_lock` slab. `dlmlock()` is exported and handles both new locks and conversions. `dlmlock_master()` grants or queues a lock on a locally mastered resource. `dlmlock_remote()` records a secondary blocked lock and sends `DLM_CREATE_LOCK_MSG` to the owner. `dlm_create_lock_handler()` creates the master-side representation for a remote lock. `dlm_new_lock()`, `dlm_lock_get()`, `dlm_lock_put()`, `dlm_lock_attach_lockres()`, and `dlm_lock_release()` manage lock lifetime. `dlm_revert_pending_lock()` unwinds failed remote creation.

Control flow: a new `dlmlock()` validates mode, flags, name length, and recovery-lock constraints, allocates a lock cookie with the local node in the high byte, allocates `struct dlm_lock`, waits for recovery unless this is a recovery lock, and obtains a lock resource through `dlm_get_lock_resource()`. If this node owns the resource, `dlmlock_master()` checks compatibility against granted and converting queues, grants immediately with AST if possible, queues on blocked if allowed, or returns `DLM_NOTQUEUED`. If another node owns the resource, `dlmlock_remote()` adds the lock locally to the blocked queue with `lock_pending`, sends a create request, reverts on failure, or manually grants the special `$RECOVERY` lock. Convert requests in `dlmlock()` validate the original lock callbacks/LKSB and dispatch to `dlmconvert_master()` or `dlmconvert_remote()`.

State and persistence behavior: lock state is entirely in memory. `struct dlm_lock` stores mode, conversion mode, node, cookie, callback pointers, AST/BAST pending bits, operation pending bits, list linkage, LKSB, and a kref. Locks hold references to their lock resource while attached. Lock resource queues (`granted`, `blocked`, `converting`) define the effective DLM state. The global `dlm_next_cookie` is protected by `dlm_cookie_lock` and wraps within the low 56 bits.

Dependencies and integration points: relies on `dlmmaster.c` for `dlm_get_lock_resource()`, inflight refs, migration/recovery ownership, and lockres lifetime; `dlmconvert.c` for conversions; DLM thread/AST code for callback delivery; o2net for create-lock messages; DLM common helpers for compatibility and queue/list text; and domain handler registration in `dlmdomain.c`.

Risks: remote create has a two-sided state transition: the secondary queues a local lock before the master accepts, so failures must remove the list entry and drop the extra ref exactly once. The `$RECOVERY` lock is special because AST delivery may be frozen, so manual grant logic must remain isolated. `dlmlock()` retries on recovery/migration/forward states with sleeps, which can hide livelock if ownership never stabilizes. Public conversion requests must use the same callbacks and LKSB as the original lock; otherwise AST delivery could target inconsistent state. Lock release BUGs if any queue or AST/BAST list still references the lock, making cleanup regressions immediately fatal.

Test signals: basic EX/PR/NL lock acquisition, incompatible lock queueing, `LKM_NOQUEUE`, remote lock grant and refusal, recovery-lock acquisition, cookie uniqueness and wrap warnings, invalid mode/flag/name checks, conversion argument mismatch, recovery/migration retry paths, master-side create handler invalid domain/name/recovering state, LKSB status propagation on errors, and slab lifetime under stress lock/unlock cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmmaster.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmmaster.c

Purpose: implements OCFS2 DLM lock-resource mastering, master-list-entry coordination, lock-resource allocation/lifetime, mastery assertions, mastery reference tracking, dereference handshakes, migration, and cleanup when nodes die. This file is the core distributed ownership state machine for lock resources.

Important APIs and functions: cache/lifetime APIs include `dlm_init_mle_cache()`, `dlm_destroy_mle_cache()`, `dlm_init_master_caches()`, `dlm_destroy_master_caches()`, `dlm_new_lockres()`, and `dlm_lockres_put()`. Mastering APIs include `dlm_get_lock_resource()`, `dlm_master_request_handler()`, `dlm_assert_master_handler()`, `dlm_assert_master_post_handler()`, and `dlm_dispatch_assert_master()`. Refmap APIs include `dlm_lockres_set_refmap_bit()`, `dlm_lockres_clear_refmap_bit()`, `dlm_drop_lockres_ref()`, `dlm_deref_lockres_handler()`, and `dlm_deref_lockres_done_handler()`. Migration/recovery APIs include `dlm_empty_lockres()`, `dlm_finish_migration()`, `dlm_migrate_request_handler()`, `dlm_clean_master_list()`, `dlm_force_free_mles()`, and AST reservation helpers `__dlm_lockres_reserve_ast()`/`dlm_lockres_release_ast()`.

Control flow: `dlm_get_lock_resource()` first looks up an existing lockres, waiting if owner is unknown or purge is in progress, and grabs an inflight ref before returning. If none exists, it allocates a lockres and MLE. `LKM_LOCAL` makes the local node owner immediately. Otherwise it checks the master hash for a blocking or migration MLE, creates a `DLM_MLE_MASTER` when this node will participate in mastery, inserts the lockres while still `IN_PROGRESS`, sends `DLM_MASTER_REQUEST_MSG` to voting peers, and waits in `dlm_wait_for_lock_mastery()`. The lowest maybe-voter becomes master after all responses and then asserts mastery across the domain with `DLM_ASSERT_MASTER_MSG`; peers use assert handling to set owners, clear MLEs, and report whether they hold a mastery reference.

State and persistence behavior: MLEs are in-memory coordination records keyed by lock name and type (`BLOCK`, `MASTER`, `MIGRATION`) with node maps (`node_map`, `vote_map`, `response_map`, `maybe_map`), master/new-master fields, heartbeat attachment, waitqueue, `woken`, `inuse`, and kref. Lock resources store owner, state bits, queues, LVB, refmap, inflight counts, AST reservations, dirty/recovery/purge/tracking linkage, and kref. Refmap bits tell the master which remote nodes have a mastery reference. Inflight refs pin resources while lock acquisition is in progress; inflight assert workers pin resources while asynchronous assertion work runs.

Dependencies and integration points: depends on o2net message types for master request/assert, deref, migrate request, and migration lockres transfer; heartbeat/domain maps from `dlmdomain.c`; recovery cleanup via `dlm_clean_master_list()` and recovery list movement; DLM thread dirty/purge handling via `dlm_lockres_calc_usage()` and `dlm_kick_thread()`; AST queues and migration barriers; and lock serialization helpers in `dlmcommon.h`. It interacts directly with `dlmlock.c` through lockres lookup and with domain unregister through `dlm_empty_lockres()`.

Risks: this file has the highest concurrency risk in the subset. MLE refcounts are manipulated under both `dlm->spinlock` and `dlm->master_lock`, with extra refs for blocked/migration cases; missed puts leak MLEs while extra puts free waiters. Mastery can restart when heartbeat node maps change; bad restart logic can elect two masters or leave owner unknown. Assert-master responses can request reassertion and mastery-ref updates, so refmap correctness depends on multi-round messaging. Deref requests arriving while `DLM_LOCK_RES_SETREF_INPROG` are deferred to workqueue and completed with `DLM_DEREF_LOCKRES_DONE`; mishandling can purge resources before ref bits settle. Migration must flush ASTs, block dirtying, set `MIGRATING` only when no ASTs remain, transfer lock state, notify all peers, and handle old/new master death. Numerous `BUG()` calls intentionally fail fast on impossible distributed states.

Test signals: concurrent first lock acquisition for the same name from multiple nodes, master request MAYBE/NO/YES paths, node death during mastery voting, assert-master cleanup and reassert, resource purge/deref with protocol 1.3 `DLM_DEREF_LOCKRES_DONE`, lockres migration during domain leave, migration target death, old master death during migration, recovery cleanup of `BLOCK` and `MIGRATION` MLEs, refmap bit accounting, AST reservation blocking migration, debugfs MLE visibility, and lockdep/KCSAN/KASAN stress under multi-node join/leave and lock churn.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmmaster.c -->
