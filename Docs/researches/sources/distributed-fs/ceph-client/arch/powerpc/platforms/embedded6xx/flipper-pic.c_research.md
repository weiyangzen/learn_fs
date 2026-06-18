# sources/distributed-fs/ceph-client/arch/powerpc/platforms/embedded6xx/flipper-pic.c

Purpose: interrupt-controller driver and reset-button helpers for the Nintendo GameCube/Wii Flipper PI interrupt block.

Important APIs and control flow: irq-chip callbacks mask, unmask, and ack bits in Flipper IMR/ICR registers. `flipper_pic_init` validates the parent `nintendo,flipper-pi` node, maps the parent register resource, quiesces all IRQs, and creates a linear 32-entry irq domain. `flipper_pic_probe` finds `nintendo,flipper-pic`, installs the domain as default, and `flipper_pic_get_irq` returns the first pending enabled interrupt mapping. `flipper_quiesce`, `flipper_platform_reset`, and `flipper_is_reset_button_pressed` expose chipset operations to board files.

State, dependencies, and risks: state is global `flipper_irq_host` and its MMIO base. Dependencies include OF compatible names, big-endian MMIO helpers, irqdomain, and board machine descriptors. Risks include `BUG_ON` if firmware lacks the node, no ioremap failure check in `flipper_pic_init`, and global state assumed valid by reset/quiesce helpers. Test signals are interrupt delivery, reset button state, clean shutdown quiesce, and GameCube/Wii reset behavior.
