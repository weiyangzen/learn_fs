# sources/distributed-fs/ceph-client/drivers/soc/microchip/Makefile

## Purpose
Maps Microchip PolarFire SoC Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
No C APIs. Object rules are `mpfs-irqmux.o`, `mpfs-sys-controller.o`, and syscon children `mpfs-control-scb.o mpfs-mss-top-sysreg.o`.

## Control Flow
Kernel build includes each object when its matching `CONFIG_POLARFIRE_SOC_*` symbol is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Consumes the symbols declared in the local Kconfig and defines which source files participate in the Microchip SoC driver build.

## Risks
The syscon symbol builds both MFD/syscon wrapper drivers as a pair. Splitting either file without changing this Makefile would change runtime child-device availability.

## Test Signals
Expected objects appear in built-in or module link output according to enabled config symbols.
