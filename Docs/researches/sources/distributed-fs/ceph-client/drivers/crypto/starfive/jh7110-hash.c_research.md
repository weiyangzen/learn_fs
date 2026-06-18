# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-hash.c

## Purpose

This file implements the StarFive JH7110 HASH/HMAC acceleration side of the shared `jh7110-cryp` driver. It registers asynchronous ahash engine algorithms for SHA-224, SHA-256, SHA-384, SHA-512, SM3, and their HMAC variants, while using software ahash fallbacks for streaming `init`/`update`/`final`/`export`/`import` operations that the hardware path does not maintain incrementally.

## Important APIs, types, and functions

The code is built around `struct starfive_cryp_ctx`, `struct starfive_cryp_request_ctx`, and the shared device object from `jh7110-cryp.h`. Hardware access is through HASH registers such as `STARFIVE_HASH_SHACSR`, `SHAWDR`, `SHARDR`, `SHAWKR`, and `SHAWKLEN`, plus the shared algorithm FIFO and DMA length registers. `starfive_hash_wait_busy()`, `starfive_hash_wait_hmac_done()`, and `starfive_hash_wait_key_done()` poll hardware status bits. `starfive_hash_hmac_key()` loads the HMAC key into the hardware key FIFO. `starfive_hash_dma_init()` and `starfive_hash_dma_xfer()` configure and run memory-to-device DMA into the accelerator FIFO. `starfive_hash_one_request()` is the crypto-engine request body, and `starfive_hash_digest()` queues one-shot digest work to the engine. `starfive_hash_setkey()` stores short HMAC keys directly and hashes long HMAC keys through `starfive_hash_long_setkey()`.

The algorithm table `algs_sha2_sm3[]` exposes `sha224`, `sha256`, `sha384`, `sha512`, `sm3`, `hmac(sha224)`, `hmac(sha256)`, `hmac(sha384)`, `hmac(sha512)`, and `hmac(sm3)` with priority 200 and fallback-required flags. `starfive_hash_register_algs()` and `starfive_hash_unregister_algs()` are the integration points called by the parent StarFive crypto driver.

## Control flow, state, and persistence

Transform initialization finds a StarFive crypto device, allocates a named lib fallback (`sha256-lib`, `hmac-sha256-lib`, `sm3-lib`, and similar), sets ahash statesize from that fallback, and records whether the transform is HMAC plus the hardware hash mode. Streaming operations simply re-target a fallback request and delegate to the fallback implementation. One-shot `digest` clears the request context, records the source sg list, total length, block size, digest size, and request pointer in `cryp->req.hreq`, then transfers the request to the crypto engine.

For each hardware request, `starfive_hash_one_request()` resets the HASH unit, initializes `rctx->csr.hash.mode`, either loads the HMAC key or starts a normal hash, DMA-transfers each sg entry into the shared FIFO, sets the final bit, waits for completion, optionally waits for HMAC completion, reads digest words from `SHARDR`, and finalizes the ahash request. Runtime state is transient: per-transform key material and mode live in `struct starfive_cryp_ctx`, per-request scatterlist and size fields live in `struct starfive_cryp_request_ctx`, and the hardware register state is reset before each engine request. No file-backed or cross-boot state is persisted.

## Dependencies and integration points

The driver depends on the Linux crypto engine and ahash APIs, `crypto/internal/hash.h`, scatterwalk helpers, DMAengine slave transfers, completions, I/O polling, the shared StarFive crypto device and CSR bit definitions in `jh7110-cryp.h`, and parent driver resource setup for MMIO, physical FIFO address, DMA channel `tx`, and `dma_maxburst`. It integrates with the crypto API as async ahash algorithms and with the parent JH7110 crypto module through the exported register/unregister functions.

## Risks and test signals

The main risks are DMA mapping and alignment behavior, the direct assignment to `sg_dma_len(sg)` after programming the real hardware byte count, timeout paths that return before all engine-side state is naturally finalized, and long HMAC key handling that hashes via the driver's own registered algorithm names. The streaming API is intentionally fallback-backed, so test coverage must distinguish one-shot hardware digest from fallback streaming behavior. Useful signals are crypto selftests for every SHA2/SM3 and HMAC variant, comparison against software fallbacks for zero-length and multi-sg messages, HMAC keys shorter and longer than the block size, DMA timeout/error injection where possible, and module load/unload verifying algorithm registration cleanup.
