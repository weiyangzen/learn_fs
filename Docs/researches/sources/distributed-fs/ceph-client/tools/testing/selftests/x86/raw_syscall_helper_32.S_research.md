<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/raw_syscall_helper_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/raw_syscall_helper_32.S

## Purpose

`raw_syscall_helper_32.S` provides 32-bit assembly glue for x86 syscall ABI tests. It lets C tests load all 32-bit syscall registers, call an arbitrary syscall entry function, and capture the resulting registers without compiler ABI interference.

## Important APIs, Types, and Functions

The exported `sys32_helper` accepts a `struct syscall_args32 *` and a function pointer. It saves `%ebp/%ebx/%esi/%edi`, loads `%eax/%ebx/%ecx/%edx/%esi/%edi/%ebp` from the argument block, calls the supplied entry point, writes all registers back into the block, restores callee-saved registers, and returns. `int80_and_ret` is a tiny `int $0x80; ret` entry point.

## Control Flow and State

All state is transient CPU register state plus the caller-owned argument block. The helper carefully pushes `%eax` after the syscall so the return value can be stored without losing the pointer to the argument block. It has no global data or persistence.

## Dependencies and Integration Points

This file is consumed by `ptrace_syscall.c` and similar 32-bit selftests. It depends on i386 calling conventions, the caller's struct layout matching the assembly offsets, and a non-executable stack note.

## Risks and Test Signals

The primary risks are offset drift between C and assembly, failing to preserve callee-saved registers, or corrupting syscall return values while recovering the pointer. Successful downstream tests validate that syscall argument registers round-trip as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/raw_syscall_helper_32.S -->
