# sources/distributed-fs/ceph-client/arch/mips/sgi-ip32/ip32-irq.c

Purpose: IP32 CRIME/MACE interrupt controller implementation. It maps CRIME, MACE PCI, and MACE ISA interrupts to Linux IRQs and dispatches CP0 IRQ lines.

Important APIs and control flow: mask/unmask routines update `crime_mask`, `macepci_mask`, and `maceisa_mask`, flushing buses after posted writes. Separate irq_chips handle CRIME level, CRIME edge, MACE PCI, MACE ISA level/edge, and regular MACE interrupts. `ip32_irq0()` reads `crime->istat & crime_mask`, resolves daisy-chained MACE ISA interrupts from MACE ISTAT, and calls `do_IRQ()`. Unknown CPU IRQ lines dump extensive state and spin. `arch_init_irq()` clears CRIME/MACE state, initializes CPU IRQs, assigns handlers for every IP32 IRQ range, requests CRIME memory/CPU error IRQs, and enables CPU interrupt mask bits.

State, persistence, and integration: state includes CRIME/MACE masks, hardware interrupt registers, and Linux IRQ descriptors. Dependencies include `crime_init()` having mapped CRIME/MACE, error handlers from `crime.c`, and IP32 IRQ number definitions. Risks include 32-bit shifts against wider masks, fatal spin on unknown IRQs, comments about CRIME 1.1 interrupt delivery quirks, and careful edge clear ordering. Test signals are working serial, RTC, Ethernet, PCI, audio, and CRIME error IRQs plus stable interrupt masks.
