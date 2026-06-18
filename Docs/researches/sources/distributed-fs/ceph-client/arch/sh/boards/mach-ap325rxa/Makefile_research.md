<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/Makefile

Purpose: This Makefile builds AP325RXA machine support objects.

Important APIs/types/functions: It sets `obj-y := setup.o sdram.o`.

Control flow: When the AP325RXA machine directory is selected, Kbuild compiles both the C platform setup and SDRAM suspend/resume assembly.

State and persistence: It controls build inclusion only.

Dependencies and integration points: It depends on `CONFIG_SH_AP325RXA` selecting this directory from the board Makefile and integrates `setup.c` with `sdram.S`.

Risks and test signals: Omitting `sdram.o` would break suspend self-refresh support; omitting `setup.o` would lose board devices. Tests are AP325RXA build and suspend/resume boot coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ap325rxa/Makefile -->
