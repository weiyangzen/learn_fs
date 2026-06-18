# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/syscall.h

## Purpose
Compatibility shim for code including `<sys/syscall.h>` under nolibc.

## APIs, Types, and Functions
Includes `<asm/unistd.h>` to expose `__NR_*` syscall numbers and defines no local wrappers.

## Control Flow, State, and Persistence
There is no runtime control flow or state. It simply makes syscall-number constants available through a libc-like include path.

## Dependencies and Integration
Depends on architecture UAPI unistd headers. It integrates with programs that occasionally issue raw nolibc architecture syscall macros or need numeric syscall constants.

## Risks and Test Signals
Risks are architecture-specific syscall-number differences and callers expecting libc's variadic `syscall()` function, which this header does not provide. Test signals are compile checks for required `__NR_*` constants and raw syscall smoke tests through arch macros.
