# sources/distributed-fs/ceph-client/drivers/ata/sata_dwc_460ex.c

## Purpose
`sata_dwc_460ex.c` is a platform driver for the Synopsys DesignWare SATA core as used by AMCC 460EX-class systems. It combines SFF-style ATA register access with SATA SCR support, a DMAEngine-backed AHB DMA path, optional legacy DesignWare DMA probing, PHY management, and limited NCQ handling.

## Important APIs, Types, and Functions
Important structures are `struct sata_dwc_regs`, `struct sata_dwc_device`, and `struct sata_dwc_device_port`. Core functions include `dma_dwc_xfer_setup()`, `dma_dwc_xfer_done()`, `sata_dwc_scr_read()`, `sata_dwc_scr_write()`, `sata_dwc_isr()`, `sata_dwc_error_intr()`, `sata_dwc_dma_xfer_complete()`, `sata_dwc_qc_complete()`, `sata_dwc_port_start()`, `sata_dwc_exec_command_by_tag()`, `sata_dwc_bmdma_setup/start()`, `sata_dwc_qc_issue()`, `sata_dwc_hardreset()`, `sata_dwc_probe()`, and `sata_dwc_remove()`.

## Control Flow, State, and Persistence
Probe allocates a one-port ATA host and private controller state, maps platform MMIO, identifies DesignWare registers and FIFO DMA address, sets up ATA/SCR windows, enables SATA interrupts, obtains an IRQ, optionally initializes old DW DMA, initializes an optional PHY, and calls `ata_host_activate()`. Port start allocates per-port state, requests a DMA channel, powers on the PHY, initializes command state arrays, clears DMAC bits, sets burst sizes, clears SError, and stores private data. `qc_issue` prepares DMA descriptors for DMA protocols, handles NCQ by setting `SCR_ACTIVE` and issuing by tag, or delegates non-NCQ to `ata_bmdma_qc_issue()`. The ISR distinguishes error, NEWFP DMA setup FIS, non-NCQ completion, and NCQ completion using `sactive_issued`, `SCR_ACTIVE`, per-tag command state, and a two-interrupt DMA completion counter.

## Dependencies and Integration Points
The driver depends on OF platform probing, DMAEngine slave channels named `sata-dma`, optional old DW DMA glue, generic PHY APIs, libata SFF/BMDMA callbacks, SATA SCR access, tracepoints, and hardreset helpers. It sets `ATA_FLAG_SATA | ATA_FLAG_NCQ` but the SCSI template notes queue depth is effectively constrained because NCQ handling is not fully correct.

## Risks and Test Signals
Risks include fragile two-interrupt DMA completion accounting, NCQ tag-mask races, stale `active_tag` updates, missing cleanup when `phy_power_on()` succeeds but later paths fail, old-DMA versus DMAEngine differences, and error interrupts that always map to host-bus reset. Tests should cover non-NCQ DMA and PIO, NCQ with queue depth one and stress attempts above one, DMA callback/IRQ ordering permutations, SError injection, hardreset register reinitialization, PHY init/power/remove paths, missing DMA channel probe failure, and 8K DMA boundary behavior.
