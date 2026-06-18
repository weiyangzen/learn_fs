# sources/distributed-fs/ceph-client/drivers/thermal/tegra/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/Makefile` maps Tegra thermal Kconfig symbols to kernel objects. The source was read as a complete 10-line file.

## Important APIs, Types, and Functions

The key build targets are `tegra-soctherm.o`, `tegra-bpmp-thermal.o`, and `tegra30-tsensor.o`. The composite `tegra-soctherm-y` includes `soctherm.o` and `soctherm-fuse.o`, then conditionally adds `tegra114-soctherm.o`, `tegra124-soctherm.o`, `tegra132-soctherm.o`, and `tegra210-soctherm.o`.

## Control Flow

There is no runtime flow. Kbuild evaluates `obj-$(CONFIG_...)` and `tegra-soctherm-$(CONFIG_ARCH_TEGRA_..._SOC)` to build the proper object set.

## State and Persistence Behavior

State is the generated build graph and module composition. The file does not create runtime or persistent state.

## Dependencies and Integration Points

It integrates the Tegra thermal Kconfig symbols with kbuild. It also matches conditional externs in `soctherm.h` and `of_match_table` entries in `soctherm.c`, ensuring descriptors exist only for selected SoC families.

## Risks and Edge Cases

If a compatible is enabled in `soctherm.c` without the matching descriptor object in this Makefile, link failures or missing runtime matches result. Conversely, descriptor objects compiled without matching C preprocessor entries add dead code.

## Test Signals

Kernel build tests for each Tegra architecture symbol and module/static configurations are the primary signal. `nm` or module object inspection can verify the composite contains the expected descriptor symbols.
