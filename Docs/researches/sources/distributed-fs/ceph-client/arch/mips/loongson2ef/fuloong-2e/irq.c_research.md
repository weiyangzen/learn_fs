<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/irq.c

Purpose: Supplies Fuloong 2E-specific MIPS pending-bit dispatch and interrupt-controller cascade setup.

Important APIs/types/functions: `mach_irq_dispatch()` routes timer IP7, ignores perf IP6, dispatches i8259 on IP5, and Bonito on IP2. `mach_init_irq()` initializes CPU, i8259, and Bonito IRQs and registers cascade handlers.

Control flow: Pending bits are tested in priority order. Board init sets Bonito edge behavior for error/mailbox sources, initializes controllers, and requests no-thread cascade IRQs for IP2 and IP5.

State and persistence: Programs `LOONGSON_INTEDGE` and installs cascade IRQ descriptors.

Dependencies and integration: Common `plat_irq_dispatch()` calls this board hook.

Risks: IP6 perf counter overflow is silently returned. Incorrect edge/level setup can lose device interrupts.

Test signals: Timer, i8259, and Bonito interrupts should route through distinct pending bits; cascade request failures should be visible in boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/fuloong-2e/irq.c -->
