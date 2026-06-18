
# sources/distributed-fs/ceph-client/lib/tests/bitfield_kunit.c

## Purpose
`bitfield_kunit.c` tests the typed bitfield encode/get helpers across native, little-endian, and big-endian integer forms. It is aimed at compile-time constant folding and runtime variable mask correctness.

## Important APIs, types, and functions
The macros `CHECK_ENC_GET_U`, `CHECK_ENC_GET_LE`, `CHECK_ENC_GET_BE`, and `CHECK_ENC_GET` exercise `u8/u16/u32/u64_encode_bits()`, `*_get_bits()`, and endian wrappers such as `le16_encode_bits()` and `be64_get_bits()`. `test_bitfields_constants()` uses literal masks and expected encoded values. `test_bitfields_variables()` uses `hweight32()` and `__ffs64()` to verify variable mask shifting for many typed widths.

## Control flow
The KUnit suite registers two test functions. Constant tests run a fixed matrix for 8-, 16-, 32-, and 64-bit fields. Variable tests loop every value representable by the mask width and assert that encoding equals `v << __ffs64(mask)`. An optional `TEST_BITFIELD_COMPILE` block contains deliberately invalid uses for negative compile testing but is not part of the normal suite.

## State and persistence
The file has no persistent state; all checks are expression-level assertions.

## Dependencies and integration points
It depends on `<linux/bitfield.h>`, endian conversion helpers, and KUnit. The Makefile disables the structleak plugin for this object and builds it through `CONFIG_BITFIELD_KUNIT`.

## Risks and edge cases
This test is tightly coupled to macro diagnostics and compiler optimization. The variable loop uses `1 << hweight32(mask)`, which is safe for the listed masks but would need care for full-width masks. The compile-fail block must stay disabled in regular test runs.

## Test signals
Failures report the encoded value and mask through KUnit assertion messages. Passing means native and endian encode/get helpers preserve value semantics for the covered masks.
