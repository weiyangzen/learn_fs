## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc6_cfg_regs.h

Purpose: auto-generated TPC6 configuration register map. It exports 432 `mmTPC6_CFG_*` offsets from `0xF86400` to `0xF86E2C`, with the same normalized CFG layout as TPC4 and TPC5.

Important API surface: kernel and QM descriptor banks for eight tensors, five-dimensional TID geometry, 32 SRF registers per bank, kernel base/config/sync message, TBUF/semaphore/flag/status registers, CFG and shared-memory address translation, command/execute/stall, icache base, MSS/TSB, interrupt cause/mask, ARUSER/AWUSER, and MBIST registers.

Control flow and state: declarative only. Execution flow is driven by writes from driver/firmware to descriptor and control registers, followed by hardware status/interrupt updates.

Dependencies and integration: included via `goya_regs.h`; associated with `mmTPC6_CFG_BASE` in `goya_blocks.h`, TPC loops bounded by `TPC_MAX_NUM`, and async events for TPC6 ECC/decoder/kernel errors.

Risks and test signals: offset mistakes can affect only TPC6 and survive broad tests if that engine is disabled or masked. Test with explicit TPC6 enablement, kernel dispatch, stall/recovery, interrupt cause/mask, MBIST, and protection-bit validation.
