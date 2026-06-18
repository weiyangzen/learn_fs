# sources/distributed-fs/ceph-client/drivers/soc/nuvoton/Kconfig

## Purpose
Defines the Nuvoton WPCM450 SoC information driver build option.

## Important APIs, Types, And Functions
Kconfig `menuconfig WPCM450_SOC` is tristate, defaults to y on `ARCH_WPCM450`, and selects `SOC_BUS`.

## Control Flow
When enabled, the Makefile builds the WPCM450 SoC identification driver, which registers SoC model and revision data.

## State And Persistence
No runtime state in this file.

## Dependencies And Integration Points
Connects architecture selection to the Linux SoC bus framework.

## Risks
If disabled, user space loses standardized SoC identification for WPCM450 even though the platform may otherwise boot.

## Test Signals
With `ARCH_WPCM450`, config should default to enabled and select `SOC_BUS`.
