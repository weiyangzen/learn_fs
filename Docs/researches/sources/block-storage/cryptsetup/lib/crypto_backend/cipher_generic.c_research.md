# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_generic.c

## Purpose
Generic cipher metadata helpers independent of a concrete crypto provider.

## Key Content
Maintains a static cipher table with block sizes and wrapped-key support, including common dm-crypt algorithms and Adiantum compound names. `crypt_cipher_ivsize()` returns IV size, with special handling for `hctr2` and `ecb`. `crypt_cipher_wrapped_key()` reports whether an algorithm uses a wrapped key. `crypt_fips_mode_kernel()` reads `/proc/sys/crypto/fips_enabled`.

## Dependencies and Coupling
Includes `crypto_backend.h` and POSIX file APIs. Used by setup/validation paths that need cipher properties before initializing a full cipher context.

## Invariants and Risks
Algorithm matching is case-insensitive and allows mode-prefix matches for table entries with a mode. Unknown algorithms return `-EINVAL` for IV size and false for wrapped-key status.
