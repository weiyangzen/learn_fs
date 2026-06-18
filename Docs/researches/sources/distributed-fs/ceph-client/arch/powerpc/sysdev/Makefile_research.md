<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Makefile

Purpose: selects and groups PowerPC sysdev object files according to Kconfig symbols.

Important APIs/types/functions: object assignments for MPIC/MSI/MSGR, ePAPR HV PIC, DART, Freescale SoC/PCI/PMC/RCPM/LBC/GTM/RIO, CPM/CPM2/GPIO, DCR, XICS/XIVE subdirectories, and suspend-only `6xx-suspend.o`.

Control flow: Kbuild expands `obj-$(CONFIG_*)` and helper variables such as `mpic-msi-obj-*` and `fsl-msi-obj-*` to compile the correct platform support set. The file includes MPIC twice, once for base/MSI and once with message registers, relying on Kbuild duplicate handling.

State and persistence: build graph only. It determines which runtime drivers and low-level assembly helpers exist in a kernel image.

Dependencies and integration points: consumes symbols from sysdev Kconfig and broader arch/platform Kconfig. Subdirectory entries hand off to XICS/XIVE/GE FPGA Makefiles.

Risks: duplicate or missing object selections can cause link omissions or redundant object references. Conditional suspend object selection must match symbols exported by platform suspend code.

Test signals: build coverage across pSeries, PowerNV, FSL BookE, 4xx, CPM, and suspend configs; link success; and expected module/builtin object presence validate this Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/Makefile -->
