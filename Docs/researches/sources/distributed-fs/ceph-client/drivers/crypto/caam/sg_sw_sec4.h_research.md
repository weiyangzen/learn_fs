# sources/distributed-fs/ceph-client/drivers/crypto/caam/sg_sw_sec4.h

Purpose: builds SEC4-format scatter/gather entries for CAAM descriptors, with a runtime branch that emits DPAA2 SG entries on DPAA2 CAAM platforms.

Important APIs and types: `struct sec4_sg_entry` is the classic CAAM table entry containing a pointer, length, and BPID/offset word. `dma_to_sec4_sg_one()` emits either a DPAA2 entry via `dma_to_qm_sg_one()` or a SEC4 entry using `cpu_to_caam_dma64()` and `cpu_to_caam32()`. `sg_to_sec4_sg()`, `sg_to_sec4_set_last()`, and `sg_to_sec4_sg_last()` convert full scatterlists and mark the final entry.

Control flow and state: conversion consumes mapped scatterlist DMA addresses until `len` is exhausted. State is caller-owned output memory plus the global `caam_dpaa2` platform flag and CAAM endian/DMA conversion state from `regs.h`.

Dependencies and integration points: depends on `ctrl.h`, `regs.h`, DPAA2 FD helpers, Linux scatterlists, and descriptor-building code for CAAM symmetric/hash/AEAD operations.

Risks and test signals: risks include ABI aliasing between SEC4 and DPAA2 entries, missed final-bit conversion, wrong DMA-endian conversion on i.MX or 32-bit platforms, debug hex dumps exposing excessive log noise, and no SG-chain bounds check. Test signals include SEC4 and DPAA2 requests completing with identical buffer contents, final-entry bit validation, and successful partial-length conversions over longer scatterlists.
