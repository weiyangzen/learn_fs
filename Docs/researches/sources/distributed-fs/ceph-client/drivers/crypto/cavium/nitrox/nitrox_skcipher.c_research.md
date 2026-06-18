# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_skcipher.c

## Purpose

`nitrox_skcipher.c` registers and implements asynchronous skcipher algorithms backed by Nitrox SE firmware. It supports AES CBC/ECB/XTS/RFC3686 CTR/CTS-CBC and 3DES CBC/ECB, prepares firmware flexi crypto contexts, builds request-local SG layouts with IV and completion metadata, submits requests through `nitrox_process_se_request()`, and updates IVs on completion.

## Important APIs, Types, And Functions

- `struct nitrox_cipher` and `flexi_cipher_table[]` map Crypto API algorithm names to firmware `enum flexi_cipher` values.
- `nitrox_skcipher_init()` gets the first ready Nitrox device, allocates a DMA crypto context, stores a context handle, sets default callback, and extends request size by `struct nitrox_kcrypt_request`.
- `nitrox_cbc_init()` swaps in a CBC-specific callback for IV preservation.
- `nitrox_skcipher_exit()` zeroes key/auth context material, frees the crypto context, and drops the device reference.
- `nitrox_skcipher_setkey()`, `nitrox_aes_setkey()`, `nitrox_3des_setkey()`, `nitrox_aes_xts_setkey()`, and `nitrox_aes_ctr_rfc3686_setkey()` validate and store key/context data.
- `alloc_src_sglist()` and `alloc_dst_sglist()` build synthetic source/destination SG lists using helpers from `nitrox_req.h`.
- `nitrox_skcipher_crypt()` fills `se_crypto_request` opcode, GP header offsets, context handle, and submits the request.
- `nitrox_cbc_decrypt()` preserves the previous ciphertext block for in-place CBC decrypt IV update.
- `nitrox_register_skciphers()`/`nitrox_unregister_skciphers()` register/unregister the algorithm array.

## Control Flow

When a transform is created, init obtains a ready PF device and allocates a firmware context. `setkey` chooses a firmware cipher type from the algorithm name, fills flexi context flags, stores AES key length encoding, sets IV source to input data, converts flags to big endian, and copies key material. XTS additionally copies key2 into the auth key area; RFC3686 stores the nonce in `fctx->crypto.iv` and then stores the AES key.

Encryption/decryption calls `nitrox_skcipher_crypt()`. It sets request allocation flags from Crypto API sleep flags, opcode `FLEXI_CRYPTO_ENCRYPT_HMAC`, encrypt/decrypt arg, GP header data length and encryption offset, context length, then allocates source and destination request buffers. It submits through `nitrox_process_se_request()` and returns the async status.

Completion frees source/destination SG buffers, converts nonzero firmware status to `-EINVAL`, and completes the Crypto API request. CBC completion additionally updates `skreq->iv`: encrypt uses the final destination block; out-of-place decrypt uses the final source block; in-place decrypt uses a saved copy from before submission.

## State And Persistence Behavior

Transform state contains a `nitrox_crypto_ctx`, device reference, DMA context header, firmware context flags, and key material. Request state contains `nitrox_kcrypt_request`, allocated synthetic SG arrays, and optional saved CBC IV block. Device request state persists in the request manager until hardware completion. Key material is explicitly zeroed during transform exit.

## Dependencies And Integration Points

This file depends on Linux Crypto API skcipher, AES, DES3 verification, XTS verification, CTR RFC3686 constants, scatterwalk, Nitrox common/device/request headers, and `nitrox_process_se_request()`. It is registered by the higher Nitrox crypto registration layer called from `nitrox_main.c`.

## Risks And Edge Cases

- ECB algorithms still declare an IV size equal to the block size in this file, and request construction always prepends IV data; this matches firmware input expectations but differs from common ECB API intuition.
- CBC decrypt with `cryptlen < ivsize` computes an unsigned underflow for the IV-copy offset; blocksize enforcement by the Crypto API should prevent this but local checks are limited.
- `nitrox_skcipher_setkey()` chooses firmware cipher by name string; driver-name changes must keep names synchronized.
- RFC3686 nonce is stored in context, while per-request IV is still placed in request data; incorrect firmware interpretation would break counter construction.
- `crypto_skcipher_set_reqsize(tfm, existing + sizeof(...))` assumes any previous reqsize should be preserved.

## Test Signals

Use skcipher known-answer tests for AES CBC/ECB/XTS/RFC3686 CTR/CTS and 3DES CBC/ECB, in-place and out-of-place CBC decrypt IV update tests, invalid AES/3DES/XTS key tests, fragmented SG tests, async backlog tests, request allocation under atomic flags, and key zeroization checks under memory debugging.
