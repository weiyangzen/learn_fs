# sources/distributed-fs/ceph-client/lib/crypto/tests/nh_kunit.c

## Purpose
This file defines a focused KUnit known-answer test for the NH hash primitive. It validates the `nh()` implementation at four message lengths using generated fixtures from `nh-testvecs.h`.

## Important APIs, Types, and Functions
- `test_nh()` allocates a mutable `u32` key buffer of `NH_KEY_BYTES`, copies `nh_test_key`, converts it from little-endian words with `le32_to_cpu_array()`, and hashes `nh_test_msg`.
- The output buffer is `__le64 hash[NH_NUM_PASSES]`, matching NH's little-endian output representation.
- The test calls `nh(key, nh_test_msg, 16/96/256/1024, hash)` and compares with `KUNIT_ASSERT_MEMEQ()`.
- The suite registers a single case under suite name `nh`.

## Control Flow
KUnit invokes `test_nh()`. The test allocates key memory, asserts allocation success, prepares host-order key words, runs four one-shot calls, and aborts on the first mismatch due to `KUNIT_ASSERT_MEMEQ`.

## State and Persistence Behavior
The only dynamic state is KUnit-owned key allocation and a stack output buffer. Static fixture data remains read-only. No persistent or global mutable state is used.

## Dependencies and Integration Points
The file depends on `<crypto/nh.h>` for `nh()`, constants, and types; KUnit for allocation/assertions; endian helper `le32_to_cpu_array()` through kernel headers; and `nh-testvecs.h` for fixtures. It registers via `kunit_test_suite(nh_test_suite)`.

## Risks and Edge Cases
The test does not exercise alignment variants, invalid lengths, buffer boundaries, or concurrency. It assumes `nh()` receives host-order key words while vectors are stored as little-endian bytes. The fixture set is small but covers multiple lengths including full generated-message size.

## Test Signals
The suite gives direct known-answer signals for NH at 16, 96, 256, and 1024 bytes and catches key-endian conversion regressions in the test path.
