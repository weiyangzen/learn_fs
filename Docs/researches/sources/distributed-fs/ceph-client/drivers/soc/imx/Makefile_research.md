
# sources/distributed-fs/ceph-client/drivers/soc/imx/Makefile

## Purpose
Builds legacy ARM i.MX SoC ID code and selected i.MX8M/i.MX9 drivers.

## Important APIs, Types, and Functions
No runtime APIs. Rules: on ARM, `CONFIG_ARCH_MXC` builds `soc-imx.o`; `CONFIG_SOC_IMX8M` builds `soc-imx8m.o`; `CONFIG_SOC_IMX9` builds `imx93-src.o soc-imx9.o`.

## Control Flow
Build inclusion depends on architecture and Kconfig symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes symbols from the directory Kconfig and parent architecture config.

## Risks
The legacy `soc-imx.o` is ARM-only by Makefile guard; ARM64 i.MX identity goes through i.MX8M/i.MX9 paths.

## Test Signals
Build matrix for ARM ARCH_MXC, ARM64 i.MX8M, and ARM64 i.MX9 configurations.
