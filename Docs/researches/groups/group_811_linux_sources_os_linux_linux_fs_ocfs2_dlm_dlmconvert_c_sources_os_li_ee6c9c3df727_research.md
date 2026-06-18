# Group Research: OCFS2 DLM conversion, debug, domain, lock, and mastership sources

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.c

## Purpose
Implements lock conversion for OCFS2 DLM lock resources, covering both local-master conversion and remote conversion requests to the current resource master.

## Main Entry Points
- `dlmconvert_master()` handles conversion when the local node owns the lock resource.
- `dlmconvert_remote()` queues a local pending conversion and sends `DLM_CONVERT_LOCK_MSG` to the master.
- `dlm_convert_lock_handler()` handles incoming conversion messages on the master node.
- `dlm_revert_pending_convert()` moves a failed pending conversion back to granted state and clears LVB flags.

## Core Behavior
`__dlmconvert_master()` requires `res->spinlock` and performs the actual queue decision. It rejects already-converting locks and locks not on the granted queue. Downconverts are granted in place. Upconverts are granted only if compatible with all granted locks and both current/target modes of converting locks; otherwise they move to `res->converting` unless `LKM_NOQUEUE` is set.

The file also manages lock value block semantics:
- EX lock conversion with `LKM_VALBLK` sets `DLM_LKSB_PUT_LVB` and copies into `res->lvb` on grant.
- PR/NL conversion with a non-NL target sets `DLM_LKSB_GET_LVB`.
- NL target conversion suppresses LVB fetch.

## Remote Protocol
`dlm_send_remote_convert_request()` builds `struct dlm_convert_lock`, optionally sends the LVB as a second kvec segment for `LKM_PUT_LVB`, and maps transport errors to DLM statuses. Host-down errors wait briefly for heartbeat recognition and return `DLM_RECOVERING`.

`dlm_convert_lock_handler()` validates domain state, name length, LVB flag combinations, resource state, and the lock identity on the granted queue before invoking `__dlmconvert_master()`. It reserves AST capacity while the conversion is in progress and queues AST/kicks the DLM thread after releasing locks.

## Locking and State
The file is explicit that only `__dlmconvert_master()` enters and exits with `res->spinlock` held. Public paths reserve/release AST slots, mark `DLM_LOCK_RES_IN_PROGRESS`, wake `res->wq`, and avoid holding spinlocks during network sends.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.h

## Purpose
Small interface header for OCFS2 DLM lock conversion.

## Exposed API
- `dlmconvert_master()` converts a lock on a locally mastered resource.
- `dlmconvert_remote()` converts a lock by contacting a remote resource master.

## Notes
The header is guarded by `DLMCONVERT_H` and relies on DLM core types declared elsewhere. It intentionally exposes only the two conversion entry points used by the lock path.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.c

## Purpose
Provides diagnostic printing and debugfs views for OCFS2 DLM state: lock resources, locks, MLEs, purge lists, domain state, recovery state, and error names.

## Main Entry Points
- `dlm_print_one_lock_resource()` and `__dlm_print_one_lock_resource()` dump a lock resource and its granted/converting/blocked queues.
- `dlm_print_one_lock()` exports lock-resource printing for a lock handle.
- `dlm_errname()` maps `enum dlm_status` values to strings.
- `dlm_print_one_mle()` formats a master-list entry.
- `dlm_debug_init()` creates per-domain debugfs files.
- `dlm_create_debugfs_root()` / `dlm_destroy_debugfs_root()` manage `/sys/kernel/debug/o2dlm`.

## Debugfs Files
When `CONFIG_DEBUG_FS` is enabled, per-domain files are created:
- `dlm_state`: domain protocol, thread, node maps, resource counts, MLE counts, recovery state.
- `locking_state`: seq-file dump of tracked lock resources, including queues and LVB bytes.
- `mle_state`: current master-list entries and hash bucket statistics.
- `purge_list`: lock resources waiting on purge and age in seconds.

Without debugfs, the header supplies no-op inline functions.

## Formatting Helpers
`stringify_lockname()` contains OCFS2-specific knowledge to make dentry lock names more readable by decoding an inode block number. `stringify_nodemap()` prints node bitmaps. `dump_lockres()` emits compact machine-readable `NAME`, `LRES`, `RMAP`, `LVBX`, and `LOCK` records.

## Locking
Printing paths take the appropriate resource, DLM, master, tracking, AST, or lock spinlocks before traversing shared lists. The seq-file lockres iterator pins the current lock resource with `dlm_lockres_get()` and releases the previous one as iteration advances.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.h

## Purpose
Declares OCFS2 DLM debug helpers and debugfs lifecycle hooks.

## Exposed API
- Always declares `dlm_print_one_mle()`.
- Under `CONFIG_DEBUG_FS`, declares `struct debug_lockres` and debugfs init/create/destroy functions.
- Without `CONFIG_DEBUG_FS`, provides empty inline replacements for debugfs lifecycle calls.

## Notes
This isolates debugfs conditional compilation from the rest of the DLM domain code. Callers can invoke debug initialization and teardown unconditionally.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdebug.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.c

## Purpose
Defines OCFS2 DLM domain lifecycle: allocation, registration, join negotiation, leave/shutdown, network handler registration, heartbeat/node-region validation, and eviction callbacks.

## Main Entry Points
- `dlm_register_domain()` creates or references a DLM domain and joins the cluster domain.
- `dlm_unregister_domain()` leaves the domain, migrates locks, sends exit messages, and tears down workers/handlers.
- `dlm_lookup_lockres()` and internal lookup helpers locate lock resources in per-domain hashes.
- `dlm_grab()` / `dlm_put()` manage domain references.
- `dlm_domain_fully_joined()` checks whether network handlers may accept domain traffic.
- `dlm_fire_domain_eviction_callbacks()` runs filesystem eviction callbacks before recovery completes.

## Join Protocol
The file registers global join handlers for:
- `DLM_QUERY_JOIN_MSG`
- `DLM_ASSERT_JOINED_MSG`
- `DLM_CANCEL_JOIN_MSG`
- `DLM_QUERY_REGION`
- `DLM_QUERY_NODEINFO`

`dlm_try_to_join_domain()` snapshots live heartbeat nodes, asks each live node whether this node may join, gathers `JOIN_OK` responders into `domain_map`, validates node info and heartbeat regions for protocol 1.1+, sends join asserts, and transitions to `DLM_CTXT_JOINED`.

The protocol negotiates DLM and filesystem locking minor versions. Major mismatch or older remote minor than required fails with protocol mismatch. Join is rejected during recovery, parallel joins, stale domain-map visibility, or incompatible cluster configuration.

## Leave Protocol
`dlm_unregister_domain()` transitions to shutdown when the last join reference is dropped. It sends best-effort begin-exit messages for protocol 1.2+, kicks the DLM thread, repeatedly migrates or purges lock resources with `dlm_migrate_all_locks()`, marks the domain leaving after any active joiner clears, sends exit messages to remaining nodes, force-frees MLEs, and unregisters handlers/threads/workqueue.

## Context and Resource Management
`dlm_alloc_ctxt()` allocates hash page vectors for lock resources and MLEs, initializes all lists, locks, waitqueues, recovery state, counters, worker infrastructure, and debugfs subroot. `dlm_ctxt_release()` removes failed or shut-down domains from the global list and frees memory.

## Locking
The file documents global spinlock order:
`dlm_domain_lock`, `dlm_ctxt->spinlock`, `dlm_lock_resource->spinlock`, `dlm_ctxt->master_lock`, `dlm_ctxt->ast_lock`, `dlm_master_list_entry->spinlock`, `dlm_lock->spinlock`.

This ordering is central because join/leave handlers and lookup paths combine global domain state, per-domain maps, lock resources, and MLE structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.h -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.h

## Purpose
Small header for domain-global state and domain status helpers.

## Exposed API
- Externs `dlm_domain_lock` and `dlm_domains`.
- `dlm_joined()` checks for `DLM_CTXT_JOINED` under `dlm_domain_lock`.
- `dlm_shutting_down()` checks for `DLM_CTXT_IN_SHUTDOWN`.
- Declares `dlm_fire_domain_eviction_callbacks()`.

## Notes
The inline helpers centralize protected reads of `dlm->dlm_state` for users that only need boolean domain state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmdomain.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmlock.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmlock.c

## Purpose
Implements the public OCFS2 DLM lock acquisition API and the network handler for remote lock creation.

## Main Entry Points
- `dlmlock()` is the exported API for lock and convert requests.
- `dlm_create_lock_handler()` handles `DLM_CREATE_LOCK_MSG` on the master node.
- `dlm_new_lock()`, `dlm_lock_get()`, `dlm_lock_put()`, and `dlm_lock_attach_lockres()` manage lock allocation, references, and lock-resource attachment.
- `dlm_init_lock_cache()` / `dlm_destroy_lock_cache()` manage the lock slab cache.

## Lock Acquisition
For new locks, `dlmlock()` validates mode/flags/name, allocates a node-local cookie, creates a `struct dlm_lock`, waits for recovery unless this is a recovery lock, obtains or masters the lock resource through `dlm_get_lock_resource()`, and then calls either `dlmlock_master()` or `dlmlock_remote()`.

`dlmlock_master()` grants immediately if compatible with granted and converting queues. Otherwise it returns `DLM_NOTQUEUED` for `LKM_NOQUEUE` or queues the lock on `blocked`. Granted locks reserve/queue ASTs except for the special `$RECOVERY` lock.

`dlmlock_remote()` places the lock on the local secondary blocked queue, marks `lock_pending`, sends `DLM_CREATE_LOCK_MSG`, and reverts on failure. `$RECOVERY` has special handling because it may be granted without a later AST.

## Conversion Path
When `LKM_CONVERT` is set, `dlmlock()` validates that the caller passed the original `lksb`, AST, BAST, and AST data. It then retries `dlmconvert_master()` or `dlmconvert_remote()` through recovery/migration/forward statuses.

## Remote Create Handler
`dlm_create_lock_handler()` validates domain state, lock name length, allocates a remote-node lock and kernel-owned LKSB, applies `LKM_GET_LVB`, looks up the lock resource, rejects non-normal lockres state, attaches the lock to the resource, and invokes `dlmlock_master()`.

## Reference and Cookie Model
Cookies combine the node number in the top byte with a per-node 56-bit sequence protected by `dlm_cookie_lock`. Lock release asserts the lock is off all queues and AST/BAST lists before detaching the lock resource and freeing any kernel-allocated LKSB.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmlock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmmaster.c -->
# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmmaster.c

## Purpose
Implements OCFS2 DLM mastership: lock-resource allocation, master-list entries, master discovery, assert-master cleanup, refmap dereference, lock-resource migration, and recovery cleanup for mastership state.

## Main Entry Points
- `dlm_get_lock_resource()` finds, allocates, hashes, masters, or waits for a lock resource.
- `dlm_master_request_handler()` handles remote mastership probes.
- `dlm_assert_master_handler()` handles mastership assertions and MLE cleanup.
- `dlm_dispatch_assert_master()` queues asynchronous assert-master work.
- `dlm_drop_lockres_ref()` and deref handlers maintain remote reference maps.
- `dlm_empty_lockres()` migrates lock resources during domain leave.
- `dlm_finish_migration()` completes migration on the new master.
- `dlm_clean_master_list()` cleans MLEs after node death.
- Cache lifecycle functions initialize/destroy lockres, lockname, and MLE slab caches.

## MLE Model
Master List Entries represent in-progress mastership decisions:
- `DLM_MLE_MASTER`: local node is trying to master a resource.
- `DLM_MLE_BLOCK`: local node is blocking because another node may master it.
- `DLM_MLE_MIGRATION`: mastership is moving from one node to another.

MLEs carry `node_map`, `vote_map`, `response_map`, `maybe_map`, `master`, `new_master`, waitqueue state, refcount, and heartbeat event linkage. Heartbeat callbacks update MLE node maps so mastership waits can restart when nodes join or die.

## Master Discovery
`dlm_get_lock_resource()` first checks the lockres hash. Existing resources are pinned with an inflight reference after waiting for unknown owner or dropping-ref state. New resources are inserted while marked `DLM_LOCK_RES_IN_PROGRESS`, then mastership is resolved through MLEs and `DLM_MASTER_REQUEST_MSG`.

`dlm_wait_for_lock_mastery()` waits until votes complete, another master is asserted, or the local node is the lowest possible master. If local wins, it calls `dlm_do_assert_master()` and sets lockres owner. Node-map changes call `dlm_restart_lock_mastery()`.

## Master Request and Assert
`dlm_master_request_handler()` answers `YES`, `NO`, `MAYBE`, or `ERROR` based on local lockres ownership, in-progress state, MLE type, and migration/recovery state. If this node owns the resource, it sets the requester’s refmap bit and may dispatch assert-master cleanup to lower nodes.

`dlm_assert_master_handler()` validates any local MLE and lockres state, records the asserting node as master, wakes waiters, updates lockres owner, handles migration completion assertions, returns whether this node needs a mastery ref, and requests reassertion if prior master requests reached other nodes.

## Refmap Dereference
`dlm_drop_lockres_ref()` tells the master to clear this node from a lockres refmap. If `DLM_LOCK_RES_SETREF_INPROG` is active, `dlm_deref_lockres_handler()` defers cleanup to `dlm_deref_lockres_worker()` and later sends `DLM_DEREF_LOCKRES_DONE`. This prevents races between assert-master ref propagation and dereference.

## Migration
A migratable lock resource is locally mastered, has no local locks, is not already migrating/recovering, and has nonlocal locks or remote refmap bits. `dlm_migrate_lockres()` installs a migration MLE, marks the lockres migrating after AST/dirty activity drains, sends full lockres state to the target, waits for the target assert, switches owner, removes nonlocal locks, and recalculates usage.

`dlm_finish_migration()` runs on the new master. It notifies other nodes with `DLM_MIGRATE_REQUEST_MSG`, asserts mastership to all except the old master, then asserts back to the old master last, sets itself as owner, clears migration state, and dirties/kicks the resource for normal processing.

## Recovery Cleanup
`dlm_clean_master_list()` removes or wakes MLEs affected by a dead node. Migration MLEs reset associated lockres ownership to unknown if either old or new master died, moving the resource to recovery. `dlm_force_free_mles()` wakes and frees remaining block MLEs during final domain leave.

## Locking and Invariants
The file heavily relies on the domain lock order documented in `dlmdomain.c`. Lock-resource release asserts the resource is unhashed and absent from all queues/lists. AST reservation and release are integral to migration: the final AST release can atomically set `DLM_LOCK_RES_MIGRATING` and wake migration waiters.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ocfs2/dlm/dlmmaster.c -->