<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Kconfig

## Purpose
This platform Kconfig file declares ARC platform selection for `plat-hsdk` and gates the platform objects and dependent drivers used by the ARC build.

## Important APIs, Types, and Functions
Exported Kconfig symbols are `ARC_SOC_HSDK`. They select `ARC_HAS_ACCL_REGS`, `ARC_IRQ_NO_AUTOSAVE`, `ARC_FPU_SAVE_RESTORE`, `CLK_HSDK`, `RESET_CONTROLLER`, `RESET_HSDK`, `HAVE_PCI` and depend on `ISA_ARCV2`.

## Control Flow
During Kconfig resolution, selecting the menuconfig enables the platform symbol, pulls in selected irqchip/GPIO/clock/reset/pinctrl support, and lets the platform Makefile compile the corresponding early machine descriptor. Child symbols choose CPU-card variants where present.

## State and Persistence Behavior
Kconfig files do not mutate runtime state. Their persistent output is the generated `.config` and derived headers such as `include/generated/autoconf.h`, which control compilation, linked objects, linker flags, and runtime code paths until the next configuration run.

## Dependencies and Integration Points
Dependencies and integration points include selected symbols `ARC_HAS_ACCL_REGS`, `ARC_IRQ_NO_AUTOSAVE`, `ARC_FPU_SAVE_RESTORE`, `CLK_HSDK`, `RESET_CONTROLLER`, `RESET_HSDK`, `HAVE_PCI`, dependency expressions `ISA_ARCV2`, sourced Kconfig files none, architecture Makefiles, board DTS choices, and drivers enabled by the selected platform capabilities.

## Risks
Risks include overusing `select` to force symbols whose dependencies are not met, missing dependency guards for CPU ISA or MMU assumptions, hidden build breakage when sourced Kconfig files move, and configuration combinations that compile a platform without the DT or driver support required to boot it.

## Test Signals
Run `make ARCH=arc olddefconfig` or `make ARCH=arm olddefconfig` for affected defconfigs, `make ARCH=... savedefconfig` to detect unintended symbol churn, and build representative platform defconfigs. For `arch/arm/Kconfig`, also test `multi_v7_defconfig`, NOMMU/v7-M configurations, and selected errata combinations.

Source read size: 14 lines, 340 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arc/plat-hsdk/Kconfig -->
