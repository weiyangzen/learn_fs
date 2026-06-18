# sources/distributed-fs/ceph-client/arch/csky/kernel/vmlinux.lds.S

Purpose: kernel link layout for text/data/init/BSS, vectors, and C-SKY memory regions.

Important APIs/types/functions: functions: `AT`; macros: `VBR_BASE`, `ITCM_SIZE`

Control flow: Control enters through architecture entry labels, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `asm/vmlinux.lds.h`, `asm/page.h`, `asm/memory.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
