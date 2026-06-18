# sources/distributed-fs/ceph-client/include/linux/rcupdate_wait.h

## Purpose

This header provides helper infrastructure for waiting on one or more RCU grace-period domains concurrently. It wraps callback-based RCU APIs into completion-backed waits and exposes small helpers for rescheduling or detecting blocked readers inside RCU read-side sections.

## Important APIs, Types, and Functions

`struct rcu_synchronize` combines an `rcu_head`, a `completion`, and debug old-state tracking in `struct rcu_gp_oldstate`. `wakeme_after_rcu()` is the callback used to complete a wait after a grace period. `__wait_rcu_gp()` is the implementation entry point taking an array of `call_rcu_func_t` functions and matching `rcu_synchronize` objects.

The macros `_wait_rcu_gp()`, `wait_rcu_gp()`, `wait_rcu_gp_state()`, and `synchronize_rcu_mult()` build stack arrays from variadic callback functions. `synchronize_rcu_mult()` can wait for multiple RCU flavors, such as normal RCU and tasks RCU, in parallel.

`cond_resched_rcu()` drops and reacquires a normal RCU read lock around `cond_resched()` on debug atomic sleep builds or non-preemptible RCU builds. `has_rcu_reader_blocked()` checks `current->rcu_node_entry` under `CONFIG_PREEMPT_RCU`.

## Control Flow

A caller passes callback-queueing functions such as `call_rcu_hurry` or a wrapper around `call_srcu()`. The macro creates one `rcu_synchronize` object per domain, calls into `__wait_rcu_gp()`, and sleeps in the requested task state until all callbacks run. Tiny RCU can skip normal RCU waits in `synchronize_rcu_mult()` because the calling context is already considered a grace period there.

`cond_resched_rcu()` uses the safe sequence `rcu_read_unlock(); cond_resched(); rcu_read_lock();` only where needed. `has_rcu_reader_blocked()` is a read-only state probe.

## State and Persistence Behavior

All wait objects are stack-local to the macro expansion. The only persistent state touched is the global state of whichever RCU domains receive callbacks. Debug oldstate values help diagnose grace-period ordering but are not persisted.

## Dependencies and Integration Points

The header depends on `rcupdate.h`, `completion.h`, and `sched.h`. It is used by code that needs to wait on multiple RCU domains without serializing the grace periods. SRCU users integrate by providing a wrapper function with the same shape as `call_rcu_func_t`.

## Risks

The variadic macro stores arrays on the caller's stack, so extremely large lists would be inappropriate. Passing plain `call_rcu()` instead of `call_rcu_hurry()` under lazy RCU can add multi-second delay. The `cond_resched_rcu()` helper must only be used when dropping the read lock temporarily is semantically valid.

## Test Signals

Tests should cover waits over one and multiple RCU domains, interrupted task states through `wait_rcu_gp_state()`, Tiny RCU builds, lazy callback behavior, and lockdep/debug atomic sleep checks around `cond_resched_rcu()`.
