# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss-hash.c

## Purpose

`sun8i-ss-hash.c` accelerates one-shot MD5/SHA1/SHA224/SHA256 and HMAC-SHA1 on A83T Security System hardware, while forwarding streaming ahash operations and unsupported request layouts to fallback implementations.

## Important APIs, Types, And Functions

Key functions are `sun8i_ss_hash_init_tfm()`, `sun8i_ss_hash_exit_tfm()`, `sun8i_ss_hmac_setkey()`, `sun8i_ss_hashkey()`, `sun8i_ss_hash_need_fallback()`, `sun8i_ss_hash_digest()`, `hash_pad()`, `sun8i_ss_run_hash_task()`, and `sun8i_ss_hash_run()`. TFM state stores fallback ahash, device pointer, HMAC ipad/opad, and normalized key.

## Control Flow

TFM init allocates fallback ahash, sets state/request sizes, records fallback name, and resumes the device. Streaming callbacks configure and call fallback. One-shot digest rejects zero length, too-large requests for the fixed pad buffer, too many SGs, non-final partial blocks, unaligned offsets, and non-word SG lengths. The engine callback maps source SGs, maps a per-flow result buffer, copies the final partial block into the flow pad buffer, appends MD/SHA padding, and runs the hardware. For HMAC, it first shifts SG entries to prepend `ipad`, runs the inner digest, then retries with `opad || inner_digest`.

## State And Persistence Behavior

Request state contains source/destination descriptor arrays, selected method, flow, and fallback request. Per-flow pad and result buffers are reused. HMAC key material persists in TFM context until exit and is freed with sensitive cleanup for pads. Hardware hash state is passed between multi-SG chunks by using the previous result as key/IV and setting continuation bit `BIT(17)`.

## Dependencies And Integration Points

It depends on core flow buffers, `sun8i_ss_run_hash_task()`, CryptoAPI ahash/HMAC helpers, SHA/MD5 constants, scatterwalk, DMA mapping, and runtime PM acquired at TFM lifetime. It registers through hash templates in `sun8i-ss-core.c`.

## Risks And Test Signals

Risks include `sg_nents()` not bounded by request length, fixed 4096-byte pad buffer limits, HMAC allocation leaks on repeated setkey, digest-size normalization for SHA224, and complex map/unmap retry flow for HMAC. Test hash vectors, HMAC-SHA1 vectors with long keys, final partial block handling, maximum accepted length, fallback counters, DMA map failure paths, and multi-SG continuation.
