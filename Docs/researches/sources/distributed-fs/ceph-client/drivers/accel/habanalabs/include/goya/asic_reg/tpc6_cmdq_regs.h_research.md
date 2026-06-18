## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cmdq_regs.h

Purpose: auto-generated TPC6 CMDQ register map with 58 offsets from `0xF89000` through `0xF8930C`.

Important API surface: global configuration/protection/error/status, completion queue setup and status, queue read-rate limiter, CP message base registers, LDMA offsets, fence read/counter registers, CP status/current instruction/barrier/debug, and CQ buffer debug registers.

Control flow and state: no executable code. Runtime command flow is software-programmed CQ/CP MMIO state consumed by hardware; completion, FIFO, and fence values expose progress.

Dependencies and integration: included by `goya_regs.h`; mapped by `mmTPC6_CMDQ_BASE`; async event handling distinguishes `GOYA_ASYNC_EVENT_ID_TPC6_CMDQ`.

Risks and test signals: wrong offsets can hang TPC6 command processing or misreport completions. Test with TPC6 command queue self-tests, LDMA/fence operations, CQ status polling, interrupt decoding, and generated layout comparison with other TPC CMDQs.
