# sources/distributed-fs/ceph-client/include/linux/tracepoint.h

## Purpose
Implements the public kernel tracepoint declaration/definition macro layer, probe registration APIs, module iteration, static-key/static-call dispatch, RCU/SRCU unregister synchronization, and trace event macro fallbacks.

## Important APIs, Types, And Functions
Exports registration APIs `tracepoint_probe_register*()`, `tracepoint_probe_unregister()`, iteration helpers, module notifier helpers, `tracepoint_synchronize_unregister()`, grace-period wrappers, syscall tracepoint hooks, `tracepoint_string()`, `DECLARE_TRACE*`, `DEFINE_TRACE*`, `EXPORT_TRACEPOINT_SYMBOL*`, and default `TRACE_EVENT`/`DEFINE_EVENT` macro expansions.

## Control Flow
With tracepoints enabled, each declared tracepoint gets inline `trace_name()` and `trace_name_enabled()` helpers guarded by a static branch. Enabled calls enter `__do_trace_name()`, acquire the appropriate SRCU or tasks-trace guard, then dispatch either through static call to the first probe or an iterator over an RCU-protected `tracepoint_func` array. Syscall tracepoints are marked faultable and use tasks-trace RCU plus `might_fault()`. Disabled builds generate stubs returning `-ENOSYS` or false.

## State, Persistence, And Dependencies
Tracepoint definitions create section entries in `__tracepoints`, `__tracepoints_ptrs`, and string sections. Runtime state includes static keys, static calls, function arrays, priorities, module ownership, and optional extension registration/unregistration callbacks. Dependencies include SMP, SRCU, RCU tasks trace, static calls, modules, errno, and tracepoint definitions.

## Integration Points
Used by all `TRACE_EVENT` providers, ftrace, perf, BPF, modules exporting tracepoints, Rust tracepoint call wrappers, and userspace tracepoint string decoding.

## Risks And Test Signals
Risks include unregistering probes without waiting for both SRCU and tasks-trace grace periods, wrong faultable classification, RCU-not-watching calls, module unload races, static-call/probe-array mismatches, and macro redefinition issues across multiple trace headers. Test signals include probe register/unregister races, module unload tests, syscall tracepoint faulting-context tests, static key disabled overhead tests, and `__tracepoint_check` build validation.
