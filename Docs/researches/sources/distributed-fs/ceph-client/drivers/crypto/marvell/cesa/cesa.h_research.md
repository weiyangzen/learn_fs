# sources/distributed-fs/ceph-client/drivers/crypto/marvell/cesa/cesa.h

Purpose: central header for the Marvell CESA driver. It defines hardware registers, descriptor layouts, per-device/engine/request state, inline helpers, TDMA APIs, SRAM copy APIs, and algorithm externs.

Important APIs and types: register macros cover TDMA, interrupt, security-accelerator command/config/status, SRAM descriptor offsets, and crypto/hash descriptor fields. Core types include `mv_cesa_sec_accel_desc`, `mv_cesa_op_ctx`, `mv_cesa_tdma_desc`, `mv_cesa_caps`, `mv_cesa_dev_dma`, `mv_cesa_dev`, `mv_cesa_engine`, `mv_cesa_req_ops`, `mv_cesa_ctx`, `mv_cesa_req`, `mv_cesa_skcipher_req`, and `mv_cesa_ahash_req`. Inline helpers update operation config, adjust SRAM-relative descriptor pointers, set crypt/hash lengths, manage interrupt mask cache, select the least-loaded engine, and determine cleanup requirements.

Control flow and integration: algorithm code fills an `mv_cesa_op_ctx`, initializes either standard or DMA request state, selects an engine through `mv_cesa_select_engine()`, and submits via `mv_cesa_queue_req()`. Core interrupt code calls `ctx->ops` callbacks defined by cipher/hash files. TDMA functions declared here are implemented in `tdma.c`; SRAM SG copy is shared by standard-mode cipher/hash processing.

State and persistence: this header defines persistent device/engine state and per-request state. The global `cesa_dev` is used by inline helpers and algorithms, making the driver effectively singleton. Atomic engine load is incremented by request weight and decremented in cleanup.

Dependencies: includes crypto internal hash/skcipher APIs, DMA pool types, scatterlist concepts, gen_pool, and CESA algorithm definitions from sibling files.

Risks and test signals: singleton global access makes multi-device support and remove/reprobe delicate. Inline engine selection assumes `cesa_dev` and at least one engine are valid. Descriptor offset adjustment depends on SRAM DMA low bits matching hardware expectations. Tests should cover descriptor endianness, SRAM offset calculations, interrupt-mask caching, TDMA descriptor flags, request cleanup decisions for `-EINPROGRESS`/`-EBUSY`/errors, and load balancing across multi-engine Armada XP-like devices.
