# sources/distributed-fs/ceph-client/drivers/soc/atmel/Kconfig

## Purpose
This file defines Atmel/Microchip AT91 SoC support options for soc_bus identification and Special Function Register support.

## Important APIs, Types, And Functions
Symbols are `AT91_SOC_ID` and `AT91_SOC_SFR`. `AT91_SOC_ID` is a bool defaulting to `ARCH_AT91`; `AT91_SOC_SFR` is a tristate driver for SAMA5Dx SFR access.

## Control Flow
Kconfig exposes these options when `ARCH_AT91` or `COMPILE_TEST` is enabled. Selections drive the Atmel Makefile object list.

## State, Persistence, And Dependencies
Configuration persists in `.config`. `AT91_SOC_ID` affects early/subsys init registration; `AT91_SOC_SFR` affects module or built-in SFR/NVMEM support.

## Integration Points
These symbols build `soc.o` and `sfr.o`.

## Risks
`AT91_SOC_SFR` help mentions the module name `sfr`, while Kbuild object naming under the Atmel folder determines the actual module path. Dependencies are broad for compile testing.

## Test Signals
Check AT91 defconfigs, allmodconfig module naming, and COMPILE_TEST builds.
