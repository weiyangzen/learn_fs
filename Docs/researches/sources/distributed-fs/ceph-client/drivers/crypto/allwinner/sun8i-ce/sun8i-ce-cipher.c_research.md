<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-cipher.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-cipher.c

## Purpose

`sun8i-ce-cipher.c` implements skcipher support for the Allwinner sun8i Crypto Engine. It prepares DMA task descriptors for AES and 3DES cipher requests, queues work through `crypto_engine`, and falls back to software for requests the hardware cannot safely process.

## Important APIs, Types, And Functions

`sun8i_ce_cipher_need_fallback()` enforces hardware constraints. `sun8i_ce_cipher_fallback()` dispatches to a fallback skcipher. `sun8i_ce_cipher_prepare()` maps keys, IVs, and scatterlists and fills a `struct ce_task`. `sun8i_ce_cipher_unprepare()` unmaps DMA and updates CBC IVs. `sun8i_ce_cipher_do_one()` runs a task and finalizes the engine request. Public request callbacks are `sun8i_ce_skencrypt()` and `sun8i_ce_skdecrypt()`. TFM/key APIs are `sun8i_ce_cipher_init()`, `sun8i_ce_cipher_exit()`, `sun8i_ce_aes_setkey()`, and `sun8i_ce_des3_setkey()`.

## Control Flow

Encrypt/decrypt sets request direction, checks fallback gates for SG count, crypt length, IV size, zero length, 16-byte multiple, and 32-bit SG alignment, then selects a CE flow and transfers the request to that flow's crypto engine. The worker fills task control fields from variant algorithm and block-mode tables, maps key/IV/SGs, runs `sun8i_ce_run_task()`, unmaps everything, updates IV state, and completes the skcipher request.

## State And Persistence Behavior

TFM context stores a DMA-friendly key buffer, key length, CE device, and fallback TFM. Request context stores direction, flow, DMA addresses, mapped SG counts, bounce IV, backup IV, and embedded fallback request. Runtime PM is held for the TFM lifetime and released on exit.

## Dependencies And Integration Points

It depends on crypto_engine, skcipher API, DMA mapping, scatterwalk IV handling, DES3 key verification, runtime PM, CE variant descriptors and helpers from `sun8i-ce.h`, and core functions that allocate flows and submit tasks.

## Risks And Test Signals

Risks include DMA mapping leaks on error, using original SG counts instead of mapped counts, strict `% 16` fallback that may exclude DES-sized requests, IV update mistakes for decrypt, flow selection races, and fallback flag propagation. Test AES/3DES ECB/CBC vectors, in-place/out-of-place DMA, unaligned and over-`MAX_SG` fallback cases, runtime PM, concurrent flows, and DMA API debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce-cipher.c -->
