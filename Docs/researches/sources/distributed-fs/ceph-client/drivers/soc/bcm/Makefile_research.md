# sources/distributed-fs/ceph-client/drivers/soc/bcm/Makefile

## Purpose
This Makefile conditionally descends into the Broadcom STB SoC driver directory.

## Important APIs, Types, And Functions
It contains one object-directory rule: `obj-$(CONFIG_SOC_BRCMSTB) += brcmstb/`.

## Control Flow
Kbuild recurses into `brcmstb/` only when `SOC_BRCMSTB` is enabled.

## State, Persistence, And Dependencies
Build state is determined by `.config`. There is no runtime behavior.

## Integration Points
It is included from the top-level SoC Makefile and pairs with `drivers/soc/bcm/Kconfig`.

## Risks
If a brcmstb child option is selected without `SOC_BRCMSTB`, objects will not build. Current Kconfig gates child options under `SOC_BRCMSTB`.

## Test Signals
Build with `SOC_BRCMSTB=y` and `n`, and confirm brcmstb objects appear only when selected.
