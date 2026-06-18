# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spum.h

Purpose: SPU-M-specific hardware message definition header. It defines the big-endian SPU-M request/response layout, status values, header sizes, payload limits, SCTX/BDESC/BD structures, and bit masks used by `spu.c`.

Important APIs and types: `struct MHEADER`, `SCTX`, `BDESC_HEADER`, `BD_HEADER`, and `SPUHEADER`; request/response sizing constants such as `SPU_REQ_FIXED_LEN`, `SPU_HEADER_ALLOC_LEN`, `SPU_RESP_HDR_LEN`, and `SPU_HASH_RESP_HDR_LEN`; payload caps `SPUM_NS2_MAX_PAYLOAD` and `SPUM_NSP_MAX_PAYLOAD`; status masks `SPU_STATUS_ERROR_FLAG` and `SPU_STATUS_INVALID_ICV`; MH flag bits and SCTX word masks for cipher/hash algorithm, mode, type, inbound/order, ICV, IV, and BD suppression.

Control flow: SPU-M builders in `spu.c` fill `SPUHEADER`, append variable SCTX key/IV material, then append `BDESC_HEADER` and `BD_HEADER`. Response parsing uses the fixed response header lengths and status masks.

State and persistence: no runtime state; the definitions describe serialized DMA message state.

Dependencies and integration points: included by `spu.c`; relies on Linux endian types and common max key/IV sizes from the Broadcom crypto driver.

Risks: all structures are big-endian hardware formats; field sizes are small, especially 16-bit BD payload lengths and 8-bit SCTX word count. Allocation sizing must remain in sync with max key sizes and RC4 legacy assumptions.

Test signals: packet dump comparison against expected MH/SCTX/BDESC/BD words, large payload chunking around 64 KiB and 8 KiB NSP limits, BD suppression hash responses, and invalid ICV status handling.
