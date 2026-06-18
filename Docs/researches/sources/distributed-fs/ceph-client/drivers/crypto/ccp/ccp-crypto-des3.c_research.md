# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-des3.c

## Purpose

`ccp-crypto-des3.c` implements CCP-backed 3DES ECB and CBC skcipher algorithms for v5 hardware. It validates DES3 keys, builds DES3 CCP commands, updates CBC IVs on completion, and registers mode-specific skcipher algorithms.

## Important APIs, Types, And Functions

- `ccp_des3_complete()` copies updated IV back to the request for non-ECB modes.
- `ccp_des3_setkey()` uses `verify_skcipher_des3_key()`, sets type `CCP_DES3_TYPE_168`, records mode from algorithm metadata, stores key bytes, and initializes key SG.
- `ccp_des3_crypt()` validates key and block alignment, prepares IV SG for CBC, fills `CCP_ENGINE_DES3` command fields, and enqueues.
- `ccp_des3_init_tfm()` sets completion and DMA request size.
- `des3_algs[]` defines v5-only ECB and CBC registrations.
- `ccp_register_des3_algs()` version-gates and registers algorithms.

## Control Flow

At registration, each definition copies common defaults into an allocated wrapper, records mode, sets names/blocksize/ivsize, and registers with Crypto API. At runtime, setkey stores the mode chosen by that wrapper. Encrypt/decrypt calls share `ccp_des3_crypt()`, which rejects missing keys and invalid block lengths for ECB/CBC, optionally copies IV into request context, fills key/source/destination fields, and submits through `ccp_crypto_enqueue_request()`.

## State And Persistence Behavior

Transform state stores DES3 type/mode/key/key SG/key length. Request state stores IV buffer, IV SG, and command. Hardware-visible state is transient command queue and DMA SG references.

## Dependencies And Integration Points

This file depends on Crypto API skcipher, DES3 key verification, CCP shared crypto structures, `ccp_version()`, and the shared CCP enqueue path. It integrates with v5 operation code through `CCP_ENGINE_DES3`; v3 `ccp_actions` has no DES3 handler, so registration is v5-gated.

## Risks And Edge Cases

- Only 168-bit 3DES keys are supported; 112-bit behavior is intentionally left to callers making K1 equal K3.
- CBC/ECB reject non-block-aligned request lengths.
- DES3 is legacy crypto; deployments may disable it with the module parameter in `ccp-crypto-main.c`.

## Test Signals

Signals include DES3 ECB/CBC known-answer tests on v5 hardware, absence on v3, weak-key rejection, IV update correctness, unaligned length rejection, and `des3_disable` module parameter behavior.
