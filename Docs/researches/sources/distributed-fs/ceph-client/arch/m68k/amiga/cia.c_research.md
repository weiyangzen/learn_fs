# sources/distributed-fs/ceph-client/arch/m68k/amiga/cia.c

Purpose: IRQ control and fan-out for the Amiga CIAA and CIAB complex interface adapter chips.

Important types and APIs include `struct ciabase`, global `ciaa_base`/`ciab_base`, `cia_set_irq()`, `cia_able_irq()`, and `cia_init_IRQ()`. `cia_set_irq()` updates cached CIA interrupt data and can raise the matching Amiga custom interrupt request. `cia_able_irq()` updates interrupt masks in both software and CIA hardware.

Control flow: `cia_handler()` reads and clears pending CIA causes, acknowledges the parent custom interrupt, dispatches the timer source under local IRQ protection, then dispatches remaining CIA sub-IRQs. `cia_irq_chip` maps logical CIA IRQ enable/disable to CIA masks. `auto_irq_chip` overrides autovectors 2 and 6 so external CIA parent interrupts can be controlled through the generic IRQ layer. `cia_init_IRQ()` initializes the child IRQ range, clears/masks hardware, starts the parent IRQ, and requests the shared parent handler.

State is cached `icr_mask`/`icr_data`, CIA hardware registers, and irq-core chip assignments.

Dependencies include Amiga custom registers, CIA hardware structs, `m68k_setup_irq_controller()`, `m68k_irq_startup_irq()`, and request_irq. Integration is essential for CIAB Timer A scheduler ticks in `config.c`, external ports, and CIA child device interrupts.

Risks and test signals: CIA ICR reads are destructive, so cached state and locking order matter. Validate timer ticks, CIA child IRQ enable/disable, shared parent request success, and no lost timer interrupts under heavy interrupt load.
