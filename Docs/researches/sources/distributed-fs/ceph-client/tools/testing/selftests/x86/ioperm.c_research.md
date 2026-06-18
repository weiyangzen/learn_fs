# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/ioperm.c

## Purpose

`ioperm.c` tests Linux `ioperm(2)` I/O port bitmap behavior. It verifies default denial, enabling/disabling a port, fork inheritance and copy-on-write behavior, and privilege checks after dropping uid.

## Important APIs, Types, and Functions

The test uses `ioperm()`, inline `outb`, `sched_setaffinity()`, fork/wait, `setresuid()`, and SIGSEGV recovery through `sigsetjmp()`. Helpers are `try_outb()`, `expect_ok()`, and `expect_gp()`.

## Control Flow

`main()` pins to CPU 0, confirms writes to ports `0x80` and `0xed` fault by default, tries to enable port `0x80`, and exits successfully with an informational message if permission is unavailable. With permission, it verifies port `0x80` works and `0xed` faults, disables `0x80`, verifies both fault, re-enables `0x80`, forks a child to check inherited permission and child-local bitmap changes, confirms the parent still has `0x80`, drops uid to 1, verifies disabling still works unprivileged, and verifies enabling again fails unprivileged.

## State and Persistence Behavior

State is the process I/O permission bitmap, CPU affinity, and uid. There is no file persistence. The test writes to legacy I/O port `0x80` when permitted.

## Dependencies and Integration Points

It requires x86 I/O port instruction support and sufficient privilege for positive `ioperm()` coverage. It integrates with signal delivery for general-protection faults.

## Risks and Edge Cases

Running as non-root reduces coverage but exits success after noting the skip-like condition. Port writes can have platform-specific side effects, though port `0x80` is traditionally used as a safe delay/debug port. `try_outb()` installs a reset-on-use SIGSEGV handler and does not clear it after successful paths because return occurs before `clearhandler()`.

## Test Signals

Pass signals are expected `[OK]` messages for faulting/default ports, working `0x80` after enable, failure after disable, child success with independent bitmap changes, and unprivileged enable failure.
