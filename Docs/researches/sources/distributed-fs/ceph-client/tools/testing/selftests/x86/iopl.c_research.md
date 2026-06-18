# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/iopl.c

## Purpose

`iopl.c` tests x86 `iopl(2)` semantics, especially that IOPL level 3 does not let userspace actually disable interrupts with CLI/STI, that I/O bitmap state is preserved/restored, that IOPL behavior across fork is correct, and that privilege checks work after dropping uid.

## Important APIs, Types, and Functions

It uses `iopl()`, `ioperm()`, inline `outb`, `cli`, `sti`, `pushf/pop`, fork/wait, `setresuid()`, and SIGSEGV recovery. Helpers include `try_outb()`, `expect_ok_outb()`, `expect_gp_outb()`, `try_cli()`, `try_sti()`, `expect_gp_sti()`, and `test_cli()`.

## Control Flow

The test pins to CPU 0 and tries `iopl(3)`, exiting successfully with a note if unsupported or not privileged. With IOPL 3, it ensures CLI/STI fault or are NOP-emulated rather than disabling interrupts, and that `outb 0x80` works. It establishes an I/O bitmap, drops IOPL to 0, verifies bitmap still permits `0x80`, clears the bitmap, forks a child that sets IOPL 3 and writes `0x80`, then confirms the parent still cannot write. Finally it tests that unprivileged callers can keep/drop an already-held IOPL 3 but cannot raise from 0.

## State and Persistence Behavior

State is process-local IOPL, I/O bitmap, CPU affinity, and uid. No persistence exists. The test can write to I/O port `0x80`.

## Dependencies and Integration Points

It requires x86 IOPL support and privilege for full coverage. It targets kernel entry/return, Xen-like emulation, signal delivery, fork inheritance, and capability checks.

## Risks and Edge Cases

The code checks `case -ENOSYS` after `iopl(3)`, but libc returns `-1` with `errno`, so this branch is unlikely to trigger as intended. CLI/STI behavior can be fault or NOP-emulation, both accepted. Running unprivileged reduces coverage.

## Test Signals

Pass signals include blocked/NOPed CLI/STI, working port I/O only when expected, child success without contaminating parent, and correct unprivileged iopl transitions.
