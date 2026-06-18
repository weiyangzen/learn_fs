# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/bitsperlong.h

## Purpose
MIPS UAPI word-size selector.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` from `_MIPS_SZLONG` and includes the generic bits-per-long header.

## Control Flow, State, and Persistence
No runtime state; ABI word size comes from compiler-provided MIPS ABI macros.

## Dependencies and Integration Points
Used by copied UAPI and perf/tools code for MIPS o32/n32/n64 builds.

## Risks and Test Signals
Risk is missing `_MIPS_SZLONG` in non-MIPS cross builds or mismatched ABI mode. Test signals are builds under o32, n32, and n64 toolchains.
