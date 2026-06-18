<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/irq.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/irq.c

Purpose: Implements Lemote 2F interrupt dispatch and controller setup, including a custom i8259 query path.

Important APIs/types/functions: `mach_i8259_irq()` reads PIC ISR/IMR under `i8259A_lock`; `mach_irq_dispatch()` routes timer, northbridge/Bonito, CPU UART, and southbridge/i8259; `mach_init_irq()` initializes cascades.

Control flow: The i8259 path first checks Loongson INT0 pending, then reads master/slave ISR masked by IMR and handles IRQ7 spurious detection. Board dispatch sends IP6 to Bonito, IP3 to CPU UART, and IP2 to i8259.

State and persistence: Programs `LOONGSON_INTPOL` and `LOONGSON_INTEDGE`; registers IP6 and IP2 cascade handlers.

Dependencies and integration: `wakeup_loongson()` in PM calls `mach_i8259_irq()` during suspend polling.

Risks: Uses ISR rather than generic `i8259_irq()` to avoid boot hangs, so PIC behavior must be carefully matched. Shared IP6 action is a dummy handler.

Test signals: Keyboard, SCI, Bonito, CPU UART, and timer interrupts should dispatch on expected pending bits; spurious IRQ7 should be filtered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/lemote-2f/irq.c -->
