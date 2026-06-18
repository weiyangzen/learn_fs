# sources/distributed-fs/ceph-client/arch/um/kernel/ptrace.c

## Purpose
Implements UML's architecture ptrace hooks and syscall tracing bridge. It translates generic ptrace requests into UML register accessors, controls user single-step state, and emits audit/tracepoint/ptrace syscall entry and exit events around UML syscall dispatch.

## Important APIs, Types, and Functions
`user_enable_single_step()`, `user_disable_single_step()`, and `ptrace_disable()` manipulate `TIF_SINGLESTEP` plus optional subarchitecture hooks. `arch_ptrace()` handles `PTRACE_PEEKUSR`, `PTRACE_POKEUSR`, register get/set, TLS thread-area requests, and delegates unknown operations to generic and subarch ptrace handlers. `syscall_trace_enter()` and `syscall_trace_leave()` integrate audit, tracepoints, ptrace syscall stops, and synthetic SIGTRAP delivery for single stepping.

## Control Flow, State, and Persistence
State is per-task thread flags and ptrace state; no persistent storage is used. Syscall entry records audit data, emits tracepoints when enabled, and can stop for ptrace. Syscall exit audits, injects single-step traps, emits exit tracepoints, and sets `TIF_SIGPENDING` when a ptraced task needs signal processing.

## Dependencies and Integration Points
Depends on UML register helpers (`getreg`, `putreg`, `peek_user`, `poke_user`), generic ptrace/audit/tracepoint infrastructure, and subarch TLS/ptrace hooks. It is called from `arch/um/kernel/skas/syscall.c` during syscall handling and from generic kernel ptrace paths.

## Risks and Test Signals
Risk centers on register offset validation and ptrace semantics matching x86 expectations. Test with `strace`, `gdb`, syscall tracepoints, single-step debugging, TLS ptrace requests, and audit records; failures typically show as wrong syscall stops, missed SIGTRAPs, or corrupted register state.
