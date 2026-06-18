# sources/distributed-fs/ceph-client/drivers/bus/Kconfig

## Purpose
Defines Kconfig entries for the kernel bus-driver menu. It selects architecture-specific SoC interconnect, external bus, firewall, configuration, and management-complex bus drivers and includes subordinate Kconfig files for fsl-mc and MHI.

## Important APIs, Types, And Functions
The file is declarative Kconfig. Key symbols in this subset include `ARM_CCI`, `ARM_CCI400_COMMON`, `ARM_CCI400_PORT_CTRL`, `ARM_INTEGRATOR_LM`, `BRCMSTB_GISB_ARB`, `DA8XX_MSTPRI`, and the included `FSL_MC_BUS` subtree. Other symbols cover MOXTET, HiSilicon LPC, i.MX, IXP4xx, MIPS CDMM, MVEBU, OMAP, Qualcomm, STM32, Allwinner, Tegra, TI, TS-NBUS, UniPhier, and Versatile Express.

## Control Flow
Kconfig evaluation controls build inclusion. Dependencies restrict symbols to relevant architectures or `COMPILE_TEST`, `select` enables helper subsystems such as `GENERIC_MSI_IRQ`, `REGMAP`, or `OF_DYNAMIC`, and `default` expresses platform defaults. The `source` statements include `drivers/bus/fsl-mc/Kconfig` and `drivers/bus/mhi/Kconfig`.

## State And Persistence
The state is the generated kernel configuration. It persists through `.config` and derived build artifacts, not through runtime code.

## Dependencies And Integration Points
This file connects architecture/platform configuration to `drivers/bus/Makefile`. The fsl-mc section depends on OF and supported architectures, MHI has its own included configuration, and individual entries coordinate with platform device-tree support and subsystem dependencies.

## Risks And Test Signals
Risks include incorrect dependency constraints, missing `select`s, silent build exclusion on valid platforms, and overly broad defaults that build unusable drivers. Test signals are `allyesconfig`, `allmodconfig`, architecture defconfigs, `COMPILE_TEST` builds, and confirming Makefile objects appear only under the intended symbols.
