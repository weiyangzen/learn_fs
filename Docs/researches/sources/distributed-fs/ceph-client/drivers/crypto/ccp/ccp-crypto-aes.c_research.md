# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes.c

## Purpose

`ccp-crypto-aes.c` implements standard AES skcipher offload for ECB, CBC, CTR, and RFC3686 CTR modes using the CCP AES engine. It validates keys and block sizes, stores key/nonce state, builds `struct ccp_cmd` requests, updates IVs on completion, and registers version-gated algorithms.

## Important APIs, Types, And Functions

- `ccp_aes_complete()` copies the updated IV from request context back to the request for non-ECB modes.
- `ccp_aes_setkey()` maps AES key lengths to CCP AES types, stores mode from the registered algorithm wrapper, copies key bytes, and initializes `key_sg`.
- `ccp_aes_crypt()` validates key, block alignment for ECB/CBC, IV presence for non-ECB, fills a `CCP_ENGINE_AES` command, and enqueues it.
- `ccp_aes_init_tfm()` sets completion and request size.
- `ccp_aes_rfc3686_setkey()` separates trailing nonce from key material.
- `ccp_aes_rfc3686_crypt()` constructs a full 16-byte RFC3686 counter block from nonce, per-request IV, and counter value 1, temporarily replaces `req->iv`, and delegates to `ccp_aes_crypt()`.
- `ccp_aes_rfc3686_complete()` restores the original IV pointer before normal completion handling.
- `ccp_register_aes_algs()` registers ECB/CBC/CTR/RFC3686 definitions when `ccp_version()` is sufficient.

## Control Flow

Registration allocates a `ccp_crypto_skcipher_alg` per mode, copies default skcipher ops, sets `ccp_alg->mode`, overrides names/blocksize/ivsize, and calls `crypto_register_skcipher()`. Runtime crypt operations use the algorithm wrapper to set `ctx->u.aes.mode` at key setup. Each request populates command engine, AES type/mode/action, key SG, IV SG when needed, source length, and destination. The shared queue handles async ordering and hardware dispatch.

## State And Persistence Behavior

Transform state stores AES mode/type, key bytes, key length, key SG, and RFC3686 nonce. Request state stores IV buffer, IV SG, optional original RFC3686 IV pointer, constructed counter block, and CCP command. No state is written outside kernel memory and hardware command queues.

## Dependencies And Integration Points

This file depends on Crypto API skcipher, AES/CTR constants, Linux scatterlists, `ccp-crypto.h`, `ccp_version()`, and `ccp_crypto_enqueue_request()`. It integrates with the lower operation layer through `CCP_ENGINE_AES` command fields.

## Risks And Edge Cases

- ECB and CBC reject non-block-multiple lengths; CTR modes allow byte granularity.
- RFC3686 temporarily mutates `req->iv`; completion must always restore it, including error paths through `ccp_aes_rfc3686_complete()`.
- `CRYPTO_ALG_NEED_FALLBACK` is set, but this file itself does not allocate a fallback transform for standard AES modes; fallback handling is left to the crypto stack/provider selection.
- Key material is stored in context and should be cleared by broader transform teardown if added in future.

## Test Signals

Signals include AES ECB/CBC/CTR/RFC3686 known-answer tests, invalid key lengths, CBC/ECB unaligned length rejection, IV update checks, RFC3686 nonce/counter construction, fragmented SG coverage, and v3 registration gating.
