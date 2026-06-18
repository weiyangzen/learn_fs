# sources/distributed-fs/ceph-client/drivers/crypto/intel/keembay/keembay-ocs-aes-core.c

## Purpose
This is the Crypto API and platform-driver front end for the Intel Keem Bay OCS AES/SM4 accelerator. It registers asynchronous SKCIPHER and AEAD algorithms, queues requests through `crypto_engine`, prepares DMA linked lists, invokes the low-level `ocs-aes.c` hardware helpers, and handles software fallback for AES-192.

## Important APIs, Types, And Functions
- `struct ocs_aes_tctx` stores selected OCS device, key material, key length, cipher type, fallback cipher, and fallback flag.
- `struct ocs_aes_rctx` stores per-request instruction/mode, SG/DMA counts, linked-list descriptors, CBC/CTS scratch state, and AEAD tag buffers.
- Device registry: `struct ocs_aes_drv ocs_aes` and `kmb_ocs_aes_find_dev()` maintain the single expected platform device and bind transforms to it.
- Key setup: `check_key()`, `save_key()`, `kmb_ocs_sk_set_key()`, and `kmb_ocs_aead_set_key()` validate keys and route AES-192 to fallback.
- SKCIPHER path: `kmb_ocs_sk_common()` validates input, handles zero-length cases, or queues to the engine; `kmb_ocs_sk_run()` prepares DMA, invokes `ocs_aes_op()`, updates IVs, and performs CTS CS2/CS3 block swaps.
- AEAD path: `kmb_ocs_aead_common()` queues requests or uses fallback; `kmb_ocs_aead_dma_prepare()` builds AAD and payload linked lists; `kmb_ocs_aead_run()` invokes CCM/GCM helpers and handles tag compare/copy.
- Engine callbacks: `kmb_ocs_aes_sk_do_one_request()` and `kmb_ocs_aes_aead_do_one_request()` program the hardware key then run the request and finalize it.
- Algorithm tables: `algs[]` and `algs_aead[]` register AES/SM4 ECB/CBC/CTR/CTS and GCM/CCM variants, with optional ECB/CTS entries behind Kconfig.
- Platform lifecycle: `kmb_ocs_aes_probe()` configures a 32-bit DMA mask, maps registers, requests IRQ, starts the crypto engine, and registers algorithms; remove unregisters and exits the engine.

## Control Flow
Transform initialization allocates fallback tfms where needed and sets request-context size. Setkey validates or configures fallback. Encrypt/decrypt calls initialize request context and enqueue to the device engine. The engine callback programs the hardware key, maps SG lists into OCS DMA descriptors, runs the synchronous low-level operation, unmaps DMA, performs required post-processing (CBC IV update, CTS swap, GCM tag append/compare), and finalizes the Crypto API request.

## State And Persistence
Device state lives in `struct ocs_aes_dev` and the global device list. Transform state holds keys until tfm exit, where `clear_key()` zeroes both memory and hardware key registers if a device is bound. Request state is transient and cleaned by `kmb_ocs_sk_dma_cleanup()` or `kmb_ocs_aead_dma_cleanup()`. No persistent on-disk state exists.

## Dependencies And Integration Points
The file depends on the low-level OCS AES API in `ocs-aes.h`, Crypto API engine helpers, platform device resources, threaded IRQ registration, DMA mapping, scatterlist copy helpers, GCM authentication-size helpers, and Kconfig optional mode symbols.

## Risks
- AES-192 fallback must preserve request flags/authsize and request sizing; AEAD fallback stores a subrequest in request context and is sensitive to `crypto_aead_reqsize()`.
- In `register_aes_algs()`, the error unwind unregisters `ARRAY_SIZE(algs)` AEAD entries instead of `ARRAY_SIZE(algs_aead)`, which looks suspicious and should be tested.
- The non-in-place AEAD AAD copy uses `ocs_aes_bypass_op(..., req->cryptlen)` after building AAD lists of `req->assoclen`; this length mismatch is a risk signal.
- GCM decrypt uses `memcmp()` for tag comparison rather than a constant-time compare.
- The driver assumes one OCS device; list-first lookup without an empty-list check can be unsafe if transform initialization races platform removal.
- DMA linked-list creation failures rely on later cleanup; every error path needs DMA API debug coverage.

## Test Signals
- Crypto API self-tests for AES and SM4 CBC/CTR/GCM/CCM, plus optional ECB/CTS.
- AES-192 fallback tests for SKCIPHER and AEAD.
- In-place and out-of-place SG tests with nonzero AAD, empty payload, empty AAD, and multi-entry SG.
- CTS compatibility vectors for CBC-CS3 semantics.
- DMA API debug and KASAN tests around all preparation error paths.
