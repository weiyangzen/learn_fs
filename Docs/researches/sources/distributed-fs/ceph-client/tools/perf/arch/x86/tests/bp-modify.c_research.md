# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/bp-modify.c

## Purpose
This x86_64-only perf test validates kernel ptrace behavior for modifying hardware breakpoints through debug registers. It checks both a successful breakpoint address change and rejection of a bogus address while preserving the original breakpoint.

## Important APIs, Types, and Functions
The file defines two noinline breakpoint targets, `bp_1()` and `bp_2()`, to provide stable function addresses. `spawn_child()` forks a tracee, calls `ptrace(PTRACE_TRACEME)`, raises `SIGCONT` to let the parent attach, then calls `bp_1()` and exits.

`bp_modify1()` writes debug register 0 first with `bp_2`, then overwrites it with `bp_1`, enables the breakpoint through debug register 7, continues the child, reads `rip`, detaches, and expects the stop RIP to equal `bp_1`. `bp_modify2()` sets a breakpoint on `bp_1`, enables it, attempts to change debug register 0 to `(unsigned long)-1`, expects that write to fail, then verifies the original breakpoint still fires. `test__bp_modify()` requires both subtests to pass.

## Control Flow
Each subtest follows the same parent/child control pattern: fork, wait for the trace stop, program debug registers with `PTRACE_POKEUSER`, continue, wait for a breakpoint stop, read `rip` using `PTRACE_PEEKUSER`, detach, then compare the observed instruction pointer against `bp_1`. Failures use `goto out` to ensure detach is attempted.

## State and Persistence
No persistent state is written. Runtime state includes a child process, ptrace relationship, x86 hardware debug registers DR0 and DR7 in the tracee, and signal/wait status. The child is detached at the end of each subtest unless detach itself fails.

## Dependencies and Integration Points
The test depends on x86_64 ptrace ABI details (`struct user`, `u_debugreg[]`, `struct user_regs_struct.rip`), `<asm/ptrace.h>`, Linux wait/signal behavior, and perf's test/debug macros. It is registered only when `__x86_64__` is defined by `arch-tests.c`.

## Risks and Edge Cases
The test is sensitive to ptrace restrictions such as Yama policy, sandboxing, seccomp, container capabilities, and nonstandard debug-register behavior. It assumes the breakpoint trap RIP reported by ptrace equals the function address exactly. Compiler/linker instrumentation, sanitizers, control-flow protection, or architecture behavior changes could alter stop addresses and fail the equality check.

## Test Signals
Passing signals are both modify tests reaching `rip == bp_1`. Failure logs identify whether PTRACE_TRACEME, debug-register writes, continue, peek, or detach failed. A failure in the bogus-address path indicates the kernel accepted an invalid debug-register value or lost the original breakpoint.
