# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-hcu-core.c

## Purpose
This file is the Crypto API/front-end driver for the Keem Bay OCS Hash Control Unit. It registers asynchronous hash and HMAC algorithms, manages request buffering and DMA-list preparation, chooses hardware versus software-assisted HMAC, and delegates register-level operations to `ocs-hcu.c`.

## Important APIs, Types, And Functions
- `struct ocs_hcu_ctx` stores the bound device, HMAC key, key length, and transform flags for SM3/HMAC.
- `struct ocs_hcu_rctx` stores request flags, algorithm, block/digest sizes, DMA list, intermediate hash context, a double-block buffer, SG cursor state, and DMA mapping metadata.
- Device lookup: `kmb_ocs_hcu_find_dev()` binds transforms to the single expected HCU device.
- Buffering: `kmb_get_total_data()` and `flush_sg_to_ocs_buffer()` manage block-aligned streaming hash state.
- DMA preparation/cleanup: `kmb_ocs_dma_prepare()` maps the request buffer and the processable part of the SG list into an OCS DMA list; `kmb_ocs_hcu_dma_cleanup()` unmaps and frees it.
- HMAC helpers: `prepare_ipad()` prepares software-assisted HMAC inner padding; `kmb_ocs_hcu_setkey()` stores short keys or hashes long keys using the corresponding OCS hash algorithm.
- Request execution: `kmb_ocs_hcu_do_one_request()` handles update, final/finup, hardware HMAC, and software-assisted OPAD finalization.
- Crypto API methods: `kmb_ocs_hcu_init()`, `update()`, `final()`, `finup()`, `digest()`, `export()`, and `import()`.
- Algorithm table: `ocs_hcu_algs[]` registers SHA256, SM3, SHA384, SHA512, their HMACs, and optional SHA224/HMAC-SHA224.
- Platform lifecycle: `kmb_ocs_hcu_probe()` configures DMA mask, maps registers, requests IRQ, starts the crypto engine, and registers ahashes; remove unregisters and exits.

## Control Flow
`init()` resets request state and selects the algorithm from digest size and transform flags. `update()` either buffers small data or queues a block-aligned DMA update. `final()`/`finup()` mark the request final and choose hardware HMAC if the entire HMAC can be processed in one final request with a hardware-supported key length; otherwise they use software-assisted HMAC. The engine callback maps data, calls `ocs_hcu_hash_update()`, `ocs_hcu_hash_finup()`, `ocs_hcu_hash_final()`, `ocs_hcu_digest()`, or `ocs_hcu_hmac()`, then finalizes the Crypto API request.

## State And Persistence
Transform state persists HMAC keys until tfm exit, where HMAC transforms clear the key. Request state, including intermediate digest and partial buffers, is exportable/importable through raw `struct ocs_hcu_rctx` copies. DMA mappings and OCS DMA lists are transient and cleaned after each engine operation. There is no disk persistence.

## Dependencies And Integration Points
This file depends on `ocs-hcu.h`, Crypto API ahash/engine helpers, SHA2/SM3/HMAC constants, DMA mapping, scatterlist copy helpers, platform resources, and OF matching on `intel,keembay-ocs-hcu`.

## Risks
- `export()`/`import()` memcpy the whole request context, including pointers and device references. This is a known pattern in some drivers but can be risky if imported across device lifetime changes.
- Hardware HMAC supports only nonzero final messages and key length <= 64; all other cases rely on software-assisted ipad/opad sequencing.
- `kmb_ocs_hcu_do_one_request()` returns errors directly in some paths instead of always finalizing through `crypto_finalize_hash_request()`, so engine error semantics should be verified.
- `ocs_hcu_digest()` in the low-level helper has an error path that can return before `dma_unmap_single()`, which this front end may expose through long-key hashing or SW HMAC OPAD digest.
- Buffer accounting is subtle because update requests process block-aligned data and retain remainders in `buffer`.

## Test Signals
- Ahash self-tests for SHA256, SM3, SHA384, SHA512, all HMAC variants, and optional SHA224.
- Streaming tests with one-byte updates, block-boundary updates, `final()` with no new data, `finup()`, `digest()`, and export/import.
- HMAC tests covering short key, exactly block-size key, long key hashing, zero-length message, and multi-update message.
- DMA API debug and fault-injection tests around DMA map/list allocation failures.
