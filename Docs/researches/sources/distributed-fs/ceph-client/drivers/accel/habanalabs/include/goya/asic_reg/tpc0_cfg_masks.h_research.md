# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc0_cfg_masks.h

Purpose: supplies 863 bitfield constants for TPC0 configuration and queue-manager-visible TPC descriptor registers. It describes tensor descriptors, kernel base and TID dimensions, scalar register file slots, kernel config, sync object messages, status, command/execute/stall controls, cache base/config, interrupt cause/mask, TSB config, ARUSER/AWUSER attributes, and functional MBIST controls/status.

Important APIs/types/functions: macro-only field API. Important groups include eight `TPC0_CFG_KERNEL_TENSOR_*` descriptor sets, `TPC0_CFG_KERNEL_*`, `TPC0_CFG_STATUS_*`, `TPC0_CFG_TPC_CMD_*`, `TPC0_CFG_TPC_EXECUTE_V`, `TPC0_CFG_TPC_STALL_V`, `TPC0_CFG_MSS_CONFIG_*`, `TPC0_CFG_TPC_INTR_CAUSE_CAUSE_MASK`, `TPC0_CFG_QM_*`, `TPC0_CFG_ARUSER_*`, `TPC0_CFG_AWUSER_*`, and `TPC0_CFG_FUNC_MBIST_*`.

Control flow: TPC setup writes tensor/kernel descriptors and SRFs, configures memory/cache attributes, invalidates/prefetches instruction cache through `TPC_CMD`, polls `STATUS` for idle/empty bits, then writes `TPC_EXECUTE`. Interrupt handlers read/mask `TPC_INTR_CAUSE`, and security/MMU code packs ARUSER/AWUSER ASID/MMBP values.

State and persistence: TPC config registers hold execution descriptors and control state until overwritten or reset. Status and interrupt cause fields reflect live engine state; MBIST fields reflect test progress/failures.

Dependencies and integration: included by `goya_regs.h`, paired with `tpc0_cfg_regs.h`, and mirrored conceptually across TPC1..TPC7. Goya driver code uses these fields for stall, MMU/user attributes, kernel launch, interrupt handling, and idle polling.

Risks: descriptor field widths are execution-critical. Wrong tensor dimensions, base addresses, ASID bits, or sync-object message packing can corrupt memory or hang workloads. Status polling must use the correct empty/ready bits, and interrupt cause masks must not clear unrelated faults.

Test signals: TPC kernel launch tests, tensor descriptor validation, idle polling, cache invalidate/prefetch behavior, interrupt injection, ASID/MMU isolation, sync object writes, and MBIST readback.
