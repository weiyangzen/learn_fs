# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_qi2.h

## Purpose
`caamalg_qi2.h` defines the DPAA2 CAAM QI2 driver contracts shared by the implementation and other CAAM code. It captures device-private DPSECI/DPIO state, per-CPU receive queue state, operation-specific extended descriptor layouts, flow-context storage, operation direction enums, and the `caam_request` envelope passed to `dpaa2_caam_enqueue()`.

## Important APIs, Types, And Functions
`struct dpaa2_caam_priv` is the per-device anchor: DPSECI object ID/version/attributes, SEC capabilities, queue attributes, congestion notification memory and DMA address, device/MC/IOMMU handles, per-CPU private data, debugfs root, and cleanup CPU mask. `struct dpaa2_caam_priv_per_cpu` stores NAPI, dummy netdev, request/response FQIDs, notification context, dequeue store, backpointer, and selected DPIO service.

`struct aead_edesc`, `struct skcipher_edesc`, and `struct ahash_edesc` describe operation-specific software descriptors containing DMA metadata and inline DPAA2 SG tables. `struct caam_flc` stores FLC words plus a shared descriptor. `enum optype` indexes encrypt/decrypt flow contexts. `struct caam_request` is the generic queue request with two frame-list entries, mapped FLC, callback, opaque context, operation edesc, and an embedded fallback skcipher request. The only declared function is `int dpaa2_caam_enqueue(struct device *dev, struct caam_request *req)`.

## Control Flow
The header itself has no executable control flow, but it determines the lifecycle used in `caamalg_qi2.c`: probe allocates/fills `dpaa2_caam_priv` and per-CPU state; setkey paths fill `caam_flc`; request paths allocate one of the edesc layouts and fill `caam_request`; enqueue maps `fd_flt`; completion uses the callback/context/edesc fields to unmap resources and complete the Crypto API request.

## State And Persistence Behavior
All structures are volatile kernel memory. `dpaa2_caam_priv` persists for the bound DPSECI device lifetime, per-CPU structures persist while the device is enabled, transform flow contexts persist for a crypto transform lifetime, and edesc/request fields persist for a single in-flight operation. DMA addresses in these structures are only valid while the corresponding mapping remains active.

## Dependencies And Integration Points
The header includes Crypto API skcipher internals, DPAA2 IO/FD definitions, Linux thread/netdevice support, `dpseci.h`, and CAAM descriptor construction definitions. It bridges the Linux Crypto API, DPAA2 queue manager frame-list format, and CAAM shared descriptor format. The flexible SG arrays in edesc structures assume callers allocate enough trailing storage, which `caamalg_qi2.c` does via `qi_cache_zalloc()`.

## Risks
Structure layout matters for DMA and cache alignment. `caam_flc` is explicitly aligned to `CRYPTO_DMA_ALIGN`, and `caam_request.fd_flt` is aligned because hardware consumes its DMA image. Mis-sizing the fixed 512-byte cache user structures or changing flexible array assumptions can break SG construction. The embedded fallback skcipher request means request-size calculations must include fallback request size for XTS transforms.

## Test Signals
Compile-time coverage should catch missing DPAA2/CAAM type definitions and structure users. Runtime signals are indirect: successful QI2 probe/enqueue/completion paths validate the layout. Stressing multi-SG AEAD/skcipher/hash operations, XTS fallback, and congestion/backlog behavior exercises the fields declared here.
