# sources/cloud-native/ostree/src/libotcore/otcore-spki-verify.c

## Purpose
Implements SPKI signature verification using OpenSSL for otcore signing support.

## Important APIs, Types, And Functions
`otcore_spki_init` is an idempotent no-op success. `otcore_validate_spki_signature(data, public_key, signature, out_valid, error)` validates a signature using a DER SubjectPublicKeyInfo public key parsed by OpenSSL `d2i_PUBKEY`.

## Control Flow
The verifier asserts input pointers, checks public key and signature sizes against `OSTREE_SIGN_MAX_METADATA_SIZE`, creates an `EVP_MD_CTX`, parses the public key, and runs `EVP_DigestVerifyInit` plus `EVP_DigestVerify`. A valid signature sets `*out_valid = true`; invalid signatures return success with false. Builds without OpenSSL return a hard error.

## State And Persistence Behavior
No persistent state. All inputs are in-memory `GBytes`.

## Dependencies And Integration Points
Depends on OpenSSL EVP/X509 APIs, otcore signature size constants, GLib, and libglnx errors. It supports signature types declared in `otcore.h` and used by higher-level repository verification paths.

## Risks
As with ed25519, callers must initialize `out_valid` to false. Large but under-limit malformed DER inputs rely on OpenSSL parse behavior. No alternative backend exists when OpenSSL is unavailable.

## Test Signals
Good/bad SPKI signatures, malformed DER public keys, oversize public key/signature inputs, no-OpenSSL build behavior, and invalid-signature-without-error behavior are key signals.
