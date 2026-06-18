# sources/cloud-native/ostree/src/libotcore/otcore-ed25519-verify.c

## Purpose
Implements ed25519 signature-verification support for otcore, using libsodium when available or OpenSSL otherwise.

## Important APIs, Types, And Functions
`otcore_ed25519_init` initializes libsodium once when compiled with libsodium and is otherwise a no-op success. `otcore_validate_ed25519_signature(data, public_key, signature, out_valid, error)` validates one detached signature over a `GBytes` payload.

## Control Flow
Initialization uses `g_once_init_enter/leave` to cache success or failure of `sodium_init`. Verification asserts non-null inputs, validates public key and signature lengths when a crypto backend exists, then calls `crypto_sign_verify_detached` or OpenSSL `EVP_DigestVerifyInit`/`EVP_DigestVerify`. Invalid signatures return success with `*out_valid` left false; malformed inputs or unavailable support return errors.

## State And Persistence Behavior
Only process-global libsodium init state is cached. The function reads in-memory commit or metadata bytes and does not persist anything.

## Dependencies And Integration Points
Depends on compile-time `HAVE_LIBSODIUM` and `HAVE_OPENSSL`, otcore signature constants, GLib `GBytes`, GError helpers, and OpenSSL EVP APIs. It is used by composefs/commit signature validation paths.

## Risks
Callers must initialize or set `*out_valid` expectations carefully; the function only sets it true on success and relies on caller-initialized false. Builds without libsodium or OpenSSL cannot validate signatures. Error text has a typo in a comment only; behavior is unaffected.

## Test Signals
Known-good and known-bad signatures, wrong key/signature lengths, no-backend builds, libsodium initialization failure simulation, and OpenSSL backend coverage are important.
