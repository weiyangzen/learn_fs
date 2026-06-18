# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/argon2_generic.c

## Purpose
cryptsetup wrapper around either external libargon2 or bundled Argon2.

## Key Content
When Argon2 headers/internal code are available, `argon2()` maps string type names `argon2i` and `argon2id` to libargon2 context execution and translates failures to errno-style values. It asserts the active crypto backend does not already provide native Argon2. If Argon2 is unavailable, the function returns `-EINVAL`. `crypt_argon2_version()` reports whether external libargon2 or cryptsetup’s bundled libargon2 is used.

## Dependencies and Coupling
Includes `crypto_backend_internal.h` and either system `<argon2.h>` or bundled `argon2/argon2.h`.

## Invariants and Risks
Argon2d is not exposed through this wrapper. Backend-native Argon2 takes precedence over external/internal wrapper code.
