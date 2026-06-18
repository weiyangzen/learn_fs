# subset-b-006046 research

Work item: `subset-b-006046`

Sources researched:
- `sources/distributed-fs/ceph-client/kernel/rcu/tree.c`
- `sources/distributed-fs/ceph-client/kernel/rcu/tree.h`
- `sources/distributed-fs/ceph-client/kernel/rcu/tree_exp.h`

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/tree.h

## Purpose

`tree.h` is the internal data-structure and forward-declaration header for Tree RCU. It is included by `tree.c` before the implementation fragments, and it defines the core objects used by normal grace periods, expedited grace periods, per-CPU callback processing, CPU hotplug, NOCB offload, priority boosting, stall diagnostics, and batched `synchronize_rcu()` completion.

This is not a public RCU API header. It exposes internals within the `kernel/rcu` implementation and intentionally couples `tree.c`, `tree_exp.h`, `tree_nocb.h`, `tree_plugin.h`, and `tree_stall.h`.

## Important types, macros, and declarations

`struct rcu_exp_work` carries an expedited GP sequence snapshot plus a `kthread_work` object. It is embedded both in `struct rcu_node` for per-leaf expedited CPU selection and used on the stack by `synchronize_rcu_expedited()`.

`struct rcu_node` represents one node in the combining tree:

- `lock` protects the node's GP masks and, for the root node, selected `rcu_state` fields.
- `gp_seq`, `gp_seq_needed`, and `completedqs` track current and requested normal grace periods.
- `qsmask`, `qsmaskinit`, `qsmaskinitnext`, and `rcu_gp_init_mask` track CPUs or child nodes still needed for the current normal GP, the committed online mask, pending online/offline changes, and CPUs found offline during GP init.
- `expmask`, `expmaskinit`, `expmaskinitnext`, `exp_seq_rq`, `exp_wq[]`, `exp_kworker`, `rew`, `exp_poll_lock`, `exp_seq_poll_rq`, and `exp_poll_wq` support expedited GP selection, wait/wake funneling, and polled expedited GPs.
- `cbovldmask` tracks CPUs whose callback queues are overloaded so GP forcing can be more aggressive.
- `ffmask` tracks fully functional CPUs for stall diagnostics and irq-work checks.
- `grplo`, `grphi`, `grpnum`, `grpmask`, `level`, and `parent` encode the tree topology.
- `blkd_tasks`, `gp_tasks`, `exp_tasks`, `boost_tasks`, `boost_mtx`, boost kthread state, and `wait_blkd_tasks` support preemptible-RCU readers and priority boosting.
- Optional `nocb_gp_wq[]` gives NOCB callback kthreads a per-node GP wait target.

`leaf_node_cpu_bit(rnp, cpu)` computes a node-local CPU bit for leaf masks. This is a common helper for translating a global CPU number into `qsmask`/`expmask` space.

`union rcu_noqs` stores normal and expedited "CPU still owes a quiescent state" flags in separately addressable bytes while allowing an aggregate 16-bit view.

`struct rcu_snap_record` stores cputime, irq, softirq, context-switch, and jiffies snapshots for CPU-stall diagnostics.

`struct rcu_data` is the per-CPU RCU state:

- Grace-period and quiescent-state fields include `gp_seq`, `gp_seq_needed`, `cpu_no_qs`, `core_needs_qs`, `beenonline`, `gpwrap`, `cpu_started`, `mynode`, `grpmask`, `ticks_this_gp`, `defer_qs_iw`, `defer_qs_pending`, and `strict_work`.
- Callback fields include `cblist`, `qlen_last_fqs_check`, `n_cbs_invoked`, `n_force_qs_snap`, and `blimit`.
- Dynticks/nohz fields include `watching_snap`, `rcu_need_heavy_qs`, `rcu_urgent_qs`, `rcu_forced_tick`, and `rcu_forced_tick_exp`.
- Barrier and expedited fields include `barrier_seq_snap`, `barrier_head`, and `exp_watching_snap`.
- `CONFIG_RCU_NOCB_CPU` fields hold callback offload wait queues, locks, bypass lists, timers, GP and CB kthread references, wakeup state, and offload toggling links.
- Per-CPU RCU core kthread fields include `rcu_cpu_kthread_task`, `rcu_cpu_kthread_status`, `rcu_cpu_has_work`, and `rcuc_activity`.
- Diagnostic fields include `softirq_snap`, `rcu_iw`, `rcu_iw_pending`, online/offline GP snapshots, `last_fqs_resched`, `last_sched_clock`, `snap_record`, `lazy_len`, and the CPU number.

`struct sr_wait_node` and the `SR_*` constants define the fixed dummy wait-head pool used by normal `synchronize_rcu()` batching in `tree.c`.

`struct rcu_state` is the global Tree RCU object. It embeds the dense-array `rcu_node` hierarchy and level pointers, tracks CPU counts, stores root-lock-protected GP state (`gp_seq`, `gp_kthread`, `gp_wq`, `gp_flags`, `gp_state`, polled sequence state), owns `rcu_barrier()` state, expedited GP state, force-QS timing, stall timing, global name/abbreviation strings, offline-hotplug serialization, batched synchronize-RCU lists, and optional NOCB setup state.

The header also defines:

- RCU kthread tracing states `RCU_KTHREAD_STOPPED`, `RUNNING`, `WAITING`, `OFFCPU`, and `YIELDING`.
- NOCB deferred wake levels `RCU_NOCB_WAKE_NOT`, `BYPASS`, `LAZY`, and `WAKE`.
- Timing constants `RCU_JIFFIES_TILL_FORCE_QS`, `RCU_JIFFIES_FQS_DIV`, and `RCU_STALL_RAT_DELAY`.
- `rcu_wait(cond)`, a simple interruptible wait loop used by RCU internals.
- GP flags `RCU_GP_FLAG_INIT`, `RCU_GP_FLAG_FQS`, and `RCU_GP_FLAG_OVLD`.
- GP state-machine values `RCU_GP_IDLE`, `WAIT_GPS`, `DONE_GPS`, `ONOFF`, `INIT`, `WAIT_FQS`, `DOING_FQS`, `CLEANUP`, and `CLEANED`.
- Name/abbreviation selection for `CONFIG_PREEMPT_RCU` versus non-preempt Tree RCU, including tracepoint-string handling under `CONFIG_TRACING`.

Forward declarations cover implementation fragments for preemptible RCU, NOCB, boost, stall, nohz-full, and expedited polling. The `rcu_nocb_lock_irqsave()` macro changes behavior depending on `CONFIG_RCU_NOCB_CPU`: with NOCB it disables IRQs and conditionally takes `nocb_lock`; without NOCB it only disables IRQs.

## Control flow enabled by the header

The central design is a combining tree over CPUs. Leaf `rcu_node` objects represent ranges of CPU IDs; internal nodes represent groups of children. During GP initialization, `tree.c` sets each node's `qsmask` to the current online mask. As CPUs or tasks report quiescent states, bits clear at the leaf and then propagate upward by clearing the child `grpmask` in each parent. The grace period completes when the root has no remaining `qsmask` bits and no blocked preemptible readers.

The same topology is reused for expedited GPs through `expmask` and `exp_wq[]`. Expedited requesters funnel through `exp_seq_rq` under `exp_lock`, wait on a sequence-indexed wait queue, and either perform the expedited GP or piggyback on a concurrent one.

Per-CPU `rcu_data` is the bridge between local events and the global tree. Scheduler ticks and RCU core work update `cpu_no_qs`, `core_needs_qs`, callback segments, and urgency fields; `mynode` and `grpmask` let the local CPU report into the proper leaf node without global CPU-mask scans on the hot path.

NOCB fields split callback ownership away from the invoking CPU. In non-offloaded mode, `tree.c` manipulates `cblist` with IRQ exclusion and leaf-node locks; in offloaded mode, the NOCB locks, bypass list, and GP/CB kthreads become the integration point. This is why the header groups NOCB fields by producer, GP-kthread, and callback-kthread cachelines.

## State and persistence behavior

All state in this header is in-memory kernel state. The types are deliberately cacheline-aligned in several places because they are written by different CPUs in hot paths:

- `struct rcu_node` uses cacheline/internode alignment for locks and expedited state to reduce contention in large systems.
- `struct rcu_data` groups fields by usage: GP/QS handling, callback handling, dynticks, barrier/expedite, NOCB offload, boosting, and diagnostics. Some NOCB groups are explicitly separated onto new cachelines.
- `struct rcu_state` keeps root-lock-protected fields together and comments the lock domains for barrier and GP fields.

Persistence across events is semantic rather than durable. `gp_seq` values preserve grace-period identity across callback enqueue, GP start, GP cleanup, and poll checks. `qsmaskinitnext` and `expmaskinitnext` preserve hotplug changes until the next normal or expedited reset commits them. `barrier_seq_snap` and `barrier_sequence` preserve barrier epochs so repeated or concurrent `rcu_barrier()` calls can avoid duplicate work.

## Dependencies and integration points

The header depends on kernel infrastructure headers for kthreads, spinlocks, rtmutexes, CPU masks, seqlocks, simple wait queues, cache alignment, and `linux/rcu_node_tree.h` geometry constants. It depends on `rcu_segcblist.h` for segmented callback lists.

Its declarations are consumed by:

- `tree.c` for all core normal RCU implementation.
- `tree_exp.h` for expedited masks, work items, expedited wait queues, and polled expedited GP state.
- `tree_nocb.h` for callback offload fields and helper declarations.
- `tree_plugin.h` for preemptible-RCU blocked-task and priority-boost fields.
- `tree_stall.h` for stall timing, diagnostics, and irq-work fields.

## Risks and correctness concerns

The main risk is that this header encodes lock ownership and memory-order contracts through field comments and grouping rather than type-level enforcement. Misusing `qsmaskinitnext` instead of `qsmaskinit`, or reading `gp_seq` from `rcu_state` where the root node's `gp_seq` is required, can create subtle grace-period shortening bugs.

Bit masks are node-local, not global CPU masks. Code must use `leaf_node_cpu_bit()` or `rdp->grpmask` rather than `BIT(cpu)` for `rcu_node` masks. This matters especially for CPU hotplug, expedited selection, and barrier entrainment.

The dense-array hierarchy assumes boot-time geometry has been computed before initialization and remains stable. `rcu_init_geometry()` may adjust `rcu_num_lvls`, `num_rcu_lvl[]`, and `rcu_num_nodes`, but the arrays are still sized by compile-time maxima.

NOCB state has several locks and cacheline ownership domains. Accessing offloaded callback lists with only local IRQ exclusion is incorrect; callers must follow the `rcu_nocb_lock*()` and helper contracts.

The forward declarations make include-order changes risky. `tree_exp.h` and other implementation headers expect specific statics and prototypes to exist in this translation unit.

## Test signals

Good validation signals for data-structure changes include:

- Build coverage across `CONFIG_PREEMPT_RCU`, `CONFIG_RCU_NOCB_CPU`, `CONFIG_RCU_BOOST`, `CONFIG_NO_HZ_FULL`, `CONFIG_HOTPLUG_CPU`, `CONFIG_RCU_STRICT_GRACE_PERIOD`, `CONFIG_TRACING`, and `CONFIG_PROVE_RCU`.
- RCU torture tests with CPU hotplug and callback flooding to stress `qsmask*`, `expmask*`, `cbovldmask`, `gp_seq`, and NOCB fields.
- Lockdep and KCSAN runs focused on `rcu_node->lock`, `barrier_lock`, NOCB locks, and expedited `exp_lock`.
- Boot tests on small and large `nr_cpu_ids` values, including non-default `rcu_fanout_leaf`, to validate hierarchy geometry and cacheline-sensitive tree traversal.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_exp.h -->
# sources/distributed-fs/ceph-client/kernel/rcu/tree_exp.h

## Purpose

`tree_exp.h` implements expedited Tree RCU grace periods inside the `tree.c` translation unit. Expedited grace periods provide the same semantic guarantee as `synchronize_rcu()`, but they aggressively identify and poke CPUs that might still be in pre-existing RCU read-side critical sections. The file also implements expedited variants of the polled and conditional synchronization APIs.

Because this header is included at the end of `tree.c`, it directly uses `rcu_state`, `rcu_data`, the `rcu_node` hierarchy, normal polled-GP helpers, context tracking helpers, stall reporting helpers, NOCB/workqueue state, and preemptible-RCU hooks declared in `tree.h` and defined in `tree.c` or `tree_plugin.h`.

## Important APIs and functions

Sequence helpers:

- `rcu_exp_gp_seq_start()` starts `rcu_state.expedited_sequence` and also starts the expedited snapshot of the combined polled GP state.
- `rcu_exp_gp_seq_endval()` returns the sequence value that will represent the end of the current expedited GP.
- `rcu_exp_gp_seq_end()` ends both the polled expedited snapshot and `expedited_sequence`, then issues a memory barrier to serialize consecutive expedited GPs.
- `rcu_exp_gp_seq_snap()` returns a snapshot cookie and orders caller updates before remote CPUs observe the expedited GP.
- `rcu_exp_gp_seq_done()` tests whether a snapshot has completed.

Tree reset and reporting:

- `sync_exp_reset_tree_hotplug()` propagates newly onlined CPUs into `expmaskinit` up the tree. Offline CPUs are intentionally not cleared from expedited initial masks, so the state is the union of CPUs that have ever been online.
- `sync_exp_reset_tree()` initializes each node's `expmask` from `expmaskinit` and records blocked preemptible tasks in `exp_tasks`.
- `sync_rcu_exp_done()` and `sync_rcu_exp_done_unlocked()` test whether a node has no remaining CPUs and no blocking tasks for the expedited GP.
- `__rcu_report_exp_rnp()`, `rcu_report_exp_rnp()`, `rcu_report_exp_cpu_mult()`, and `rcu_report_exp_rdp()` clear expedited wait bits and propagate completion up the tree, waking the global expedited wait queue if the root completes.

Expedited request funnel and CPU selection:

- `sync_exp_work_done()` tests completion and provides the memory barrier paired with `rcu_seq_end()`.
- `exp_funnel_lock()` lets concurrent callers either piggyback on an existing expedited GP, wait at an intermediate `rcu_node`, or acquire `rcu_state.exp_mutex` and become the worker for a new expedited GP.
- `__sync_rcu_exp_select_node_cpus()` scans one leaf node, treats self/offline/idle CPUs as already quiescent where valid, records context-tracking snapshots, sends IPIs to remaining CPUs via `smp_call_function_single()`, retries races with CPU hotplug, and reports CPUs that went idle or offline.
- `sync_rcu_exp_select_cpus()` resets expedited masks, schedules or directly runs per-leaf CPU selection work, and flushes per-node workers.
- `rcu_exp_sel_wait_wake()` drives a full expedited GP by selecting CPUs and then waiting/waking.

Wait and stall handling:

- `synchronize_rcu_expedited_wait_once()` waits for root completion for a bounded timeout.
- `synchronize_rcu_expedited_wait()` loops until completion, handles nohz-full forced ticks, and emits expedited stall reports through `synchronize_rcu_expedited_stall()`.
- `synchronize_rcu_expedited_stall()` prints CPUs/tasks still blocking the expedited GP, dumps blocking CPU tasks, and optionally prints blocked preemptible reader stacks.
- `rcu_exp_wait_wake()` finishes the expedited GP, ends the sequence, updates per-node `exp_seq_rq`, and wakes all waiters that piggybacked on this sequence.

IPI/deferred-QS handling:

- `rcu_exp_need_qs()` marks the current CPU as owing an expedited QS and requests rescheduling.
- Under `CONFIG_PREEMPT_RCU`, `rcu_exp_handler()` distinguishes CPUs currently inside preemptible RCU read-side critical sections from CPUs that can report immediately. It sets `t->rcu_read_unlock_special.b.exp_hint` for readers that must report at unlock time.
- Without `CONFIG_PREEMPT_RCU`, `rcu_exp_handler()` reports immediately when idle or preempt/BH-enabled and otherwise requests a deferred expedited QS.
- `rcu_print_task_exp_stall()` and `rcu_exp_print_detail_task_stall_rnp()` report task blockers only for preemptible RCU; non-preempt builds return no task blockers.

Exported public APIs:

- `synchronize_rcu_expedited()` is the main blocking expedited GP primitive.
- `start_poll_synchronize_rcu_expedited()` and `start_poll_synchronize_rcu_expedited_full()` snapshot state and arrange for an expedited GP if needed.
- `cond_synchronize_rcu_expedited()` and `cond_synchronize_rcu_expedited_full()` wait only if the supplied cookie has not already seen a full normal or expedited GP.

`sync_rcu_do_polled_gp()` is the workqueue bridge for polled expedited requests. It repeatedly invokes `synchronize_rcu_expedited()` until the normal polled cookie completes, then clears the per-node request if no longer needed.

## Control flow

`synchronize_rcu_expedited()` first rejects use from RCU read-side critical sections via lockdep warnings. In earliest boot, `rcu_blocking_is_gp()` allows a vacuous GP and simply advances the expedited sequence. If expedited GPs are globally disabled or normal-only policy is active, it falls back to `synchronize_rcu_normal()`.

In the runtime expedited path, the caller takes a snapshot with `rcu_exp_gp_seq_snap()`. `exp_funnel_lock()` then either returns true because another task completed the needed GP, blocks behind another in-progress expedited GP at a node wait queue, or returns false with `rcu_state.exp_mutex` held so the caller owns the new expedited GP. The owner starts the sequence, then either runs `rcu_exp_sel_wait_wake()` directly during scheduler initialization or before the expedited worker exists, or queues `wait_rcu_exp_gp()` to the global expedited kworker. The original caller waits on the root's sequence-indexed `exp_wq[]` until `sync_exp_work_done()` sees completion, then unlocks `exp_mutex`.

`sync_rcu_exp_select_cpus()` prepares the tree with `sync_exp_reset_tree()`. For each leaf node with a nonzero `expmask`, it uses a per-node expedited worker when available and useful, but falls back to direct execution for early boot, non-running scheduler state, or the last leaf. Each leaf worker calls `__sync_rcu_exp_select_node_cpus()`. That function first checks each target CPU under the leaf lock: current CPU, CPUs no longer in the online mask, and CPUs already in extended quiescent states are added to a local report mask. CPUs still potentially active get a context-tracking snapshot and are later sent an IPI. Before sending or after IPI failure, it rechecks whether the CPU passed through idle/offline state to avoid unnecessary or invalid IPIs.

The remote `rcu_exp_handler()` is the critical fast path. If the CPU is not in an RCU read-side critical section and is in a context where it can report, it calls `rcu_report_exp_rdp()`. If it cannot report immediately, it sets the per-CPU expedited no-QS bit and urgent-QS state so a later context switch, scheduler tick, or read-unlock path will report. For preemptible readers, it sets the current task's expedited unlock-special hint while holding the leaf node lock if the leaf still waits on this CPU.

Waiting is centralized in `synchronize_rcu_expedited_wait()`. It first gives nohz-full CPUs a short chance to complete, then forces `TICK_DEP_BIT_RCU_EXP` on CPUs still blocking the GP if necessary. It waits repeatedly on the expedited swait queue and, on timeout, emits stall diagnostics, invokes the stall notifier chain, and honors `panic_on_rcu_stall()`.

Completion uses `rcu_exp_wait_wake()`. It serializes wakeup with `exp_wake_mutex`, ends the expedited sequence, updates all `exp_seq_rq` values that lag behind the completed sequence, issues a memory barrier before wakeups, and wakes all per-node wait queues for the sequence index. This lets later callers piggyback safely and prevents sequence-wrap confusion.

The polled expedited API starts with the normal combined state from `get_state_synchronize_rcu()`. If that state is not already complete, it records the request under the current leaf node's `exp_poll_lock` and queues `exp_poll_wq` on `rcu_gp_wq`. The work item drives expedited GPs until the normal polling cookie completes, which allows callers to poll with the same `poll_state_synchronize_rcu()` function used by normal polling.

## State and persistence behavior

Expedited state is in memory and layered on the normal Tree RCU topology:

- `rcu_state.expedited_sequence` is the primary expedited GP sequence counter.
- `rcu_state.exp_mutex` serializes expedited GP execution. `exp_wake_mutex` serializes completion wakeups with the start of the next expedited GP.
- `rcu_state.expedited_wq` wakes the owner waiting for root completion.
- Each `rcu_node` has `expmask`, `expmaskinit`, and `expmaskinitnext` for expedited CPU/task wait state, plus `exp_seq_rq` and `exp_wq[4]` for funnel-lock waiters.
- Each leaf `rcu_node` has `rew` and optional `exp_kworker` for parallel CPU selection.
- Each `rcu_data` uses `cpu_no_qs.b.exp`, `exp_watching_snap`, and `rcu_forced_tick_exp` to track per-CPU expedited obligations.
- `exp_seq_poll_rq` and `exp_poll_wq` hold outstanding polled expedited work per node.

`sync_exp_reset_tree_hotplug()` commits newly onlined CPUs but intentionally does not remove offline CPUs from `expmaskinit`. That design avoids missing CPUs that have ever participated while allowing offline or idle checks to clear them quickly during selection.

Memory ordering is explicit. `rcu_exp_gp_seq_snap()` orders caller updates before the expedited GP is requested; `rcu_exp_gp_seq_end()` and `sync_exp_work_done()` provide completion ordering; and leaf selection relies on context-tracking acquire loads plus the lock/unlock chain through the `rcu_node` tree.

## Dependencies and integration points

This file depends heavily on `tree.c` internals:

- Normal GP/poll helpers: `rcu_poll_gp_seq_start_unlocked()`, `rcu_poll_gp_seq_end_unlocked()`, `get_state_synchronize_rcu()`, `poll_state_synchronize_rcu()`, and `synchronize_rcu_normal()`.
- Context and dynticks helpers: `ct_rcu_watching_cpu_acquire()`, `rcu_watching_snap_in_eqs()`, `rcu_watching_snap_stopped_since()`, `rcu_is_cpu_rrupt_from_idle()`, and nohz-full tick dependency APIs.
- Preemptible-RCU hooks: `rcu_preempt_depth()`, `rcu_preempt_has_tasks()`, task blocked-reader lists, and `rcu_read_unlock_special`.
- Stall/reporting infrastructure: `rcu_exp_jiffies_till_stall_check()`, `rcu_stall_is_suppressed()`, `rcu_stall_notifier_call_chain()`, `trace_rcu_stall_warning()`, `panic_on_rcu_stall()`, `dump_cpu_task()`, and `sched_show_task()`.
- Kthread workers and workqueues: global `rcu_exp_gp_kworker`, per-node `exp_kworker`, and `rcu_gp_wq`.
- CPU hotplug and SMP IPI mechanisms: `cpu_online()`, `smp_call_function_single()`, and per-node `qsmaskinitnext` checks.

The exported expedited APIs integrate with the public RCU API surface and may be selected indirectly by `synchronize_rcu()` when `rcu_gp_is_expedited()` is true.

## Risks and correctness concerns

Expedited RCU is intentionally aggressive, so most risks involve races with CPU state changes:

- `__sync_rcu_exp_select_node_cpus()` must recheck context-tracking snapshots and online masks around IPI attempts. Treating an IPI failure as a quiescent state without confirming hotplug state can shorten a GP incorrectly.
- The `exp_funnel_lock()` protocol relies on `exp_seq_rq`, per-node wait queues, and `exp_mutex` to avoid duplicate expedited GPs while still letting followers wait. Incorrect sequence comparisons can strand waiters or allow overlapping expedited GPs.
- The four-entry `exp_wq[]` array is indexed by sequence counter bits. Wakeups must update `exp_seq_rq` and issue barriers before waking to avoid missed completion on wrap-prone low bits.
- Preemptible-RCU `rcu_exp_handler()` must check `rnp->expmask` under the lock before setting task unlock-special hints, because the expedited GP can complete concurrently.
- Forced ticks for nohz-full expedited waiters must be cleared in `rcu_report_exp_cpu_mult()` when the corresponding CPU reports. Leaking `TICK_DEP_BIT_RCU_EXP` harms isolation and power behavior.
- Stall diagnostics run while expedited GP progress is impaired and sometimes while holding locks. The code touches watchdogs in task-detail printing to reduce hard-lockup risk.

## Test signals

Useful validation includes:

- `rcutorture` expedited scenarios, especially with `CONFIG_PREEMPT_RCU`, `CONFIG_NO_HZ_FULL`, hotplug, and high CPU counts.
- Concurrent loops of `synchronize_rcu_expedited()`, `synchronize_rcu()`, `start_poll_synchronize_rcu_expedited()`, and `cond_synchronize_rcu_expedited()` to stress piggybacking and sequence wakeups.
- CPU hotplug while expedited GPs are in flight, watching for WARNs in `__sync_rcu_exp_select_node_cpus()`, stuck `expmask` bits, or expedited stalls.
- nohz-full isolation tests confirming forced expedited ticks are set only for blocking CPUs and cleared after reporting.
- Preemptible reader tests that block in RCU read-side critical sections during expedited GPs, validating `exp_tasks`, task stall printing, and unlock-special reporting.
- Tracepoint checks for `rcu_exp_grace_period` and `rcu_exp_funnel_lock` transitions: `snap`, `start`, `reset`, `select`, `startwait`, `end`, and `endwake`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/rcu/tree_exp.h -->
