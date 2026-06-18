# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/bitsperlong.h

## Purpose
Provides the arm64 UAPI word-size contract for tools headers.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` as 64 and includes `asm-generic/bitsperlong.h` for derived generic definitions.

## Control Flow, State, and Persistence
No control flow or state exists; preprocessing selects a fixed 64-bit ABI.

## Dependencies and Integration Points
Used by perf/tools UAPI consumers and any copied kernel header that needs userspace word size. Depends on the generic bits-per-long header.

## Risks and Test Signals
Risk is accidental mismatch with arm64 userspace ABI. Test signals are preprocessing on arm64 and build checks that size-dependent UAPI structs use 64-bit long semantics.
