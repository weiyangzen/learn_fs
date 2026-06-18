# sources/distributed-fs/ceph-client/drivers/clk/sprd/Makefile

## Purpose
Maps Spreadtrum clock Kconfig symbols to build objects.

## Important APIs, Types, And Functions
`clk-sprd.o` is built from `common.o`, `gate.o`, `mux.o`, `div.o`, `composite.o`, and `pll.o` under `CONFIG_SPRD_COMMON_CLK`. SoC drivers are separate objects: `sc9860-clk.o`, `sc9863a-clk.o`, and `ums512-clk.o`.

## Control Flow
Kbuild links the common helper object when the common symbol is enabled, then links each SoC-specific platform driver according to its symbol.

## State And Persistence
No runtime state. Build output placement determines whether symbols are available built-in or as loadable modules.

## Dependencies And Integration Points
The SoC object files depend on exported symbols from the common helper modules (`sprd_clk_probe`, `sprd_clk_regmap_init`, and `sprd_*_ops`). This file is the integration point between Kconfig and those link dependencies.

## Risks And Edge Cases
Missing a helper object causes unresolved symbols in SoC modules. Adding a new SoC driver requires both Kconfig and Makefile updates. If helper code is modular while a SoC driver is built-in, symbol availability must remain valid through Kconfig dependencies.

## Test Signals
Build logs should show `clk-sprd.o` plus selected SoC objects. `modinfo` should work for modular builds, and no unresolved symbol warnings should appear at link or module load time.
