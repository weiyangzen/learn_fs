# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/include/mach/irqs.h

Purpose: RiscPC IRQ and FIQ numbering definitions.

Important APIs/types/functions: defines platform IRQ numbers for IOMD devices, expansion cards, timers, DMA, serial, and FIQ sources, plus board IRQ ranges.

Control flow: no local flow; constants are consumed by IRQ setup, DMA, ecard, and machine devices.

State and persistence: no state; constants encode interrupt wiring.

Dependencies and integration points: included by `irq.c`, `dma.c`, `ecard.c`, and device setup.

Risks: numbering must match the IRQ controller priority tables and generic IRQ descriptors. Wrong constants route interrupts to the wrong handlers.

Test signals: interrupt delivery for timer, DMA, expansion cards, keyboard/mouse, serial, and floppy FIQ.
