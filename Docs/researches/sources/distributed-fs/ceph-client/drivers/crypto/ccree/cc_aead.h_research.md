<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.h -->
## sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.h

Purpose: declares the AEAD request contract and constants shared by AEAD processing and buffer mapping. It defines tag, CCM, and GCM layout constants and exposes driver-level AEAD allocation and teardown.

Important APIs, types, and functions: the central type is `struct aead_req_ctx`, the per-request private context allocated by `crypto_aead_set_reqsize_dma()`. It contains cacheline-aligned MAC, CTR IV, GCM IV variants, GHASH key, GCM length block, CCM configuration block, DMA addresses for those buffers, original IV backup, association length, source/destination MLLI state, scatterlist pointers, offsets, buffer type selections, auth size, cipher mode, and flags for fragmented ICV, single-pass flow, and RFC4543 plaintext-authenticate-only behavior. Externally visible functions are `cc_aead_alloc()` and `cc_aead_free()`.

Control flow: this header does not execute logic, but its layout drives `cc_aead.c` and `cc_buffer_mgr.c`. AEAD callbacks zero this structure at request start, fill mode-specific fields before mapping, let the buffer manager populate DMA/MLLI fields, and then consume those fields while building descriptors and completing requests.

State and persistence behavior: `struct aead_req_ctx` is transient per crypto request, but it holds pointers and DMA addresses that must be valid until request completion. Cacheline alignment on key buffers and MAC/config blocks is part of the DMA coherency contract. `backup_iv` preserves caller-visible request state across internal IV rewrites, and `backup_mac` temporarily preserves authentication tags where coherent in-place decrypt could overwrite source data.

Dependencies and integration points: the header depends on kernel crypto AEAD APIs, AES/CTR constants, `cc_driver.h` through downstream users, and `cc_buffer_mgr.h` types such as `cc_mlli`, `mlli_params`, and `cc_req_dma_buf_type`. It is included by both AEAD implementation and buffer manager, making it a shared ABI inside the driver.

Risks: field layout and alignment affect DMA safety. Adding per-request fields without updating request-size setup in `cc_aead_init()` would corrupt adjacent crypto API memory. Misinterpreting `assoclen`, `cryptlen`, `req_authsize`, or `is_icv_fragmented` can cause tag comparison against the wrong bytes. The enum `aead_ccm_header_size` uses sentinel `-1`; code must consistently distinguish no-CCM from zero-length CCM AAD header.

Test signals: tests should exercise all flags represented here: CCM with and without AAD, GCM and RFC GCM IV handling, fragmented ICV, in-place decrypt on coherent platforms, single-pass and double-pass flows, zero-length payload, and request-size sanity under KASAN or crypto self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/ccree/cc_aead.h -->
