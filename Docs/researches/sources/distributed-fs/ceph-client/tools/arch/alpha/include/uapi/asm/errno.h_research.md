# sources/distributed-fs/ceph-client/tools/arch/alpha/include/uapi/asm/errno.h

## Purpose
Provides Alpha-specific errno number definitions for tools UAPI builds.

## Important APIs, Types, And Functions
- Includes generic errno base definitions.
- Undefines generic `EAGAIN` and assigns Alpha-specific errno values.
- Defines networking, IPC, filesystem, stream, library, restart, medium, key, robust mutex, rfkill, and hardware poison errors.
- Aliases include `EWOULDBLOCK`, `EDEADLOCK`, `EFSBADCRC`, and `EFSCORRUPTED`.

## Control Flow
No runtime flow; this is compile-time constant mapping.

## State And Persistence
No state. Constants must match kernel/userspace ABI.

## Dependencies And Integration Points
Used by Linux tools built against copied UAPI headers for Alpha.

## Risks
Errno number mismatches would make tools misinterpret syscall or perf-event errors on Alpha.

## Test Signals
Cross-compile and run syscall/error-path tests on Alpha or compare constants against kernel UAPI.
