# sources/distributed-fs/ceph-client/arch/mips/sgi-ip22/ip22-eisa.c

Purpose: minimal EISA support for SGI Indigo2. It probes EISA slots, initializes the EISA interface unit and 8259 IRQs, and bridges EISA interrupts into Linux.

Important APIs and control flow: `decode_eisa_sig()` reads and decodes the four-byte EISA vendor signature. `ip22_eisa_intr()` reads the EIU interrupt acknowledge byte, drains DMA status ports, dispatches valid IRQs, and resets PICs on out-of-range values. `ip22_eisa_init()` checks MC EISA-present status, scans four slots, programs EIU registers, resets external NMI/DMA state, calls `init_i8259_irqs()`, requests `SGI_EISA_IRQ`, and sets `EISA_bus = 1`.

State, persistence, and integration: state is hardware EISA configuration and global EISA bus presence. Dependencies include FullHouse/Indigo2 hardware, I/O port base setup, IOC/MC registers, and i8259 support. Risks include PIO-only support, comments noting missing DMA/ISA robustness, and out-of-range IRQ handling that only resets PICs. Test signals are EISA slot detection logs, successful IRQ request, and functioning low-end EISA devices.
