
# sources/distributed-fs/ceph-client/drivers/soc/imx/Kconfig

## Purpose
Defines i.MX SoC driver options for i.MX8M and i.MX9 family support.

## Important APIs, Types, and Functions
No runtime APIs. `SOC_IMX8M` and `SOC_IMX9` are tristate options depending on `ARCH_MXC || COMPILE_TEST`, defaulting on ARM64 i.MX builds, and selecting `SOC_BUS`. `SOC_IMX8M` also selects `ARM_GIC_V3` in an ARM multi-v7 condition.

## Control Flow
These symbols gate objects in the Makefile.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
Integrates with `soc-imx8m.o`, `imx93-src.o`, and `soc-imx9.o` build rules. Runtime drivers register SoC bus devices.

## Risks
Tristate SoC identity drivers may need to be available early enough for consumers; defaults target built-in on normal ARCH_MXC ARM64 builds.

## Test Signals
Kconfig dependency visibility, default selection on ARCH_MXC ARM64, compile-test, and object inclusion for each symbol.
