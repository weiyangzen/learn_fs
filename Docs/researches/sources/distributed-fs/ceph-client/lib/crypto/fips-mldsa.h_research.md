# sources/distributed-fs/ceph-client/lib/crypto/fips-mldsa.h

## Purpose
Generated ML-DSA-65 FIPS self-test vector header containing signature, public key, and message bytes.

## Important APIs, Types, And Functions
Defines `fips_test_mldsa65_signature`, `fips_test_mldsa65_public_key`, and `fips_test_mldsa65_message` as `static const u8` arrays marked `__initconst __maybe_unused`.

## Control Flow
There is no executable control flow. Including self-test code reads these arrays during init-time FIPS validation and the compiler can drop them when unused.

## State, Persistence, And Dependencies
The arrays live in init-const storage and are not mutable. They depend on `<linux/fips.h>` for annotations and common FIPS declarations.

## Integration Points
Consumed by ML-DSA self-test code to verify post-quantum signature verification against a known message and public key.

## Risks
The header is generated from leancrypto vectors; accidental byte edits, truncation, or length mismatches would invalidate FIPS self-tests. Because arrays are large and opaque, review should verify sizes and source provenance rather than hand-inspect every byte.

## Test Signals
FIPS power-up self-test success for ML-DSA-65, array-size assertions in consuming code, and regeneration diff checks from the source vector are the main signals.
