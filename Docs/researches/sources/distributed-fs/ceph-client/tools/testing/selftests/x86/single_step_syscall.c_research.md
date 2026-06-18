<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/single_step_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/single_step_syscall.c

## Purpose

`single_step_syscall.c` verifies x86 single-step behavior around fast syscall entry and return. It ensures the trap flag does not leak, disappear, or generate traps at the wrong instruction boundary around `syscall` and other entry paths.

## Important APIs, Types, and Functions

The test uses `get_eflags()`/`set_eflags()` from `helpers.h`, a `SIGTRAP` handler that counts traps and records EFLAGS, a generic fault handler using `sigsetjmp`, and inline assembly in `fast_syscall_no_tf()` and `main()` to execute syscalls with controlled flags. `check_result()` validates expected trap counts and flag state.

## Control Flow and State

`main()` installs signal handlers, toggles TF, runs syscall sequences, and validates whether the kernel delivered a single-step trap and restored flags correctly. State is held in `sig_traps`, `sig_eflags`, and jump-buffer recovery for exceptional cases.

## Dependencies and Integration Points

It depends on x86 EFLAGS semantics, syscall instruction behavior, signal frames, and kselftest helper functions. It integrates with broader x86 entry-path selftests.

## Risks and Test Signals

Risks include losing TF across syscall, taking an unexpected SIGTRAP after return, leaking internal flags, or mishandling fault recovery. Successful output shows expected trap counts; failures report wrong flags or signal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/single_step_syscall.c -->
