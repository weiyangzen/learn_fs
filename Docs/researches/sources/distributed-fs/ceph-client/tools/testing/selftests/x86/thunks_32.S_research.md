<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks_32.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks_32.S

## Purpose

`thunks_32.S` provides the inverse mixed-bitness helper: a 32-bit object can call a 64-bit function while running on a 64-bit kernel. It supports compat syscall tests that inspect or poison 64-bit registers.

## Important APIs, Types, and Functions

The exported `call64_from_32` reads the function pointer from the 32-bit stack, saves registers clobbered by the 64-bit ABI, far-jumps to USER64_CS, calls the function through `%rax`, then returns to USER32_CS using an `lretq` sequence designed to avoid problematic 32-bit relocations.

## Control Flow and State

State is transient in CPU registers and the user stack. The helper does not allocate memory or store globals; it only performs controlled segment transitions and register save/restore.

## Dependencies and Integration Points

It depends on standard Linux x86 user selectors, compatibility-mode execution, and a 64-bit kernel. It is used by `test_syscall_vdso.c` to check whether compat syscalls leak high registers.

## Risks and Test Signals

Risks include wrong relocation handling, incorrect selector constants, or register corruption across the transition. Successful downstream tests observe expected 64-bit register poison and preservation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/thunks_32.S -->
