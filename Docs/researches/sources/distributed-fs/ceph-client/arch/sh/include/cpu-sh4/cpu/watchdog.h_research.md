<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/watchdog.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/watchdog.h

Purpose: maps SH-4 watchdog registers and bit meanings.

Important APIs/types/functions: `WTCNT`, `WTCSR`, `WTST`, `WTBST`, `WTCSR_TME`, `WTCSR_WT`, `WTCSR_RSTS`, `WTCSR_WOVF`, `WTCSR_IOVF` with endian/CPU conditional addresses.

Control flow: watchdog drivers read/write these addresses to start, refresh, stop, and inspect overflow/reset state.

State and persistence: state persists only in watchdog hardware registers across kernel code paths and possibly reset causes.

Dependencies/integration: integrates with SH watchdog driver code and CPU subtype/endian configuration.

Risks: register aliases differ across subtypes and byte order, so one wrong address can disable or accidentally reset the machine.

Test signals: verify watchdog probe, ping, timeout interrupt/reset, and endian-specific register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/watchdog.h -->
