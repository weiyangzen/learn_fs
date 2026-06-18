# sources/distributed-fs/ceph-client/kernel/rcu/tree.c

## Purpose

`tree.c` is the main implementation file for Linux Tree RCU in this source tree. It owns the global `rcu_state`, the per-CPU `rcu_data` array, normal grace-period sequencing, callback enqueueing and invocation, synchronous `synchronize_rcu()` handling, polled grace-period APIs, `rcu_barrier()`, CPU hotplug state transitions, boot-time RCU tree geometry, and the runtime path that invokes RCU core work from either `RCU_SOFTIRQ` or per-CPU `rcuc/%u` kthreads.

The file is also the compilation unit that includes `tree_stall.h`, `tree_exp.h`, `tree_nocb.h`, and `tree_plugin.h` at the end. Those headers are not standalone public headers; they are implementation fragments that depend on `tree.c` statics such as `rcu_state`, `rcu_data`, `rcu_gp_kthread_wake()`, `rcu_report_qs_rnp()`, and callback-list helpers.

## Important APIs, functions, and data

Core exported APIs implemented here include:

- `call_rcu()` and `call_rcu_hurry()`, which enqueue callbacks onto the current CPU's segmented callback list, or route them to NOCB offload handling when configured.
- `synchronize_rcu()` and the internal `synchronize_rcu_normal()`, which wait for a full normal grace period unless runtime policy redirects to expedited RCU.
- `get_state_synchronize_rcu()`, `get_state_synchronize_rcu_full()`, `start_poll_synchronize_rcu()`, `start_poll_synchronize_rcu_full()`, `poll_state_synchronize_rcu()`, `poll_state_synchronize_rcu_full()`, `cond_synchronize_rcu()`, and `cond_synchronize_rcu_full()`, which expose cookie-based grace-period polling and conditional waiting.
- `rcu_barrier()`, which waits for all in-flight RCU callbacks to run by entraining barrier callbacks on CPUs with pending callback lists.
- `rcu_force_quiescent_state()`, which requests a force-quiescent-state scan by the grace-period kthread.
- Diagnostic and torture-test exports such as `rcu_get_gp_seq()`, `rcu_exp_batches_completed()`, `rcutorture_get_gp_data()`, `rcutorture_gather_gp_seqs()`, `rcutorture_format_gp_seqs()`, `rcu_get_gpwrap_count()`, `rcu_get_gp_kthreads_prio()`, `rcu_set_gpwrap_lag()`, and `rcu_gp_set_torture_wait()`.
- Context-tracking helpers `rcu_is_watching()`, `rcu_softirq_qs()`, `rcu_momentary_eqs()`, `rcu_request_urgent_qs_task()`, and `rcu_needs_cpu()`.
- CPU lifecycle hooks `rcutree_prepare_cpu()`, `rcutree_online_cpu()`, `rcutree_report_cpu_starting()`, `rcutree_report_cpu_dead()`, `rcutree_migrate_callbacks()`, `rcutree_dead_cpu()`, `rcutree_dying_cpu()`, and `rcutree_offline_cpu()`.
- Boot/runtime initialization entry points `rcu_scheduler_starting()`, `rcu_init_geometry()`, and `rcu_init()`.

Important file-local data:

- `DEFINE_PER_CPU_SHARED_ALIGNED(struct rcu_data, rcu_data)` is the per-CPU runtime state for callbacks, quiescent-state tracking, NOCB state, hotplug state, and diagnostics.
- `static struct rcu_state rcu_state` is the global state machine containing the `rcu_node` hierarchy, GP sequence counters, wait queues, expedited GP state, barrier state, callback-overload state, hotplug serialization, and synchronize-RCU request batching.
- Tunables include `use_softirq`, `rcu_fanout_leaf`, `rcu_fanout_exact`, `kthread_prio`, `jiffies_till_first_fqs`, `jiffies_till_next_fqs`, `jiffies_till_sched_qs`, `blimit`, `qhimark`, `qlowmark`, `qovld`, `rcu_divisor`, `rcu_resched_ns`, `rcu_normal_wake_from_gp`, and test-only delay parameters.
- `rcu_gp_wq` is a per-CPU workqueue used by Tree SRCU and expedited/polled GP work; `sync_wq` runs deferred completion work for batched `synchronize_rcu()` users.

## Control flow

Normal grace-period requests start when callbacks or polling APIs call `rcu_start_this_gp()`. This function performs funnel locking up the `rcu_node` hierarchy from a leaf toward the root, records the furthest needed `gp_seq` in each relevant `rcu_node`, sets `RCU_GP_FLAG_INIT` in `rcu_state.gp_flags` if a new grace period must start, and tells the caller whether to wake the GP kthread. The wake path is centralized in `rcu_gp_kthread_wake()`, which avoids unnecessary self-wakeups and records wake diagnostics.

`rcu_gp_kthread()` is the normal GP state machine. It waits in `RCU_GP_WAIT_GPS` for `RCU_GP_FLAG_INIT`, calls `rcu_gp_init()`, loops in `rcu_gp_fqs_loop()` until all CPUs/tasks have reported quiescent states, then calls `rcu_gp_cleanup()` and returns to the wait state. `rcu_gp_init()` starts `rcu_state.gp_seq`, initializes the batched `synchronize_rcu()` wait-head list, applies pending CPU hotplug mask changes, sets each `rcu_node` `qsmask` from `qsmaskinit`, starts priority boosting for blocked readers, and immediately reports a quiescent state for the GP kthread's own CPU. `rcu_gp_fqs_loop()` performs delayed or overload-accelerated force-QS scans through `force_qs_rnp()`, which checks dynticks snapshots, offline CPUs, and blocked preemptible readers. `rcu_gp_cleanup()` propagates the completed `gp_seq` breadth-first to every `rcu_node`, advances callbacks, checks for more requested GPs, ends the global sequence, schedules `synchronize_rcu()` completion work, and optionally pokes all CPUs in strict-GP configurations.

Per-CPU RCU core work begins from `rcu_sched_clock_irq()`, `invoke_rcu_core()`, the `RCU_SOFTIRQ` handler `rcu_core_si()`, or the per-CPU `rcu_cpu_kthread()`. `rcu_core()` first handles deferred preemptible-RCU quiescent states, then calls `rcu_check_quiescent_state()` to observe new GP starts/ends and report the first local quiescent state through `rcu_report_qs_rdp()`. If ready callbacks exist and the CPU is not NOCB-offloaded, `rcu_do_batch()` extracts ready callbacks, invokes them under RCU callback tracing/debug state, respects callback count and time limits, reinserts any leftovers, and updates overload bookkeeping.

Callback enqueueing enters `__call_rcu_common()`. It validates the `rcu_head`, records debug/KASAN metadata, selects current `rcu_data`, initializes early-boot callback lists if needed, updates callback-overload masks, then routes to `call_rcu_nocb()` for offloaded CPUs or `call_rcu_core()` for normal CPUs. `call_rcu_core()` appends to the segmented list, invokes RCU core if the CPU is in an extended quiescent state, and, under high callback pressure, starts or kicks a grace period through `rcu_accelerate_cbs_unlocked()` or `rcu_force_quiescent_state()`.

`synchronize_rcu()` has three major paths. During earliest boot, `rcu_blocking_is_gp()` treats the call as a vacuous grace period and advances only the relevant counters. At runtime, global policy can route it to `synchronize_rcu_expedited()` from `tree_exp.h`; otherwise `synchronize_rcu_normal()` either uses `wait_rcu_gp(call_rcu_hurry)` or, on small systems or when enabled by `rcu_normal_wake_from_gp`, batches waiters into the `rcu_state.srs_next` lockless list and completes them at GP cleanup through `rcu_sr_normal_gp_cleanup()` and `rcu_sr_normal_gp_cleanup_work()`.

The polled API maintains `rcu_state.gp_seq_polled` and two snapshots, one for normal and one for expedited GP starts. `rcu_poll_gp_seq_start()` starts the polled sequence if idle, and `rcu_poll_gp_seq_end()` ends it only if the matching snapshot is still current. The "full" poll state records both `rcu_state.gp_seq` and `rcu_state.expedited_sequence`; `poll_state_synchronize_rcu_full()` deliberately checks the root `rcu_node` `gp_seq` for the normal path so callback invocation ordering is not reported complete too early.

`rcu_barrier()` serializes callers with `barrier_mutex`, starts `barrier_sequence`, scans every possible CPU, and entrains `rcu_barrier_callback()` behind existing callbacks on each CPU that has pending work. It handles online CPUs by calling `rcu_barrier_handler()` on the target CPU and offline CPUs under the barrier lock. It also flushes NOCB bypass queues so lazy/offloaded callbacks cannot hide from the barrier. The initial atomic count of two prevents a too-early completion if callbacks execute immediately.

CPU hotplug control flow is split across early prepare, precise starting/dead hooks, and later online/offline cpuhp stages. `rcutree_report_cpu_starting()` runs on the incoming CPU with interrupts disabled, marks the CPU in `qsmaskinitnext` and `expmaskinitnext`, updates `rcu_state.ncpus`, and handles any impossible "RCU already waiting on incoming CPU" state by reporting a QS. `rcutree_report_cpu_dead()` runs on the outgoing CPU with interrupts disabled, reports a QS before clearing `qsmaskinitnext`, and leaves later propagation to `rcu_gp_init()` and `rcu_cleanup_dead_rnp()`. `rcutree_migrate_callbacks()` moves callbacks from a non-offloaded dying CPU to the current CPU and preserves barrier and GP ordering.

## State and persistence behavior

This code has no filesystem persistence. Its persistent state is in kernel memory and is designed to survive for the life of the boot:

- `rcu_state.gp_seq`, per-node `rnp->gp_seq`, and per-CPU `rdp->gp_seq` are sequence counters encoding whether a grace period is idle or in progress and which callbacks can advance.
- `gp_seq_needed` fields cache future GP demand at per-CPU, leaf, and internal-node levels to reduce contention and avoid losing callback requests.
- `qsmask`, `qsmaskinit`, and `qsmaskinitnext` encode current, committed, and pending-online CPU masks for normal grace periods. `expmask`, `expmaskinit`, and `expmaskinitnext` do the analogous work for expedited grace periods.
- `rcu_segcblist` segments in each `rcu_data` hold callbacks in done, wait, next-ready, and next buckets. These queues are protected by local IRQ state, `rcu_node` locks, or NOCB locks depending on CPU mode.
- `srs_next`, `srs_wait_tail`, `srs_done_tail`, and `srs_wait_nodes[]` form a lockless/RCU-GP-assisted batching structure for normal `synchronize_rcu()` users.
- `barrier_sequence`, `barrier_seq_snap`, `barrier_cpu_count`, and `barrier_completion` track in-flight `rcu_barrier()` epochs.
- Hotplug fields such as `ncpus`, `n_online_cpus`, `cpu_started`, `beenonline`, `rcu_ofl_gp_seq`, and `rcu_onl_gp_seq` preserve CPU lifecycle state across GP boundaries.

Ordering is central to correctness. The file uses `raw_spin_lock_rcu_node()` unlock-lock chains, explicit `smp_mb()`, acquire/release operations on context-tracking snapshots and `srs_done_tail`, and sequence-counter helpers from `rcu_seq_*()` to enforce GP memory-order guarantees. The comments around `rcu_gp_init()`, `rcu_gp_cleanup()`, `poll_state_synchronize_rcu_full()`, and hotplug hooks document several races this ordering prevents, especially newly onlined CPUs being missed by a GP and callbacks being observed before a completed GP is fully published.

## Dependencies and integration points

`tree.c` integrates with:

- Core scheduler and interrupt infrastructure: scheduler ticks, `set_need_resched_current()`, `resched_cpu()`, softirqs, irq work, `smpboot_register_percpu_thread()`, kthreads, and workqueues.
- Context tracking and dynticks: `ct_rcu_watching()`, `ct_rcu_watching_cpu_acquire()`, `ct_state_inc()`, idle/user/nohz-full state, and tick dependencies.
- RCU support files: `tree.h`, `rcu.h`, `rcu_segcblist.h`, `tree_stall.h`, `tree_exp.h`, `tree_nocb.h`, and `tree_plugin.h`.
- CPU hotplug and power management: cpuhp callbacks, stop-machine assumptions, `pm_notifier()`, suspend/hibernate expedite and lazy-callback policy changes.
- Debug and observability: tracepoints, lockdep maps, `CONFIG_PROVE_RCU`, stall notifiers, KASAN aux stack recording, debug-objects RCU head tracking, `mem_dump_obj()`, and torture-test exports.
- Memory reclaim and OOM-related behavior: `WQ_MEM_RECLAIM` workqueues, NOCB bypass flushing, callback barrier support, and conservative behavior when kthread creation fails.

The file's inclusion model is important: `tree_exp.h`, `tree_nocb.h`, `tree_plugin.h`, and `tree_stall.h` are compiled into the same translation unit after all major statics are defined. A change to static function names, ordering-sensitive data, or compile-time guards in `tree.c` can break these included implementation headers even though a normal C include dependency graph may not make that obvious.

## Risks and correctness concerns

The highest-risk areas are concurrency and ordering:

- `rcu_gp_init()` must start `rcu_state.gp_seq` before scanning hotplug state, or a newly onlining CPU can be missed by the current GP.
- `rcu_gp_cleanup()` must publish completed GP state to every `rcu_node` before ending the global `rcu_state.gp_seq`, or CPUs and pollers can see inconsistent completion.
- `rcu_report_qs_rnp()` releases the incoming lock on all paths and walks parent nodes with interrupts disabled; callers must not assume the original lock remains held.
- `rcu_do_batch()` temporarily extracts callbacks and invokes arbitrary callback functions; count accounting and reinsertion must remain correct for `rcu_barrier()` and debug checks.
- The `srs_*` batching structure relies on lockless `llist` operations and fixed wait-head nodes. Running out of wait heads is handled by starting another polled GP, but changes here can strand `synchronize_rcu()` waiters.
- CPU hotplug paths distinguish `qsmaskinit`, `qsmaskinitnext`, `expmaskinit`, and `expmaskinitnext`. Clearing a CPU from the wrong mask too early can allow use-after-free by treating an active reader as quiescent.
- NOCB/offloaded callback state must be accessed under NOCB locks. The normal GP cleanup path deliberately avoids `rcu_accelerate_cbs()` on offloaded CPUs because `nocb_lock` contention and locking context matter.
- Module tunables can drastically change timing, batching, and urgency. Tests need coverage for defaults and configured values such as `use_softirq=0`, strict GP, lazy callbacks, NOCB CPUs, and large `rcu_fanout_leaf`.

## Test signals

Useful validation signals for this file include:

- `rcutorture` scenarios covering normal, expedited, lazy, NOCB, CPU hotplug, stall, and callback-flood cases. The exported torture hooks in this file exist specifically to inspect GP sequence progress and inject delays.
- CPU hotplug stress while continuously running `call_rcu()`, `synchronize_rcu()`, `synchronize_rcu_expedited()`, and `rcu_barrier()`, checking for stalls, WARNs, lost callbacks, and counter wrap diagnostics.
- Boot tests with varied `rcutree.*` parameters: `use_softirq`, `rcu_fanout_leaf`, `jiffies_till_first_fqs`, `jiffies_till_next_fqs`, `qhimark`, `qovld`, `rcu_normal_wake_from_gp`, and `kthread_prio`.
- Lockdep/PROVE_RCU/KCSAN/KASAN/debug-objects builds to catch illegal RCU read-side usage, double `call_rcu()`, stale callback heads, missing barriers, and offline-CPU use.
- Tracepoint inspection for `rcu_grace_period`, `rcu_future_grace_period`, `rcu_quiescent_state_report`, `rcu_batch_start/end`, `rcu_barrier`, and expedited events from `tree_exp.h`.
- Suspend/hibernate tests verifying `rcu_pm_notify()` expedites before suspend and restores normal/lazy policy afterward.
