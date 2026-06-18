<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Makefile

Purpose: Selects XIVE object files for PowerPC builds.

Important APIs/types/functions: Always builds `common.o`; conditionally builds `native.o` for `CONFIG_PPC_XIVE_NATIVE` and `spapr.o` for `CONFIG_PPC_XIVE_SPAPR`.

Control flow: No runtime flow; Kbuild object selection only.

State and persistence: No state.

Dependencies and integration points: Connects XIVE Kconfig symbols to the common, native PowerNV, and sPAPR backend implementations.

Risks: Common code is always included when this directory is entered, so platform Makefile/Kconfig selection must only enter the directory when XIVE support is intended.

Test signals: Link/build tests for native-only, sPAPR-only, both-enabled, and XIVE-disabled platform configurations.

Source read size: 5 lines, 144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xive/Makefile -->
