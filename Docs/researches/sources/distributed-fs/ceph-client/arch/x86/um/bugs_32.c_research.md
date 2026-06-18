<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/bugs_32.c

## Purpose
`bugs_32.c` probes host CMOV support for 32-bit UML and diagnoses SIGILL in init caused by CMOV instructions.

## Important APIs, types, and functions
`arch_check_bugs()`, `arch_examine_signal()`, `cmov_sigill_test_handler()`, `host_has_cmov`, and `cmov_test_return`.

## Control flow
Boot installs a SIGILL handler, executes a CMOV test under setjmp/longjmp, records support, and later examines SIGILL instruction bytes in PID 1 to print a targeted diagnostic.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/bugs_32.c -->
