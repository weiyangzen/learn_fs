# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/qedr_hsi_rdma.h

## Purpose
`qedr_hsi_rdma.h` defines host-side interface layouts for QED RDMA firmware queues. It is a hardware contract header for CNQ elements, CQEs, SQ/RQ/SRQ WQEs, doorbell payloads, status enums, and DIF metadata used by the QEDR verbs implementation.

## Important APIs, Types, And Functions
Important layouts include `rdma_cnqe`, `rdma_cqe_responder`, `rdma_cqe_requester`, `rdma_cqe_common`, `union rdma_cqe`, `rdma_sq_sge`, `rdma_rq_sge`, `rdma_srq_wqe_header`, `rdma_srq_sge`, `union rdma_srq_elm`, `rdma_pwm_val16_data`, `rdma_pwm_val32_data`, `rdma_dif_params`, and WQE structs for atomic, bind, common, FMR, local invalidate, RDMA, and send operations. Enums cover requester/responder CQE status, CQE type, DIF options, and SQ request type.

## Control Flow
There is no runtime control flow. The bit masks and shifts are consumed by code that builds WQEs, rings doorbells, and decodes CQEs. The split "1st/2nd/3rd" WQE structs document 16-byte element boundaries used by hardware chains.

## State And Persistence Behavior
The file stores no live state, but it defines the in-memory DMA-visible state exchanged with firmware. Endianness annotations (`__le16`, `__le32`) are part of the contract and callers must use CPU-to-little-endian conversions correctly.

## Dependencies And Integration Points
The header depends on `<linux/qed/rdma_common.h>` for `regpair` and shared RDMA constants. It is included by `qedr.h`, making the layouts available to QEDR queue structs and verbs code. Firmware compatibility depends on these definitions matching the QED HSI version used by the lower-layer driver.

## Risks And Test Signals
Risks are ABI/firmware layout drift, incorrect bitfield shifts, missing endian conversion, and misuse of the max enum values as real statuses. Because these structs map DMA data, padding or compiler layout changes would be serious; the use of fixed-size fields helps but should be guarded by build-time layout checks where available. Test signals are successful RDMA traffic across every opcode class, CQE error/status injection, doorbell operation, fast MR/FMR operations, and cross-version testing with supported QED firmware.
