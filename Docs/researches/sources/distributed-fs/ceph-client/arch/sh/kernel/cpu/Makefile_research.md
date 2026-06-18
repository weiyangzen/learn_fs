<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/Makefile

Purpose: selects SH CPU-family support objects.

Important APIs/types/functions: routes `CONFIG_CPU_SH2`, `SH2A`, `SH3`, `SH4`, `SH4A`, shmobile, ADC, legacy CPG clock, IRQ, init, clock, fpu, pfc, proc.

Control flow: Kbuild descends into subtype folders and links common CPU services.

State and persistence: build-time state only.

Dependencies/integration: integrates CPU subtype support with generic SH kernel init.

Risks: wrong config expression can omit the only CPU probe or clock implementation for a platform.

Test signals: build each CPU family config and confirm expected objects are linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/Makefile -->
