<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/clk/bcm/Makefile

Purpose: This Makefile maps Broadcom clock Kconfig symbols to object files in the BCM clock driver directory.

Important APIs, types, and functions: The object mappings include BCM63xx gate/timer/core drivers, Kona core/setup plus BCM281xx and BCM21664 tables, iProc ARM PLL/PLL/ASIU helpers, BCM2711 DVP, BCM2835 CPRMAN and AUX drivers, Raspberry Pi firmware clocks, BCM53573 ILP, and iProc SoC-specific tables for Cygnus, HR2, NSP, NS2, and Stingray.

Control flow: Kbuild evaluates each `obj-$(CONFIG_...)` line and includes matching objects. `CONFIG_COMMON_CLK_IPROC` pulls the shared iProc helpers; SoC-specific configs add their descriptor files.

State and persistence behavior: The file has no runtime state. It persists build graph decisions from Kconfig to object linkage.

Dependencies and integration points: It depends on symbols defined in `Kconfig` and on helper/source files in the same directory. Several descriptors only make sense when their helper object is also selected.

Risks and test signals: Risks include omitting shared helper objects, compiling table files without their helpers, or using wrong config symbols. Test signals are successful Broadcom defconfig builds and linker coverage for each enabled DT compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/bcm/Makefile -->
