<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_null.c -->
# sources/distributed-fs/ceph-client/crypto/crypto_null.c

## Purpose

`crypto_null.c` registers no-op cryptographic algorithms used for IPsec, testing, and debugging: `cipher_null`, `digest_null`, and `ecb(cipher_null)` skcipher.

## Important APIs, Types, and Flow

Hash callbacks `null_init()`, `null_update()`, `null_final()`, and `null_digest()` all return success without producing data. Hash setkey also succeeds. `null_crypt()` copies one null cipher block for the legacy cipher API. `null_skcipher_crypt()` copies the request source scatterlist to destination when they differ and otherwise leaves data untouched.

Module init registers the legacy cipher, shash, and skcipher in order, rolling back earlier registrations on failure. Module exit unregisters all three. Registered sizes and key/IV constants come from `crypto/null.h`.

## State, Dependencies, and Integration

There is no transform context state. Dependencies are Crypto API hash and skcipher internals, scatterlist copy helpers, and null algorithm constants. Integration points are IPsec null encryption/authentication modes and tests that need a transform with predictable no-op behavior.

## Risks and Test Signals

Risks are mostly semantic: callers must understand that null digest produces zero-length/empty authentication behavior and null cipher provides no confidentiality. Implementation risks include registration rollback order and out-of-place scatterlist copying. Test signals are successful registration, no-op round trips, setkey accepting the configured null key size, and IPsec/null transform interoperability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/crypto_null.c -->
