# sources/distributed-fs/ceph-client/drivers/irqchip/alphascale_asm9260-icoll.h

Purpose: Defines register offsets and bitfields for the AlphaScale ASM9260 interrupt collector.

Important APIs/types/functions: `ASM9260_NUM_IRQS`, vector/level-ack/control/status/raw/interrupt/clear/undef-vector offsets, enable/priority/software interrupt bits, per-interrupt shift helpers, and set/clear/toggle register-layout notes.

Control flow: No code executes here. The definitions are consumed by the ASM9260 ICOLL driver to program enable bits, priorities, raw diagnostics, vector base, and interrupt completion.

State and persistence: Hardware state represented includes interrupt enable, priority, softirq generation, IRQ nesting/read-side-effect mode, current vector, raw interrupt lines, clear bits, and level acknowledge state.

Dependencies/integration: Assumes Linux `BIT()` macro availability from including code. It documents special register alias offsets and ICOLL semantics for ARM exception vector handling.

Risks and test signals: Validate `ASM9260_HW_ICOLL_CLEARn()` uses the expected set-register offset from including context, confirm priority changes are not applied while enabled, and test vector/level ack sequencing to avoid races when nested interrupts are enabled.
