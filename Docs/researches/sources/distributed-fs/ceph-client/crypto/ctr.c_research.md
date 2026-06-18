# sources/distributed-fs/ceph-client/crypto/ctr.c

## Purpose
`ctr.c` registers the `ctr` skcipher template and the `rfc3686` wrapper template. CTR turns a block cipher into a stream cipher by encrypting a counter block and XORing the keystream with input. RFC3686 adapts CTR for IPsec-style nonce/IV/counter layout and key format.

## Important APIs, Types, And Functions
- `crypto_ctr_crypt()` is both encrypt and decrypt for the base CTR template.
- `crypto_ctr_crypt_segment()`, `crypto_ctr_crypt_inplace()`, and `crypto_ctr_crypt_final()` handle out-of-place full blocks, in-place full blocks, and final partial blocks.
- `crypto_ctr_create()` allocates a simple skcipher instance, validates child block size, forces blocksize to 1, sets `chunksize`, and registers the instance.
- `struct crypto_rfc3686_ctx` stores the spawned child skcipher and the per-key nonce suffix.
- `crypto_rfc3686_setkey()` splits the last `CTR_RFC3686_NONCE_SIZE` bytes from the key as nonce and sets the remaining key on the child.
- `crypto_rfc3686_crypt()` builds the 16-byte RFC3686 counter block as nonce || request IV || big-endian 1 and forwards to child CTR encryption.
- `crypto_ctr_tmpls[]` registers `ctr` and `rfc3686`.

## Control Flow
The CTR walk starts with `skcipher_walk_virt()`. For each walk segment, it processes full blocks using the child's raw cipher encrypt function, increments the IV/counter with `crypto_inc()`, and returns any residual bytes to the skcipher walk. A trailing partial block is handled by encrypting one counter block into an aligned temporary keystream and XOR-copying only the remaining bytes.

The RFC3686 template is layered over an already-stream-like child, normally `ctr(aes)`. Setkey saves the nonce and forwards the key. Each request allocates an aligned subrequest context, synthesizes a fresh IV/counter block, and calls `crypto_skcipher_encrypt()` on the child for both encryption and decryption.

## State And Persistence
CTR state is request-local except for the child transform and, for RFC3686, the nonce saved in the transform context. The request IV is updated by the skcipher walk as the counter advances. No state is persisted outside the transform/request lifetime.

## Dependencies And Integration Points
The file depends on simple skcipher instance helpers, raw cipher APIs, `crypto_inc()`, and CTR constants from `<crypto/ctr.h>`. It is used by algorithms such as `ctr(aes)` and `rfc3686(ctr(aes))`, including AEAD compositions in testmgr such as `authenc(...,rfc3686(ctr(aes)))`.

## Risks And Edge Cases
CTR security depends on never reusing key/nonce/IV counter streams. The code enforces block size >= 4 and 4-byte alignment for `crypto_inc()`, and RFC3686 enforces a 16-byte IVsize child and stream-cipher blocksize. The implementation does not detect counter wrap or nonce reuse; callers and protocols must guarantee uniqueness. Partial blocks are allowed because CTR is registered as blocksize 1.

## Test Signals
`testmgr.h` contains CTR vectors for AES, DES, DES3, SM4, and other ciphers, plus RFC3686 AES/SM4 vectors. Useful tests cover in-place and out-of-place skcipher operation, non-block-multiple lengths, request splitting, and RFC3686 key suffix nonce parsing.
