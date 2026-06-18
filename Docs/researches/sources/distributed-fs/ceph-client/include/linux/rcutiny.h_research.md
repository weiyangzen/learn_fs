# sources/distributed-fs/ceph-client/include/linux/rcutiny.h

## Purpose

This header declares and inlines the Tiny RCU implementation interface used on uniprocessor or size-constrained builds. It presents the same public shape as tree RCU where possible, but many operations collapse to simple no-ops because there is only one CPU and quiescent-state detection is trivial.

## Important APIs, Types, and Functions

`struct rcu_gp_oldstate` contains only `rgos_norm`, and `NUM_ACTIVE_RCU_POLL_FULL_OLDSTATE` is two. The full-state helpers map only normal grace-period state: `same_state_synchronize_rcu_full()`, `get_state_synchronize_rcu_full()`, `start_poll_synchronize_rcu_full()`, `poll_state_synchronize_rcu_full()`, and `cond_synchronize_rcu_full()`.

Expedited helpers alias normal polling/synchronization. `synchronize_rcu_expedited()` calls `synchronize_rcu()`. `rcu_qs()` is the core quiescent-state function, and `rcu_softirq_qs()` delegates to it. `rcu_note_context_switch()` reports a quiescent state and a Tasks RCU quiescent state. CPU hotplug hooks are defined as `NULL` and `rcutree_report_cpu_starting()` is empty.

## Control Flow

Tiny RCU's control flow removes distributed tree coordination. Context switches and softirq quiescent states call `rcu_qs()`. Conditional synchronization helpers call `might_sleep()` but do not need to wait because, in this model, eligible call sites already imply a grace period or no extra CPU coordination is required.

## State and Persistence Behavior

The exposed grace-period old state is a single unsigned long. Most watcher, stall, deferred quiescent-state, virtualization, and hotplug functions carry no persistent state in this header. Scheduler boot state is represented by `rcu_scheduler_starting()` plus inlines that treat in-kernel boot as ended and RCU as watching.

## Dependencies and Integration Points

The header includes `asm/param.h` for `HZ` and relies on RCU core declarations from surrounding includes. It is selected instead of `rcutree.h` by kernel configuration and must match the interfaces expected by generic scheduler, hotplug, stall-check, and RCU wait code.

## Risks

The simplifications are only valid for Tiny RCU configurations. Code that assumes tree-RCU expedited state exists would misread `rgos_norm`-only old states. Because hotplug callbacks are `NULL`, code must not assume runtime CPU set changes are handled through tree callbacks in Tiny builds.

## Test Signals

Build tests should cover Tiny RCU configurations, especially generic code that calls full old-state helpers, hotplug hook variables, `synchronize_rcu_expedited()`, and `rcu_note_context_switch()`. Runtime smoke tests should verify callbacks drain and quiescent states are reported during context switches.
