# sources/distributed-fs/ceph-client/include/linux/rcutree.h

## Purpose

`rcutree.h` declares the tree-based RCU implementation interface for SMP/preemptible kernels. It exposes scheduler, hotplug, expedited, polling, boot, and callback-migration hooks consumed by generic kernel code.

## Important APIs, Types, and Functions

Core hooks include `rcu_softirq_qs()`, `rcu_note_context_switch()`, `rcu_needs_cpu()`, `rcu_cpu_stall_reset()`, `rcu_request_urgent_qs_task()`, `synchronize_rcu_expedited()`, `rcu_barrier()`, and `rcu_momentary_eqs()`. `rcu_virt_note_context_switch()` wraps `rcu_note_context_switch(false)` and requires interrupts disabled.

`struct rcu_gp_oldstate` has normal and expedited fields, `rgos_norm` and `rgos_exp`, with `NUM_ACTIVE_RCU_POLL_FULL_OLDSTATE` set to four. Full old-state helpers compare both fields and have external implementations for get/start/poll/conditional normal and expedited synchronization.

The header declares preempt RCU hooks, boot state (`rcu_scheduler_starting()`, `rcu_scheduler_active`, `rcu_end_inkernel_boot()`, `rcu_inkernel_boot_has_ended()`, `rcu_is_watching()`), CPU hotplug callbacks, callback migration, and CPU-dead reporting.

## Control Flow

Tree RCU coordinates grace periods across CPUs and RCU nodes in implementation files. This header exposes call points: scheduler context switches report quiescent states, IRQ exit may check preempt state under `CONFIG_PROVE_RCU`, CPU hotplug calls prepare/online/offline/dead/dying hooks, and callback migration moves callbacks away from a CPU being removed.

Polling flows use old-state tokens: callers get or start a grace period, poll until complete, or conditionally wait only if the old state is still incomplete. Normal and expedited streams are tracked separately.

## State and Persistence Behavior

The header itself stores no state except declarations, but its APIs manipulate global tree RCU state, per-CPU callback queues, boot/scheduler state, and CPU hotplug membership. Old-state tokens are opaque snapshots valid only for grace-period comparison and polling.

## Dependencies and Integration Points

It integrates with the scheduler, softirq/IRQ exit paths, CPU hotplug core, virtualization context switches, arm64 early secondary boot failure handling, lockdep/prove-RCU, and generic RCU polling/wait APIs. `struct task_struct` is forward-declared for deferred quiescent-state and urgent-QS APIs.

## Risks

Misplacing context-switch or hotplug calls can stall grace periods or lose callbacks. Treating `struct rcu_gp_oldstate` fields as meaningful outside RCU helpers breaks opacity assumptions. `rcu_virt_note_context_switch()` requires interrupts disabled; violating that can race quiescent-state accounting.

## Test Signals

Signals include RCU torture tests on SMP and preemptible configurations, CPU hotplug stress, expedited grace-period tests, callback migration tests, boot-state checks, stall warning tests, and lockdep/prove-RCU coverage for IRQ exit and read-side misuse.
