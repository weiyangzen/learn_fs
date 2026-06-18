# sources/distributed-fs/ceph-client/kernel/rcu/sync.c

## Purpose
Provides `rcu_sync`, a small state-machine helper for lightweight reader/writer coordination. Updaters use it to force readers off a fast path during a write-side interval and then allow fast-path readers again only after the required RCU grace period. The design batches closely spaced enter/exit cycles so repeated writers do not always pay a fresh grace-period cost.

## Important APIs, Types, and Functions
The public API is `rcu_sync_init()`, `rcu_sync_enter()`, `rcu_sync_exit()`, and `rcu_sync_dtor()` for `struct rcu_sync` from `<linux/rcu_sync.h>`. Internal states are `GP_IDLE`, `GP_ENTER`, `GP_PASSED`, `GP_EXIT`, and `GP_REPLAY`. `rss_lock` aliases `gp_wait.lock`, so the waitqueue lock also protects `gp_state` and `gp_count`. `rcu_sync_call()` queues `cb_head` with `call_rcu_hurry()`, and `rcu_sync_func()` is the RCU callback that advances the state machine and wakes waiters.

## Control Flow
`rcu_sync_init()` zeroes the structure and initializes the waitqueue. `rcu_sync_enter()` takes `rss_lock`, observes the current state, transitions an idle structure to `GP_ENTER`, increments `gp_count`, and drops the lock. The first entrant synchronously waits for `synchronize_rcu()` and then directly invokes `rcu_sync_func()` to mark that all pre-existing readers have been pushed through a grace period. Later entrants wait until `gp_state >= GP_PASSED`, avoiding redundant grace-period waits when another writer already paid the cost.

`rcu_sync_exit()` decrements `gp_count`. When the last active writer exits from `GP_PASSED`, it changes the state to `GP_EXIT` and queues the callback; that callback will run after a grace period and restore `GP_IDLE`. If a new exit sequence overlaps a callback already queued in `GP_EXIT`, exit marks `GP_REPLAY` so `rcu_sync_func()` requeues itself for another post-exit grace period rather than allowing readers back too early.

`rcu_sync_func()` handles three cases under lock: if writers are active (`gp_count` nonzero), it records `GP_PASSED` and wakes waiters; if it sees `GP_REPLAY`, it changes back to `GP_EXIT` and queues another callback; otherwise it marks `GP_IDLE`, allowing readers to use their fast paths. `rcu_sync_dtor()` normalizes `GP_REPLAY` to `GP_EXIT`, waits for outstanding callbacks via `rcu_barrier()` when not idle, and warns if the object fails to return idle.

## State and Persistence Behavior
The state is in-memory and embedded in the caller-owned `struct rcu_sync`. `gp_state` represents the state-machine phase, `gp_count` counts active write-side users, `gp_wait` wakes entrants waiting for the initial grace period, and `cb_head` is reused for queued RCU callbacks. No persistent storage exists. Correct lifetime requires `rcu_sync_dtor()` before freeing an object that might have a pending callback.

## Dependencies and Integration Points
The file depends on generic RCU (`synchronize_rcu()`, `call_rcu_hurry()`, `rcu_barrier()`), waitqueue locking/wakeup, spinlock IRQ-save sections, scheduler declarations, and the public `rcu_sync_is_idle()` style reader-side checks supplied by `<linux/rcu_sync.h>`. It integrates with subsystems that maintain a fast reader path but need to temporarily exclude it for updates, commonly percpu-rwsem-like and file-system or memory-management synchronization helpers.

## Risks and Edge Cases
The key risk is state-machine drift: `GP_REPLAY` exists specifically to avoid a close enter/exit pair racing with the post-exit callback and re-enabling fast readers too early. `rcu_sync_enter()` directly invokes `rcu_sync_func()` after `synchronize_rcu()`, so callback-state assumptions must remain valid even though that path is not an asynchronous RCU callback invocation. Destructor misuse while `gp_count` is nonzero or `gp_state == GP_PASSED` indicates callers are destroying an active synchronization domain. Because the callback head is embedded and reused, queuing discipline must ensure only one relevant RCU callback is pending for a given state.

## Test Signals
Tests should stress nested and concurrent `rcu_sync_enter()`/`rcu_sync_exit()` pairs, rapid enter/exit replay races, destruction with and without pending callbacks, and reader fast-path checks around each transition. Runtime signals include WARNs for impossible `gp_state` values, nonzero `gp_count` at destruction, and failure to return to `GP_IDLE` after `rcu_barrier()`. Lockdep and RCU callback debugging are useful for double-queue and lifetime issues.
