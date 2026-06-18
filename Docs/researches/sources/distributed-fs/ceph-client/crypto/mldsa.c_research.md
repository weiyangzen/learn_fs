# sources/distributed-fs/ceph-client/crypto/mldsa.c

Purpose: exposes ML-DSA signature verification through the crypto `sig` API for ML-DSA-44, ML-DSA-65, and ML-DSA-87 strengths.

Important APIs, types, and functions: `struct crypto_mldsa_ctx` stores a public key buffer, key length, selected `enum mldsa_alg`, and `key_set` flag. `crypto_mldsa_verify()` calls `mldsa_verify()`. `crypto_mldsa_set_pub_key()`, `crypto_mldsa_key_size()`, and `crypto_mldsa_max_size()` enforce strength-specific sizes. Signing and private-key setup return `-EOPNOTSUPP`.

Control flow: module init registers three `sig_alg` entries. Each init callback sets `ctx->strength` and clears `key_set`. Public key setup checks exact key length and copies the key into the fixed maximum buffer. Verify rejects unset keys with `-EINVAL`, then delegates to the ML-DSA library. Module exit unregisters all registered algorithms.

State and persistence: key material is stored in the crypto tfm context until tfm teardown. No private keys are accepted. There is no persistent storage.

Dependencies and integration points: depends on `crypto/internal/sig.h` and `<crypto/mldsa.h>`. Integrates with callers that use the generic signature API and expect high-priority library-backed ML-DSA verification.

Risks: the implementation is verification-only; callers needing signing must handle `-EOPNOTSUPP`. Public keys are copied but not explicitly wiped on exit, though they are public. Size dispatch must stay synchronized with ML-DSA library constants.

Test signals: NIST ML-DSA verification vectors for all three strengths, exact key/signature size boundaries, unset-key failure, unsupported sign/private-key paths, and registration rollback when a later algorithm fails.
