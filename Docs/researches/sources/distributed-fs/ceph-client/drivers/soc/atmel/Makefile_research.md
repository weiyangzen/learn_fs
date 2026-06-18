# sources/distributed-fs/ceph-client/drivers/soc/atmel/Makefile

## Purpose
This Makefile maps Atmel/Microchip AT91 SoC options to object files.

## Important APIs, Types, And Functions
`obj-$(CONFIG_AT91_SOC_ID) += soc.o` and `obj-$(CONFIG_AT91_SOC_SFR) += sfr.o`.

## Control Flow
Kbuild includes each object according to the selected config symbol.

## State, Persistence, And Dependencies
Build state comes from `.config`. There is no runtime state.

## Integration Points
Reached conditionally from `drivers/soc/Makefile` when `CONFIG_ARCH_AT91` is enabled.

## Risks
If `AT91_SOC_SFR` is enabled only through COMPILE_TEST but parent directory recursion is gated by `ARCH_AT91`, it may not build from the top-level Makefile unless another path recurses into atmel. That coupling should be kept in mind when changing recursion rules.

## Test Signals
Build AT91 defconfig and COMPILE_TEST configurations that enable each symbol.
