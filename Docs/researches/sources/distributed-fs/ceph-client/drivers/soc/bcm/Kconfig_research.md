# sources/distributed-fs/ceph-client/drivers/soc/bcm/Kconfig

## Purpose
This file defines the Broadcom SoC driver menu and the top-level `SOC_BRCMSTB` option for Broadcom set-top-box SoCs.

## Important APIs, Types, And Functions
The key symbol is `SOC_BRCMSTB`, which depends on `ARCH_BRCMSTB`, `BMIPS_GENERIC`, or `COMPILE_TEST` and selects `SOC_BUS`. The file also sources the `brcmstb/Kconfig` submenu.

## Control Flow
Kconfig presents the Broadcom menu, then loads brcmstb-specific options. Enabling `SOC_BRCMSTB` permits child options such as PM support.

## State, Persistence, And Dependencies
Configuration persists in `.config`. Dependencies model Broadcom STB architecture support and soc_bus registration.

## Integration Points
The Broadcom Makefile recurses into `brcmstb/` when `SOC_BRCMSTB` is enabled.

## Risks
The top-level option says it enables support code while individual drivers are selected separately, so user expectations depend on submenu clarity. If `SOC_BUS` behavior changes, this option affects all brcmstb support.

## Test Signals
Run BRCMSTB and BMIPS defconfigs and check menu visibility, selected `SOC_BUS`, and child menu availability.
