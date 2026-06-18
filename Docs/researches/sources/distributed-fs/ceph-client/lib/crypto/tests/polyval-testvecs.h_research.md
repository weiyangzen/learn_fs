# sources/distributed-fs/ceph-client/lib/crypto/tests/polyval-testvecs.h

## Purpose
This generated header supplies POLYVAL known-answer fixtures for the shared hash template and an all-one-bits regression oracle for POLYVAL arithmetic.

## Important APIs, Types, and Data
- `hash_testvecs[]` contains `{ data_len, digest[POLYVAL_DIGEST_SIZE] }` entries.
- Length coverage mirrors the other generated hash-vector headers: short inputs, block and near-block lengths, larger inputs, values around 4096, and 16384.
- `hash_testvec_consolidated[POLYVAL_DIGEST_SIZE]` is the expected hash-of-hashes for all lengths 0 through 4096.
- `polyval_allones_hashofhashes[POLYVAL_DIGEST_SIZE]` is the expected result for the all-one-bits key/message stress test.

## Control Flow
The header is included by `polyval_kunit.c`. The shared template reads `hash_testvecs` and `hash_testvec_consolidated`; the POLYVAL-specific all-one-bits test reads `polyval_allones_hashofhashes`.

## State and Persistence Behavior
All arrays are static const data with no mutation or persistence.

## Dependencies and Integration Points
The data depends on POLYVAL constants from `<crypto/gf128hash.h>` and the shared generated-vector PRNG contract. It integrates with both `hash-test-template.h` and `test_polyval_allones_key_and_message()`.

## Risks and Edge Cases
Because POLYVAL is related to GHASH but uses different bit/byte ordering conventions, fixture correctness is critical. The generated vectors and the explicit RFC 8452 test in the C file together help detect accidental GHASH/POLYVAL endianness substitution.

## Test Signals
The header drives known-answer vectors, exhaustive length consolidation through 4096, maximum-buffer coverage, and all-one-bits arithmetic stress.
