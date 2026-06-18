# sources/distributed-fs/ceph-client/drivers/soc/tegra/cbb/Makefile

## Purpose

This Makefile builds Tegra Control Backbone error handling drivers when CBB support is enabled.

## Important APIs, Types, and Functions

Inside `ifdef CONFIG_SOC_TEGRA_CBB`, it builds common `tegra-cbb.o`, Tegra194-specific `tegra194-cbb.o` when `CONFIG_ARCH_TEGRA_194_SOC` is enabled, and CBB2 `tegra234-cbb.o` when `CONFIG_ARCH_TEGRA_234_SOC` is enabled.

## Control Flow

The parent Tegra Makefile always descends into `cbb/`, but this file emits objects only when the CBB symbol is active.

## State and Persistence Behavior

There is no runtime state.

## Dependencies and Integration Points

It connects the common CBB helper layer with SoC-specific implementations and Kconfig architecture symbols.

## Risks and Edge Cases

The CBB2 implementation supports compatible data for newer SoCs too, but object selection is tied to `ARCH_TEGRA_234_SOC`; configs for newer SoCs must ensure this object is available through Kconfig selection or shared symbol behavior.

## Test Signals

Build Tegra194, Tegra234, and non-CBB Tegra configurations and verify object inclusion/exclusion.
