# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_aead.c

Purpose: implements NITROX AEAD algorithms for `gcm(aes)` and `rfc4106(gcm(aes))`, translating Linux AEAD requests into SE flexi-crypto requests.

Important APIs and control flow: setkey/authsize callbacks populate `struct flexi_crypto_context`. `nitrox_aes_gcm_enc()` and `_dec()` validate AAD length, set salt/IV pointers, compute source/destination lengths, allocate SG lists through `nitrox_set_creq()`, and submit via `nitrox_process_se_request()`. RFC4106 paths reshape associated data and payload scatterlists with `scatterwalk_ffwd()`, use RFC IV sizing, and complete through `nitrox_rfc4106_callback()`. Init allocates a device context with `nitrox_get_first_device()` and `crypto_alloc_context()`.

State and persistence: per-transform state is a DMA-backed context in the device pool plus a device reference; per-request state includes allocated source/destination SG buffers and a `se_crypto_request` embedded in request context. Hardware writes completion via the request manager.

Dependencies and integration points: depends on crypto AEAD/GCM helpers, scatterwalk, `nitrox_req.h` layouts, common device allocation, and request submission.

Risks and test signals: risks include `nitrox_rfc4106_dec()` using `crypto_aead_ctx_dma(aead)` while other paths use `crypto_aead_ctx()`, strict GCM AAD limit of 512 bytes, resource leaks if `nitrox_set_creq()` fails after destination allocation in RFC paths, and scatterlist chaining subtleties for in-place versus out-of-place requests. Test signals include cryptomgr AEAD self-tests, RFC4106 authsize/key salt validation, large AAD rejection, async completion freeing SG buffers, and transform exit zeroing keys and dropping device references.
