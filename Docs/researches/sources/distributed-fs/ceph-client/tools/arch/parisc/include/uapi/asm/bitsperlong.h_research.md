# sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/bitsperlong.h

## Purpose
PARISC UAPI word-size selector.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` and `SHIFT_PER_LONG` based on whether `__LP64__` is set, then includes generic bits-per-long support.

## Control Flow, State, and Persistence
No runtime state; compiler ABI controls 32-bit versus 64-bit selection.

## Dependencies and Integration Points
Used by PARISC tools and copied UAPI headers.

## Risks and Test Signals
Risk is building with a compiler that does not expose the expected ABI macro. Test signals are 32-bit and 64-bit PARISC preprocessing/build checks.
