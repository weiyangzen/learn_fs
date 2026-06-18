<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_syscall_vdso.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_syscall_vdso.c

## Purpose

`test_syscall_vdso.c` is a 32-bit x86 syscall ABI conformance test. It checks `__kernel_vsyscall` and `int $0x80` argument preservation, flags behavior, ptrace syscall tracing, and absence of leaked 64-bit register contents on 64-bit kernels.

## Important APIs, Types, and Functions

`get_syscall()` finds `AT_SYSINFO`. `int80` is an inline assembly entry. `struct regs64`, `get_regs64`, and `poison_regs64` use mixed-bitness thunks from `thunks_32.S` to check high registers. `prep_args()` builds a 6-argument `pselect` call. `run_syscall()` invokes the selected syscall entry and validates argument registers and R8-R15. `ptrace_me()` forks a parent tracer using `PTRACE_SYSCALL`.

## Control Flow and State

The 32-bit `main()` detects whether it runs on a 64-bit kernel from CS, discovers the vDSO syscall entry, runs the test through vDSO and `int $0x80`, starts a ptraced child, and repeats under tracing. State includes `syscall_addr`, `kernel_is_64bit`, register snapshots, fd sets, timespec, and signal mask descriptors.

## Dependencies and Integration Points

It depends on a 32-bit userspace build, ELF auxv, mixed 32/64 thunks, ptrace, `pselect`, and x86 syscall ABI details. Non-i386 builds skip immediately.

## Risks and Test Signals

Risks include clobbered syscall arguments, leaking kernel data into R8-R15 on compat syscalls, unexpected flag preservation differences, and ptrace altering syscall behavior. Passing output reports preserved arguments and no register leaks for both syscall entry mechanisms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/test_syscall_vdso.c -->
