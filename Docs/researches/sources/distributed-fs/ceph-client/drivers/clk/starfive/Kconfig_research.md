# sources/distributed-fs/ceph-client/drivers/clk/starfive/Kconfig

## Purpose
This Kconfig file exposes build options for StarFive JH7100 and JH7110 clock drivers and their shared JH71x0 clock core.

## Important APIs, Types, And Functions
It defines `CLK_STARFIVE_JH71X0` as an internal bool, `CLK_STARFIVE_JH7100`, `CLK_STARFIVE_JH7100_AUDIO`, and JH7110 domain options for PLL, SYS, AON, STG, ISP, and VOUT. The SYS option selects `AUXILIARY_BUS`, the shared clock core, the JH7110 reset driver when reset controller support is enabled, and the PLL provider.

## Control Flow
There is no runtime flow. Kconfig dependency resolution controls which C files build and whether domain drivers are built-in or modules.

## State And Persistence
No runtime state. Defaults are tied to `ARCH_STARFIVE`, with `COMPILE_TEST` support for several built-in options.

## Dependencies And Integration Points
JH7100 audio depends on JH7100 core support. JH7110 AON/STG/ISP/VOUT depend on JH7110 SYS, and ISP/VOUT also require `JH71XX_PMU`. These dependencies mirror parent-clock and power-domain dependencies in the driver code.

## Risks
Incorrect dependency selection can build a domain driver without the parent clocks or reset infrastructure it needs. Module-capable child domains depend on built-in SYS support, so boot ordering and module autoloading matter.

## Test Signals
Kconfig tests should cover `ARCH_STARFIVE`, `COMPILE_TEST`, module builds for child domains, and reset-controller enabled/disabled combinations.
