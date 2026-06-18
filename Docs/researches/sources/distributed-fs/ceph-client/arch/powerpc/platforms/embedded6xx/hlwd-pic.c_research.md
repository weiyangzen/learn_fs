# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/hlwd-pic.c

Purpose: interrupt-domain driver for the Nintendo Wii Hollywood interrupt controller, including cascade wiring behind another interrupt source.

Important APIs and control flow: irq-chip callbacks manipulate Broadway ICR/IMR and clear Starlet ownership on unmask. `hlwd_pic_init` maps the controller, quiesces all sources, and creates a linear 32-entry domain. `hlwd_pic_probe` scans `nintendo,hollywood-pic` nodes with `interrupts`, initializes a domain, maps the cascade IRQ, and installs `hlwd_pic_irq_cascade`. The cascade masks the parent level IRQ, dispatches one pending Hollywood hwirq through `generic_handle_domain_irq`, acks, and unmasks.

State, dependencies, and risks: state is global `hlwd_irq_host` and mapped MMIO. Dependencies include OF address/interrupt properties, irqdomain, chained IRQ handlers, and Wii board setup. Risks include only handling one pending hwirq per cascade entry, `BUG_ON` on failed init, assuming the child hwirq zero is never valid because zero is treated as no IRQ, and global quiesce requiring successful probe. Test signals are Wii secondary interrupt delivery, no Starlet conflict for unmasked lines, cascade mapping, and clean shutdown quiesce.
