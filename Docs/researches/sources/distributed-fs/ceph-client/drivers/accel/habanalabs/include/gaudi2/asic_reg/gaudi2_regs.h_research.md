<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h

## Purpose
`gaudi2_regs.h` is the top-level Gaudi2 register aggregation header. It includes the generated register blocks and masks needed by Gaudi2 driver code and adds driver-facing offset macros for replicated blocks such as dcores, TPCs, EDMAs, HMMUs, NICs, PDMAs, rotators, VDEC/DEC blocks, ARC auxiliaries, queue managers, routers, and security/RAZWI windows.

## Important APIs, types, and functions
The file exports macros only. Important exports include block-spacing macros such as `DCORE_OFFSET`, `NIC_QM_OFFSET`, `PDMA_OFFSET`, `NIC_OFFSET`, and `NIC_UMR_OFFSET`; queue-manager register offsets such as `QM_PQ_BASE_LO_0_OFFSET`, `QM_CP_CFG_OFFSET`, `QM_PQC_*_OFFSET`, and `QM_SEI_STATUS_OFFSET`; ARC helper offsets such as `ARC_HALT_REQ_OFFSET`, `ARC_HALT_ACK_OFFSET`, and `ARC_REGION_CFG_OFFSET(region)`; MMU/STLB offsets for bypass, enable, invalidation, hop configuration, thresholds, and range invalidation; router RAZWI capture offsets; bridge/special block offsets; and HBM SPI interrupt bits. It includes this shard's NIC, PCIe, VDEC, and PDMA generated headers directly or through earlier includes.

## Control flow
There is no executable control flow. Driver init, reset, error handling, MMU setup, security setup, queue setup, and debug paths include this file and use its offsets to apply one programming loop across multiple replicated hardware instances. For example, a driver loop can start from a per-engine base address and add a common `*_OFFSET` macro instead of switching on every instance-specific generated symbol.

## State and persistence
The header stores no software state. Its constants define persistent hardware ABI assumptions: physical MMIO addresses, per-block spacing, register layout offsets, and interrupt bit positions. These values persist across driver builds and must match the Gaudi2 RTL/register generation for the targeted ASIC revision.

## Dependencies and integration points
It depends on many generated Gaudi2 `*_regs.h` and `*_masks.h` files plus `gaudi2_blocks_linux_driver.h`. Consumers include `gaudi2.c`, `gaudi2_security.c`, `gaudi2_masks.h`, queue-manager setup, MMU configuration, router/RAZWI handling, PCIe initialization, and NIC/PDMA programming.

## Risks and test signals
The largest risk is silent register drift: a bad included block or offset macro can program the wrong engine while still compiling. Offset macros derived from instance 0/1 base differences assume uniform layout across all replicated engines. Test signals are successful Gaudi2 probe, reset, MMU enable/invalidate, queue submission on PDMA/NIC/TPC/MME paths, PCIe interrupt delivery, RAZWI reporting at plausible addresses, and absence of hardware protection or SEI errors after init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/gaudi2_regs.h -->
