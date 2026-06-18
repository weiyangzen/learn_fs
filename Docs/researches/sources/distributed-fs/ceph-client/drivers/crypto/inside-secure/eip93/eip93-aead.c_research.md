# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-aead.c

## Purpose
Implements the EIP93 AEAD/authenc crypto API algorithms. It binds Linux `aead_request` operations for `authenc(hmac(...),cbc(...))` and `authenc(hmac(...),rfc3686(ctr(aes)))` families to the EIP93 descriptor path shared with skcipher code.

## Important APIs, Types, and Functions
The exported integration function is `eip93_aead_handle_result()`, called by `eip93-main.c` when a result descriptor with `EIP93_DESC_AEAD` and `EIP93_DESC_LAST` is consumed. Crypto API entry points are `eip93_aead_setkey()`, `eip93_aead_setauthsize()`, `eip93_aead_encrypt()`, and `eip93_aead_decrypt()`. Context is `struct eip93_crypto_ctx` from `eip93-cipher.h`; request state is `struct eip93_cipher_reqctx`.

`eip93_aead_setkey()` parses `crypto_authenc_keys`, validates DES/3DES/AES keys, strips RFC3686 nonce material when needed, programs the SA record with `eip93_set_sa_record()`, and precomputes HMAC inner/outer digests through `eip93_hmac_setkey()`. The file defines the registered `struct eip93_alg_template` instances for HMAC-MD5/SHA1/SHA224/SHA256 combined with CBC AES, RFC3686 AES, CBC DES, and CBC 3DES.

## Control Flow
Algorithm registration is performed indirectly by `eip93-main.c` through the global templates. At transform initialization, `eip93_aead_cra_init()` sets request size, copies template flags/type, stores the EIP93 device pointer, and allocates one SA record. Per request, encrypt/decrypt sets direction flags, verifies the request AAD length against the cached association length, maps the SA record, fills request context sizes and scatterlist pointers, and calls `eip93_aead_send_req()`. That validates scatterlists through `check_valid_request()` and forwards to `eip93_send_req()`.

Completion is reversed: `eip93_aead_handle_result()` unmaps request DMA, copies saved IV state through `eip93_handle_result()`, and completes the Linux AEAD request with the parsed hardware status.

## State and Persistence
Persistent transform state includes flags, block size, auth size, cached AAD length, RFC3686 nonce, and the allocated SA record. `ctx->set_assoc` causes the first request after setkey/init to program `HASH_CRYPT_OFFSET`; later requests must keep the same `assoclen`. Hardware-visible state is transient DMA mapping of the SA record plus per-request `sa_state` allocated by the common path. There is no filesystem or cross-boot persistence.

## Dependencies and Integration Points
Depends on Linux crypto AEAD/authenc helpers, AES/DES validation helpers, HMAC/hash support from `eip93-common.c`/`eip93-hash.c`, and descriptor submission from `eip93-common.c`. Templates are discovered by `eip93-main.c`, which registers only algorithms supported by hardware option bits.

## Risks
The cached AAD length means a transform rejects later requests whose AAD size differs, which is stricter than many software AEAD implementations. `eip93_aead_cra_exit()` unconditionally unmaps `ctx->sa_record_base`; if no successful request mapped it, this depends on DMA API tolerance for a zero/old DMA address. Direction bits are set on decrypt by mutating the shared SA record and are reset only by later `setkey()`/`eip93_set_sa_record()`, so encrypt-after-decrypt on the same transform deserves test attention. AEAD multi-segment requests commonly force bounce buffers in the common path.

## Test Signals
Exercise crypto self-tests for every registered authenc algorithm, including RFC3686 nonce sizing, authsize truncation, decrypt authentication failure mapping to `-EBADMSG`, mixed in-place/out-of-place scatterlists, unaligned AAD/payload, repeated requests with same AAD length, and a deliberate AAD length change on the same transform.
