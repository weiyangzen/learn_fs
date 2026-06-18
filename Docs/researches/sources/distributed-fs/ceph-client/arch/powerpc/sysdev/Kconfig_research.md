<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Kconfig -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Kconfig

Purpose: declares selected PowerPC sysdev configuration symbols and includes interrupt-controller Kconfig fragments.

Important APIs/types/functions: symbols `PPC4xx_PCI_EXPRESS`, `PPC4xx_HSTA_MSI`, `PPC_MSI_BITMAP`, `GE_FPGA`, and `FSL_CORENET_RCPM`; includes `xics/Kconfig` and `xive/Kconfig`.

Control flow: Kconfig dependency resolution enables hidden support symbols based on PCI/MSI/platform selections. `PPC_MSI_BITMAP` defaults to yes for MPIC, FSL PCI, or PowerNV with PCI MSI.

State and persistence: build-time configuration only. Resulting `.config` controls which sysdev objects are compiled.

Dependencies and integration points: feeds the sysdev Makefile and platform code. `FSL_CORENET_RCPM` enables Run Control/Power Management support, while XICS/XIVE includes expose interrupt controller options.

Risks: hidden bools without prompts rely on other platform Kconfig selecting them correctly. Missing defaults can silently omit support such as MSI bitmap allocation.

Test signals: expected objects appearing in `arch/powerpc/sysdev/` build output for representative configs and `allyesconfig`/platform defconfig coverage are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Kconfig -->
