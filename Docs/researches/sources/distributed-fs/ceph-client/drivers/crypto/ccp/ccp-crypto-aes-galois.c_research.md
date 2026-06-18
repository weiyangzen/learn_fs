# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-galois.c

## Purpose

`ccp-crypto-aes-galois.c` registers AES-GCM AEAD offload for CCP v5-capable hardware. It validates GCM keys and authentication tag sizes, builds the 16-byte GCM initial counter block, describes AAD and crypt text lengths to the CCP AES command, and registers `gcm(aes)` with the Crypto API.

## Important APIs, Types, And Functions

- `ccp_aes_gcm_complete()` currently just returns the hardware status.
- `ccp_aes_gcm_setkey()` validates AES key size, sets type/mode `CCP_AES_MODE_GCM`, stores the key, and initializes `key_sg`.
- `ccp_aes_gcm_setauthsize()` accepts tag sizes 16, 15, 14, 13, 12, 8, and 4.
- `ccp_aes_gcm_crypt()` validates key/mode/IV, builds `J0 = IV || 0x00000001`, fills a `CCP_ENGINE_AES` command with auth size, action, key, IV, source length, AAD length, and destination.
- `ccp_aes_gcm_encrypt()`/`ccp_aes_gcm_decrypt()` select action.
- `ccp_aes_gcm_cra_init()` sets completion and AEAD request DMA size.
- `ccp_register_aes_aeads()` registers version-gated AEAD definitions, currently `gcm(aes)` for CCP v5 and later.

## Control Flow

After setkey, each AEAD request copies the 12-byte nonce IV into a request-local 16-byte buffer, zeroes bytes 12-14, sets byte 15 to 1, and wraps that buffer in a scatterlist. The command treats `req->src` as AAD concatenated with plaintext/ciphertext and `req->dst` as ciphertext/plaintext plus tag, with `req->assoclen` identifying AAD length and `req->cryptlen` identifying crypt data/tag length as expected by the lower CCP operation layer.

Registration copies defaults into an allocated `ccp_crypto_aead`, overwrites algorithm names and blocksize, and calls `crypto_register_aead()` only if `ccp_version()` meets the version requirement.

## State And Persistence Behavior

Transform state stores AES type, mode, key length, key bytes, and key scatterlist. Request state stores IV buffer/scatterlist and `struct ccp_cmd` in `ccp_aes_req_ctx`. There is no additional persistent AEAD state beyond Crypto API transform lifetime.

## Dependencies And Integration Points

This file depends on Crypto API AEAD/GCM constants, AES constants, CCP shared crypto context/request structures, and the shared enqueue queue. It is linked into `ccp-crypto.o` and registered through `ccp-crypto-main.c`.

## Risks And Edge Cases

- GCM IV handling assumes the standard 96-bit IV path only; non-12-byte IV forms are not supported by the registered `ivsize`.
- The completion callback does not adjust output lengths or verify tags itself; correctness depends on lower CCP operation code.
- `def->mode` is set to `CCP_AES_MODE_GHASH` in the registration metadata while setkey uses `CCP_AES_MODE_GCM`; current metadata is not consumed by request construction but may confuse future refactors.
- AEAD source/destination layout assumptions must match the generic Crypto API GCM convention and CCP operation layer.

## Test Signals

Signals include AES-GCM known-answer encrypt/decrypt tests for all accepted tag sizes, authentication failure tests, fragmented AAD/data SGs, in-place and out-of-place buffers, rejection of unsupported tag/key sizes, and version gating on v3 versus v5 devices.
