# sources/distributed-fs/ceph-client/arch/csky/kernel/vdso/vdso.lds.S

Purpose: implements architecture support for `vdso.lds`.

Important APIs/types/functions: labels: `global`, `local`

Control flow: Control enters through `global`, `local`, follows the architecture ABI/register convention, and branches or returns into linked C/kernel entry points.

State and persistence: No durable storage is introduced; state is limited to CPU registers, stack frames, and caller-owned kernel objects.

Dependencies and integration: Depends on `asm/page.h`. It integrates with the C-SKY architecture port and generic Linux subsystems; there is no Ceph-specific runtime dependency despite the source snapshot path.

Risks: Main risk is architecture-specific behavior that generic CI may not exercise without target cross-build and boot/runtime coverage.

Test signals: C-SKY cross-build.
