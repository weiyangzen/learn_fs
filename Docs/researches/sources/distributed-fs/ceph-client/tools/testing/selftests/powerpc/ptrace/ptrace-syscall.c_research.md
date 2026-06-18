# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-syscall.c

## Purpose
`ptrace-syscall.c` tests powerpc syscall tracing and restart behavior, including register state observed at syscall-entry/exit stops and behavior around syscall emulation controls.

## Important APIs, Types, and Functions
Important pieces are register aliases for syscall number/arguments/IP, `PTRACE_SYSEMU`, global `nerrs`, `wait_trap()`, `test_ptrace_syscall_restart()`, `ptrace_syscall()`, and `main()`.

## Control Flow and State
The test forks a tracee, uses ptrace syscall-stop control, inspects and modifies `struct pt_regs`, verifies syscall arguments and restart/IP behavior, and accumulates errors before returning the kselftest result. State is child register state, wait status, errno/results, and the error counter.

## Dependencies and Integration Points
It integrates with powerpc syscall ABI register layout, ptrace syscall tracing, auxiliary vector platform checks, and kselftest utilities.

## Risks and Test Signals
Risks are ABI differences across 32/64-bit or compat modes, syscall restart semantic changes, and incorrect stop classification. A pass means traced syscall stops expose consistent registers and restart behavior.
