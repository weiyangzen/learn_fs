# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/bitsperlong.h

## Purpose
Defines the user ABI value for `__BITS_PER_LONG` on x86 before including the generic bits-per-long header.

## APIs, Types, and Functions
The only local export is `__BITS_PER_LONG`, set to 64 for `__x86_64__` except x32 (`__ILP32__`), otherwise 32.

## Control Flow, State, and Persistence
Compile-time preprocessor selection encodes the ABI word size. There is no runtime state.

## Dependencies and Integration
Includes `asm-generic/bitsperlong.h`. Used by UAPI-compatible tool builds that need Linux word-size constants independent of libc.

## Risks and Test Signals
Risks include misdetecting x32 as 64-bit long and breaking ABI-sized structures. Test signals are compile checks for i386, x86-64 LP64, and x32 targets and structure layout checks in headers including this file.
