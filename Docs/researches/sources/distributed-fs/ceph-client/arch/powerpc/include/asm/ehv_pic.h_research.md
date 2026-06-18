## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ehv_pic.h

Purpose: declares private structures and constants for the Embedded Hypervisor PIC interrupt controller.

Important APIs/types/functions: `NR_EHV_PIC_INTS`, polarity/sense macros, `struct ehv_pic` with irq domain, irq chip, and core interrupt flag, plus `ehv_pic_init()` and `ehv_pic_get_irq()`.

Control flow: initialization creates the irq domain/chip; interrupt dispatch calls `ehv_pic_get_irq()` to retrieve the active virtual interrupt.

State and persistence: `struct ehv_pic` instances hold controller mapping and Linux IRQ chip state. Hardware interrupt configuration persists in the EHV PIC.

Dependencies and integration: depends on Linux IRQ core and Freescale/ePAPR embedded hypervisor interrupt routing.

Risks and test signals: wrong sense/polarity mapping causes missed or repeated interrupts. Test signals include EHV PIC initialization, IRQ domain mapping, interrupt storm handling, and device-tree interrupt-spec parsing on embedded hypervisor systems.
