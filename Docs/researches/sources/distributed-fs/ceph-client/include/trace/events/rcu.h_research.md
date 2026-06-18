# sources/distributed-fs/ceph-client/include/trace/events/rcu.h

Purpose: Defines extensive RCU tracepoints for utilization, grace periods, expedited grace periods, funnel locks, no-CB wakeups, preempted readers, quiescent-state reporting, stall warnings, callback lifecycle, segmented callback stats, batch start/end, callback invocation, torture reads, and barriers.

Important APIs/types/functions: Events include `rcu_utilization`, `rcu_grace_period`, `rcu_future_grace_period`, `rcu_grace_period_init`, `rcu_exp_grace_period`, `rcu_exp_funnel_lock`, `rcu_nocb_wake`, `rcu_preempt_task`, `rcu_unlock_preempted_task`, `rcu_quiescent_state_report`, `rcu_fqs`, `rcu_stall_warning`, `rcu_watching`, `rcu_callback`, `rcu_segcb_stats`, `rcu_batch_start`, `rcu_invoke_callback`, `rcu_invoke_kvfree_callback`, `rcu_invoke_kfree_bulk_callback`, `rcu_sr_normal`, `rcu_batch_end`, `rcu_torture_read`, and `rcu_barrier`.

Control flow: RCU core emits events as readers enter/exit extended quiescent states, grace periods are requested/initialized/advanced/completed, callbacks are queued and invoked, stalls are detected, no-CB kthreads wake, and barriers drain callbacks. Many events use `TRACE_EVENT_RCU` to compile out cleanly when RCU tracing is disabled.

State and persistence: No state is owned. It observes RCU global/per-CPU state, GP sequence numbers, callback queues, task pointers, CPU masks, and stall diagnostics.

Dependencies and integration points: Depends on tracepoints and RCU internals. It integrates with scheduler, idle, callback offload, memory reclamation, torture testing, and ftrace/perf.

Risks and test signals: Risks include recursion or overhead in core synchronization paths, sequence-number misinterpretation, config-gated tracepoint drift, and exposing callback pointers after module unload. Test TREE_RCU/PREEMPT_RCU configs, expedited GP, callback flooding, CPU hotplug, no-CB CPUs, stall injection, rcutorture, and barrier-heavy workloads.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rcu.h` completely for this pass (830 lines, 24365 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rcu.h_research.md`.
