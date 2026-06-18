# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-sha.c

## Purpose

`ccp-crypto-sha.c` implements CCP-backed asynchronous SHA and HMAC-SHA hash algorithms. It handles streaming buffering, first/final flags, message bit counts, HMAC ipad/opad setup, export/import state, version-gated registration of SHA1/SHA224/SHA256/SHA384/SHA512, and paired HMAC registrations.

## Important APIs, Types, And Functions

- `ccp_sha_complete()` saves remainder data after non-final updates, copies final digest, and frees temporary SG tables.
- `ccp_do_sha_update()` is the shared update/final/finup path. It combines buffered and new data, keeps one block for later non-final operations when needed, updates `msg_bits`, fills a `CCP_ENGINE_SHA` command, and enqueues it.
- `ccp_sha_init()`, `update()`, `final()`, `finup()`, and `digest()` implement ahash operations.
- `ccp_sha_export()`/`ccp_sha_import()` serialize/restore hash type, bit count, first flag, context, and buffered data.
- `ccp_sha_setkey()` implements HMAC key handling: hash oversized keys with a child shash, zero-pad, and compute ipad/opad.
- `ccp_sha_cra_init()` and `ccp_hmac_sha_cra_init()` initialize plain and HMAC transforms; HMAC allocates the child shash named in `child_alg`.
- `ccp_register_sha_alg()` registers each SHA and then its HMAC wrapper.
- `ccp_register_sha_algs()` version-gates algorithms: SHA1/SHA224/SHA256 on v3+, SHA384/SHA512 on v5+.

## Control Flow

Plain SHA init clears request state, sets the type from algorithm metadata, and marks first block. HMAC init additionally preloads the request buffer with ipad for the first update when a key is set. Updates that do not exceed one block and are not final are buffered. Otherwise, the code builds either a combined SG table of prior buffer plus new SG data or uses a single buffer/request SG, computes the count to send, updates total bits, fills context SG and SHA command fields, and submits. Completion copies the digest when final and saves any remainder for streaming.

Registration allocates an algorithm wrapper for each version-supported SHA. After registering the plain hash, it clones the base wrapper, adds `setkey`, changes names to `hmac(<sha>)`, sets HMAC init/exit, and registers the HMAC ahash.

## State And Persistence Behavior

Transform state stores HMAC key length, key/ipad/opad blocks, opad SG/count, and optional child shash. Request state stores hash type, total bits, first/final flags, source/nbytes, hash counts, temporary SG table, hardware context buffer, partial block buffer, and command. Export/import preserves enough state for suspend/resume of hash operations.

## Dependencies And Integration Points

This file depends on Crypto API ahash/HMAC/shash helpers, SHA constants, scatterwalk, `ccp_crypto_sg_table_add()`, and `ccp_crypto_enqueue_request()`. It integrates with v3/v5 SHA hardware operations and Crypto API fallback selection.

## Risks And Edge Cases

- `msg_bits` is incremented before hardware completion; if a command fails, request state is already advanced.
- HMAC relies on a child software shash for oversized key hashing; missing child algorithm causes HMAC transform init failure.
- The "keep one block" behavior for non-final exact-block updates is required because CCP cannot do zero-length final; regressions affect streaming hashes.
- Temporary SG table allocation depends on request sleep flags and must be freed exactly once.

## Test Signals

Signals include SHA and HMAC known-answer tests for all registered variants, streaming update/final/finup/digest combinations, export/import resume, oversized HMAC keys, exact-block and empty-message cases, v3/v5 version gating, and allocation failure/error unwinding.
