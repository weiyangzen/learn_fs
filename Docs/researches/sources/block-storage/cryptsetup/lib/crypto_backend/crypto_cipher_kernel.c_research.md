# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_cipher_kernel.c

## Purpose
Linux AF_ALG userspace crypto backend for skcipher and selected AEAD operations.

## Key Content
When `ENABLE_AF_ALG` is enabled, initializes AF_ALG transform sockets, binds algorithm names, sets keys and optional AEAD auth size, accepts operation sockets, and performs encrypt/decrypt through `sendmsg()` control messages plus `read()`. `crypt_cipher_check_kernel()` constructs skcipher or AEAD algorithm names and tests key setup. `crypt_bitlk_decrypt_key_kernel()` uses kernel `ccm(aes)` to decrypt BITLK key material with appended tag and RFC3610-style CCM IV construction.

When AF_ALG is disabled, all kernel operations return `-ENOTSUP` or `-EINVAL` stubs.

## Dependencies and Coupling
Uses Linux `<linux/if_alg.h>`, sockets, control messages, and crypto backend memory helpers. Called by cipher checks, benchmarks, generic fallback cipher paths, and BITLK key decryption.

## Invariants and Risks
Input/output lengths must match exact AF_ALG send/read expectations. Algorithm names must fit fixed kernel sockaddr fields. Context file descriptors are reset in `crypt_cipher_destroy_kernel()`. AEAD and BITLK support are tightly coupled to kernel AF_ALG semantics.
