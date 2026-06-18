# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.S

Purpose: implements architecture support for `vdso`.

Important APIs/types/functions: labels: `vdso_start`, `vdso_end`

Control flow: Control enters through `vdso_start`, `vdso_end`, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `linux/init.h`, `linux/linkage.h`, `asm/page.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
