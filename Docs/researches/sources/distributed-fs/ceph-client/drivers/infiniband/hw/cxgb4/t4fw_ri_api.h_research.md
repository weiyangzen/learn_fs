# sources/distributed-fs/ceph-client/drivers/infiniband/hw/cxgb4/t4fw_ri_api.h

## Purpose

`t4fw_ri_api.h` is the Chelsio firmware ABI definition for RDMA/iWARP resource and data-path work requests. It defines RI opcodes, flags, MPA/QP capabilities, memory permissions, STag/TPTE bitfields, resource WRs for SQ/RQ/CQ/SRQ contexts, send/write/read/recv/bind/fast-register/invalidate WR layouts, and RDMA init/fini/terminate messages.

## Important APIs, Types, and Definitions

- Opcode and flag enums: `fw_ri_wr_opcode`, `fw_ri_wr_flags`, `fw_ri_mpa_attrs`, `fw_ri_qp_caps`, `fw_ri_addr_type`, `fw_ri_mem_perms`, `fw_ri_stag_type`, `fw_ri_data_op`, and `fw_ri_sgl_depth`.
- Data segment formats: `fw_ri_dsgl`, `fw_ri_isgl`, `fw_ri_immd`, `fw_ri_sge`, and DSGL pair structures.
- TPTE definition: `struct fw_ri_tpte` and `FW_RI_TPTE_*` masks for validity, key, state, type, PDID, permissions, page size, QPID, PBL address, DCA, and MW bind count.
- Resource WRs: `struct fw_ri_res`, `struct fw_ri_res_wr`, and `FW_RI_RES_WR_*` fields for queue context creation/reset.
- Data-path WRs: `fw_ri_rdma_write_wr`, `fw_ri_send_wr`, `fw_ri_rdma_write_cmpl_wr`, `fw_ri_rdma_read_wr`, `fw_ri_recv_wr`, `fw_ri_bind_mw_wr`, `fw_ri_fr_nsmr_wr`, `fw_ri_fr_nsmr_tpte_wr`, and `fw_ri_inv_lstag_wr`.
- Connection control: `struct fw_ri_wr` with INIT, FINI, and TERMINATE union payloads.

## Control Flow

The header has no executable control flow. Its structures are populated by `qp.c` when creating resources, posting RDMA operations, registering memory, and moving a connection into or out of RI mode. The firmware consumes these big-endian fields from DMA queues or skb control messages and returns CQEs defined in `t4.h`.

## State and Persistence Behavior

The definitions describe firmware-persistent state: queue contexts, TPTE memory registrations, QP RDMA capabilities, ORD/IRD limits, MPA attributes, and connection sequence numbers. Bitfield macros are used both to program firmware and to decode live TPTE state in resource tracking.

## Dependencies and Integration Points

This header depends on `t4fw_api.h` for common firmware WR fields and is included by `t4.h`. It is tightly coupled to Chelsio firmware, endian conversion in call sites, RDMA core operation mapping in `qp.c`, MR registration code, and diagnostic decoding in `restrack.c`.

## Risks and Edge Cases

- This is ABI-sensitive: field order, sizes, and bit positions must match firmware exactly.
- Some macro definitions are duplicated (`FW_RI_TPTE_PS_S`, `FW_RI_RES_WR_IQESIZE_G`) in this source snapshot; duplicate identical defines are benign for preprocessing but indicate generated-header drift.
- Several structures use flexible arrays and overlays; builders must compute `len16` precisely and ensure fixed headers fit in queue slots.
- `FW_RI_WRITE_IMMEDIATE` aliases `FW_RI_RDMA_INIT`, so opcode interpretation depends on context.
- TPTE permission/page-size/key fields are manually composed by callers; invalid combinations can create memory protection bugs that firmware may reject only asynchronously.

## Test Signals

Compile-time layout checks should cover struct sizes, offsets used by queue builders, and maximum inline/SGL calculations. Integration tests should post each WR type, create/reset SQ/RQ/CQ/SRQ resources, fast-register with immediate and DSGL PBLs, decode TPTEs through resource tracking, and verify firmware rejects malformed lengths/flags without hanging queues.
