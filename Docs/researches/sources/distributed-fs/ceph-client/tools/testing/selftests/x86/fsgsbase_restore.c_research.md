# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/fsgsbase_restore.c

## Purpose

`fsgsbase_restore.c` simulates a debugger redirecting a tracee into a function and then restoring saved registers with `PTRACE_SETREGS`. It verifies that FS/GS segment selector and base state is restored correctly even if the injected function modifies the segment register.

## Important APIs, Types, and Functions

The test uses `modify_ldt`, 32-bit `set_thread_area` fallback via `int $0x80`, `ptrace(PTRACE_TRACEME/GETREGS/SETREGS/CONT/DETACH)`, `tgkill(SIGSTOP)`, and helper `dereference_seg_base()` from `clang_helpers_32.S` or `clang_helpers_64.S`. `SEG` is `%gs` on x86_64 and `%fs` on i386. Important local functions are `init_seg()` and `tracee_zap_segment()`.

## Control Flow

`main()` maps a low target word containing `EXPECTED_VALUE`, installs a segment descriptor pointing at it, and verifies `dereference_seg_base()` reads the value. The child tracee stops under ptrace, later resumes and re-checks the segment. The parent saves registers, changes the tracee IP to `tracee_zap_segment()`, resumes it, waits for the function to set the segment register to a nonzero selector with base zero and stop again, restores the original register set, detaches, and checks that the tracee exits successfully after reading the expected value again.

## State and Persistence Behavior

State is confined to the process pair: low mapped memory, descriptor entries, tracee registers, and ptrace stop states. There is no persistence.

## Dependencies and Integration Points

It depends on segment descriptor support through `modify_ldt` or `set_thread_area`, ptrace register APIs, architecture-specific user register layouts, and assembly helpers for clang-compatible segment dereference.

## Risks and Edge Cases

If neither descriptor API works, the test prints a note and exits without meaningful coverage. Segment behavior differs across architectures and older CPUs, especially around null selectors, so the injected function uses a nonzero selector to avoid defeating the test. Ptrace errors abort through `err()`.

## Test Signals

Pass signals are initial and post-restore segment reads matching `EXPECTED_VALUE`, successful tracee stop/resume/detach sequencing, and final `[OK] All is well.`
