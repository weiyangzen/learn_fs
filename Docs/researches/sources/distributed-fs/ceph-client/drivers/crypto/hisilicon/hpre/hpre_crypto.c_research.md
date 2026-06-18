# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_crypto.c

## Purpose
This file implements HPRE-backed Linux Crypto API algorithms for RSA (`akcipher`), DH (`kpp`), and ECDH over NIST P-192/P-256/P-384 (`kpp`). It translates crypto requests into HPRE SQEs, manages DMA buffers for keys and operands, handles hardware completions, records debug counters, and falls back to software implementations when hardware or parameters are unavailable.

## Important APIs, Types, and Functions
Private context types are `struct hpre_ctx`, `struct hpre_rsa_ctx`, `struct hpre_dh_ctx`, `struct hpre_ecdh_ctx`, and `struct hpre_asym_request`. `struct hpre_ctx` owns a QP, device pointer, selected key size, algorithm-specific DMA key buffers, fallback transform, curve ID, and high-performance-core flag.

Common request helpers include `hpre_ctx_init()`, `hpre_msg_request_set()`, `hpre_send()`, `hpre_alg_cb()`, `hpre_alg_res_post_hf()`, `hpre_hw_data_init()`, `hpre_prepare_dma_buf()`, `hpre_get_data_dma_addr()`, `hpre_hw_data_clr_all()`, and timeout accounting helpers. RSA entry points are `hpre_rsa_enc()`, `hpre_rsa_dec()`, key parsing helpers, and the `akcipher_alg rsa`. DH entry points are `hpre_dh_set_secret()`, `hpre_dh_generate_public_key()`, `hpre_dh_compute_shared_secret()`, and `kpp_alg dh`. ECDH entry points are curve-specific init functions, `hpre_ecdh_set_secret()`, `hpre_ecdh_compute_value()`, and the `ecdh_curves[]` KPP table.

The exported registration API is `hpre_algs_register()` and `hpre_algs_unregister()`, guarded by `hpre_algs_lock` and reference counted with `hpre_available_devs`.

## Control Flow
On first HPRE device registration, the file conditionally registers RSA, DH, and ECDH algorithms based on the device capability bitmap. Algorithm init allocates software fallback transforms and tries to allocate an HPRE QP through `hpre_create_qp()`. If no QP is available, the transform remains usable in fallback mode.

RSA key setup parses public/private keys, drops leading zeros, validates hardware-supported modulus sizes, allocates coherent DMA buffers in the hardware-required layout, and optionally stores CRT parameters. RSA encrypt/decrypt either call the fallback transform or prepare an SQE with non-CRT/CRT opcode, DMA-map input/output, send it through `hisi_qp_send()`, and complete asynchronously. DH setup validates supported group sizes, formats `xa || p` and optional generator buffers, and uses either `HPRE_ALG_DH` or `HPRE_ALG_DH_G2` for generator-2 mode. ECDH setup validates curve IDs and private key bounds, fills curve parameters from `ecc_get_curve()`, generates a private key through `crypto_stdrng_get_bytes()` when none is provided, and submits ECC multiply operations.

Hardware completions arrive through the QP callback `hpre_alg_cb()`, which recovers the request from `sqe->tag` and dispatches the algorithm-specific callback. Completion callbacks parse hardware status bits, update output lengths, check optional overtime thresholds, unmap/free DMA buffers, copy bounce-buffer results into scatterlists where needed, complete the original crypto request, and increment receive counters.

## State and Persistence Behavior
There is no disk persistence. Per-transform state persists across requests in `struct hpre_ctx`: QP allocation, DMA key material, fallback transforms, key size, curve selection, and mode flags. Per-request state lives in an aligned `struct hpre_asym_request` inside the Crypto API request context and is referenced from hardware via the SQE tag. Device-level state is updated through HPRE debug counters such as send, receive, busy, fail, overtime, and invalid request counts. Sensitive private key buffers are cleared with `memzero_explicit()` before freeing in several paths.

## Dependencies and Integration Points
The file integrates with the Crypto API `akcipher` and `kpp` interfaces, RSA/DH/ECDH key parsers, ECC curve tables, the standard RNG, Linux DMA APIs, scatterwalk helpers, and HiSilicon QM functions (`hpre_create_qp()`, `hisi_qp_send()`, `hisi_qm_free_qps()`). It depends on capability values populated by `hpre_main.c` and on HPRE SQE definitions from `hpre.h`.

## Risks and Edge Cases
DMA setup has many split paths: direct single mapping for suitable scatterlists and coherent bounce buffers for padded or multi-part data. Cleanup correctness depends on sentinel `DMA_MAPPING_ERROR`, `req->src`/`req->dst` flags, and matching sizes. Some cleanup helpers return early after an invalid input DMA address, which can skip output cleanup. ECDH completion compacts x/y coordinates in-place after unmapping and assumes the destination scatterlist is directly addressable by `sg_virt()`. Hardware fallback state is parameter-dependent; tests must confirm transitions between unsupported and supported keys do not leave stale DMA material. `hpre_send()` retries only `-EBUSY` and counts failures differently for busy versus other errors.

## Test Signals
Use Crypto API self-tests and known-answer tests for RSA public/private operations, RSA CRT and non-CRT keys, DH public/shared secret for all supported groups, and ECDH P-192/P-256/P-384. Add negative tests for too-small destination buffers, unsupported RSA sizes, unsupported DH groups, invalid ECDH private keys, missing keys, no-QP fallback, send busy/fail paths, DMA mapping fault injection, and algorithm unregister ordering across multiple devices.
