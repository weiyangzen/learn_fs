# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_tofrom_user_reference.S

## Purpose
Simple byte-copy reference implementation for copy-to/from-user validation.

## Important APIs, Types, and Functions
Exports `copy_tofrom_user_reference` through `_GLOBAL`; it copies byte-by-byte from source to destination for the requested length.

## Control Flow
The loop decrements length, loads a byte, stores it, advances pointers, and returns zero remaining bytes on success.

## State and Persistence
Only caller-provided memory is modified; no persistent state.

## Dependencies and Integration Points
Uses local `asm/ppc_asm.h` and is linked with validation tests as a known-simple baseline.

## Risks and Test Signals
Risk is low; it is intentionally simple but may not model fault behavior. Test signal is matching output against optimized loops for nonfaulting cases.
