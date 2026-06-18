# sources/distributed-fs/ceph-client/tools/include/uapi/asm-generic/bitsperlong.h

## Purpose
Defines generic UAPI word-size constants for user-space header consumers.

## Important APIs, Types, and Functions
Exports `__BITS_PER_LONG`, derived from `__CHAR_BIT__ * __SIZEOF_LONG__` when available and otherwise defaulting to 32, plus `__BITS_PER_LONG_LONG` fixed at 64.

## Control Flow, State, and Persistence
All behavior is preprocessor-only. Architecture-specific headers may define `__BITS_PER_LONG` before inclusion to override the generic fallback.

## Dependencies and Integration
No includes. It integrates with UAPI bitmask, socket, ioctl, and syscall headers that need to vary constants by userspace ABI width.

## Risks and Test Signals
Risks include defaulting to 32 for older toolchains on 64-bit ABIs unless arch headers override it, and confusing kernel `CONFIG_64BIT` with userspace long size. Test signals include compile probes for 32-bit, 64-bit, and x32-style environments.
