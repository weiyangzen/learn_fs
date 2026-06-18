<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/Makefile -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/Makefile

Purpose: This Makefile builds EcoVec24 machine support objects.

Important APIs/types/functions: It sets `obj-y := setup.o sdram.o`.

Control flow: When EcoVec support is selected, Kbuild includes both platform setup and SDRAM suspend/resume support.

State and persistence: Build selection only; runtime state is implemented in the referenced source files.

Dependencies and integration points: It depends on `CONFIG_SH_ECOVEC` selecting the machine directory from `arch/sh/boards/Makefile`.

Risks and test signals: Missing either object can break board boot or suspend. Tests include EcoVec24 build, setup object linkage, and suspend/resume coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-ecovec24/Makefile -->
