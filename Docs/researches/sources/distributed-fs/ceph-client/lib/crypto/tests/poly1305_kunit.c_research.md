# sources/distributed-fs/ceph-client/lib/crypto/tests/poly1305_kunit.c

## Purpose
This file adapts the keyed Poly1305 API to the shared hash test template and adds Poly1305-specific regression tests for all-one-bits accumulator stress and modular reduction edge cases.

## Important APIs, Types, and Functions
- `static u8 test_key[POLY1305_KEY_SIZE]` is the deterministic suite key.
- Local helper `poly1305()` provides a one-shot wrapper around `poly1305_init()`, `poly1305_update()`, and `poly1305_final()`.
- `poly1305_init_withtestkey()` and `poly1305_withtestkey()` adapt the keyed API to the template macros.
- `poly1305_suite_init()` fills `test_key` using `rand_bytes_seeded_from_len()` and then calls `hash_suite_init()`.
- `test_poly1305_allones_keys_and_message()` initializes two Poly1305 contexts with all-one-bits key data, repeatedly updates a long-running MAC context with all-one-bits messages of lengths 0..4096 in 16-byte steps over 32 rounds, feeds each temporary MAC into a MAC-of-MACs context, and compares the final result to `poly1305_allones_macofmacs`.
- `test_poly1305_reduction_edge_cases()` uses `r_key=1`, `s_key=0`, and crafted three-block messages near the `2^130 - 5` modulus boundary to check final modular reduction.

## Control Flow
Suite init seeds the fixed key and guarded buffer. Template-generated tests run first through `HASH_KUNIT_CASES`. Poly1305-specific tests then exercise carry/reduction stress before `benchmark_hash()`. Suite exit frees the template buffer.

## State and Persistence Behavior
The suite key is static mutable state initialized once per suite. The shared guarded buffer and PRNG state come from the template. Poly1305 contexts are stack locals except for copied temporary context snapshots in the all-one-bits test. No persistent state exists.

## Dependencies and Integration Points
The file depends on `<crypto/poly1305.h>`, `poly1305-testvecs.h`, and `hash-test-template.h`. It registers the KUnit suite name `poly1305` and uses the template benchmark gate `CONFIG_CRYPTO_LIB_BENCHMARK`.

## Risks and Edge Cases
The one-shot helper is local because the API apparently lacks a direct one-shot function; if the library later adds one, tests may need to ensure both paths match. The all-one-bits stress intentionally mutates cumulative context over many updates, so it is sensitive to any change in Poly1305 update/final semantics. The reduction edge test covers small `i` values near the modulus boundary, not every possible boundary case.

## Test Signals
Signals include generic hash-template coverage, deterministic Poly1305 vectors, all-one-bits key/message accumulator stress, explicit modular reduction edge cases, zeroization/overlap/alignment/IRQ signals from the template, and optional throughput.
