## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc7_cmdq_regs.h

Purpose: auto-generated TPC7 CMDQ map defining 58 offsets from `0xFC9000` to `0xFC930C`.

Important API surface: global config/protection/error/status, CQ configuration and pointer/control/status mirror registers, read-rate limiter, FIFO count, CP message bases, LDMA offsets, fence read/counter registers, CP current instruction/status/barrier/debug, and CQ buffer access.

Control flow and state: the header contains no execution. Runtime queue flow is created by MMIO writes to CQ/CP registers and hardware updates to status/fence registers.

Dependencies and integration: included by `goya_regs.h`; `goya_blocks.h` gives the unusually large TPC7 CMDQ section because TPC7 sits at the end of the TPC window; async event handling includes `GOYA_ASYNC_EVENT_ID_TPC7_CMDQ`.

Risks and test signals: TPC7-specific section sizing and end-of-range placement make boundary mistakes important. Test TPC7 queue bring-up, CP fence waits, completion interrupts, security masks, and full TPC0-TPC7 queue iteration.
