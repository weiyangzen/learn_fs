
# sources/distributed-fs/ceph-client/include/trace/events/task.h

## Purpose
Defines task-management tracepoints for new task creation, task rename, and unknown `prctl()` options.

## Important APIs, Types, and Functions
Events are `task_newtask`, `task_rename`, and `task_prctl_unknown`. `task_newtask` records pid, command name, clone flags, and `oom_score_adj`. `task_rename` records pid, old/new command names, and `oom_score_adj`. `task_prctl_unknown` records the option and four argument words.

## Control Flow
Process management code emits `task_newtask` after task creation with clone flags, `task_rename` when a task command name changes, and `task_prctl_unknown` when `prctl()` receives an unsupported option. Tracepoints copy task strings and scalar values immediately.

## State and Persistence
No task state is persisted by the header. Trace records persist command names, pid, clone flags, OOM adjustment, and prctl arguments in trace buffers. The task may exit or rename again after the event.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, task structures, signal OOM adjustment state, and prctl handling. Integrates with process lifecycle diagnostics, container/runtime tracing, fork/exec analysis, and userspace observability tooling.

## Risks
Clone flags and prctl arguments can expose process behavior and raw argument values. `oom_score_adj` is read through `task->signal`, so call sites must use valid task signal state. Tooling should distinguish this file's task events from scheduler process events.

## Test Signals
Signals include fork/clone workloads, `prctl(PR_SET_NAME)` rename tests, unknown prctl option calls, OOM score adjustment changes before fork/rename, and BPF/ftrace consumers of `events/task/*`.
