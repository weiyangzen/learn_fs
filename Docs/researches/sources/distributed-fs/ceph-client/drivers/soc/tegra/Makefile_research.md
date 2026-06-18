# sources/distributed-fs/ceph-client/drivers/soc/tegra/Makefile

## Purpose

This Makefile builds common Tegra SoC support and conditionally includes feature-specific objects.

## Important APIs, Types, and Functions

It always descends into `fuse/` and `cbb/` and builds `common.o`. Conditional objects include `flowctrl.o`, `pmc.o`, Tegra20/30 voltage couplers, and `ari-tegra186.o`.

## Control Flow

Kbuild includes subdirectories first, then object files based on the Kconfig symbols. The CBB subdirectory internally checks `CONFIG_SOC_TEGRA_CBB`.

## State and Persistence Behavior

There is no runtime state. This is build orchestration only.

## Dependencies and Integration Points

It depends on Tegra Kconfig symbols and integrates the SoC directory with fuse, CBB, PMC, flowctrl, OPP/regulator, and ARI code.

## Risks and Edge Cases

`obj-y += cbb/` always enters the directory, so its Makefile must guard object selection correctly. `common.o` always builds for Tegra SoC support and must keep dependencies broadly available.

## Test Signals

Build Tegra configs with and without flowctrl, PMC, voltage couplers, Tegra186, and CBB to confirm expected object graph.
