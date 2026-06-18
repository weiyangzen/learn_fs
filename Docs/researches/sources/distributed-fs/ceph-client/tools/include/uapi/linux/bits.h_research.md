# sources/distributed-fs/ceph-client/tools/include/uapi/linux/bits.h

## Purpose
Provides low-level UAPI bitmask construction macros for unsigned long, unsigned long long, and optional 128-bit masks.

## Important APIs, Types, and Functions
Defines `__GENMASK(h, l)`, `__GENMASK_ULL(h, l)`, and `__GENMASK_U128(h, l)`. These depend on `_UL()`, `_ULL()`, `_BIT128()`, `__BITS_PER_LONG`, and `__BITS_PER_LONG_LONG` from surrounding UAPI includes.

## Control Flow, State, and Persistence
All behavior is macro arithmetic. The macros form masks by shifting all-ones values or subtracting a low-bit marker from one-past-high for 128-bit masks. There is no state.

## Dependencies and Integration
This header assumes foundational type-width macros are already available. It integrates with UAPI headers that need compile-time masks but cannot include full kernel internals.

## Risks and Test Signals
Risks include undefined behavior for invalid ranges or shifts at/above type width, missing `_UL`/`_ULL` definitions at include sites, and 128-bit support dependence. Test signals are compile-time assertions for boundary masks and negative tests for invalid high/low inputs.
