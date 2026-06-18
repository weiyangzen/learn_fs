# sources/distributed-fs/ceph-client/lib/crypto/tests/ghash-testvecs.h

## Purpose
This generated header supplies GHASH known-answer fixtures for the shared hash KUnit template and GHASH-specific all-one-bits regression test. It turns deterministically generated inputs into compact oracles by storing input lengths and expected digests rather than the input bytes themselves.

## Important APIs, Types, and Data
- `hash_testvecs[]` is a static array of `{ size_t data_len; u8 digest[GHASH_DIGEST_SIZE]; }`.
- The vector lengths include empty input, small lengths 1-3, block and boundary lengths around 16/32/48/49/63/64/65/127/128/129, larger lengths 256/511/513/1000/3333/4096/4128/4160/4224, and the template maximum of 16384.
- `hash_testvec_consolidated[GHASH_DIGEST_SIZE]` is the expected digest of the concatenated digests for all lengths 0 through 4096 in the shared template.
- `ghash_allones_hashofhashes[GHASH_DIGEST_SIZE]` is the expected result for the GHASH all-one-bits key/message stress path in `ghash_kunit.c`.

## Control Flow
The header has no functions. It is included after `GHASH_DIGEST_SIZE` is visible and before `hash-test-template.h` is included by the GHASH suite. The template reads `hash_testvecs[]` for known-answer checks and `hash_testvec_consolidated` for exhaustive-length consolidation.

## State and Persistence Behavior
All state is static const test data. It has no runtime mutation and no persistence beyond the loaded KUnit module.

## Dependencies and Integration Points
The header depends on GHASH digest-size definitions from `<crypto/gf128hash.h>` and on the shared variable names expected by `hash-test-template.h`. It also integrates with `test_ghash_allones_key_and_message()` through the `ghash_allones_hashofhashes` symbol.

## Risks and Edge Cases
Because inputs are regenerated from length-derived seeds by the template, this file depends on the generator algorithm and the template PRNG staying aligned. A mismatch between `GHASH_DIGEST_SIZE` and the actual digest size would be caught at compile time or KUnit comparison time. The all-one-bits oracle is important for carryless-multiplication implementations that use standard multiplication emulation and can overflow.

## Test Signals
The header feeds known-answer checks, exhaustive length checks up to 4096, boundary-length coverage, maximum-buffer coverage at 16384 bytes, and the all-one-bits regression signal in the GHASH suite.
