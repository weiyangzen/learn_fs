# sources/distributed-fs/ceph-client/scripts/include/hash.h

## Purpose
Supplies lightweight hash helpers for host tools.

## APIs, Control Flow, and State
`hash_str()` implements FNV-1a-like 32-bit string hashing. `hash_32()` multiplies by the 32-bit golden-ratio constant, and `hash_ptr()` casts a pointer through `unsigned long` to `unsigned int` before hashing. There is no mutable state.

## Dependencies and Integration
The header is standalone and mirrors simplified kernel hash helpers for scripts-side code that cannot include full kernel internals.

## Risks and Test Signals
The functions are non-cryptographic and `hash_ptr()` loses high pointer bits on 64-bit hosts. Test signals are compile coverage in host tools and acceptable distribution for small in-memory tables.
