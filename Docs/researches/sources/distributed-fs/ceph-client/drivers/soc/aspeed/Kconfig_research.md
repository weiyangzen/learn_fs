# sources/distributed-fs/ceph-client/drivers/soc/aspeed/Kconfig

## Purpose
This file defines ASPEED SoC support options for LPC control, LPC snoop, UART routing, P2A bridge control, and SoC information.

## Important APIs, Types, And Functions
Symbols include `ASPEED_LPC_CTRL`, `ASPEED_LPC_SNOOP`, `ASPEED_UART_ROUTING`, `ASPEED_P2A_CTRL`, and `ASPEED_SOCINFO`. Most driver options select `REGMAP` and `MFD_SYSCON`; socinfo selects `SOC_BUS`.

## Control Flow
The menu is available for `ARCH_ASPEED` or `COMPILE_TEST`. Driver options default to `ARCH_ASPEED`, making common BMC features enabled on ASPEED builds.

## State, Persistence, And Dependencies
Configuration choices persist in `.config`. Dependencies reflect syscon/regmap use and soc_bus registration.

## Integration Points
The ASPEED Makefile maps these symbols to the corresponding driver objects.

## Risks
`ASPEED_SOCINFO` contains duplicate `default ARCH_ASPEED`, which is harmless but redundant. Broad defaults can increase built-in surface on ASPEED platforms.

## Test Signals
Run ASPEED defconfig and COMPILE_TEST builds, inspect selected dependencies, and confirm each option produces its expected object.
