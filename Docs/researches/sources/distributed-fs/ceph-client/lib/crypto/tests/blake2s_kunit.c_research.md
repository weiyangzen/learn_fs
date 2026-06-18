# sources/distributed-fs/ceph-client/lib/crypto/tests/blake2s_kunit.c

## Purpose

This KUnit suite tests BLAKE2s hashing, keyed hashing, variable output lengths, guarded buffers, and benchmarks. It was read as a complete 133-line file.

## Important APIs, Types, and Functions

It defines `blake2s_default`, `blake2s_init_default`, template hash macros, `test_blake2s_all_key_and_hash_lens`, `test_blake2s_with_guarded_key_buf`, and `test_blake2s_with_guarded_out_buf`.

## Control Flow

Template tests cover unkeyed fixed-size BLAKE2s. The all-length test deterministically fills data and keys, iterates every key length and output length, feeds each result into a main BLAKE2s context, and checks the consolidated digest. Guarded-key tests compare normal and edge-of-buffer key pointers through one-shot and init-key APIs. Guarded-output tests compare normal and edge-of-buffer output pointers for every valid output size.

## State and Persistence Behavior

The suite uses hash-template shared buffers and stack-local contexts. No state persists beyond KUnit execution.

## Dependencies and Integration Points

It depends on `<crypto/blake2s.h>`, generated vectors, KUnit, and shared hash template helpers. BLAKE2s test enablement is special in Kconfig because the implementation is always built for random-device use.

## Risks and Edge Cases

The tests focus on API boundary lengths and guarded pointers. Remaining risk is platform-specific accelerated compression if tests are not run on those platforms.

## Test Signals

Passing KUnit vector, keyed aggregate, guarded key, guarded output, and benchmark cases validate this file.
