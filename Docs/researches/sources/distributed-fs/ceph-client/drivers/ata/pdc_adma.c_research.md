# sources/distributed-fs/ceph-client/drivers/ata/pdc_adma.c

## Purpose
`pdc_adma.c` drives the Pacific Digital/PDC 0x1841 two-port ADMA controller. It supports ATA disk DMA through a single command parameter block and PRD packet, while using SFF/MMIO-style issue paths for non-DMA commands and rejecting ATAPI DMA.

## Important APIs, Types, and Functions
Important types are `enum adma_state_t` and `struct adma_port_priv` containing the coherent packet, DMA address, and state. Core functions are `adma_reset_engine()`, `adma_reinit_engine()`, `adma_qc_prep()`, `adma_fill_sg()`, `adma_qc_issue()`, `adma_intr_pkt()`, `adma_intr_mmio()`, `adma_intr()`, `adma_port_start()`, `adma_port_stop()`, `adma_host_init()`, and `adma_ata_init_one()`.

## Control Flow, State, and Persistence
Probe allocates a two-port host, maps MMIO BAR 4, sets a 32-bit DMA mask, lays out ATA register windows, resets/locks the ADMA engine, and activates the host with a custom interrupt handler. Each port allocates a coherent packet containing a CPB and PRDs, stores it in `ap->private_data`, initializes FIFO thresholds and CPB pointers, and resets engine state. DMA `qc_prep` builds CPB register writes, LBA48 fields, command byte, and PRDs; DMA `qc_issue` marks `adma_state_pkt` and starts the packet engine. Non-DMA commands mark `adma_state_mmio` and go through `ata_sff_qc_issue()`. Interrupt handling first processes packet-status interrupts, then MMIO status completion, completing or freezing/aborting the port based on ADMA status and CPB response flags.

## Dependencies and Integration Points
The driver uses MMIO register access, coherent DMA allocation, libata SFF port ops without standard BMDMA, custom host interrupts, `ATA_FLAG_PIO_POLLING`, and libata EH freeze/thaw/reset callbacks. It relies on `LIBATA_MAX_PRD` and 32-bit DMA addresses in the ADMA packet format.

## Risks and Test Signals
Risks include PRD length/address truncation, packet alignment constraints, race-prone `state` transitions between packet and MMIO modes, incomplete ATAPI support, CPB response interpretation bugs, and missed error recovery after host-bus errors. Tests should cover DMA read/write with many SG entries, LBA48 commands, non-DMA internal commands, simultaneous two-port interrupts, host-bus and device-error injection, freeze/thaw/prereset reinitialization, port stop cleanup, and verification that ATAPI DMA is consistently disabled.
