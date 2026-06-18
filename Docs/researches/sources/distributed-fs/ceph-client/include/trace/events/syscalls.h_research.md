
# sources/distributed-fs/ceph-client/include/trace/events/syscalls.h

## Purpose
Defines raw syscall entry and exit tracepoints, exposing syscall number, up to six arguments, and return value for architectures that support syscall tracepoints.

## Important APIs, Types, and Functions
`TRACE_SYSTEM` is `raw_syscalls` while `TRACE_INCLUDE_FILE` is `syscalls`. Under `CONFIG_HAVE_SYSCALL_TRACEPOINTS`, `TRACE_EVENT_SYSCALL(sys_enter)` records syscall id and arguments via `syscall_get_arguments()`, and `TRACE_EVENT_SYSCALL(sys_exit)` records syscall id from `syscall_get_nr()` plus return value. Both use `syscall_regfunc` and `syscall_unregfunc` and are marked `TRACE_EVENT_FL_CAP_ANY`.

## Control Flow
Architecture syscall entry code invokes `sys_enter` before dispatching the syscall, and exit code invokes `sys_exit` with the return value. Registration functions allow arch-specific syscall tracepoint enable/disable handling.

## State and Persistence
No syscall state is owned here. Trace records persist numeric syscall ids, argument snapshots, and return values in tracing buffers. Argument interpretation is architecture and syscall-table dependent.

## Dependencies and Integration Points
Depends on `linux/tracepoint.h`, `asm/ptrace.h`, `asm/syscall.h`, current task state, and architecture syscall tracing support. Integrates with strace-like tracing, perf, ftrace, BPF raw tracepoints, seccomp diagnostics, and audit-adjacent investigations.

## Risks
Raw syscall tracing can expose sensitive arguments such as pointers, file descriptors, addresses, and return codes. Field semantics differ across architectures and compat modes. Tools must map syscall ids against the correct table. Events do not decode pointed-to memory.

## Test Signals
Signals include syscall trace selftests, BPF raw tracepoint programs, arch builds with and without `CONFIG_HAVE_SYSCALL_TRACEPOINTS`, compat syscall coverage, and comparing trace output with known syscall workloads.
