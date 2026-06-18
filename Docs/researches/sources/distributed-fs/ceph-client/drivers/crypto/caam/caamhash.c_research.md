# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamhash.c

## Purpose
`caamhash.c` implements classic job-ring CAAM asynchronous hash support for the Linux Crypto API. It registers unkeyed hashes and keyed HMAC/XCBC/CMAC variants, builds shared descriptors for update/final/digest operations, maintains per-request hash continuation state, maps scatterlists into SEC4 SG tables, submits job descriptors to CAAM job rings, and completes requests through either direct job-ring completion or crypto-engine backlog finalization.

## Important APIs, Types, And Functions
`struct caam_hash_ctx` is per-transform state holding four shared descriptors, key storage, DMA addresses, directions, job-ring device, context length, and `alginfo`. `struct caam_hash_state` is per-request state holding DMA addresses, partial input buffer, CAAM context bytes, state-machine function pointers, current edesc, and completion callback. `struct ahash_edesc` contains a job descriptor and optional SEC4 SG table.

Descriptor setup functions include `ahash_set_sh_desc()`, `axcbc_set_sh_desc()`, and `acmac_set_sh_desc()`, all using constructors from `caamhash_desc.c`. Key handling is in `hash_digest_key()`, `ahash_setkey()`, `axcbc_setkey()`, and `acmac_setkey()`. Submission and cleanup helpers include `ahash_edesc_alloc()`, `ahash_edesc_add_src()`, `ahash_enqueue_req()`, `ahash_do_one_req()`, `ahash_unmap*()`, and completion callbacks `ahash_done*()`. Registration uses `driver_hash[]`, `caam_hash_alloc()`, `caam_hash_cra_init()`, `caam_algapi_hash_init()`, and `caam_algapi_hash_exit()`.

## Control Flow
Module initialization checks the CAAM MDHA block and digest-size capability, then registers HMAC forms for all templates and unkeyed forms for non-AES digest templates. Transform init allocates a job ring, determines context length and DMA directions by algorithm and era, maps shared descriptor/key memory, sets request size, and creates descriptors immediately for unkeyed hashes.

Each request begins at `ahash_init()`, which installs first-operation handlers. `update` buffers partial blocks until a full block is available; first updates use `sh_desc_update_first`, later updates import prior CAAM context with `sh_desc_update`. `final` and `finup` either digest buffered data directly or import context plus remaining data. `digest` creates a one-shot descriptor. Completion unmaps context/source/buffer/SG mappings, copies digest output from `state->caam_ctx` when needed, frees the edesc, and completes through the direct ahash callback or crypto engine depending on backlog.

## State And Persistence Behavior
Shared descriptors and optional key/split-key material persist for the transform lifetime and are DMA-mapped once. Per-request state tracks buffered tail data, CAAM running context, and which function should handle the next operation. Export/import copies buffer, context, buffer length, and function pointers into `caam_export_state`. No persistent storage is used outside kernel memory and hardware queues.

## Dependencies And Integration Points
This file depends on CAAM job-ring APIs (`caam_jr_alloc`, `caam_jr_enqueue`, `caam_jr_free`), crypto-engine ahash backlog support, descriptor constructors from `caamhash_desc.h`, SEC4 SG helpers, split-key generation, CAAM error decoding, Linux scatterwalk/DMA APIs, and Crypto API ahash registration. Hardware capability probing reads CAAM perfmon/version registers from `caam_drv_private`.

## Risks
The hash state machine is sensitive to block-size tail handling, especially XCBC/CMAC keeping the last full block buffered for finalization semantics. DMA direction varies by era and algorithm; wrong direction or missed unmap can corrupt context or leak mappings. `hash_digest_key()` submits a synchronous job and waits for completion, so setkey can block. Error paths must free edescs and unmap partially mapped SG/context buffers. Export/import containing function pointers is kernel-internal and should not be treated as stable serialized data.

## Test Signals
Expected runtime signals are registered algorithms such as `sha256-caam`, `hmac-sha256-caam`, `xcbc-aes-caam`, and `cmac-aes-caam`. Crypto selftests should cover one-shot digest, multi-update, final without update, finup, export/import continuation, HMAC keys larger than block size, AES XCBC/CMAC key validation, MDHA LP256 capability limits, backlog paths, fragmented SG inputs, and zero-length messages.
