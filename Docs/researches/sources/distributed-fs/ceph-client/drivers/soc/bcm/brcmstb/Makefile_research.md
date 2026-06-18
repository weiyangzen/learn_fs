# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/Makefile

## Purpose
This Makefile builds Broadcom STB common support and optional PM support.

## Important APIs, Types, And Functions
It unconditionally includes `common.o` and `biuctrl.o` when the brcmstb directory is built, and conditionally includes `pm/` for `CONFIG_BRCMSTB_PM`.

## Control Flow
Kbuild reaches this file only when `SOC_BRCMSTB` is enabled. It then builds common STB support and optional suspend/resume code.

## State, Persistence, And Dependencies
Build state comes from `SOC_BRCMSTB` and `BRCMSTB_PM`.

## Integration Points
Works with the Broadcom Kconfig hierarchy to compile shared brcmstb SoC code and PM support.

## Risks
Unconditional common object build means `common.o` and `biuctrl.o` must be valid for every `SOC_BRCMSTB` configuration. Missing PM directory coverage would break only when `BRCMSTB_PM` is enabled.

## Test Signals
Build with `SOC_BRCMSTB=y` and `BRCMSTB_PM` both enabled and disabled, and verify expected object inclusion.
