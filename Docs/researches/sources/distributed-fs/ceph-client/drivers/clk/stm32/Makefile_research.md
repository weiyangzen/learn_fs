# sources/distributed-fs/ceph-client/drivers/clk/stm32/Makefile

## Purpose
This Makefile maps STM32MP clock Kconfig symbols to their object files.

## Important APIs, Types, And Functions
It builds `clk-stm32mp13.o`, `clk-stm32mp1.o`, `clk-stm32mp21.o`, or `clk-stm32mp25.o` depending on the selected SoC family. Newer families also build `clk-stm32-core.o`; all listed families build `reset-stm32.o`.

## Control Flow
No runtime flow. Kbuild uses the selected symbols to include the correct object set.

## State And Persistence
No state. The rule controls which drivers and reset support are linked.

## Dependencies And Integration Points
It integrates with `stm32/Kconfig`. The object combinations show that MP13, MP21, and MP25 use shared core support, while MP15 uses the older `clk-stm32mp1.o` plus reset object.

## Risks
Changing object groupings can break shared-core linkage or reset provider availability. Build tests are needed because shared object dependencies differ by family.

## Test Signals
Build each `COMMON_CLK_STM32MP*` option individually and in combinations allowed by Kconfig, verifying reset support links successfully.
