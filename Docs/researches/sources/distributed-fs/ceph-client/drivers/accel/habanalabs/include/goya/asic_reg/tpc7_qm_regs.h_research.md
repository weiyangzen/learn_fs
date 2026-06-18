## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_qm_regs.h

Purpose: auto-generated TPC7 QMAN register map defining 78 offsets from `mmTPC7_QM_GLBL_CFG0` at `0xFC8000` through `mmTPC7_QM_CQ_BUF_RDATA` at `0xFC830C`.

Important API surface: global QMAN config/protection/error/status, PQ/CQ setup and status, producer/consumer indices, push words, rate limiter controls, CP message bases, LDMA offsets, fence and current instruction registers, barrier/debug, and queue buffer readback.

Control flow and state: no C flow. TPC7 queue work is driven by MMIO programming of these registers and observed through hardware-updated status and fence fields.

Dependencies and integration: included via `goya_regs.h`; associated with `mmTPC7_QM_BASE`; TPC queue SRAM reservation in `goyaP.h` includes TPC7 as the last QMAN slot; async event ID `GOYA_ASYNC_EVENT_ID_TPC7_QM` reports failures.

Risks and test signals: last-engine offset or SRAM-slot mistakes can affect only TPC7. Test full eight-TPC queue initialization, TPC7 QMAN stress, fence timeout paths, event reporting, and security mask setup.
