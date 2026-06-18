# sources/distributed-fs/ceph-client/arch/s390/include/asm/hw_irq.h

Purpose: This header declares initialization entry points for s390 hardware interrupt classes.

Important APIs/types/functions: `init_airq_interrupts()` initializes adapter interrupt handling and `init_cio_interrupts()` initializes channel I/O interrupts.

Control flow: Architecture boot code invokes these init functions before devices that depend on adapter or channel interrupts are activated.

State and persistence: Interrupt descriptor and low-level dispatch state lives in the implementations; this header only publishes init hooks.

Dependencies and integration points: It includes Linux MSI/PCI headers and integrates with channel I/O, PCI MSI/adapter interrupts, and boot-time IRQ setup.

Risks and test signals: Ordering mistakes can leave devices without interrupt routing. Tests should cover boot with CIO devices, PCI MSI devices, adapter interrupt users, and configs with or without PCI.
