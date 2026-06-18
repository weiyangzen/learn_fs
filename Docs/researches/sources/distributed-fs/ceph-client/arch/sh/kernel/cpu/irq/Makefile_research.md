<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/Makefile

Purpose: builds SH CPU IRQ helper objects.

Important APIs/types/functions: `imask.o` always and `ipr.o` when `CONFIG_CPU_HAS_IPR_IRQ` is enabled.

Control flow: Kbuild includes the right interrupt-controller helpers for the CPU.

State and persistence: build-time only.

Dependencies/integration: integrates CPU IRQ controller support with platform IRQ setup files.

Risks: omitting `ipr.o` breaks platforms whose vectors depend on IPR priority registers.

Test signals: build configs with and without CPU_HAS_IPR_IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/irq/Makefile -->
