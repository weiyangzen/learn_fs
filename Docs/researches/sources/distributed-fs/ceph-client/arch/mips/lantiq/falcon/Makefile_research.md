# sources/distributed-fs/ceph-client/arch/mips/lantiq/falcon/Makefile

Purpose: builds Falcon-specific platform support.

Important APIs/types/functions: includes `prom.o`, `reset.o`, and `sysctrl.o`.

Control flow: unconditional within the Falcon subdirectory selected by parent Makefile.

State and persistence: build-system only.

Dependencies and integration: supplies Falcon `ltq_soc_detect()`, reboot hooks, and clock/sysctrl initialization.

Risks: omitting any object breaks Falcon boot or reset behavior.

Test signals: Falcon defconfig link and boot tests.
