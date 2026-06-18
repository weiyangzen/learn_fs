# File Research: sources/cow-pools/openzfs/module/zfs/txg.c

## Role

`txg.c` implements ZFS transaction group coordination. Transaction groups batch in-memory mutations into monotonically increasing TXG IDs, move them through open, quiescing, and syncing states, and provide wait/kick/delay/list APIs used by DMU, DSL, SPA, ZIL, and administrative sync tasks.

The file owns the two worker threads that advance TXGs: a quiesce thread and a sync thread. It also implements per-TXG callback dispatch and generic per-TXG object lists.

## TXG States

The file's top comment explains the three active TXG states.

The open TXG accepts new transactions. A TXG exits open state when thresholds, timeouts, sync waiters, scans, or administrative work require it to move forward.

The quiescing TXG no longer accepts new transactions but waits for all open handles to be released to sync. This gives in-memory operations time to finish before disk sync.

The syncing TXG writes accumulated dirty state to stable storage through `spa_sync()`, potentially in multiple sync passes until metadata changes converge and a new uberblock can be written.

## Initialization And Threads

`txg_init()` clears `tx_state_t`, allocates per-CPU `tx_cpu_t` state, initializes per-CPU locks, open locks, per-TXG condition variables and callback lists, initializes sync-lock CVs, and sets the initial open TXG.

`txg_sync_start()` starts the quiesce and sync threads and sets `tx_threads` to two. `txg_sync_stop()` waits far enough ahead to drain deferred metaslab work, sets `tx_exiting`, wakes all TXG CVs, and waits for both threads to exit. `txg_fini()` asserts threads are stopped, destroys locks/CVs/lists/taskq, frees per-CPU state, and clears the structure.

`txg_thread_enter()`, `txg_thread_wait()`, and `txg_thread_exit()` wrap thread lock/CPR integration, idle waits, exit bookkeeping, and `thread_exit()`.

## Open Handles And Quiescing

`txg_hold_open()` chooses a per-CPU slot with `CPU_SEQID_UNSTABLE`, takes that slot's `tc_open_lock`, reads the current open TXG, increments the per-TXG per-CPU hold count under `tc_lock`, and returns a `txg_handle_t`. Holding `tc_open_lock` prevents that TXG from being fully closed to new entrants until the caller releases to quiesce.

`txg_rele_to_quiesce()` releases the open lock. `txg_rele_to_sync()` decrements the per-CPU hold count and broadcasts the per-TXG CV when it reaches zero. `txg_register_callbacks()` moves DMU transaction commit callbacks onto the per-CPU callback list for the handle's TXG.

`txg_quiesce()` takes every per-CPU open lock to block new entrants, increments `tx_open_txg`, records open/quiesce timestamps in SPA TXG history, releases open locks so new transactions enter the next TXG, then waits for all per-CPU hold counts for the old TXG to drop to zero. It then records the quiesced timestamp.

## Sync And Quiesce Threads

`txg_quiesce_thread()` waits until a future TXG has been requested for quiescing and there is no already-quiesced TXG waiting for sync. It sets `tx_quiescing_txg`, drops `tx_sync_lock`, calls `txg_quiesce()`, reacquires the lock, hands the TXG to the sync thread via `tx_quiesced_txg`, and broadcasts sync/quiesce CVs.

`txg_sync_thread()` wakes when scanning is active, a sync waiter exists, a quiesced TXG is ready, or `zfs_txg_timeout` expires. It skips syncing while the pool is suspended, requests quiescing when needed, consumes `tx_quiesced_txg`, sets `tx_syncing_txg`, drops the lock, records initial I/O stats through `spa_txg_history_init_io()`, calls `spa_sync(spa, txg)`, records final I/O stats, marks `tx_synced_txg`, clears `tx_syncing_txg`, broadcasts sync waiters, and dispatches commit callbacks.

`txg_dispatch_callbacks()` lazily creates a `tx_commit_cb` taskq, moves registered callbacks into temporary lists, and dispatches them to worker threads. `txg_wait_callbacks()` waits for outstanding callback tasks and warns in comments that calling from a callback would deadlock.

## Waiting, Kicking, And Delay

`txg_wait_synced_flags()` waits until a target TXG has synced, defaulting TXG zero to open plus deferred size. It records the highest requested sync TXG, broadcasts the sync thread, and waits either interruptibly, uninterruptibly, or with early `ESHUTDOWN` return when `TXG_WAIT_SUSPEND` is requested and the pool is suspended. `txg_wait_synced()` wraps it with no flags.

`txg_wait_open()` waits until the open TXG reaches a target, optionally marking that target for immediate quiescing. It accounts wait time as I/O wait for callers that request quiescing and idle wait otherwise.

`txg_kick()` asks the sync thread to advance at least through a supplied TXG. `txg_wait_kick()` broadcasts sync-done waiters. `txg_delay()` sleeps a caller for a requested time when its TXG is still open and the pipeline is backed up, aborting if the TXG advances or the pipeline stalls.

`txg_stalled()` reports that quiescing is waiting beyond the open TXG. `txg_sync_waiting()` reports whether syncing is at or behind a requested TXG or a quiesced TXG is waiting.

## Per-TXG Lists

The bottom section implements `txg_list_t`, an intrusive list set indexed by `txg & TXG_MASK`. `txg_list_create()` initializes the lock, offset, SPA pointer, and heads. `txg_list_add()` inserts at the head if not already present for the TXG; `txg_list_add_tail()` inserts at the tail. `txg_list_remove()` removes the head, and `txg_list_remove_this()` removes a specific object. `txg_list_member()`, `txg_list_head()`, `txg_list_next()`, `txg_list_empty()`, `txg_all_lists_empty()`, and `txg_list_destroy()` provide membership, traversal, emptiness, and teardown helpers.

In debug builds, `txg_verify()` ensures manipulated TXGs are active: not older than synced state, not beyond the open TXG, and within the concurrent TXG window.

## Tunables And Exports

`zfs_txg_timeout` defaults to five seconds and controls the maximum time worth of delta per TXG before the sync thread advances work. The file exports TXG lifecycle, hold/release, callback, delay, wait, stalled, and sync-waiting functions, and exposes `zfs_txg_timeout` as a module parameter.

## Risks And Invariants

The ordering around `tc_open_lock`, per-CPU hold counts, `tx_sync_lock`, and CV broadcasts is the core correctness constraint. A TXG cannot be handed to sync until every open handle has released to sync, and new handles must observe monotonically nondecreasing open TXGs.

The sync and quiesce threads maintain a bounded pipeline: one open TXG, at most one quiescing TXG, and at most one quiesced TXG waiting for sync. Waiters must not hold DSL pool config locks when calling the wait APIs, as asserted in the code. Callback dispatch occurs only after the TXG has synced; callback list ownership is transferred to taskq-owned temporary lists.
