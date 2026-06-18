# sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.c

## Purpose
This file implements the Texas Instruments K3 SA2UL/SA3UL crypto accelerator driver. It supports skcipher AES-CBC, AES-ECB, 3DES-CBC, 3DES-ECB, ahash SHA1/SHA256/SHA512, and authenc HMAC-SHA1/HMAC-SHA256 with AES-CBC AEAD, with supported algorithms gated by SoC match data. The driver builds SA security contexts, command labels, DMA metadata, and scatterlist mappings used by the accelerator packet interface.

## Important APIs, types, and functions
The main algorithm table is `sa_algs[]`, whose entries are selected by `enum sa_algo_id` and registered by `sa_register_algos()`. SoC capability is expressed by `struct sa_match_data` instances `am654_match_data` and `am64_match_data`; OF compatibles include `ti,j721e-sa2ul`, `ti,am654-sa2ul`, `ti,am64-sa2ul`, and `ti,am62-sa3ul`.

Security context setup flows through `sa_init_ctx_info()`, `sa_init_sc()`, `sa_set_sc_enc()`, `sa_set_sc_auth()`, `sa_set_swinfo()`, and `sa_format_cmdl_gen()`. `sa_update_cmdl()` patches per-request lengths, offsets, IVs, and auth information into command-label templates. `sa_run()` is the common DMA submission path for skcipher, ahash digest, and AEAD. Algorithm-facing entry points include `sa_cipher_cra_init()`, `sa_cipher_setkey()`, `sa_cipher_run()`, `sa_sha_cra_init_alg()`, `sa_sha_run()`, `sa_aead_setkey()`, and `sa_aead_run()`.

## Control flow
Probe allocates `struct sa_crypto_data`, maps registers, enables runtime PM, creates a DMA pool for security contexts, requests `rx1`, `rx2`, and `tx` DMA channels, configures slave widths, enables SA engine bits, registers supported algorithms, populates child devices, and adds device links.

For skcipher transforms, init allocates encryption and decryption security contexts plus a software fallback. Setkey validates key size, configures mode-control instruction arrays for AES or 3DES, sets inverse-key behavior where needed, builds encrypt/decrypt security contexts, and formats command label templates. Request execution rejects empty input as success, rejects non-block-aligned lengths, and falls back for sizes over `SA_MAX_DATA_SZ` or within the documented unsafe 240..255 byte range. Hardware requests fill `struct sa_req` and call `sa_run()`.

`sa_run()` allocates `struct sa_rx_data`, chooses `rx1` for packets below 256 bytes and `rx2` otherwise, copies the command label template, updates it for the request, maps source and destination SGs with `dma_map_sgtable()`, uses `sg_split()` when the operation length needs a bounded SG view, prepares RX and TX DMA descriptors, writes SA metadata via `dmaengine_desc_get_metadata_ptr()`, submits RX before TX, and returns `-EINPROGRESS`. Completion callbacks sync DMA, update IV/tag/digest material, free split/mapped SG state, and complete the Crypto API request.

Hash digest requests use hardware only for one-shot `digest()` in `sa_sha_run()`; incremental `init/update/final/finup/export/import` delegate to the fallback ahash. Zero-length hashes copy kernel zero-message constants. AEAD parses authenc keys, prepares HMAC ipad/opad via shash helpers, builds combined auth/encrypt contexts, and compares or appends tags in `sa_aead_dma_in_callback()`.

## State and persistence behavior
Per-device state in `struct sa_crypto_data` includes the MMIO base, DMA pool, three DMA channels, SoC match data, runtime PM device, and security-context ID bitmap guarded by `scid_lock`. Per-transform `struct sa_tfm_ctx` owns encryption, decryption, and auth `struct sa_ctx_info`, fallback transforms, key storage, shash handle, and auth key. Per-request state is stack `struct sa_req` plus heap `struct sa_rx_data` for asynchronous completion. No persistent storage exists. Security context memory is DMA-pool allocated and explicitly freed; context buffers are cleared before reuse.

## Dependencies and integration points
The driver depends on Linux DMAengine metadata support, DMA pools, scatterlist splitting, runtime PM, OF platform population, `crypto_authenc_extractkeys()`, shash/ahash/skcipher/aead Crypto API helpers, and register/packet contracts from `sa2ul.h`. It integrates with K3 UDMA-style channels named `rx1`, `rx2`, and `tx`, and with child platform devices under the SA node.

## Risks
The hardware has a documented unsafe packet-size window from 240 to 255 bytes and a max request size of 64 KiB; fallback coverage for these boundaries is critical. DMA cleanup is subtle because `sa_run()` can use original SGs, static single-entry SGs, or `sg_split()` allocations. Several init error paths allocate fallback transforms or context IDs before later failure and should be checked for leaks. Authentication tag comparison uses `memcmp()` rather than a constant-time helper. In this source snapshot, `struct sa_cmdl_upd_info` in `sa2ul.h` declares `aux_key_info` twice; that would normally be a compile-time error and should be reconciled against the intended upstream header.

## Test signals
Run Crypto API manager tests for all registered algorithms on each supported SoC capability mask. Cover packet lengths 0, 1 block, 239, 240, 255, 256, 257, 65535, and 65536+, with fallback assertions for unsafe/oversize cases. Test AES key sizes, 3DES key validation, authenc key parsing, AEAD encrypt/decrypt and bad-tag `-EBADMSG`, SHA zero-message constants, SHA digest versus incremental fallback behavior, in-place and split SGs, RX channel selection around 256 bytes, DMA mapping failures, probe deferral for channels, and remove cleanup.
