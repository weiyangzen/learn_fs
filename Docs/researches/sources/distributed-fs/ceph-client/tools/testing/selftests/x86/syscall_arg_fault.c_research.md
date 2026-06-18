<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_arg_fault.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_arg_fault.c

## Purpose

`syscall_arg_fault.c` tests x86 syscall entry behavior when syscall arguments or return paths are arranged to fault. It verifies signal delivery, IP advancement, and trap behavior around invalid user pointers and consecutive syscall instructions.

## Important APIs, Types, and Functions

The file uses `SIGSEGV`/`SIGBUS`, `SIGTRAP`, and `SIGILL` handlers, `sigsetjmp`, ucontext register edits, raw inline `syscall` or `int $0x80` style assembly, and direct inspection of `REG_AX` and `REG_IP`. `sigsegv_or_sigbus()` recovers from expected memory faults. `sigtrap()` tracks consecutive syscall single-step behavior. `sigill()` handles unsupported instruction paths.

## Control Flow and State

`main()` installs handlers, executes syscall sequences with invalid or boundary arguments, and uses signal handlers to skip or validate the faulting instruction. State includes `n_errs`, `sigtrap_consecutive_syscalls`, and the jump buffer. The test mutates only its own context.

## Dependencies and Integration Points

It depends on architecture-specific ucontext names, x86 syscall ABI, signal delivery from bad user memory access, and kselftest helper conventions. It complements syscall numbering and single-step tests by focusing on fault handling.

## Risks and Test Signals

Risks include wrong signal type, failure to advance or restore IP, losing `rax/eax` error conventions, and incorrect trap behavior between adjacent syscalls. Passing cases recover through handlers and report no accumulated errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/syscall_arg_fault.c -->
