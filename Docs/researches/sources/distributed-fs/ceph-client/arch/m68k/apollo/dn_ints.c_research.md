# sources/distributed-fs/ceph-client/arch/m68k/apollo/dn_ints.c

Purpose: Apollo PIC-backed IRQ controller setup.

Important functions are `dn_init_IRQ()`, `apollo_irq_startup()`, `apollo_irq_shutdown()`, and `apollo_irq_eoi()`. IRQs below 8 are controlled through PIC A mask register `pica+1`; IRQs 8-15 use PIC B `picb+1`. EOI writes `0x20` to both PIC command ports.

Control flow in `dn_init_IRQ()` reserves 16 user interrupt vectors starting at `VEC_USER + 96` and installs `apollo_irq_chip` with `handle_fasteoi_irq` for `IRQ_APOLLO` through the 16-source range.

State is hardware PIC mask/command registers and generic IRQ-core chip assignments. There is no additional software status cache.

Dependencies include `asm/apollohw.h`, `asm/traps.h`, `m68k_setup_user_interrupt()`, and `m68k_setup_irq_controller()`. Integration is through `config_apollo()` assigning `mach_init_IRQ`.

Risks and test signals: incorrect PIC split or EOI can wedge interrupts. Validate by booting Apollo config, confirming timer IRQ runs, and observing IRQ mask/unmask behavior for devices on both PICs.
