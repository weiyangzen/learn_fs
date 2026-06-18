# sources/distributed-fs/ceph-client/crypto/xts.c

## Purpose
This file implements the `xts(...)` skcipher template for IEEE 1619 XTS mode. It composes an ECB-capable data cipher with a raw block cipher for tweak generation.

## Important APIs, Types, And Functions
`struct xts_tfm_ctx` stores the child skcipher and tweak cipher. `xts_setkey()` verifies and splits the key into data and tweak halves. `xts_xor_tweak_pre()` and `xts_xor_tweak_post()` apply GF(2^128) tweak masks before and after child encryption/decryption. `xts_cts_final()` handles ciphertext stealing for non-block-multiple lengths. `xts_create()` handles template instantiation, including legacy `ecb(...)` name mangling and tweak cipher lookup.

## Control Flow
Each request encrypts the IV with the tweak key to get `T`, XORs each block with successive `T` values, runs the ECB child over all full blocks, then XORs tweaks again. If there is a partial final block, the code stops near the last two blocks and performs ciphertext stealing through a temporary two-block scatterlist view and a subrequest. Async child completions resume in `xts_encrypt_done()` or `xts_decrypt_done()`.

## State, Dependencies, Integration, Risks, And Tests
Persistent transform state is two spawned cipher handles; per-request state includes the current tweak, tail scatterlist, and embedded subrequest. Dependencies include `xts_verify_key()`, GF128 helpers, scatterwalk, DRM-independent CryptoAPI skcipher infrastructure, and the `ecb` template soft dependency. Risks include CTS corner cases, async completion ordering, key-half validation, alignment requirements, and name-mangling behavior. Test signals are XTS-AES known-answer vectors, partial-sector ciphertext-stealing vectors, async child tests, minimum-length rejection, and same-key-half rejection.
