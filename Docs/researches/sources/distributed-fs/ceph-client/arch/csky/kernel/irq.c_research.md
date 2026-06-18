# sources/distributed-fs/ceph-client/arch/csky/kernel/irq.c

Purpose: architecture interrupt initialization and generic irqchip hookup.

Important APIs/types/functions: functions: `init_IRQ`

Control flow: Runtime flow is organized around `init_IRQ`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/init.h`, `linux/interrupt.h`, `linux/irq.h`, `linux/irqchip.h`, `asm/traps.h`, `asm/smp.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
