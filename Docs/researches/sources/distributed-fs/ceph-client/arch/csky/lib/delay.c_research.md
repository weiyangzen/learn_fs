# sources/distributed-fs/ceph-client/arch/csky/lib/delay.c

Purpose: busy-wait delay calibration wrappers.

Important APIs/types/functions: functions: `__aligned`, `__const_udelay`, `__udelay`, `__ndelay`; exports: `__delay`, `__const_udelay`, `__udelay`, `__ndelay`

Control flow: Runtime flow is organized around `__aligned`, `__const_udelay`, `__udelay`, `__ndelay`, called by generic kernel subsystems through architecture hooks.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/kernel.h`, `linux/module.h`, `linux/init.h`, `linux/delay.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
