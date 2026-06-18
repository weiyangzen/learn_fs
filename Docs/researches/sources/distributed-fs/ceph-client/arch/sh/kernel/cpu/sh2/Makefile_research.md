<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/Makefile

Purpose: builds SH-2 CPU support.

Important APIs/types/functions: `ex.o`, `probe.o`, `entry.o`, SH7619 setup/clock, and optional J2 SMP support.

Control flow: Kbuild selects subtype setup and SMP object based on config.

State and persistence: build-time only.

Dependencies/integration: integrates SH-2 exception entry, CPU probe, subtype platform devices, and SMP hooks.

Risks: wrong object selection prevents boot or secondary CPU bring-up.

Test signals: build SH7619, J2, SMP and non-SMP configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh2/Makefile -->
