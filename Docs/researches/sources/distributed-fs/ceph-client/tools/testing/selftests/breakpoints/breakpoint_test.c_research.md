# sources/distributed-fs/ceph-client/tools/testing/selftests/breakpoints/breakpoint_test.c

## Purpose

This x86 kselftest validates hardware instruction breakpoints, write watchpoints, read/write watchpoints, ICEBP traps, and `int3` traps through `ptrace` debug-register programming. It exercises the `do_debug()` path and verifies that a traced child traps exactly when expected.

## Important APIs, Types, and Functions

Important constants are `COUNT_ISN_BPS`, `COUNT_WPS`, and breakpoint modes `BP_X`, `BP_RW`, and `BP_W`. Key functions are `set_breakpoint_addr`, `toggle_breakpoint`, dummy functions/variables, `check_trapped`, `write_var`, `read_var`, `trigger_tests`, `check_success`, `launch_instruction_breakpoints`, `launch_watchpoints`, `launch_tests`, and `main`. It uses `PTRACE_POKEUSER`, `PTRACE_PEEKUSER`, `PTRACE_POKEDATA`, `PTRACE_CONT`, x86 `struct user.u_debugreg`, signals, wait status, and kselftest reporting.

## Control Flow

The parent forks a child. The child calls `PTRACE_TRACEME`, signals readiness, then executes the exact sequence of dummy function calls, watched writes/reads, ICEBP, and int3. The parent sets DR addresses and DR7 control bits for each local/global/type/length combination, resumes the child, waits for SIGTRAP, confirms the child-side sequence counter matches the parent, pokes `trapped = 1`, reports pass/fail, disables the breakpoint, and continues to the next case.

## State and Persistence Behavior

State is in child debug registers, shared-by-ptrace child globals `nr_tests` and `trapped`, and parent `child_pid`. It leaves no persistent state after the child exits.

## Dependencies and Integration Points

It depends on x86 debug register layout, ptrace permissions, signal delivery, and kselftest. The Makefile limits it to x86.

## Risks and Test Signals

Risks include ptrace policy restrictions, DR7 encoding mistakes, sequence desynchronization, and false failures if the child exits early. Signals are planned pass results for all breakpoint/watchpoint/trap combinations and final `ksft_exit_pass`.
