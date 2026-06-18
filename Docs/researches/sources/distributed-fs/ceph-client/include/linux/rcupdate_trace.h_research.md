# sources/distributed-fs/ceph-client/include/linux/rcupdate_trace.h

## Purpose

This header exposes the Tasks Trace RCU read-side API used by tracing, BPF, ftrace, and other code that may need to protect instruction-patching or profiling-hook state while normal task scheduling and tracing constraints apply. It adapts the generic SRCU fast paths to the `rcu_tasks_trace_srcu_struct` domain and provides build-time stubs when `CONFIG_TASKS_TRACE_RCU` is disabled.

## Important APIs, Types, and Functions

The exported state is `rcu_tasks_trace_srcu_struct` under `CONFIG_TASKS_TRACE_RCU`. `rcu_read_lock_trace_held()` reports lockdep state through `srcu_read_lock_held()` when both lockdep and Tasks Trace RCU are enabled; otherwise it returns true so generic checks compile away.

The low-level pair `rcu_read_lock_tasks_trace()` and `rcu_read_unlock_tasks_trace()` return and accept a `struct srcu_ctr __percpu *` cookie from `__srcu_read_lock_fast()`. The higher-level pair `rcu_read_lock_trace()` and `rcu_read_unlock_trace()` stores that cookie in `current->trc_reader_scp` and tracks nesting in `current->trc_reader_nesting`, allowing nested trace read sections without repeated SRCU acquisition.

Grace-period and callback APIs are wrappers over SRCU: `call_rcu_tasks_trace()` calls `call_srcu()`, `synchronize_rcu_tasks_trace()` calls `synchronize_srcu()`, `rcu_barrier_tasks_trace()` calls `srcu_barrier()`, and `rcu_tasks_trace_expedite_current()` calls `srcu_expedite_current()`. `DEFINE_LOCK_GUARD_0(rcu_tasks_trace, ...)` provides cleanup-attribute guard support.

## Control Flow

The direct `rcu_read_lock_tasks_trace()` path acquires the SRCU read counter, records a lockdep acquisition, and conditionally issues `smp_mb()` unless `CONFIG_TASKS_TRACE_RCU_NO_MB` promises the architecture does not need the fallback barrier. Unlock mirrors this with a barrier before `__srcu_read_unlock_fast()` and a lockdep release.

The task-nesting path first increments the current task nesting count. If already nested, it returns immediately after lockdep acquisition. On the first entry it orders the nesting update before publishing `trc_reader_scp`, enters the SRCU domain, and optionally issues the memory barrier. Unlock reads the stored cookie, orders that read before decrementing nesting, and only exits the SRCU read side when the outermost reader ends.

When Tasks Trace RCU is disabled, the BPF JIT still needs symbol addresses to exist, so the small inline stubs call `BUG()` rather than silently accepting use.

## State and Persistence Behavior

State is per-task and in the global SRCU domain. `trc_reader_nesting` and `trc_reader_scp` persist only for the duration of the current task's nested read-side critical section. Callback state is held by SRCU until the trace grace period elapses. There is no storage across reboot or module lifetime beyond normal kernel objects.

## Dependencies and Integration Points

The header depends on `sched.h`, `rcupdate.h`, and `cleanup.h`, plus SRCU internals exposed through the RCU headers. It integrates with lockdep through `dep_map`, with BPF/ftrace code through the trace read lock names, and with architecture instrumentation policy through `CONFIG_TASKS_TRACE_RCU_NO_MB` and `ARCH_WANTS_NO_INSTR` assumptions described in comments.

## Risks

Incorrect nesting handling can strand a task in a trace read-side section or unlock the SRCU domain too early. Missing barriers on architectures that can trace code while RCU is not watching can break grace-period ordering. Calling the API when `CONFIG_TASKS_TRACE_RCU` is disabled intentionally crashes through `BUG()`, so configuration assumptions must be explicit. Misusing the cookie-returning low-level API without matching the exact cookie to unlock can corrupt SRCU accounting.

## Test Signals

Useful tests include lockdep coverage for nested `rcu_read_lock_trace()` use, BPF/ftrace attach-detach stress while callbacks are queued through `call_rcu_tasks_trace()`, grace-period tests that verify `synchronize_rcu_tasks_trace()` waits for active readers, and config-build tests with and without `CONFIG_TASKS_TRACE_RCU`, `CONFIG_DEBUG_LOCK_ALLOC`, and `CONFIG_TASKS_TRACE_RCU_NO_MB`.
