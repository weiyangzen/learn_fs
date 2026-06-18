# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/eip93-cipher.c

## Purpose
Implements EIP93 skcipher support for AES, DES, and 3DES in ECB/CBC/CTR/RFC3686 modes. It is the non-AEAD symmetric cipher frontend to the shared EIP93 descriptor machinery.

## Important APIs, Types, and Functions
The result callback `eip93_skcipher_handle_result()` is exported for `eip93-main.c`. Crypto API callbacks include `eip93_skcipher_cra_init()`, `eip93_skcipher_cra_exit()`, `eip93_skcipher_setkey()`, `eip93_skcipher_encrypt()`, and `eip93_skcipher_decrypt()`. Algorithm templates are defined for `ecb(aes)`, `cbc(aes)`, `ctr(aes)`, `rfc3686(ctr(aes))`, `ecb/cbc(des)`, and `ecb/cbc(des3_ede)`.

## Control Flow
Transform initialization allocates one SA record and stores the EIP93 device pointer/type. `setkey()` validates the key using crypto library helpers, extracts an RFC3686 nonce when applicable, programs `sa_cmd` words through `eip93_set_sa_record()`, and copies the key into the SA record. Encrypt/decrypt sets request flags, with decrypt also setting `EIP93_SA_CMD_DIRECTION_IN` in the SA record. `eip93_skcipher_crypt()` rejects zero length as a no-op, enforces block alignment for ECB/CBC, maps the SA record, fills the request context, and submits through `eip93_skcipher_send_req()` and `eip93_send_req()`.

## State and Persistence
Persistent transform state is the allocated SA record, block size, RFC3686 nonce, type, and EIP93 pointer. Per-request state is `struct eip93_cipher_reqctx`, including scatterlists, DMA addresses, descriptor flags, IV size, and per-request SA state allocated in the common layer. No state survives transform destruction.

## Dependencies and Integration Points
Depends on Linux AES/DES validation helpers, DMA mapping, `eip93-common.c` for SA record generation and request submission, and `eip93-main.c` for registration/completion. AES templates use `CRYPTO_ALG_NEED_FALLBACK` and kernel-driver-only flags for AES modes.

## Risks
Like AEAD, `cra_exit()` unmaps the last SA record DMA address unconditionally. Decrypt mutates the shared SA record direction bit, so encrypting later with the same transform may rely on setkey or fresh SA setup to clear it. CTR mode handles non-block-size lengths, but ECB/CBC reject unaligned sizes. Descriptor submission busy-waits in the common path if the ring is full.

## Test Signals
Run AES/DES/3DES known-answer tests for encrypt/decrypt, RFC3686 nonce handling, zero-length no-op, CBC/ECB unaligned length rejection, CTR partial-block operation, and repeated encrypt/decrypt ordering on a single transform.
