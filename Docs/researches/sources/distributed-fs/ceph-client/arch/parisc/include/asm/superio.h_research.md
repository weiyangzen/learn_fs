# sources/distributed-fs/ceph-client/arch/parisc/include/asm/superio.h

Purpose: defines PA-RISC SuperIO legacy device registers, IRQ routing constants, device structure, and helper declarations.

Important APIs/types/functions: exports PIC/SuperIO config register offsets, trigger/routing registers, legacy IRQ constants for USB/serial/parallel/floppy/IDE, `SUPERIO_NIRQS`, `struct superio_device`, `is_superio_device`, and `superio_fixup_irq`.

Control flow: PCI/legacy setup identifies SuperIO functions, programs or reads IRQ routing, and fixes PCI device IRQ lines through IOSAPIC integration.

State and persistence: SuperIO config registers and IRQ routing persist in hardware. Dependencies and integration: used by serial, parport, floppy, IDE, USB legacy support, and PCI fixup code.

Risks and test signals: wrong routing can make legacy devices unusable or share IRQs incorrectly. Test SuperIO probe logs, serial/floppy/parallel IRQ delivery, and PCI fixup paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
