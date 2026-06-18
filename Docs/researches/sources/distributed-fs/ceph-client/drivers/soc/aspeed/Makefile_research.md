# sources/distributed-fs/ceph-client/drivers/soc/aspeed/Makefile

## Purpose
This Makefile maps ASPEED SoC configuration symbols to object files.

## Important APIs, Types, And Functions
Object entries are `aspeed-lpc-ctrl.o`, `aspeed-lpc-snoop.o`, `aspeed-uart-routing.o`, `aspeed-p2a-ctrl.o`, and `aspeed-socinfo.o`.

## Control Flow
Kbuild includes objects according to `CONFIG_ASPEED_*` values. There is no runtime flow.

## State, Persistence, And Dependencies
Build state is determined by `.config` symbols from the ASPEED Kconfig file.

## Integration Points
Reached from `drivers/soc/Makefile` via ASPEED directory recursion.

## Risks
Symbol/object mismatches would break selected driver builds. Direct single-object mappings are otherwise low complexity.

## Test Signals
Build each ASPEED option as module or built-in where supported and verify expected outputs.
