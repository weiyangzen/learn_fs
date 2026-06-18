# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto.h

## Purpose

`ccp-crypto.h` is the shared internal header for CCP Crypto API providers. It defines algorithm wrapper types, per-transform contexts, per-request contexts, export/import state layouts, common priorities, helper accessors, and provider registration prototypes.

## Important APIs, Types, And Functions

- `CCP_CRA_PRIORITY` sets Crypto API priority 300.
- `struct ccp_crypto_skcipher_alg`, `ccp_crypto_aead`, `ccp_crypto_ahash_alg`, and `ccp_crypto_akcipher_alg` wrap registered Crypto API algorithms with list entries and CCP metadata.
- `ccp_crypto_skcipher_alg()` and `ccp_crypto_ahash_alg()` recover wrappers from Crypto API transform/algorithm pointers.
- `struct ccp_aes_ctx` stores AES mode/type/key, nonce, fallback XTS tfm, and CMAC subkeys.
- `struct ccp_aes_req_ctx` stores IV/tag buffers, RFC3686 state, command, and embedded fallback skcipher request.
- `struct ccp_aes_cmac_req_ctx` and `ccp_aes_cmac_exp_ctx` store CMAC streaming/export state.
- `struct ccp_des3_ctx`/`ccp_des3_req_ctx`, `struct ccp_sha_ctx`/`ccp_sha_req_ctx`/`ccp_sha_exp_ctx`, and `struct ccp_rsa_ctx`/`ccp_rsa_req_ctx` define family-specific state.
- `struct ccp_ctx` is the common transform context with a completion hook and a union of algorithm family contexts.
- Function prototypes expose shared enqueue, SG table helper, and family registration functions.

## Control Flow

There is no executable control flow except small accessors. Provider files include this header, allocate `struct ccp_ctx` as transform context, set the `complete` function during transform init, and place a `struct ccp_cmd` in each request context before calling `ccp_crypto_enqueue_request()`.

## State And Persistence Behavior

The header defines all long-lived crypto transform state for keys, HMAC pads, fallback transforms, and RSA key buffers, plus request-scoped state for IVs, hash buffers, temporary SG tables, and commands. It also defines export/import state for SHA and CMAC so partial hash operations can persist across Crypto API export/import calls.

## Dependencies And Integration Points

It depends on Linux lists/wait queues, `linux/ccp.h` command definitions, Crypto API headers for AES/AEAD/hash/SHA/RSA/skcipher, and provider files in the same module. It is the type contract between `ccp-crypto-main.c` and every algorithm implementation.

## Risks And Edge Cases

- `struct ccp_aes_req_ctx` keeps `skcipher_request fallback_req` at the end; XTS init sizes request memory to append fallback request private data after it.
- Context structs store sensitive key material; provider exit paths must clear or free sensitive data appropriately.
- Wrapper recovery helpers depend on Crypto API internal container layout and must match the algorithm type.
- DMA padding in `cra_ctxsize`/request sizing must stay consistent with `*_ctx_dma()` accessors.

## Test Signals

Compile coverage across all provider files is the primary signal. Runtime signals include no DMA alignment warnings, correct request-size handling for XTS fallback, export/import state compatibility, and memory-sanitizer checks for context/request overrun.
