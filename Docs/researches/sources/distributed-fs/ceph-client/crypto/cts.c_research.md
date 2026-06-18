# sources/distributed-fs/ceph-client/crypto/cts.c

## Purpose
`cts.c` implements the `cts` skcipher template for CBC ciphertext stealing as described by RFC2040 and used by RFC3962. It permits CBC-like encryption of messages that are at least one block but not necessarily a multiple of the block size, without expanding ciphertext length.

## Important APIs, Types, And Functions
- `struct crypto_cts_ctx` holds the spawned CBC child skcipher.
- `struct crypto_cts_reqctx` stores temporary scatterlists, the final-block offset, and the embedded child request.
- `crypto_cts_encrypt()` and `crypto_cts_decrypt()` are the public skcipher operations.
- `cts_cbc_encrypt()` performs the stealing transform after the prefix CBC operation.
- `cts_cbc_decrypt()` reconstructs the penultimate ciphertext block, recovers the final partial plaintext, and decrypts the final full block.
- `crypto_cts_init_tfm()` computes request size for child request context plus aligned scratch block space.
- `crypto_cts_create()` only accepts child algorithms whose name begins with `cbc(` and whose IV size equals block size.

## Control Flow
Encryption rejects messages smaller than one block. A one-block message is delegated directly to the CBC child. Longer messages first encrypt the prefix through the last full block boundary before the partial tail. Completion continues in `cts_cbc_encrypt()`, which reads the last encrypted full block, overlays the partial plaintext, writes the stolen ciphertext layout, and encrypts the adjusted final full block in place.

Decryption also delegates exact one-block requests. For longer inputs, it saves the IV or previous ciphertext block into aligned scratch, decrypts the full-block prefix, and then `cts_cbc_decrypt()` uses the saved block and partial tail to reconstruct and decrypt the penultimate block. Async child completions are bridged through `crypto_cts_encrypt_done()`, `crypto_cts_decrypt_done()`, and `cts_cbc_crypt_done()`.

## State And Persistence
The transform context owns the child skcipher. Request-local state includes final offset, temporary scatterlist, embedded request, and aligned scratch for the saved block. Sensitive stack buffer `d` is wiped with `memzero_explicit()`.

## Dependencies And Integration Points
The template wraps CBC skciphers and uses scatterwalk helpers for offsets and partial block copies. It integrates with the crypto template registry as `cts(...)`, and testmgr lists `cts(cbc(aes))`, `cts(cbc(paes))`, and `cts(cbc(sm4))` style entries.

## Risks And Edge Cases
The implementation is careful about the one-block case and rejects sub-block messages. The stealing logic is scatterlist-sensitive and depends on correct `offset = rounddown(nbytes - 1, bsize)`. Bugs here tend to appear only with partial tails, in-place requests, split scatterlists, or async child completion. The template assumes a CBC child; non-CBC names are rejected by prefix check rather than deeper semantic validation.

## Test Signals
`testmgr.h` includes `cts_mode_tv_template` and SM4 CTS vectors. High-value tests include exact block length, one byte over a block, multiple blocks plus partial tail, in-place/out-of-place operation, fragmented scatterlists, and async child behavior.
