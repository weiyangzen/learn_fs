# sources/distributed-fs/ceph-client/crypto/xcbc.c

## Purpose
This file implements the `xcbc(...)` keyed-hash template for 16-byte block ciphers. It turns a child `crypto_cipher` into an XCBC-MAC shash instance.

## Important APIs, Types, And Functions
`struct xcbc_tfm_ctx` stores the spawned child cipher and two derived finalization constants. `crypto_xcbc_digest_setkey()` derives K1, K2, and K3 by encrypting fixed 0x01, 0x02, and 0x03 blocks, then rekeys the child with K1. `crypto_xcbc_digest_init()`, `crypto_xcbc_digest_update()`, and `crypto_xcbc_digest_finup()` implement CBC-MAC chaining and final block handling. `xcbc_create()` validates the shash template request and requires a 16-byte child block size.

## Control Flow
Initialization zeroes the previous-block state. Update XORs each full block into the state and encrypts it in place, returning any tail length to the block-only shash wrapper. Finalization XORs the supplied final bytes, applies `0x80` padding and K3 for a partial block or K2 for a full block, then encrypts once to produce the MAC.

## State, Dependencies, Integration, Risks, And Tests
Per-transform state is the child cipher and derived constants; per-request state is the previous block stored in `descsize`. It integrates through the CryptoAPI template registry and imports `CRYPTO_INTERNAL`. Risks include relying on block-only callers to avoid mid-stream partial updates, missing zeroization for derived stack key material, and incorrect child algorithms being rejected only by block size. Test signals include AES-XCBC known-answer vectors, exact-full-block versus partial-final tests, invalid child block size tests, and template lifecycle tests.
