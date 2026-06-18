# sources/distributed-fs/ceph-client/include/linux/siphash.h

## Purpose

`siphash.h` declares the kernel SipHash and HalfSipHash APIs. SipHash2-4 is intended as a secure short-input PRF, while HalfSipHash1-3 and SipHash1-3 helpers are documented as insecure PRFs suitable only for hash tables.

## Important APIs, Types, And Functions

Types are `siphash_key_t`, aligned `siphash_aligned_key_t`, and `hsiphash_key_t`. APIs include `siphash_key_is_zero()`, `__siphash_aligned()`, `__siphash_unaligned()`, fixed-argument helpers `siphash_1u64()` through `siphash_4u64()`, `siphash_1u32()`, `siphash_2u32()`, `siphash_3u32()`, `siphash_4u32()`, generic `siphash()`, `__hsiphash_aligned()`, `__hsiphash_unaligned()`, fixed-argument `hsiphash_1u32()` through `hsiphash_4u32()`, and generic `hsiphash()`.

Internal macros expose raw permutations and constants: `SIPHASH_PERMUTATION`, `SIPHASH_CONST_*`, `HSIPHASH_PERMUTATION`, and `HSIPHASH_CONST_*`.

## Control Flow

The generic `siphash()` and `hsiphash()` wrappers choose aligned or unaligned implementations depending on efficient unaligned access support and pointer alignment. Aligned inline helpers use compile-time constant length checks to select specialized fixed-width helpers for 4, 8, 16, 24, and 32 byte SipHash inputs or 4, 8, 12, and 16 byte HalfSipHash inputs; otherwise they call the general aligned implementation.

## State And Persistence

No persistent state is stored in the header. Security depends on callers providing secret, initialized keys. `siphash_key_is_zero()` helps detect uninitialized all-zero keys.

## Dependencies And Integration Points

Dependencies include kernel types, endian conversion, alignment helpers, rotation helpers, and config for efficient unaligned access. Integration points are kernel hash tables, randomized identifiers, networking, filesystem hash salts, and any short-input keyed hash use.

## Risks And Test Signals

Risks are using HalfSipHash for security-sensitive PRF use, using all-zero or predictable keys, alignment-selection regressions, endian mistakes in fixed-width helpers, and direct misuse of raw permutation macros. Test signals include SipHash known-answer tests, unaligned buffer tests, compile-time constant length specialization coverage, big-endian builds, zero-key checks, and hash table collision resistance tests under randomized keys.
