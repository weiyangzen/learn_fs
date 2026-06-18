# sources/distributed-fs/ceph-client/drivers/clk/starfive/Makefile

## Purpose
This Makefile maps StarFive clock Kconfig symbols to object files.

## Important APIs, Types, And Functions
It builds `clk-starfive-jh71x0.o` for the shared core, JH7100 system and audio providers, and JH7110 PLL, SYS, AON, STG, ISP, and VOUT providers according to their config symbols.

## Control Flow
No runtime control flow. Kbuild includes the objects selected by configuration.

## State And Persistence
No state. It affects which driver registration code is linked or built as a module.

## Dependencies And Integration Points
The object mapping follows the dependencies in `Kconfig`. Child domain objects rely on exported symbols from the shared JH71x0 core and, for JH7110 resets, the SYS/header helper.

## Risks
If config dependencies and object rules diverge, undefined symbols or missing providers can result. The shared core must be built whenever any table-driven domain uses `starfive_jh71x0_clk_ops()` or `jh71x0_clk_get()`.

## Test Signals
All StarFive configs should be build-tested in built-in and module combinations allowed by Kconfig.
