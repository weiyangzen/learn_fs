<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_nt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_nt.c

## Purpose

`syscall_nt.c` checks that x86 syscall entry and return handle the EFLAGS Nested Task bit correctly. User mode can set unusual flags, and the kernel must avoid returning with unsafe or architecturally invalid state.

## Important APIs, Types, and Functions

`do_it()` sets extra EFLAGS bits and performs syscalls with inline assembly. `sigtrap()` observes trap delivery and saved context. `main()` runs baseline and NT-modified cases, accumulating `nerrs`.

## Control Flow and State

The test is linear: install a SIGTRAP handler, run syscall sequences with selected extra flags, and verify that no unexpected trap or crash occurs. State is limited to the global error counter and signal context.

## Dependencies and Integration Points

It depends on x86 EFLAGS semantics, syscall instruction behavior, and Linux signal delivery. It is part of the x86 selftest entry-path coverage.

## Risks and Test Signals

Risks include preserving NT inappropriately, causing task-switch faults, or delivering unexpected signals. Passing behavior completes the syscall cases without incrementing `nerrs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_nt.c -->
