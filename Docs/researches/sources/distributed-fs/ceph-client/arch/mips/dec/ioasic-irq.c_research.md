# sources/distributed-fs/ceph-client/arch/mips/dec/ioasic-irq.c

Purpose: implements IRQ chip operations for DEC I/O ASIC interrupt lines and DMA interrupt subtypes.

Important APIs: `init_ioasic_irqs(int base)` masks all ASIC interrupts, assigns `ioasic_irq_type` to regular lines, assigns `ioasic_dma_irq_type` to DMA lines, and selects edge or fasteoi flow based on informational versus error DMA interrupt masks.

Control flow: mask/unmask manipulate the IOASIC SIMR enable register. Regular ack masks and flushes. DMA ack/eoi clears the SIR bit. Informational DMA interrupts are cleared early with `handle_edge_irq`; DMA error interrupts clear at EOI after handlers run.

State and integration: `ioasic_irq_base` records the Linux IRQ base. Hardware state is in SIMR/SIR registers. The dispatch assembly selects these IRQs based on `asic_mask_nr_tbl`.

Risks and test signals: DMA informational/error classification affects whether a device can resume DMA correctly. Test network, SCSI, SCC, and other IOASIC DMA users, including threaded handlers with `IRQF_ONESHOT` for error DMA lines.
