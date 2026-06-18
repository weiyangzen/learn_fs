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
