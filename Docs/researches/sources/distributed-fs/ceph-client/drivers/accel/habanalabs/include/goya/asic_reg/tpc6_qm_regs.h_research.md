## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_qm_regs.h

Purpose: auto-generated TPC6 QMAN register map defining 78 `mmTPC6_QM_*` offsets from `0xF88000` to `0xF8830C`.

Important API surface: global QMAN control/protection/error/status; PQ base, size, indices, config, ARUSER, push words, status and rate-limit controls; CQ config/pointers/size/control/status and rate-limit controls; CP message bases, LDMA offsets, fences, status/current instruction/barrier/debug, and queue buffer debug windows.

Control flow and state: no C flow. Software writes QMAN setup, pushes work, and observes hardware-updated indices/fences/status. State is volatile hardware state.

Dependencies and integration: included through `goya_regs.h`; base and section data come from `goya_blocks.h`; TPC QMAN SRAM offsets in `goyaP.h` assume this shared queue model.

Risks and test signals: offset drift may corrupt PQ/CQ state or security masks. Test TPC6 QMAN execution, fence waits, producer/consumer index updates, MMIO protection setup, event reporting for `GOYA_ASYNC_EVENT_ID_TPC6_QM`, and map parity across TPC QMAN headers.
