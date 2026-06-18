# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_qm_regs.h

## Purpose

`dma1_qm_regs.h` is an auto-generated GPL-2.0 register map for the Gaudi `DMA1_QM` block, identified in the file as prototype `QMAN`. It exports C preprocessor constants for memory-mapped register offsets in the DMA1 queue manager window. The file contains 406 `mmDMA1_QM_*` macros spanning `0x528000` through `0x528D00`; `gaudi_blocks.h` maps the corresponding full block base as `mmDMA1_QM_BASE` at `0x7FFC528000ull`.

## Important APIs, Types, And Register Groups

The header defines no C functions, structs, enums, or inline APIs. Its API surface is the macro namespace. The important groups are global configuration and protection (`GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, secure/non-secure property banks), producer queue registers for four exposed queues (`PQ_BASE_*`, `PQ_SIZE_*`, `PQ_PI_*`, `PQ_CI_*`, `PQ_CFG*`, `PQ_STS*`), completion queue registers for five queues (`CQ_CFG*`, `CQ_PTR_*`, `CQ_TSIZE_*`, `CQ_CTL_*`, status mirrors, IFIFO counters), command processor message base registers, LDMA offset registers, fence data/count/status/current-instruction registers, arbitration registers (`ARB_*`), CGM and rate-limit registers, indirect APB gateway registers, and global error message registers.

## Control Flow And State

The file has no executable control flow. Runtime control flow is created by Gaudi driver users that program these offsets with `WREG32`/`RREG32`. `gaudi_init_pci_dma_qman()` initializes DMA QMAN instances by calculating `dma_id * DMA_QMAN_OFFSET` and programming the common DMA0-relative QMAN layout; the DMA1 constants also appear directly in reset paths such as `gaudi_disable_pci_dma_qmans()` and `gaudi_stop_pci_dma_qmans()`. DMA1 is treated as a PCI DMA queue manager: the PCI stop path stops four upper CPs with `0xF << DMA0_QM_GLBL_CFG1_CP_STOP_SHIFT`.

The persistent state represented by this header is hardware state, not software storage. Queue base addresses, queue sizes, producer/consumer indexes, command processor message bases, fence counters, ARB credits, error causes, and MMU ASID bits remain in device registers until reset, reinitialization, context preparation, or explicit driver writes. `gaudi_mmu_prepare()` writes `mmDMA1_QM_GLBL_NON_SECURE_PROPS_0..4` for ASID/MMU setup. `gaudi_restore_qm_registers()` restores QMAN ARB configuration by offset arithmetic after user register reset.

## Dependencies And Integration Points

This header is included through `gaudi_regs.h`, which aggregates Gaudi ASIC register maps. Bit definitions live in sibling shift/mask headers; users combine this file's offsets with field macros such as `DMA0_QM_GLBL_CFG1_CP_STOP_SHIFT`. Address spacing is tied to `DMA_QMAN_OFFSET` in `gaudiP.h`, defined from `mmDMA1_QM_BASE - mmDMA0_QM_BASE`. Queue diagnostics use the same layout to derive queue IDs for `GAUDI_EVENT_DMA0_QM ... GAUDI_EVENT_DMA7_QM`; fence lookup directly uses `mmDMA1_QM_CP_FENCE2_RDATA_0..3` for DMA1 queue fences.

## Risks And Test Signals

Because this is generated hardware ABI, the main risk is stale or incorrect offsets. A single wrong constant can route queue programming, MMU properties, error messages, or fence reads to the wrong block. Particular risk areas are the four-queue PCI behavior, the fifth CQ slot used internally, and the distinction between absolute per-instance constants and DMA0-relative offset arithmetic. Test signals are successful Gaudi driver build, PCI DMA queue initialization without RAZWI/error interrupts, idle-state reporting from `QM_GLBL_STS0` and `CGM_STS`, fence address reads for DMA1 queues, debugfs/engine idle output, and reset/stall paths that leave DMA1 idle.
