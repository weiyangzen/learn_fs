# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-hash.c

## Purpose

`aspeed-hace-hash.c` implements the hash half of Aspeed HACE. It exposes asynchronous SHA1, SHA224, and SHA256 on all supported HACE devices, plus SHA384 and SHA512 on AST2600, using hardware accumulation mode and software fallback for cases the hardware path cannot prepare. It manually tracks SHA byte counts and padding, because requests can arrive as streaming updates and finup/digest operations.

## Important APIs, Types, And Functions

Important state is `struct aspeed_sham_ctx`, `struct aspeed_sham_reqctx`, and `struct aspeed_engine_hash`. `aspeed_sham_init()`, `update()`, `finup()`, `digest()`, `export()`, and `import()` implement ahash callbacks. `aspeed_ahash_dma_prepare()` builds a linear DMA buffer for AST2500, while `aspeed_ahash_dma_prepare_sg()` builds AST2600 source SG descriptors and optional padding buffer descriptors. `aspeed_hace_ahash_trigger()` writes source, digest, key-buffer, length, and command registers. `aspeed_ahash_fallback()` replays the remaining request through a software ahash if hardware setup fails.

## Control Flow

Initialization selects algorithm flags, digest size, block size, IV size, and initial digest constants. Update/finup records the source sg, total length, offset, and final flag, then queues the request on the hash crypto engine. The engine prepare step selects linear or SG DMA preparation by SoC version. Hardware completion unmaps DMA state, decides whether another chunk is required, and either loops back into `aspeed_ahash_req_update()` or copies the final digest to `req->result` and finalizes the request. AST2600 SG mode appends a separate padding buffer for final blocks and marks the last SG descriptor with `HASH_SG_LAST_LIST`.

## State And Persistence Behavior

Request context preserves digest words, 128-bit byte count, source walk position, command bits, final flag, and DMA addresses. Export/import serializes digest plus byte count so the crypto API can suspend/resume partial hashes. The device hash engine stores one active request, coherent source/descriptor buffer, active DMA addresses/lengths, callbacks, and busy flag. Digest DMA is mapped bidirectionally for each hardware round and unmapped before continuing or finalizing.

## Dependencies And Integration Points

The file depends on `aspeed-hace.h`, crypto ahash and crypto-engine APIs, SHA constants, `memcpy_from_sglist()`, scatterwalk fallback, DMA mapping, and HACE hash registers. It is registered by the parent HACE platform driver and version-gates SHA384/SHA512 and SG mode to AST2600.

## Risks And Test Signals

Risks include padding/count mistakes for SHA512-family two-word lengths, final SG descriptor indexing when zero or truncated SG entries occur, digest DMA lifetime across multi-chunk requests, fallback import/export compatibility, and registration failure only being logged. Test with crypto selftests for all advertised digests, streaming update/final/export/import, short and exact-block messages, very large messages crossing chunk limits, fragmented sg lists, AST2500 linear and AST2600 SG paths, and injected DMA mapping failures.
