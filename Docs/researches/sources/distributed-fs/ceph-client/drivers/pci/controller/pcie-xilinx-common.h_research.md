# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-common.h

Purpose: Provides shared Xilinx PCIe interrupt index constants used by multiple Xilinx host drivers, especially CPM and PL DMA variants.

Important APIs/types/functions: Defines symbolic interrupt numbers such as `XILINX_PCIE_INTR_LINK_DOWN`, `HOT_RESET`, `CFG_PCIE_TIMEOUT`, `CFG_TIMEOUT`, `CORRECTABLE`, `NONFATAL`, `FATAL`, `CFG_ERR_POISON`, `PME_TO_ACK_RCVD`, `INTX`, `PM_PME_RCVD`, `MSI`, `SLV_UNSUPP`, `SLV_UNEXP`, `SLV_COMPL`, `SLV_ERRP`, `SLV_CMPABT`, `SLV_ILLBUR`, `MST_DECERR`, `MST_SLVERR`, and `SLV_PCIE_TIMEOUT`.

Control flow: The header has no runtime logic. Drivers use these indices to build bit masks with `BIT(XILINX_PCIE_INTR_*)`, populate interrupt-cause tables, map event IRQs in irqdomains, and route INTx/MSI status.

State and persistence: No state. The constants encode hardware interrupt bit positions and therefore indirectly affect persistent interrupt mask/status programming.

Dependencies/integration: Includes PCI, ECAM, and platform-device headers for users. Included by `pcie-xilinx-cpm.c` and `pcie-xilinx-dma-pl.c`; older `pcie-xilinx.c` and `pcie-xilinx-nwl.c` carry their own local definitions.

Risks: `XILINX_PCIE_INTR_PM_PME_RCVD` and `XILINX_PCIE_INTR_MSI` both use bit 17 for different controller variants. Shared users must select the semantic appropriate to their hardware. Wrong indices lead to unmasked errors, missed INTx/MSI, or misleading logs.

Test signals: Compile both CPM and PL DMA drivers, verify event masks against hardware manuals, trigger AER/error interrupts, INTx, MSI, PME, and timeout events where supported, and confirm cause strings match the asserted bits.
