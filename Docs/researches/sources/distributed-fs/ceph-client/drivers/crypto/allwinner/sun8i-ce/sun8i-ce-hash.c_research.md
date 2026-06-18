# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-hash.c

## Purpose

`sun8i-ce-hash.c` implements one-shot hardware acceleration for MD5, SHA1, SHA224, SHA256, SHA384, and SHA512 on the Allwinner CE while delegating streaming `init/update/final/finup/export/import` and unsupported request shapes to fallback ahash implementations.

## Important APIs, Types, And Functions

Key entry points are `sun8i_ce_hash_init_tfm()`, `sun8i_ce_hash_exit_tfm()`, `sun8i_ce_hash_init()`, `sun8i_ce_hash_update()`, `sun8i_ce_hash_final()`, `sun8i_ce_hash_finup()`, `sun8i_ce_hash_digest()`, and `sun8i_ce_hash_run()`. Hardware preparation is split across `sun8i_ce_hash_need_fallback()`, `hash_pad()`, `sun8i_ce_hash_prepare()`, and `sun8i_ce_hash_unprepare()`. The request context stores fallback request storage, selected flow, mapped SG count, result/pad DMA addresses, aligned result buffer, and two-block padding buffer.

## Control Flow

TFM init allocates a fallback ahash with `CRYPTO_ALG_NEED_FALLBACK`, mirrors its state size, sets request size with DMA padding, records debug fallback name, and holds a runtime PM reference. `digest()` rejects zero-length, too-many-SG, unaligned, or non-word-length source requests to fallback; otherwise it selects a CE flow and queues the request to that flow's `crypto_engine`. The engine callback maps source SGs, maps an internal result buffer, builds software MD/SHA padding as an extra source segment, fills `ce_task` source/destination descriptors and length units, runs `sun8i_ce_run_task()`, unmaps DMA resources, copies the digest to `areq->result`, and finalizes the hash request.

## State And Persistence Behavior

The hardware path is stateless per digest request except for flow selection and per-request DMA mappings. Streaming hash state is entirely owned by the fallback ahash. Runtime PM lifetime is tied to hash TFM allocation, not individual digest operations. Debug builds accumulate request and fallback counters in the shared algorithm template.

## Dependencies And Integration Points

This file depends on the CE core for variant algorithm IDs, length-unit quirks, flow engines, descriptor address conversion, and task execution. It uses Linux ahash internals, scatterlists, DMA mapping, SHA/MD5 constants, and local bottom-half disabling around CryptoAPI completion.

## Risks And Test Signals

Risks include padding overflow, SHA224/SHA384 digest-size normalization errors, incorrect bit-vs-word `t_dlen` on H6-like variants, insufficient fallback for malformed SGs, DMA map/unmap imbalance, and assumptions that all source SG lengths are word multiples. Test zero-length and misaligned fallback, all digest algorithms and sizes, multi-SG boundaries near padding-block transitions, H6 length-bit behavior, runtime PM TFM lifetime, and CryptoAPI hash selftests.
