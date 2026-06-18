# Group Research: group_1053_linux_stable_sources_os_linux_linux_stable_fs_ocfs2_dlm_dlmconvert__f312e10bdeeb

Scope: `Docs/research_subset_a.md`

This grouped report covers the requested OCFS2 DLM source files under `sources/os/linux/linux-stable/fs/ocfs2/dlm/`. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.c

## Purpose

`dlmconvert.c` implements OCFS2 DLM lock conversion: changing an already granted lock from one mode to another, either on the local lock-resource master or by sending a remote convert request to the master node.

It is responsible for moving locks between the granted and converting queues, preserving lock value block behavior, reserving/releasing AST capacity, and coordinating retry semantics when recovery or migration interrupts conversion.

## Main Entry Points

- `dlmconvert_master()` handles conversion when the local node owns the lock resource.
- `dlmconvert_remote()` handles conversion when another node owns the lock resource.
- `dlm_convert_lock_handler()` handles `DLM_CONVERT_LOCK_MSG` on the master node.
- `dlm_revert_pending_convert()` restores a failed pending conversion to the granted queue.

The central implementation is `__dlmconvert_master()`, which requires `res->spinlock` held on entry and keeps it held on exit.

## Conversion Logic

`__dlmconvert_master()` enforces two key preconditions before conversion:

- The lock must not already have `ml.convert_type` set.
- The lock must be present on the lock resource granted queue.

Downconverts are granted immediately because the requested mode is less restrictive than or equal to the current mode. Upconverts are granted only if compatible with all other granted locks and all converting locks, including their requested conversion modes. Existing conversion requests take precedence.

If the upconvert cannot be granted immediately:

- `LKM_NOQUEUE` returns `DLM_NOTQUEUED`.
- Otherwise, the lock is moved from `res->granted` to `res->converting`, and `lock->ml.convert_type` records the requested mode.

Immediate grants update `lock->ml.type`, set `lksb->status = DLM_NORMAL`, move the lock to the tail of the granted list, and request AST delivery.

## LVB Handling

The file handles lock value block flags during conversion:

- Converting from `LKM_EXMODE` with `LKM_VALBLK` sets `DLM_LKSB_PUT_LVB` and copies the caller LVB into `res->lvb` on grant.
- Converting from `LKM_PRMODE` or `LKM_NLMODE` to a mode above `LKM_NLMODE` sets `DLM_LKSB_GET_LVB`.
- Converting to `LKM_NLMODE` clears `LKM_VALBLK` because there is no LVB fetch.

Remote conversion translates local LVB intent into wire flags `LKM_PUT_LVB` or `LKM_GET_LVB`.

## Remote Path

`dlmconvert_remote()` waits for the lock resource to be idle, rejects conversion during recovery, moves the local lock to the converting queue, marks `convert_pending`, and sends `DLM_CONVERT_LOCK_MSG`.

After the remote response:

- Non-normal status reverts the local queue move.
- `DLM_NOTQUEUED` is treated as a legitimate non-grant result.
- If the master returned success but recovery already moved the lock back, the function returns `DLM_RECOVERING` to retry.
- `convert_pending` is cleared before exit.

`dlm_send_remote_convert_request()` sends either a single convert message or a two-element vector when an LVB is being pushed.

## Network Handler

`dlm_convert_lock_handler()` runs on the lock-resource master. It validates the domain, name length, LVB flags, and resource state. It looks up the target lock on the granted queue by cookie and node, applies LVB get/put flags to the lock status block, reserves an AST, marks the lock resource in progress, and calls `__dlmconvert_master()`.

On failure it clears transient LVB flags. On success it either queues the AST or releases the reserved AST.

## Concurrency And Invariants

The file’s locking contract is explicit:

- Only `__dlmconvert_master()` requires `res->spinlock` held across entry and exit.
- Other entry points acquire and release locks internally.
- `DLM_LOCK_RES_IN_PROGRESS` serializes conversion with other resource operations.
- AST reservation via `__dlm_lockres_reserve_ast()` must be balanced by either `dlm_queue_ast()` or `dlm_lockres_release_ast()`.

Important invariants:

- A converting lock has `ml.convert_type != LKM_IVMODE`.
- A non-converting lock has `ml.convert_type == LKM_IVMODE`.
- Failed pending conversions must be restored to `res->granted`.
- Conversion is only legal for locks already granted.

## Dependencies

This file depends on:

- Lock resource and lock structures from `dlmcommon.h`.
- AST queuing and migration barriers from the wider DLM implementation.
- Network messaging through `o2net_send_message_vec()`.
- Master/resource behavior implemented in `dlmmaster.c`.
- Lock creation and public locking API behavior in `dlmlock.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.h

## Purpose

`dlmconvert.h` declares the two conversion entry points used by the lock path.

## API

- `dlmconvert_master(struct dlm_ctxt *dlm, struct dlm_lock_resource *res, struct dlm_lock *lock, int flags, int type)`
- `dlmconvert_remote(struct dlm_ctxt *dlm, struct dlm_lock_resource *res, struct dlm_lock *lock, int flags, int type)`

The caller chooses the function based on whether `res->owner == dlm->node_num`.

## Role In The DLM

This header is consumed by `dlmlock.c`, where `dlmlock()` routes `LKM_CONVERT` requests to the local or remote conversion path. It keeps conversion internals separated from general lock creation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.c

## Purpose

`dlmdebug.c` provides diagnostic dumping and debugfs support for OCFS2 DLM state. It can print individual lock resources and locks, map DLM status codes to names, stringify lock names and node maps, and expose debugfs files for domain state, lock resources, master-list entries, and purge-list contents.

## Non-debugfs Diagnostics

Key functions:

- `dlm_print_one_lock_resource()` prints one lock resource with locking.
- `__dlm_print_one_lock_resource()` prints a lock resource while `res->spinlock` is already held.
- `dlm_print_one_lock()` exports lock-resource printing through a lock pointer.
- `dlm_errname()` exports human-readable names for `enum dlm_status`.
- `dlm_print_one_mle()` formats a master-list entry into a temporary page buffer.

The lock-resource dump includes:

- Lock name, owner, state, last-used timestamp, kref count.
- Purge, dirty, recovery, and migration flags.
- Inflight lock count and reserved AST count.
- Refmap nodes.
- Granted, converting, and blocked queues.
- Per-lock mode, convert mode, node, cookie, kref, AST/BAST state, and pending operation flags.

## Formatting Helpers

`stringify_lockname()` mostly emits the raw lock name, but has OCFS2-specific handling for names beginning with `N`, where it decodes an inode block number embedded in the name. This knowingly reaches beyond generic DLM semantics to make debug output more useful for OCFS2.

`stringify_nodemap()` emits set node numbers from a bitmap.

`dump_mle()` formats an MLE with:

- Lock name.
- Type: block, master, or migration.
- Current master and new master.
- Heartbeat event attachment.
- In-use flag and reference count.
- Maybe, vote, response, and node maps.

## Debugfs Files

When `CONFIG_DEBUG_FS` is enabled, the module creates a root directory named `o2dlm`, with one subdirectory per domain. Each domain gets:

- `dlm_state`
- `locking_state`
- `mle_state`
- `purge_list`

`dlm_state` prints domain-level information: key, negotiated protocol, thread pids, node number, DLM state, join state, domain maps, live maps, lock-resource and MLE counts, dirty/purge/AST lists, purge count, refcount, dead node, recovery master, recovery state, recovery map, and per-node recovery state.

`locking_state` is seq-file based and iterates `dlm->tracking_list`, dumping one lock resource at a time in a structured format with `NAME`, `LRES`, `RMAP`, `LVBX`, and `LOCK` records.

`mle_state` dumps all MLEs across the master hash and reports total count and longest bucket.

`purge_list` dumps lock resources on the purge list and their age in seconds.

## Concurrency

The debug code uses the same lock hierarchy as the DLM core:

- `dlm->spinlock` for domain state.
- `dlm->master_lock` for MLE hash traversal.
- `dlm->track_lock` for tracking list iteration.
- `res->spinlock` for lock-resource internals.
- `lock->spinlock` for individual lock state.

The lock-resource seq iterator holds and releases references across iterations to avoid use-after-free while walking the tracking list.

## Dependencies

This file depends heavily on structures and helpers from `dlmcommon.h`, plus debugfs, seq_file, kref, and OCFS2 cluster node/heartbeat infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.h

## Purpose

`dlmdebug.h` declares DLM debug helpers and provides debugfs setup/teardown APIs, with no-op stubs when `CONFIG_DEBUG_FS` is disabled.

## API

Always declared:

- `dlm_print_one_mle(struct dlm_master_list_entry *mle)`

With `CONFIG_DEBUG_FS`:

- `struct debug_lockres`
- `dlm_debug_init(struct dlm_ctxt *dlm)`
- `dlm_create_debugfs_subroot(struct dlm_ctxt *dlm)`
- `dlm_destroy_debugfs_subroot(struct dlm_ctxt *dlm)`
- `dlm_create_debugfs_root(void)`
- `dlm_destroy_debugfs_root(void)`

Without debugfs, the setup and teardown functions compile as empty inline stubs.

## Role In The DLM

This header lets domain setup and teardown call debugfs functions unconditionally while preserving builds without debugfs support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.c

## Purpose

`dlmdomain.c` implements OCFS2 DLM domain lifecycle management: module initialization, domain allocation, domain join, protocol negotiation, heartbeat integration, network handler registration, domain leave, shutdown migration, and eviction callbacks.

A DLM domain is the cluster-wide context in which lock resources, master-list entries, recovery, ASTs, and network messages operate.

## Global State And Protocol

Global domain state:

- `dlm_domain_lock` protects `dlm_domains` and domain state transitions.
- `dlm_domains` tracks active domain contexts.
- `dlm_domain_events` wakes waiters during registration and teardown.

The supported DLM protocol is major `1`, minor `3`. The comments document additions in minor versions:

- `1.1`: heartbeat region query and nodeinfo query.
- `1.2`: begin-exit-domain message.
- `1.3`: deref-lockres-done message.

`dlm_protocol_compare()` requires equal major versions and negotiates down to the lower compatible minor version.

## Lock Resource Lookup

This file provides hash-table operations for lock resources:

- `__dlm_insert_lockres()`
- `__dlm_unhash_lockres()`
- `__dlm_lookup_lockres_full()`
- `__dlm_lookup_lockres()`
- `dlm_lookup_lockres()`

The “full” lookup returns resources even if they are dropping their master reference. The ordinary lookup filters out `DLM_LOCK_RES_DROPPING_REF`, which is suitable for most network handlers.

## Domain References

Domain lifetime is kref-based:

- `dlm_grab()` safely takes a reference only if the context is still in `dlm_domains`.
- `dlm_put()` releases a reference.
- `dlm_ctxt_release()` removes a failed or no-longer-joined context and frees memory.

`dlm_domain_fully_joined()` treats both `DLM_CTXT_JOINED` and `DLM_CTXT_IN_SHUTDOWN` as usable for message handling.

## Join Protocol

The join flow is implemented by:

- `dlm_try_to_join_domain()`
- `dlm_request_join()`
- `dlm_send_join_asserts()`
- `dlm_send_join_cancels()`
- handlers for query, assert, cancel, region, and nodeinfo messages.

Join requests are gated by:

- Heartbeat liveness.
- Existing domain state.
- Parallel join exclusion through `joining_node`.
- Recovery state.
- Node map consistency.
- DLM and filesystem protocol compatibility.
- Optional global heartbeat region matching.
- Node address/port consistency.

The join response is encoded as a packed four-byte packet carried as a `u32`, with endian conversion helpers to keep wire format consistent.

If all live nodes agree, the joining node builds `domain_map`, sends nodeinfo and heartbeat region queries when supported, asserts the join to peers, and transitions to `DLM_CTXT_JOINED`.

If maps change or a peer disallows the join, the join restarts with randomized short backoff, timing out after `DLM_JOIN_TIMEOUT_MSECS`.

## Leave And Shutdown

`dlm_unregister_domain()` decrements `num_joins`. On the last unregister it:

1. Marks the domain `DLM_CTXT_IN_SHUTDOWN`.
2. Sends begin-exit notifications for protocol 1.2+.
3. Kicks the DLM thread.
4. Repeatedly migrates or purges all lock resources via `dlm_migrate_all_locks()`.
5. Reports lock resources still on the tracking list.
6. Marks the domain `DLM_CTXT_LEAVING`.
7. Sends final exit-domain messages.
8. Force-frees remaining MLEs.
9. Completes DLM shutdown and removes the context from global lists.

`dlm_leave_domain()` clears the local node from `domain_map` and sends `DLM_EXIT_DOMAIN_MSG` until all peers are cleared or known unreachable.

## Domain Allocation

`dlm_alloc_ctxt()` allocates and initializes:

- Lock-resource and master hash page vectors.
- Debugfs subroot.
- Spinlocks and wait queues.
- Dirty, recovery, purge, handler, tracking, AST, BAST, MLE heartbeat, and work lists.
- Recovery state and node maps.
- MLE and lock-resource counters.
- Workqueue dispatch structure.
- Eviction callback list.

The initial state is `DLM_CTXT_NEW`.

## Message Handler Registration

`dlm_register_domain_handlers()` registers per-domain handlers keyed by the domain key for lock/resource operations, including master requests, assert master, create, convert, unlock, proxy AST, exit, deref, migration, recovery, and begin-exit messages.

`dlm_register_net_handlers()` registers global join-phase handlers using `DLM_MOD_KEY`.

Module init creates MLE, master, and lock caches, registers global net handlers, and creates the debugfs root. Module exit reverses this.

## Eviction Callbacks

The file provides exported callback APIs:

- `dlm_setup_eviction_cb()`
- `dlm_register_eviction_cb()`
- `dlm_unregister_eviction_cb()`

`dlm_fire_domain_eviction_callbacks()` invokes callbacks under a global rwsem. The comment explains why callbacks are needed before DLM recovery completes: the filesystem must know about node death before it can safely acquire recovery-sensitive locks.

## Concurrency

The file documents the DLM spinlock ordering:

1. `dlm_domain_lock`
2. `dlm_ctxt->spinlock`
3. `dlm_lock_resource->spinlock`
4. `dlm_ctxt->master_lock`
5. `dlm_ctxt->ast_lock`
6. `dlm_master_list_entry->spinlock`
7. `dlm_lock->spinlock`

Domain join and leave logic is careful to release locks around network sends and sleeps, then recheck state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.h -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.h

## Purpose

`dlmdomain.h` exposes minimal domain state helpers and the domain eviction callback trigger.

## API

Exports:

- `dlm_domain_lock`
- `dlm_domains`
- `dlm_fire_domain_eviction_callbacks(struct dlm_ctxt *dlm, int node_num)`

Inline helpers:

- `dlm_joined()` returns true when `dlm->dlm_state == DLM_CTXT_JOINED`.
- `dlm_shutting_down()` returns true when `dlm->dlm_state == DLM_CTXT_IN_SHUTDOWN`.

Both helpers acquire `dlm_domain_lock` before reading domain state.

## Role In The DLM

This header gives other DLM source files a safe, shared view of high-level domain lifecycle state without exposing the larger registration and join implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmlock.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmlock.c

## Purpose

`dlmlock.c` implements OCFS2 DLM lock creation and the exported `dlmlock()` API. It handles new lock requests, conversion routing, local master grants, remote create-lock messaging, lock allocation, lock lifetime, cookie generation, and the create-lock network handler.

## Lock Allocation And Lifetime

The file owns the `o2dlm_lock` slab cache:

- `dlm_init_lock_cache()`
- `dlm_destroy_lock_cache()`

Lock objects are kref-managed:

- `dlm_lock_get()`
- `dlm_lock_put()`
- `dlm_lock_release()`

A lock release asserts the lock is on no queue and has no pending AST/BAST state before detaching its lock resource and freeing the lock and optional kernel-allocated LKSB.

`dlm_new_lock()` allocates a lock, optionally allocates a kernel LKSB, initializes list heads, spinlock, modes, cookie, pending flags, callbacks, kref, and stores the lock pointer in `lksb->lockid`.

## Cookie Generation

`dlm_get_next_cookie()` creates a u64 cookie by storing the node number in the top 8 bits and a node-local sequence in the lower 56 bits. It wraps when the sequence would enter the top byte.

## Local Master Locking

`dlmlock_master()` is used when the local node owns the lock resource. It waits for the resource to be usable, reserves an AST, then either:

- Grants immediately and queues the lock on `res->granted`.
- Returns `DLM_NOTQUEUED` for incompatible `LKM_NOQUEUE`.
- Queues the lock on `res->blocked` for normal waiting.

`dlm_can_grant_new_lock()` checks compatibility with both granted locks and converting locks, including conversion target modes.

The recovery lock is a special case: if granted, no AST is queued because the DLM thread is frozen during recovery.

## Remote Locking

`dlmlock_remote()` is used when another node owns the lock resource. It waits out resource state changes, marks the resource `DLM_LOCK_RES_IN_PROGRESS`, queues the local lock on the blocked queue, sets `lock_pending`, and sends `DLM_CREATE_LOCK_MSG`.

On success, the remote master has accepted or granted the request. For the `$RECOVERY` lock, the local node manually moves the lock to granted because no AST will arrive.

On failure, the pending local lock is removed from the queue and its reference is dropped. Recovery and migration statuses are routed back to the caller for retry.

## Create Lock Message

`dlm_send_remote_lock_request()` sends `DLM_CREATE_LOCK_MSG` to `res->owner` and converts transport errors into DLM statuses. Host-down style errors become `DLM_RECOVERING`.

`dlm_create_lock_handler()` runs on the master node. It validates:

- DLM context availability.
- Fully joined domain state.
- Name length.
- Lock allocation.
- Lock resource lookup.
- Lock resource state.

It creates a lock for the remote node, applies `DLM_LKSB_GET_LVB` if requested, attaches the lock resource, and calls `dlmlock_master()`.

## Exported API: dlmlock()

`dlmlock()` supports two broad paths:

- New lock request.
- Convert request via `LKM_CONVERT`.

It validates LKSB presence, mode, flags, recovery-lock rules, local-convert rules, and name length.

For conversion:

- The existing lock comes from `lksb->lockid`.
- The existing lock resource is reused.
- Callback and LKSB arguments must match the original lock.
- The request routes to `dlmconvert_master()` or `dlmconvert_remote()`.
- `DLM_RECOVERING`, `DLM_MIGRATING`, and `DLM_FORWARD` cause retry after a short sleep.

For new locks:

- A new cookie and lock are allocated.
- The caller waits for recovery unless this is a recovery-lock request.
- `dlm_get_lock_resource()` finds or masters the lock resource.
- LVB fetch intent is set for eligible lock modes.
- The request routes to local or remote lock handling.
- Inflight references from `dlm_get_lock_resource()` are dropped after the request.

## Concurrency And Invariants

Important invariants:

- New locks acquire and later drop an inflight lock-resource reference.
- Local master grants reserve an AST and must either queue it or release it.
- Remote lock requests use `lock_pending` and `DLM_LOCK_RES_IN_PROGRESS` to serialize state.
- Failed new lock requests drop the newly allocated lock unless this is a convert path.
- Failed lock requests set `lksb->status`.

## Dependencies

This file depends on:

- Conversion APIs from `dlmconvert.h`.
- Lock resource creation/mastering from `dlmmaster.c`.
- AST queueing and DLM thread behavior from the broader DLM.
- Network transport through `o2net_send_message()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmmaster.c -->
# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmmaster.c

## Purpose

`dlmmaster.c` implements lock-resource ownership for OCFS2 DLM. It manages lock-resource allocation, distributed master election, master-list entries, refmaps, assert-master cleanup, lock-resource dereferencing, lock-resource migration, and cleanup after node death.

The core abstraction is the lock resource owner: exactly one node is master for a lock resource unless the owner is temporarily unknown during mastery, migration, or recovery.

## Master List Entries

Master-list entries, or MLEs, coordinate ownership discovery and migration. The file supports three MLE types:

- `DLM_MLE_MASTER`: local node is trying to master a resource.
- `DLM_MLE_BLOCK`: local node is waiting for another node to master it.
- `DLM_MLE_MIGRATION`: resource ownership is moving from one node to another.

MLEs contain maybe, vote, response, and node maps. They attach to DLM heartbeat events so node up/down changes can restart mastery without allocating in heartbeat callbacks.

Key functions:

- `dlm_init_mle()`
- `dlm_find_mle()`
- `__dlm_insert_mle()`
- `__dlm_unlink_mle()`
- `dlm_put_mle()`
- `dlm_get_mle_inuse()`
- `dlm_put_mle_inuse()`
- `dlm_clean_master_list()`

MLE references are kref-managed and tracked per domain by type counters.

## Lock Resource Allocation

The file owns slab caches for:

- `o2dlm_lockres`
- `o2dlm_lockname`
- `o2dlm_mle`

`dlm_new_lockres()` allocates a lock resource and lock name, initializes queues, wait queues, refcount, owner, state, AST reservation count, migration fields, refmap, LVB, and tracking-list membership.

`dlm_lockres_put()` releases a lock resource once it is unhashed and removed from all queues and lists. Release asserts the resource is no longer on hash, grant, convert, blocked, dirty, recovery, or purge lists.

## Lock Resource Mastery

`dlm_get_lock_resource()` is the main lookup/mastering function. It:

1. Looks for an existing lock resource.
2. Waits if ownership is unknown or dropping-ref is in progress.
3. Pins existing resources with an inflight reference.
4. Allocates a lock resource and MLE if no resource exists.
5. Handles `LKM_LOCAL` by immediately mastering locally.
6. Checks for existing MLEs.
7. Creates a `DLM_MLE_MASTER` if this node should attempt mastery.
8. Sends master requests to peers.
9. Waits until master election completes.
10. Clears `DLM_LOCK_RES_IN_PROGRESS` and wakes waiters.

Master election uses `DLM_MASTER_REQUEST_MSG` and responses:

- `DLM_MASTER_RESP_YES`: peer is master.
- `DLM_MASTER_RESP_NO`: peer is not master.
- `DLM_MASTER_RESP_MAYBE`: peer may also be trying.
- `DLM_MASTER_RESP_ERROR`: retry.

If all votes complete and no peer is known master, the lowest candidate in `maybe_map` wins. The winner asserts mastery to peers.

## Master Request Handler

`dlm_master_request_handler()` answers ownership queries from other nodes. It checks domain state, existing lock resources, resource recovery/migration state, current owner, and local MLEs.

It may:

- Return YES and set the requestor bit in the refmap if this node owns the resource.
- Return NO if another owner is known or this node is blocked.
- Return MAYBE if local mastery is also in progress.
- Create a `DLM_MLE_BLOCK` when the lock resource is not known locally.
- Dispatch assert-master work to clean stale MLEs created on lower-numbered nodes.

## Assert Master

`dlm_do_assert_master()` sends `DLM_ASSERT_MASTER_MSG` to a node map and sets `DLM_LOCK_RES_SETREF_INPROG` while refmap updates are in progress.

`dlm_assert_master_handler()` processes an asserted owner. It validates MLE and lock-resource state, updates MLE master fields, wakes waiters, changes the lock-resource owner, handles migration completion, and returns response flags indicating whether the sender should reassert or set a mastery reference.

`dlm_dispatch_assert_master()` queues asynchronous assert-master work, and `dlm_assert_master_worker()` sends asserts while respecting migration state and AST reservation barriers.

The post handler clears `DLM_LOCK_RES_SETREF_INPROG` and drops the returned lock-resource reference.

## Refmap And Dereference

The refmap tracks which nodes hold a reference to a mastered lock resource.

Key functions:

- `dlm_lockres_set_refmap_bit()`
- `dlm_lockres_clear_refmap_bit()`
- `dlm_drop_lockres_ref()`
- `dlm_deref_lockres_handler()`
- `dlm_deref_lockres_done_handler()`
- `dlm_deref_lockres_worker()`

If a deref arrives while `DLM_LOCK_RES_SETREF_INPROG` is active, work is deferred until assert-master ref setup finishes. Protocol minor 1.3 adds `DLM_DEREF_LOCKRES_DONE` so the non-master can be told when the master has completed the deref and purge-related state can proceed.

## Migration

A lock resource is migratable when:

- It is locally mastered.
- It has no local locks.
- It has non-local locks or refmap references.
- It is not already migrating or recovering.

`dlm_empty_lockres()` is used during domain leave to migrate such resources away.

`dlm_pick_migration_target()` chooses a target from non-local locks first, then refmap references, skipping nodes exiting the domain.

`dlm_migrate_lockres()` performs the original-master side:

1. Allocates a migration buffer and MLE.
2. Adds a migration MLE.
3. Marks the resource migrating after AST/dirty barriers.
4. Flushes assert-master work.
5. Sends the full lock-resource state to the target through `dlm_send_one_lockres()`.
6. Waits for the target to assert mastery.
7. Sets owner to target.
8. Removes nonlocal lock structures and clears remote refmap bits.
9. Recalculates usage and wakes waiters.

`dlm_migrate_request_handler()` runs on third-party nodes when a new master announces migration. It adds a migration MLE and marks any local resource migrating.

`dlm_finish_migration()` runs on the new master after receiving all lock-resource data. It sends migration requests to other nodes, asserts mastery to all nodes except the old master, then asserts back to the old master so the migration completes everywhere.

## AST Reservation And Migration Barrier

Migration depends on AST reservation accounting:

- `__dlm_lockres_reserve_ast()` increments `res->asts_reserved` and refuses to reserve while migrating.
- `dlm_lockres_release_ast()` decrements the count. If migration is pending and this was the last reserved AST, it atomically sets `DLM_LOCK_RES_MIGRATING` and wakes migration waiters.

`dlm_mark_lockres_migrating()` uses this mechanism to block new dirtying, wait for pending AST work to drain, and ensure migration starts only when the lock-resource queues are stable.

## Node Death Cleanup

`dlm_clean_master_list()` handles MLE cleanup after a node dies:

- `DLM_MLE_MASTER` entries are left for their local waiters to notice node-map changes.
- `DLM_MLE_BLOCK` entries are cleaned if the dead node would have been the expected master.
- `DLM_MLE_MIGRATION` entries are cleaned if either old or new master died, unless the target died while the MLE is still actively in use.
- Associated lock resources may have ownership reset to unknown and be moved to recovery.

`dlm_force_free_mles()` is used during domain leave after all peers are gone. It wakes and frees remaining block MLEs.

## Recovery Lock Special Case

`dlm_pre_master_reco_lockres()` handles `$RECOVERY`. It cannot wait for full node recovery before mastering the recovery lock, so it requeries live nodes to ensure none still believe a dead node owns the recovery lock.

## Concurrency And Invariants

This file is highly lock-order sensitive. It follows the domain-level lock order documented in `dlmdomain.c` and uses explicit comments where it must drop and reacquire locks.

Important invariants:

- Only one MLE for a given lock name should be visible in the master hash.
- A lock resource with unknown owner should normally be `DLM_LOCK_RES_IN_PROGRESS`.
- Mastery refmap updates are serialized by `DLM_LOCK_RES_SETREF_INPROG`.
- Migration requires no dirty state and no pending ASTs.
- Lock-resource release requires removal from all hash/list/queue structures.
- Nonlocal locks are removed from the old master after successful migration.

## Dependencies

This file coordinates with:

- `dlmdomain.c` for domain maps, lifecycle, message handler registration, and recovery maps.
- `dlmlock.c` for inflight references and lock-resource acquisition.
- `dlmconvert.c` and unlock/AST paths through shared lock-resource state.
- `dlmrecovery.c` for migration payload send/receive and master requery helpers.
- `dlmthread.c` for dirty-list processing, purge, and usage recalculation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmmaster.c -->