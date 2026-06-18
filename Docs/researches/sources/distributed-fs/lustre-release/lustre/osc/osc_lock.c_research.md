# sources/distributed-fs/lustre-release/lustre/osc/osc_lock.c research

## Purpose
`osc_lock.c` implements OSC `cl_lock_operations` and bridges CL locks to LDLM extent locks. It builds lock policies, sends enqueue requests, handles enqueue callbacks, lockless conversion, blocking/cancel/glimpse ASTs, early-cancel weight, conflicting-lock wait queues, and DLM lock lookup by page offset.

## Important APIs, Types, and Functions
Important exported functions include `osc_lock_fini()`, `osc_ldlm_glimpse_ast()`, `osc_ldlm_weigh_ast()`, `osc_lock_to_lockless()`, `osc_lock_wake_waiters()`, `osc_lock_enqueue_wait()`, `osc_lock_cancel()`, `osc_lock_print()`, `osc_lock_set_writer()`, `osc_lock_set_reader()`, and `osc_obj_dlmlock_at_pgoff()`. The operation tables are `osc_lock_ops` and `osc_lock_lockless_ops`.

The private `struct osc_lock` state is observed through fields such as `ols_state`, `ols_dlmlock`, `ols_handle`, `ols_hold`, `ols_has_ref`, `ols_flags`, `ols_lvb`, `ols_glimpse`, `ols_speculative`, `ols_locklessable`, `ols_owner`, `ols_waiting_list`, and links into `osc_object::oo_ol_list`.

## Control Flow
`osc_lock_init()` allocates a lock slice, initializes wait lists and flags, translates CL enqueue flags to LDLM flags, detects glimpse/speculative requests, builds enqueue info, optionally converts to lockless mode, and records read/write locks in the current `osc_io`. `osc_lock_enqueue()` waits for conflicting local OSC locks unless the request is glimpse/speculative/test-only, grants lockless locks locally, or calls `osc_enqueue_base()` with `osc_lock_upcall()` or `osc_lock_upcall_speculative()`.

`osc_lock_upcall()` runs when a lock is matched or the server replies. It transitions `OLS_ENQUEUED` to `OLS_UPCALL_RECEIVED`, calls `osc_lock_granted()` on success, maps NDELAY failures to `-EAGAIN`, handles glimpse `-ENAVAIL` by using the returned LVB, and wakes the sync owner. `osc_lock_granted()` takes the LDLM reference, stores handle/hold state, updates the CL descriptor to the granted extent, and refreshes object attributes from the LVB unless already cached.

Blocking AST flow is split: `osc_ldlm_blocking_ast()` handles `LDLM_CB_BLOCKING` by asynchronously cancelling the DLM lock; `LDLM_CB_CANCELING` creates a fresh environment and calls `__osc_dlm_blocking_ast()`. Canceling flushes or discards pages in the lock extent via `osc_lock_flush()`, clears `l_ast_data`, shifts KMS down with `ldlm_extent_shift_kms()`, and drops the object reference.

## State and Persistence Behavior
The file does not persist data itself, but it protects persistence by ensuring dirty pages are written before lock cancellation and by updating object LVB/KMS from lock replies and glimpses. `oo_ol_list` serializes local lock compatibility and lockless waiters. LDLM lock lifetime is reference-counted through `ldlm_handle2lock_long()`, `ldlm_lock_addref()`, `ldlm_lock_decref()`, and `ldlm_lock_put()`. `osc_lock_detach()` is the central cleanup point for LDLM references.

## Dependencies and Integration Points
Dependencies include LDLM policy/mode/AST APIs, FID/OST resource naming, CL lock and sync IO primitives, object attribute APIs, and `osc_cache.c` writeback/discard/high-priority helpers. The lock code integrates with `osc_io.c` by setting `oi_write_osclock`, `oi_read_osclock`, and `oi_lockless`; with `osc_object.c` through `oo_ol_list` and object LVB updates; and with lower request code through `osc_enqueue_base()` and `osc_match_base()`.

## Risks
The main risks are races between CL lock state and LDLM lock destruction, recursive cancel callbacks, and missing writeback during lock loss. `osc_lock_invariant()` documents expected relationships between handle, DLM pointer, state, and hold reference. The code intentionally avoids taking `cl_lock` mutex in glimpse AST; this relies on server-side race tolerance. Lockless conversion depends on connection flags and IO lock requirements; wrong conversion could bypass required client-side locking.

## Test Signals
Tests should cover normal enqueue and local match, glimpse success and `-ENAVAIL`, speculative enqueue cleanup, NDELAY `-EAGAIN`, lockless reads/writes, lock cancellation with dirty writeback, discard-data callbacks, KMS update after lock loss, waiter wakeups for incompatible locks, early-cancel weight for dirty/locked/writeback pages, and `osc_obj_dlmlock_at_pgoff()` retry when a matched lock is concurrently canceled.
