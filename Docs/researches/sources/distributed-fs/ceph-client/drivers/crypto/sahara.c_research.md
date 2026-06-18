# sources/distributed-fs/ceph-client/drivers/crypto/sahara.c

## Purpose
This file implements the Freescale/NXP SAHARA2 crypto accelerator driver for i.MX27/i.MX53-era hardware. It registers AES ECB/CBC skcipher acceleration and SHA1/SHA256 ahash acceleration depending on hardware version, builds SAHARA hardware descriptors and link tables, handles interrupts, and uses the Linux crypto engine to serialize requests.

## Important APIs, types, and functions
`struct sahara_hw_desc` and `struct sahara_hw_link` describe the hardware descriptor rings. `struct sahara_ctx` stores AES key material and fallback skcipher. `struct sahara_aes_reqctx` stores mode, decrypt IV backup, and fallback request storage. `struct sahara_sha_reqctx` stores buffered hash bytes, saved hardware context, mode flags, digest sizes, SG chains, total length, and first/last flags. `struct sahara_dev` owns MMIO, clocks, completion, coherent descriptor/key/IV/context/link buffers, current SG state, and the crypto engine.

AES registration is in `aes_algs[]`, SHA1 in `sha_v3_algs[]`, and SHA256 in `sha_v4_algs[]` for versions above 3. Request execution is centralized by `sahara_do_one_request()`. AES uses `sahara_aes_setkey()`, `sahara_aes_crypt()`, `sahara_hw_descriptor_create()`, and `sahara_aes_process()`. Hashing uses `sahara_sha_init()`, `sahara_sha_enqueue()`, `sahara_sha_prepare_request()`, descriptor creation helpers, and `sahara_sha_process()`.

## Control flow
Probe maps MMIO, requests IRQ, enables `ipg` and `ahb` clocks, allocates coherent descriptors, key/IV buffers, context buffer, and link table, starts a crypto engine, verifies hardware version against compatible strings, resets hardware into batch mode, enables interrupts, and registers algorithms.

AES setkey accepts only AES-128 in hardware; AES-192 and AES-256 are configured on the fallback transform. AES crypt rejects zero-length as no-op, falls back when key length is not 128 bits, rejects non-block-aligned requests, stores mode, and transfers the request to the engine. The engine callback assigns the request to global device fields, copies IV for CBC, builds a key descriptor followed by a data-link descriptor, maps source and destination SGs, writes descriptor address to `SAHARA_REG_DAR`, waits up to one second for IRQ completion, unmaps DMA, updates CBC IV, and finalizes the request.

Hash update/final calls enqueue ahash requests to the same crypto engine. `sahara_sha_prepare_request()` buffers insufficient data until a block can be processed, carries trailing partial blocks across updates, and builds chained SGs when buffered bytes precede request SG data. The first hash operation uses a mode/init descriptor; later operations load the saved context then hash more data. Completion copies the hardware context back and, on the last request, copies the digest to `req->result`.

## State and persistence behavior
`dev_ptr` is a singleton pointer used by transform and request paths. Coherent memory for descriptors, links, key/IV, and hash context persists for the device lifetime. Transform state persists AES key length/key and fallback. Request state persists hash context through export/import by copying `struct sahara_sha_reqctx`. There is no disk persistence. The driver does not explicitly zero AES key buffers on exit.

## Dependencies and integration points
The file integrates with platform OF compatibles `fsl,imx53-sahara` and `fsl,imx27-sahara`, Linux clocks, IRQ, DMA mapping, coherent DMA allocation, scatterwalk, and the crypto engine registration helpers. Hardware completion depends on `sahara_irq_handler()` clearing interrupt/error bits and completing `dma_completion`.

## Risks
Hardware AES supports only AES-128, so fallback correctness for AES-192/256 is required. Descriptor link capacity is fixed at 20 links; high-fragmentation SGs fail. `dev_ptr` implies a singleton and can be fragile around multiple devices. The remove path calls `crypto_engine_exit()` before unregistering algorithms, while probe failure unregister order should be checked against engine users. Hash processing mutates `req->nbytes` in final and depends on copied context sizes. Timeout handling returns errors after DMA unmap, but hardware reset/recovery after timeout is limited.

## Test signals
Test AES ECB/CBC AES-128 hardware, AES-192/256 fallback, CBC IV update for encrypt and decrypt, non-block-aligned rejection, SG lists near and beyond 20 links, in-place and out-of-place requests, IRQ timeout injection, and probe version mismatch. Hash tests should cover SHA1 on v3/v4, SHA256 only on v4, update/final/finup/digest, messages shorter than a block, exact-block messages, multi-update context carry, export/import, and timeout/error IRQ decoding paths.
