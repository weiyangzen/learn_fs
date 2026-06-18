# sources/distributed-fs/ceph-client/tools/include/nolibc/inttypes.h

## Purpose
Compatibility shim for code that includes `<inttypes.h>` while using nolibc.

## APIs, Types, and Functions
The header currently includes `stdint.h` and does not define printf format macros or conversion functions of its own.

## Control Flow, State, and Persistence
There is no runtime control flow or state. Its value is include-path compatibility and fixed-width integer availability.

## Dependencies and Integration
Depends on `nolibc/stdint.h`. It integrates with source files that need integer typedefs but do not rely on full libc `inttypes` formatting support.

## Risks and Test Signals
Risks are callers expecting `PRI*`, `SCN*`, `imaxdiv`, or other full `<inttypes.h>` APIs. Test signals are compile failures in consumers that require missing macros, and simple builds that only need fixed-width types.
