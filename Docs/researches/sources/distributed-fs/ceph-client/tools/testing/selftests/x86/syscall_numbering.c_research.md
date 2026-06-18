<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_numbering.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_numbering.c

## Purpose

`syscall_numbering.c` verifies x86-64 syscall-number interpretation, including ignored high 32 bits, x32 syscall-bit handling, out-of-range numbers, and ptrace preservation of `orig_rax`.

## Important APIs, Types, and Functions

`probe_syscall()` issues raw `syscall` with a 64-bit number and saves a duplicate in `%rbx` for tracer comparison. `test_x32()`, `test_syscalls_common()`, `test_syscalls_with_x32()`, and `test_syscalls_without_x32()` encode the expected syscall matrix. `syscall_numbering_tracee()`, `mess_with_syscall()`, and `syscall_numbering_tracer()` run ptrace passes that read, write back, fuzz return values, fuzz high bits, or sign-extend syscall numbers.

## Control Flow and State

`main()` opens `/dev/null`, maps shared memory for counters and tracer state, detects x32 support by calling x32 `getpid`, runs untraced tests, then forks a traced child for repeated ptrace passes. Shared state tracks indentation, total errors, current ptrace pass, and whether the tracee is inside `probe_syscall()`.

## Dependencies and Integration Points

The test depends on x86-64 raw syscall ABI, optional x32 ABI support, `/dev/null`, shared anonymous `mmap`, `PTRACE_SYSCALL`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, and kselftest result conventions.

## Risks and Test Signals

Risks include honoring high syscall-number bits, accepting x32 numbers without the x32 bit, losing `orig_rax` fidelity under ptrace, or mishandling tracer-modified returns. Passing output reports expected `0`, `-ENOSYS`, or ptrace-modified sentinel values for all tested ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_numbering.c -->
