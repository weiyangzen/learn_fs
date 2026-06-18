<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/registers.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/registers.h

## Purpose
MMIO register map, bit definitions, reset defaults, memory-layout helpers, and typed access macros for CATPT SHIM, PCI, DMA, SSP, mailbox, SRAM, and DSP/host address conversion.

## APIs, Types, and Functions
Defines SHIM offsets (`CS1`, `ISC`, `IMC`, `IPCC`, `IPCD`, `CLKCTL`, `HMDC`), PCI offsets (`PMCS`, `VDRTCTL0`, `VDRTCTL2`), LPT/WPT SRAM-gate/APLL bits, SSP reset defaults, memory sizes and block counts, DSP DRAM offset conversion macros, and helpers such as `catpt_shim_addr()`, `catpt_dma_addr()`, `catpt_ssp_addr()`, `catpt_inbox_addr()`, `catpt_outbox_addr()`, `catpt_readl_shim()`, `catpt_updatel_shim()`, `catpt_readl_poll_shim()`, `catpt_readl_pci()`, and `catpt_updatel_pci()`.

## Control Flow, State, and Persistence
The header has no runtime state. Its constants determine how platform specs are interpreted, how power/clock/IPCC/IPCD control flow reaches hardware, how mailbox offsets received from firmware become host MMIO addresses, and how DSP DRAM addresses are converted for IPC payloads and DMA.

## Dependencies and Integration
Includes Linux bitops, iopoll, and PCI PM register definitions. Used by every CATPT implementation file for register I/O, power sequencing, DMA address construction, firmware loading, IPC, coredump, and sysfs/PCM register reads.

## Risks and Test Signals
Risks include incorrect platform-specific masks, read-modify-write races in simple update macros, address macro misuse with unvalidated firmware mailbox offsets, and conversion macros assuming only the `0x400000` DSP DRAM alias bit differs. Test signals are stable probe/power sequences, correct IRQ/IPCC/IPCD behavior, successful firmware memory copies, accurate coredump register sections, and no MMIO faults from mailbox or stream register addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/registers.h -->
