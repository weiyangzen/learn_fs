# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/resource.h

## Purpose
Provides resource-limit wrappers for nolibc.

## APIs, Types, and Functions
Includes Linux resource UAPI and defines `getrlimit` and `setrlimit`, using `prlimit64` when needed.

## Control Flow, State, and Persistence
Calls query or update kernel rlimit state for the current process and translates errors. No userspace state persists beyond caller-provided `struct rlimit` values.

## Dependencies and Integration
Depends on syscall macros, `sys.h`, and Linux resource definitions. It integrates with tests or tools that constrain address space, file size, or descriptor counts.

## Risks and Test Signals
Risks include 32-bit vs 64-bit limit layout, privilege-sensitive limit increases, and kernel support differences. Test signals are reading `RLIMIT_NOFILE`, lowering/restoring soft limits, invalid resource ids, and cross-architecture struct-size checks.
