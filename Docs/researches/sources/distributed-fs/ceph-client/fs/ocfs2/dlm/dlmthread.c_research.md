# sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmthread.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmthread.c` implements the normal OCFS2 DLM maintenance thread. It purges unused lock resources, shuffles granted/converting/blocked lock queues on dirty resources, queues ASTs and BASTs when locks become grantable or incompatible, and flushes pending AST/BAST callbacks to local or remote owners. The source was read as a complete 809-line file.

## Important APIs, Types, and Functions

Thread lifecycle is exposed through `dlm_launch_thread()`, `dlm_complete_thread()`, and `dlm_kick_thread()`. Lock-resource wait and usage helpers include `__dlm_wait_on_lockres_flags()`, `__dlm_lockres_has_locks()`, `__dlm_lockres_unused()`, `__dlm_lockres_calc_usage()`, `dlm_lockres_calc_usage()`, `__dlm_do_purge_lockres()`, and `__dlm_dirty_lockres()`.

The core worker functions are `dlm_thread()`, `dlm_run_purge_list()`, `dlm_purge_lockres()`, `dlm_shuffle_lists()`, `dlm_flush_asts()`, and `dlm_dirty_list_empty()`. The code relies on `struct dlm_ctxt` lists (`dirty_list`, `purge_list`, `pending_asts`, `pending_basts`), `struct dlm_lock_resource` queues (`granted`, `converting`, `blocked`), and per-lock fields such as `ml.type`, `ml.convert_type`, `ml.highest_blocked`, `ast_pending`, and `bast_pending`.

## Control Flow

`dlm_kick_thread()` optionally marks a lock resource dirty under `dlm->spinlock` and `res->spinlock`, then wakes `dlm->dlm_thread_wq`. `__dlm_dirty_lockres()` only adds locally mastered resources, skips migrating resources and resources with `DLM_LOCK_RES_BLOCK_DIRTY`, takes a dirty-list reference, appends to `dlm->dirty_list`, and sets `DLM_LOCK_RES_DIRTY`.

The `dlm_thread()` loop first purges stale unused resources via `dlm_run_purge_list()`, then processes up to `DLM_THREAD_MAX_DIRTY` dirty resources per pass. Each dirty resource is removed from the dirty list, locked with `dlm->ast_lock` and `res->spinlock`, and either delayed if in progress/recovering/recovery-waiting or passed to `dlm_shuffle_lists()`. Delayed resources are re-dirtied at the tail. After dirty processing, `dlm_flush_asts()` drains pending AST and BAST lists, then the thread sleeps until dirty work or timeout.

`dlm_shuffle_lists()` grants at most the compatible head of the converting or blocked queues, recursing back to the converting queue after each grant. For a converting lock, it compares the requested convert level against all granted and converting peers. For a blocked lock, it compares the requested level against granted and converting queues. Incompatible holders get BASTs queued and their `highest_blocked` level raised; compatible targets move to the granted list, update lksb status to `DLM_NORMAL`, reserve AST accounting, and queue AST delivery.

Purge handling starts when `__dlm_lockres_calc_usage()` detects a resource has no locks, no inflight locks, no dirty state, no recovery state, and no refmap bits. It adds such resources to `purge_list` with `last_used`. `dlm_run_purge_list()` removes expired entries, skips entries that became used/migrating/asserting, and calls `dlm_purge_lockres()`. Remote-master purge first sends a deref to the master with `dlm_drop_lockres_ref()` and handles asynchronous deref completion; local-master purge can unhash directly. Both paths remove tracking-list membership and wake waiters once dropping-ref state clears.

## State and Persistence Behavior

All state is in-memory DLM state. The thread maintains dirty-list membership and `DLM_LOCK_RES_DIRTY`, purge-list membership and `dlm->purge_count`, lock-resource hash/tracking membership, AST/BAST pending lists, per-lock `highest_blocked`, queue membership, granted lock levels, and lksb status. It performs no disk persistence.

References are central to safety: dirty and purge list insertion takes lock-resource references, AST/BAST list handling takes lock references while callbacks are delivered, purge takes temporary refs while unhashing, and non-master purge may leave `DLM_LOCK_RES_DROPPING_REF` set until deref completion. Waiters use `res->wq`, `dlm->dlm_thread_wq`, and `dlm->ast_wq`.

## Dependencies and Integration Points

This file integrates with the lock/convert/unlock paths, which call `dlm_kick_thread()` or `__dlm_dirty_lockres()` after queue changes. It depends on compatibility helpers (`dlm_lock_compatible()`), AST/BAST queueing and delivery (`__dlm_queue_ast()`, `__dlm_queue_bast()`, `dlm_do_local_ast()`, `dlm_do_remote_ast()`, `dlm_do_local_bast()`, `dlm_send_proxy_bast()`), lock-resource hash operations (`__dlm_unhash_lockres()`), deref messaging (`dlm_drop_lockres_ref()`), and shutdown state (`dlm_shutting_down()`).

Recovery integrates tightly with this thread: recovering resources are not shuffled, recovery cleanup dirties resources after removing dead locks, recovery finalization clears recovery flags and kicks the thread, and `dlmthread.c` refuses to consider recovering or recovery-waiting lock resources unused.

## Risks and Edge Cases

Queue ordering and lock compatibility determine cluster-visible fairness and correctness. Converting and blocked queue order is preserved locally except where recovery comments note ordering loss. BAST queuing must avoid duplicate pending callbacks while still raising `highest_blocked` for stronger blockers. AST/BAST delivery drops locks while callbacks or network sends execute, so the pending-list reference rules are critical.

Purge is risky because remote resources must clear their master refmap bit before local unhash. The code waits for `DLM_LOCK_RES_SETREF_INPROG`, sets `DLM_LOCK_RES_DROPPING_REF`, and handles `DLM_DEREF_RESPONSE_INPROG`; mistakes can leave leaked resources or unhash a resource still referenced by another node. The dirty thread deliberately throttles after 100 resources to limit scheduling latency.

Many invariant violations call `BUG()`: dirty resources must be locally mastered, converting locks must have non-IV convert types, resources must be unused before purge, and tracking-list membership is expected. Tests that hit these paths indicate DLM state corruption rather than recoverable user errors.

## Test Signals

Useful tests include lock compatibility matrices for PR/EX/NL modes, concurrent converts and unlocks that should trigger AST/BAST ordering, purge tests for local and remote-master resources, forced shutdown with purge-now behavior, recovery interaction tests ensuring recovering resources are delayed then reshuffled after finalize, and stress tests that repeatedly dirty and purge many resources. Runtime signals include dirty-list throttling logs, lock-resource dumps for non-local dirty entries, AST/BAST flush logs, purge-list accounting mismatches, and waiters stuck on `res->wq` or `ast_wq`.
