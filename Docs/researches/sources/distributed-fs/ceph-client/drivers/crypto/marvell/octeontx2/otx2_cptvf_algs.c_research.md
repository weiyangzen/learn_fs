# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptvf_algs.c

## Purpose
This file registers and implements the VF-facing Linux Crypto API algorithms backed by CPT hardware. It supports skcipher modes for AES/DES3, AEAD authenc HMAC+CBC AES, HMAC with null cipher, and RFC4106 GCM AES, with fallback software algorithms for unsupported sizes or conditions.

## Important APIs and functions
Public lifecycle functions are `otx2_cpt_crypto_init()` and `otx2_cpt_crypto_exit()`. Request paths include `otx2_cpt_skcipher_encrypt()`, `otx2_cpt_skcipher_decrypt()`, `otx2_cpt_aead_encrypt()`, `otx2_cpt_aead_decrypt()`, null-cipher AEAD variants, setkey functions, and init/exit callbacks. Important internal helpers build input/output lists (`create_input_list()`, `create_output_list()`, `create_aead_input_list()`, `create_aead_output_list()`), initialize HMAC pads (`aead_hmac_init()`), handle callbacks, and choose the device/LF with `get_se_device()`.

## Control flow
VF LF init calls `otx2_cpt_crypto_init()`, which records the PCI device and queue count, then registers skcipher and AEAD algorithms once the expected device count is present. Crypto requests allocate per-request context, validate length/alignment, build CPT context headers and scatter-gather lists, choose a queue based on CPU, set callback/request metadata, select the SE engine group, and call `otx2_cpt_do_request()`. Completion callbacks copy IVs or validate null-cipher HMACs, destroy CPT DMA state, and complete the Crypto API request.

## State and persistence
Global state is `se_devices`, protected by a mutex and atomic count, plus `is_crypto_registered`. Per-transform state stores keys, cipher/mac type, fallback tfm, hash state, HMAC pads, and CN10K hardware context. Per-request state is in DMA-aware request context and is transient until completion.

## Dependencies and integration points
This file depends on Linux Crypto API internals, scatterwalk helpers, request manager, LF engine-group lookup, CN10K errata context helpers, and PF-provided VF capabilities. It is the main consumer of CPT request submission.

## Risks and edge cases
Scatterlist handling uses `sg_virt()`, so callers must provide CPU-addressable SG entries. Large requests or zero authentication parameters fall back to software. CBC/DES alignment is enforced; XTS uses key layout with second key at `KEY2_OFFSET`. Null-cipher HMAC decrypt manually compares calculated/received tags. Error paths in init must release shash, pads, fallback tfms, and hardware contexts; current early returns after `get_se_device()` or hardware context init rely on transform cleanup for partially allocated members.

## Test signals
Crypto selftests should cover every registered driver name, setkey validation, fallback for large requests, fragmented SG input/output, in-place CBC decrypt IV copyback, null-cipher HMAC tag mismatch returning `-EBADMSG`, RFC4106 authsize validation, module refcount registration/unregistration, and CN10K errata hardware context setup/clear.
