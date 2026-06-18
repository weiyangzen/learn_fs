
# sources/distributed-fs/ceph-client/drivers/soc/loongson/Kconfig

## Purpose
Defines Loongson-2 GUTS and power-management controller driver options.

## Important APIs, Types, and Functions
No runtime APIs. `LOONGSON2_GUTS` is tristate, depends on LoongArch or compile testing, and selects `SOC_BUS`. `LOONGSON2_PM` is bool, depends on LoongArch+OF and built-in input support.

## Control Flow
Symbols gate `loongson2_guts.o` and `loongson2_pm.o` in the Makefile.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
GUTS registers SoC identity. PM integrates with suspend and input power button handling.

## Risks
`LOONGSON2_PM` is bool and requires `INPUT=y`, so module-style deployments are not supported.

## Test Signals
Kconfig visibility, `SOC_BUS` selection, PM hidden when input is modular, and build coverage.
