# sources/distributed-fs/ceph-client/include/linux/trace_recursion.h

## Purpose
Implements per-task recursion guards for ftrace and internal trace event paths. It prevents tracing callbacks from recursively tracing themselves in normal, IRQ, softirq, NMI, and transition contexts.

## Important APIs, Types, And Functions
Defines recursion bit indexes, context constants, `trace_recursion_set()`, `trace_recursion_clear()`, `trace_recursion_test()`, `trace_get_context_bit()`, `trace_test_and_set_recursion()`, `trace_clear_recursion()`, `ftrace_test_recursion_trylock()`, and `ftrace_test_recursion_unlock()`. Optional helpers record recursion and validate RCU watching.

## Control Flow
`trace_test_and_set_recursion()` reads `current->trace_recursion`, optionally warns if RCU is not watching, computes the bit for the current interrupt context plus caller class, and returns `-1` if the same context is already tracing. It allows one transition case to avoid dropping events during interrupt-context accounting windows. On success it sets the bit, issues a barrier, disables preemption, and returns the bit to clear later.

## State, Persistence, And Dependencies
State is in `current->trace_recursion`, with only the current task modifying it. Dependencies include interrupt context level, scheduler current task, preemption controls, optional RCU validation, and optional recursion recording.

## Integration Points
Used by ftrace callbacks, internal tracing lists, branch tracing, function graph IRQ state, and event recursion protection.

## Risks And Test Signals
Risks include forgetting to unlock returned bits, tracing with RCU inactive, false recursion drops during context transitions, and invalid use when tracing config is disabled. Test signals include recursive ftrace callback tests, IRQ/NMI context tracing, preemption state assertions, and forced RCU-not-watching validation.
