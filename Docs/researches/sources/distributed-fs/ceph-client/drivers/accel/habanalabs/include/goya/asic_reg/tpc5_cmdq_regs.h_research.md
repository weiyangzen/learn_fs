## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_cmdq_regs.h

Purpose: auto-generated TPC5 CMDQ register map. It exports 58 offsets from `mmTPC5_CMDQ_GLBL_CFG0` at `0xF49000` to `mmTPC5_CMDQ_CQ_BUF_RDATA` at `0xF4930C`.

Important API surface: global config/protection/error/status, CQ config and pointer/control/status registers, CQ read-rate limiter, FIFO count, CP message base addresses, LDMA offsets, fence read-data/counters, CP status/current instruction/barrier/debug, and CQ buffer debug access.

Control flow and state: no executable code. Software programs queue and CP registers; hardware consumes queue work and exposes progress through status and fences. State is MMIO hardware state.

Dependencies and integration: pulled in by `goya_regs.h`; TPC5 command queue base and section sizing are in `goya_blocks.h`; event handling uses `GOYA_ASYNC_EVENT_ID_TPC5_CMDQ`.

Risks and test signals: incorrect offsets can break completion processing or fence synchronization for only one TPC lane, making defects easy to miss in partial tests. Test with per-TPC queue tests, fence timeout/recovery, CQ status reads, interrupt event decoding, and security access checks.
