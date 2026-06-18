# sources/distributed-fs/ceph-client/tools/include/nolibc/errno.h

## Purpose
Defines nolibc errno storage and error-number constants.

## APIs, Types, and Functions
Includes `<asm/errno.h>`, defines `SET_ERRNO(v)` to update `errno` unless `NOLIBC_IGNORE_ERRNO` is set, provides fallback program invocation names in ignore mode, and defines `MAX_ERRNO` as 4095.

## Control Flow, State, and Persistence
There is no function control flow. Syscall wrappers use `__sysret()` from `sys.h` to translate negative kernel errors into `-1` plus `errno`, and this header controls whether that store is real or compiled away.

## Dependencies and Integration
Depends on architecture UAPI errno definitions and optional external `errno` storage supplied by the program or nolibc runtime. It is central to every wrapper that returns libc-style errors.

## Risks and Test Signals
Risks include missing `errno` definition in unusual embedding modes, intentionally ignored errno hiding failures, and assuming all negative values are errno when only `-MAX_ERRNO..-1` are translated. Test signals are failing syscall wrappers, `NOLIBC_IGNORE_ERRNO` builds, and checking errno values against UAPI constants.
