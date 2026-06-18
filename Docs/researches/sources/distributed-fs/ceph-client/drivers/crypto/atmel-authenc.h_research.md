# sources/distributed-fs/ceph-client/drivers/crypto/atmel-authenc.h

## Purpose

`atmel-authenc.h` is the conditional internal API that lets the Atmel AES driver coordinate SPLIP/authenc processing with the Atmel SHA driver. It is compiled only when `CONFIG_CRYPTO_DEV_ATMEL_AUTHENC` is enabled and avoids exposing SHA internals directly to unrelated code.

## Important APIs, Types, And Functions

The header forward-declares `struct atmel_aes_dev` and opaque `struct atmel_sha_authenc_ctx`, defines `atmel_aes_authenc_fn_t` callbacks, and declares readiness, request-size, spawn/free, setkey, schedule, init, final, and abort helpers. These functions are implemented in `atmel-sha.c` and called from `atmel-aes.c` authenc mode. It includes crypto authenc/hash/SHA headers and `atmel-sha-regs.h` for mode constants.

## Control Flow

AES authenc starts by checking `atmel_sha_authenc_is_ready()`, spawning a SHA HMAC context for the desired algorithm, scheduling ownership of the SHA hardware, initializing SHA over associated data and ciphertext/plaintext length, transferring AES data in PLIP mode, then asking SHA to finalize and return the digest/tag through callbacks.

## State And Persistence Behavior

The header itself stores no state. Its API implies an opaque SHA authenc context per AES transform and an ahash request area embedded at the end of AES authenc request context. Callback parameters carry the AES device, error, and async-completion indication between the SHA and AES drivers.

## Dependencies And Integration Points

This is an internal cross-driver interface between `atmel-aes.c` and `atmel-sha.c`. It depends on the crypto authenc key format and SHA mode flags, and is compiled away when authenc support is disabled.

## Risks And Test Signals

Risks include ABI drift between declarations and `atmel-sha.c`, request-size mismatches because AES embeds an ahash request after its context, and callback ordering bugs that leave AES or SHA hardware busy. Test by building with and without `CONFIG_CRYPTO_DEV_ATMEL_AUTHENC`, probing AES before SHA to exercise defer, and running authenc HMAC-SHA1/SHA224/SHA256/SHA384/SHA512 CBC-AES selftests.
