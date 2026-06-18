# sources/distributed-fs/ceph-client/kernel/entry/syscall-common.c

## Purpose

`syscall-common.c` centralizes syscall tracepoint emission for generic syscall entry and exit paths. Keeping these helpers out of line prevents tracepoint code duplication in architecture entry code.

## Important APIs, Types, And Functions

- `CREATE_TRACE_POINTS` instantiates syscall trace events from `trace/events/syscalls.h`.
- `trace_syscall_enter()` emits `trace_sys_enter(regs, syscall)` and then rereads the syscall number with `syscall_get_nr(current, regs)`.
- `trace_syscall_exit()` emits `trace_sys_exit(regs, ret)`.

## Control Flow

On syscall entry, tracing runs first. Because probes or BPF hooks attached to the tracepoint can rewrite the syscall number, the helper rereads and returns the current syscall number from the registers. On syscall exit, the return value is passed to the exit tracepoint.

## State And Persistence Behavior

The file does not own state. Tracepoint handlers, probes, or BPF programs may observe or mutate syscall state during entry tracing.

## Dependencies And Integration Points

It depends on `entry-common.h`, syscall register helpers, the tracepoint subsystem, BPF/perf/ftrace consumers, and generic syscall entry code compiled through the entry Makefile.

## Risks And Edge Cases

- Consumers must use the returned syscall number from `trace_syscall_enter()`, not the original argument, because trace hooks may change it.
- Tracepoint overhead and instrumentation constraints matter because syscall entry is hot and sensitive.

## Test Signals

Validate with syscall tracepoints enabled, BPF programs that rewrite syscall numbers, perf/ftrace syscall tracing, and architecture generic syscall entry tests.
