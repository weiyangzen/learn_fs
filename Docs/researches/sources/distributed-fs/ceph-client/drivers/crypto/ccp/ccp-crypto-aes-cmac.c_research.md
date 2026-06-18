# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-cmac.c

## Purpose

`ccp-crypto-aes-cmac.c` implements the Crypto API `cmac(aes)` asynchronous hash algorithm using CCP AES-CMAC hardware support. It manages CMAC buffering, final-block padding, K1/K2 subkey generation, export/import state, and command submission through the shared CCP crypto queue.

## Important APIs, Types, And Functions

- `ccp_aes_cmac_complete()` handles hardware completion, preserves leftover data for non-final updates, copies final digest, and frees the temporary SG table.
- `ccp_do_cmac_update()` is the main update/final/finup path. It builds a composite SG table from buffered data, request data, and padding, selects K1 or K2 for final blocks, and submits an AES CMAC command.
- `ccp_aes_cmac_init()`, `update()`, `final()`, `finup()`, and `digest()` implement the ahash operation set.
- `ccp_aes_cmac_export()`/`ccp_aes_cmac_import()` serialize and restore partial CMAC state.
- `ccp_aes_cmac_setkey()` validates AES key length, computes K1/K2 by AES-encrypting zero and doubling in GF(2^128), stores the supplied key, and initializes SGs.
- `ccp_aes_cmac_cra_init()` sets completion handler and DMA request size.
- `ccp_register_aes_cmac_algs()` allocates/registers the `cmac(aes)` ahash algorithm.

## Control Flow

Init clears the request context and marks a null message. Updates that are not final and do not exceed one block are buffered locally. Otherwise, the code computes the number of full bytes to hash and the remainder to retain. For final operations, it pads null or partial blocks with `0x80` followed by zeroes, chooses K2 if padded or K1 if complete, and includes that subkey in the CCP command. Completion saves any remainder for later updates or copies the digest from the IV/context buffer when final.

`setkey()` derives CMAC subkeys synchronously using the software AES helper, then stores the actual AES key for CCP hardware commands. Registration creates an async ahash with `CRYPTO_ALG_NEED_FALLBACK`, DMA padding, priority 300, 16-byte digest, and export state size.

## State And Persistence Behavior

Transform state stores AES type/mode/key, K1/K2 and SG wrappers. Request state stores null/final flags, source/nbytes, hash counts, temporary SG table, IV/output buffer, buffered partial block, padding block, and `struct ccp_cmd`. Export/import persists null flag, IV, buffered count, and buffered block.

## Dependencies And Integration Points

This file depends on Crypto API ahash, AES software helpers for subkey generation, scatterwalk, `ccp_crypto_sg_table_add()`, and `ccp_crypto_enqueue_request()`. It is registered by `ccp_register_algs()` when AES offload is enabled.

## Risks And Edge Cases

- The temporary SG table must be freed on every completion/error path; missing callback would leak it.
- CMAC final padding and K1/K2 selection are security-sensitive and easy to regress for null or exact-block messages.
- `ccp_do_cmac_update()` keeps one block buffered for non-final exact-block updates because the hardware cannot do a zero-length final; this behavior must stay aligned with Crypto API streaming semantics.
- `ctx->u.aes.key_len` remains zero until subkeys and key are fully initialized, preventing use of partial key state.

## Test Signals

Use CMAC known-answer tests for AES-128/192/256, empty message, one-block, partial-block, multi-update, finup/digest paths, export/import resume, non-sleeping allocation paths, and error unwinding for SG allocation failure.
