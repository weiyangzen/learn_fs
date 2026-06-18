# sources/distributed-fs/ceph-client/fs/crypto/hkdf.c

## Purpose
`hkdf.c` implements fscrypt's HKDF-SHA512 extract and expand operations. It derives isolated subkeys from raw master keys or from software secrets derived by inline-crypto hardware for hardware-wrapped master keys.

## Important APIs, Types, and Functions
- `fscrypt_init_hkdf()` performs HKDF-Extract with an all-zero SHA-512-length salt, prepares an `hmac_sha512_key`, and zeroizes the pseudorandom key buffer.
- `fscrypt_hkdf_expand()` performs HKDF-Expand using the prepared HMAC key. It prefixes all info strings with `"fscrypt\0"` and a one-byte fscrypt context ID before appending caller-provided info and a counter.
- The context IDs are defined in `fscrypt_private.h`, including key identifiers, per-file encryption keys, per-mode direct keys, IV_INO_LBLK keys, dirhash keys, inode hash keys, and hardware-wrapped-key identifiers.

## Control Flow
Master-key add paths initialize `secret->hkdf` with `fscrypt_init_hkdf()`. Later key setup paths call `fscrypt_hkdf_expand()` to derive output material for key identifiers, per-file keys, per-mode keys, and SipHash keys. The expand loop emits full SHA-512 blocks directly into the output buffer and uses a temporary buffer only for the final partial block.

## State and Persistence
This file persists no external state. The prepared HKDF state is stored in `struct fscrypt_master_key_secret` while the master key is present. Intermediate PRK and temporary partial-output buffers are wiped with `memzero_explicit()`.

## Dependencies and Integration
It depends on kernel SHA-512 HMAC primitives from `crypto/sha2.h` and the private fscrypt context IDs. It is integrated by `keyring.c` for key identifiers and master-key initialization, `keysetup.c` for v2 subkeys and SipHash keys, and test dummy key generation.

## Risks and Edge Cases
- `fscrypt_hkdf_expand()` warns if output exceeds the RFC 5869 maximum of 255 hash blocks, but callers must still provide sensible lengths.
- Context byte uniqueness is security-critical; reusing a context/info combination across purposes would break key separation.
- No random salt is persisted, so the design assumes fscrypt master keys are already pseudorandom.
- The function is documented as thread-safe because it uses only stack HMAC contexts around an immutable prepared key.

## Test Signals
Test vectors can cover deterministic output for fixed master keys, distinct output across all fscrypt HKDF contexts, partial-block output zeroization paths, maximum-length warnings, and compatibility with key identifiers generated in `keyring.c`.
