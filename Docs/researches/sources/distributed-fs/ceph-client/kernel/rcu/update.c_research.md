# sources/distributed-fs/ceph-client/kernel/rcu/update.c

## Purpose
`update.c` provides common public RCU update-side infrastructure: boot/runtime mode transitions, expedited-vs-normal policy, lazy callback urgency controls, lockdep read-side queries, synchronous grace-period waiting helpers, debug object hooks for `rcu_head`, torture/test exports, stall-warning module parameters, and early boot self tests. It includes `tasks.h` to bring in Tasks RCU support.

## Important APIs, Types, and Functions
- Mode controls: `rcu_gp_is_normal()`, `rcu_gp_is_expedited()`, `rcu_expedite_gp()`, `rcu_unexpedite_gp()`, `rcu_async_should_hurry()`, `rcu_async_hurry()`, `rcu_async_relax()`, `rcu_end_inkernel_boot()`, and `rcu_set_runtime_mode()`.
- Lockdep queries: `debug_lockdep_rcu_enabled()`, `rcu_read_lock_held()`, `rcu_read_lock_bh_held()`, `rcu_read_lock_sched_held()`, and `rcu_read_lock_any_held()`.
- Grace-period wait helpers: `wakeme_after_rcu()`, `__wait_rcu_gp()`, `finish_rcuwait()`, and `get_completed_synchronize_rcu()`.
- Debug/test exports: `init_rcu_head()`, `destroy_rcu_head()`, `init_rcu_head_on_stack()`, `destroy_rcu_head_on_stack()`, `do_trace_rcu_torture_read()`, `torture_sched_setaffinity()`, `synchronize_rcu_trivial_preempt()`, `rcu_early_boot_tests()`, and `rcupdate_announce_bootup_oddness()`.
- Tunables: `rcu_expedited`, `rcu_normal`, `rcu_normal_after_boot`, stall-warning parameters, and `rcu_self_test`.

## Control Flow
During early boot, expedited and hurry nesting atomics start nonzero so early RCU operations avoid long delays. `rcu_set_runtime_mode()` runs as a core initcall, executes synchronous primitive self tests when prove-RCU is enabled, marks `rcu_scheduler_active` as running, frees scheduler-running callbacks, and retests. Later `rcu_end_inkernel_boot()` unexpedites, relaxes async callbacks, optionally forces normal mode after boot, and marks boot complete for torture users.

Callers that need to wait for several RCU flavors use `__wait_rcu_gp()`. It initializes on-stack `rcu_head` objects, deduplicates identical callback functions, queues `wakeme_after_rcu()` callbacks, waits for completions in the requested task state, and destroys stack debug objects. Lockdep query functions first call `rcu_read_lock_held_common()` to account for disabled lockdep, idle/non-watching CPUs, and offline CPUs, then inspect lock maps or preempt/softirq state.

When `CONFIG_DEBUG_OBJECTS_RCU_HEAD` is enabled, the file registers debug object operations for stack and heap/static `rcu_head` lifetime validation. With prove-RCU self tests enabled, early boot queues normal RCU, SRCU, and `kfree_rcu()` callbacks, then verifies barriers and poll cookies at late init.

## State and Persistence
State is in module parameters and in-memory globals: expedited/normal mode flags, `rcu_async_hurry_nesting`, `rcu_expedited_nesting`, `rcu_boot_ended`, lockdep maps, stall-warning tunables, early self-test counters, and static SRCU state for tests. There is no durable persistence beyond live boot/module parameters.

## Dependencies and Integration Points
The file depends on core RCU headers, scheduler state, lockdep, debugobjects, SRCU, Tasks RCU, torture modules, module parameters, completions, kprobes-safe tracing, and memory allocation. It exports many symbols used by drivers, kernel subsystems, torture tests, and RCU internals.

## Risks
Reference-count-like nesting APIs (`rcu_expedite_gp()`/`rcu_unexpedite_gp()` and async hurry/relax) can underflow or leave global policy unexpectedly expedited/lazy if callers are imbalanced. `__wait_rcu_gp()` must deduplicate callback functions correctly to avoid double waiting or double stack-object destruction. Lockdep helpers must avoid false positives while the scheduler, lockdep, CPU online state, or RCU watching state is not stable. Early boot self tests depend on callback execution ordering and SRCU cleanup.

## Test Signals
Signals include boot logs from `rcu_test_sync_prims()`, prove-RCU self-test callback counts, lockdep warnings from invalid RCU read-side use, module parameter behavior for normal/expedited/stall settings, torture tests that call exported affinity and trace helpers, and debugobjects reports for invalid `rcu_head` lifetime.
