<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cmac.c -->
# sources/distributed-fs/ceph-client/crypto/cmac.c

## Purpose

`cmac.c` implements the CMAC keyed hash template over block ciphers with 8- or 16-byte block sizes. It registers `cmac(cipher)` shash instances.

## Important APIs, Types, and Flow

`struct cmac_tfm_ctx` stores a child `crypto_cipher` and two derived subkeys immediately after the context. `crypto_cmac_digest_setkey()` sets the child cipher key, encrypts a zero block, then derives K1 and K2 by finite-field doubling with reduction constants `0x87` for 128-bit blocks and `0x1B` for 64-bit blocks. `crypto_cmac_digest_init()` zeros the chaining block. `update()` XORs and encrypts complete blocks, returning leftover length. `finup()` handles the final block: complete blocks use K1, incomplete blocks apply `0x80` padding and use K2, then one final cipher encryption produces the tag.

`cmac_create()` validates child block size, sets block-only/final-nonzero flags, installs shash callbacks, supports tfm clone by cloning the child cipher, and registers the instance.

## State, Dependencies, and Integration

Tfm state is child cipher plus CMAC subkeys; descriptor state is the current chaining block. Dependencies include internal cipher/hash APIs, `crypto_xor()`, and `crypto_cipher_encrypt_one()`. It integrates with any caller requesting `cmac(<cipher>)`.

## Risks and Test Signals

Risks include subkey endian/doubling logic, partial-final semantics, block-only update behavior, clone lifetime, and child cipher key propagation. Test signals are CMAC known-answer vectors for AES and 64-bit ciphers, exact-block versus partial-block finalization, invalid child block size rejection, clone consistency, and setkey error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cmac.c -->
