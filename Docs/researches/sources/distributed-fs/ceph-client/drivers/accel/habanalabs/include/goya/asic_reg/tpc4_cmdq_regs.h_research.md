## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cmdq_regs.h

Purpose: auto-generated TPC4 command-queue register map for the `CMDQ` block. It exports 58 `mmTPC4_CMDQ_*` offsets from `0xF09000` to `0xF0930C`, matching the TPC4 CMDQ section in `goya_blocks.h`.

Important API surface: global config/protection/error/status registers; completion queue configuration and ARUSER; CQ pointer low/high, target size, control, status mirrors, queue status words, read rate limiter controls, input FIFO count, CP message base registers, LDMA source/destination/size/commit offsets, fence read-data/counter registers, CP status/current instruction/barrier/debug registers, and CQ debug buffer access.

Control flow and state: no code executes here. Hardware command flow is through a completion-oriented command processor: software programs CQ and CP state, hardware consumes commands/messages and reports progress through status and fence counters. State is MMIO-resident and reset-sensitive.

Dependencies and integration: included by `goya_regs.h`; security setup uses CMDQ ranges for protection masks; async event IDs include `GOYA_ASYNC_EVENT_ID_TPC4_CMDQ`, giving failure reporting a stable event number.

Risks and test signals: wrong CQ or CP offsets lead to lost completions, broken LDMA commands, or stuck fences. Test via command queue bring-up, CP fence timeout paths, CQ buffer readback, interrupt/error injection, and security access validation.
