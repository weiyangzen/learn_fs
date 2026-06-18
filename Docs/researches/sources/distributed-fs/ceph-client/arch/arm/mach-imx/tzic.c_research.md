# sources/distributed-fs/ceph-client/arch/arm/mach-imx/tzic.c

Purpose: TrustZone Interrupt Controller driver for older i.MX SoCs, including irqdomain/generic-chip setup, FIQ selection, suspend wake programming, and wake synchronization.

Important APIs/types/functions: Defines `tzic_init_dt()` via `IRQCHIP_DECLARE`, `tzic_handle_irq()`, `tzic_init_gc()`, optional `tzic_set_irq_fiq()`, optional suspend/resume callbacks, and `tzic_enable_wake()`.

Control flow: DT init maps TZIC, programs controller/priorities/sync, marks interrupts secure, disables all sources, allocates 128 legacy IRQ descriptors, creates a legacy domain, installs four generic chips of 32 IRQs, sets global IRQ handler, and initializes FIQ if enabled. IRQ handling loops over high-priority pending banks masked by security registers and dispatches each hwirq through the domain. Wake setup writes DSMINT and mirrors enabled IRQ masks into wake registers.

State and persistence: Global state is `tzic_base` and `domain`. Hardware state includes INTSEC, enable/clear, priority mask, sync, pending, wake, DSMINT, and optional FIQ security routing registers.

Dependencies and integration points: Depends on irqchip/irqdomain/generic-chip APIs, ARM `set_handle_irq`, optional FIQ support, i.MX relaxed IO, and PM users such as i.MX5 idle.

Risks: Missing DT mapping or descriptor/domain allocation is only `WARN_ON`, so later IRQs can fail badly. Wake programming is bank-wide and depends on generic-chip `wake_active`. `tzic_enable_wake()` returns `-EAGAIN` if DSMINT does not latch, so callers must handle idle failure.

Test signals: Boot with TZIC, test all 128 IRQ banks, FIQ routing, suspend wake sources, and `tzic_enable_wake()` behavior before deep idle.
