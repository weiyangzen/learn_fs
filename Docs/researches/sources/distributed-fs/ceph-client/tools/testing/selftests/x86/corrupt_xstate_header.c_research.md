# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/corrupt_xstate_header.c

## Purpose

`corrupt_xstate_header.c` is a regression test for kernel handling of a deliberately corrupted xstate header in a signal frame. It verifies that returning from such a signal and then scheduling does not explode or warn.

## Important APIs, Types, and Functions

`xsave_enabled()` checks CPUID leaf 1 ECX OSXSAVE. `sigusr1()` locates `uc_mcontext.fpregs`, advances to the xstate header at offset 512, and corrupts a reserved qword. `sigsegv()` prints if a segmentation fault occurs. `main()` installs handlers with `sethandler()`, pins to CPU 0, raises SIGUSR1, forks, and waits for the child.

## Control Flow

The program skips if OSXSAVE is disabled. Otherwise it pins itself, raises SIGUSR1, corrupts the signal frame xstate header in the handler, returns from the signal, then forks and waits to force scheduling on the same CPU. Success is reaching the end without crash; kernel warnings must be checked externally.

## State and Persistence Behavior

The test modifies only its own signal frame and scheduling affinity. No persistent state exists.

## Dependencies and Integration Points

It depends on x86 XSAVE signal-frame layout, CPUID support via `kselftest.h`, signal delivery, scheduler affinity, and fork/wait.

## Risks and Edge Cases

The reserved-field offset is architecture-layout-specific. The test does not parse dmesg itself, so warnings mentioned in comments are outside the binary's exit status unless the broader runner checks logs.

## Test Signals

Pass signal is normal exit after printing back-from-signal and back-in-main-thread messages. A crash, SIGSEGV, or external kernel warning indicates failure.
