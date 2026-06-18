<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigtrap_loop.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigtrap_loop.c

## Purpose

`sigtrap_loop.c` is a small x86 selftest for trap-flag single-step forward progress. It detects regressions where returning from `SIGTRAP` re-enters the same instruction repeatedly and creates an apparent infinite trap loop.

## Important APIs, Types, and Functions

The program defines a local `sethandler()` wrapper, installs a SA_SIGINFO `SIGTRAP` handler, inspects `REG_RIP` or `REG_EIP`, and uses inline assembly to push `0x302` into EFLAGS, execute four single-stepped instructions, then restore `0x202`.

## Control Flow and State

The handler stores the last trap IP and a same-IP repeat counter. If the same IP appears more than ten times in a row, the test exits failure. Otherwise `main()` completes the short single-step sequence and prints success. State is limited to static handler counters and signal context.

## Dependencies and Integration Points

It is part of the x86 selftest suite and depends on kernel signal delivery, correct saved IP/EFLAGS semantics, and architecture ucontext register names. It complements `single_step_syscall.c` and `mov_ss_trap.c` by focusing on trap-loop avoidance in ordinary single-step signal return.

## Risks and Test Signals

The key risk is an infinite SIGTRAP loop caused by wrong resume IP or trap flag handling. Passing behavior reaches normal process termination; failure appears as a hang, excessive trap count, or explicit failure output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/sigtrap_loop.c -->
