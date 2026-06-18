# sources/distributed-fs/ceph-client/drivers/clk/stm32/Kconfig

## Purpose
This Kconfig file controls common STM32MP clock-driver availability for STM32MP13, STM32MP15, STM32MP21, and STM32MP25 families.

## Important APIs, Types, And Functions
`COMMON_CLK_STM32MP` is a menuconfig depending on `ARCH_STM32 || COMPILE_TEST` and selecting `RESET_CONTROLLER`. Family-specific bools enable `COMMON_CLK_STM32MP135`, `COMMON_CLK_STM32MP157`, `COMMON_CLK_STM32MP215`, and `COMMON_CLK_STM32MP257` with ARM/ARM64 dependencies.

## Control Flow
No runtime control flow. Kconfig selects which STM32MP clock and reset objects the Makefile builds.

## State And Persistence
No runtime state. Defaults mostly follow `ARCH_STM32`; STM32MP215 defaults to `y` when its dependencies are met.

## Dependencies And Integration Points
The selections coordinate with `drivers/clk/stm32/Makefile`, which builds SoC-specific clock files, shared core files, and reset support. `RESET_CONTROLLER` is selected at the menu level because these clock drivers include reset-provider functionality.

## Risks
Architecture dependencies must match actual SoC support. Enabling family drivers under `COMPILE_TEST` can expose missing include or type dependencies across ARM and ARM64.

## Test Signals
Kconfig build matrices should include ARCH_STM32, ARM-only, ARM64-only, and COMPILE_TEST combinations for every family option.
