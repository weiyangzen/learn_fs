## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_cfg_regs.h

Purpose: auto-generated TPC4 execution/configuration register map. It defines 432 `mmTPC4_CFG_*` offsets from `0xF06400` through `0xF06E2C`, matching `mmTPC4_CFG_BASE` and the `0x2000` CFG section in `goya_blocks.h`.

Important API surface: two descriptor banks exist: `KERNEL_*` and `QM_*`. Each bank contains eight tensor descriptors with base low/high, padding, tensor config, and five dimension size/stride/base-offset triplets; kernel base address high/low; five-dimensional TID base/size registers; 32 scalar register file (`SRF`) values; kernel config and sync-object message. Shared TPC controls cover TBUF, semaphore, VFLAGS/SFLAGS, LFSR, status, CFG/SM base translation, command/execute/stall, icache base, MSS/TSB config, interrupt cause/mask, ARUSER/AWUSER, and MBIST controls.

Control flow and state: the header does not run code. Driver or firmware writes descriptors and control registers before launching or stalling TPC work. Persistent state is hardware register state, especially descriptor banks and interrupt/status fields.

Dependencies and integration: included via `goya_regs.h`; security code references CFG registers for protection-bit masks and runtime code uses TPC index loops bounded by `TPC_MAX_NUM`.

Risks and test signals: bad tensor/TID offsets corrupt kernels; bad stall/execute or interrupt offsets hang recovery. Test with TPC kernel launch, descriptor programming, interrupt masking, MBIST, security windows, and generated-header diff checks.
