# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/sysmacros.h

## Purpose
Provides device-number composition and extraction helpers for nolibc.

## APIs, Types, and Functions
Defines inline `__nolibc_makedev`, `__nolibc_major`, and `__nolibc_minor`, then maps public `makedev`, `major`, and `minor` macros to them.

## Control Flow, State, and Persistence
Control flow is bit manipulation matching Linux device number encoding. No runtime state is retained.

## Dependencies and Integration
Depends on `dev_t` from nolibc types. It integrates with `stat`, `mknod`, and tools that inspect device ids.

## Risks and Test Signals
Risks are encoding drift if Linux changes device-number layout and truncation of large major/minor values. Test signals are round trips for boundary major/minor values and comparison with libc/sysmacros on Linux.
