# sources/distributed-fs/ceph-client/arch/powerpc/kernel/stacktrace.c

## Purpose
Provides PowerPC stack walking for generic stacktrace users, reliable stacktrace validation, and NMI-IPI based remote CPU backtraces on Book3S 64-bit systems.

## Important APIs, Types, and Functions
- `arch_stack_walk()` walks frame backchains from `pt_regs`, current stack, or `task->thread.ksp`.
- `arch_stack_walk_reliable()` validates alignment, monotonic stack growth, stack bounds, exception frames, kernel text return addresses, ftrace graph rewriting, and rethook trampoline presence.
- `arch_trigger_cpumask_backtrace()` uses `nmi_trigger_cpumask_backtrace()` with `raise_backtrace_ipi()` when supported.
- `raise_backtrace_ipi()` sends safe NMI IPIs and falls back to PACA inspection if a CPU does not respond.

## Control Flow and State
Simple walking repeatedly validates SP, reads backlink and saved LR, and calls the consumer. Reliable walking stops at the computed stack end and rejects any ambiguity. Remote backtrace sends an NMI IPI per target, waits up to five seconds for the CPU to clear itself from the mask, and prints PACA state and possibly stale `saved_r1` stack if it times out.

## State and Persistence Behavior
Mostly read-only against task stacks and PACA. The remote path mutates the cpumask passed by the NMI framework and emits diagnostic logs.

## Dependencies and Integration Points
Depends on PowerPC stack frame layout constants, `validate_sp()`, ftrace graph return address repair, rethook, `paca_ptrs`, and SMP NMI IPI functions.

## Risks
Reliable unwinding intentionally rejects exception frames and rethooks, which may reduce coverage but avoids false reliability. Remote fallback PACA stack traces can be stale or corrupt; diagnostics are guarded by `virt_addr_valid()` but still diagnostic-only.

## Test Signals
Run `stack_trace_save*`, livepatch/ftrace graph enabled traces, kretprobe/rethook stacks, blocked CPU backtraces, invalid task stack simulations, and lockup/NMI backtrace paths.
