# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/irq.c

Purpose: RiscPC IOMD interrupt controller setup and priority dispatch.

Important APIs/types/functions: defines priority lookup tables, low-level mask/unmask/ack behavior, chained/primary IRQ handlers, and init code that registers IOMD interrupt banks with the generic IRQ core.

Control flow: the top-level IRQ path reads IOMD pending/mask state, uses priority tables to select the highest pending source, and dispatches to generic IRQ handling. Init programs masks/clears and configures descriptors for normal IRQs and FIQ-capable sources.

State and persistence: hardware IOMD mask/request/clear registers hold interrupt enable/pending state. Static priority tables encode fixed dispatch order.

Dependencies and integration points: depends on IOMD register access, `mach/irqs.h`, ARM FIQ support, generic IRQ descriptors, and expansion-card chained interrupts.

Risks: priority tables are opaque and must match hardware bit layout. Incorrect masking can lose or storm interrupts. FIQ/IRQ split has low tolerance for mistakes.

Test signals: timer tick, DMA IRQs, keyboard/mouse/serial interrupts, expansion card parent IRQ dispatch, and interrupt storm handling.
