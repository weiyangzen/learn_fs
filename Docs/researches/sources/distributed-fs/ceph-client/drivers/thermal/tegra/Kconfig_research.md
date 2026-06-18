# sources/distributed-fs/ceph-client/drivers/thermal/tegra/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/tegra/Kconfig` defines the menu and build-time configuration switches for NVIDIA Tegra thermal drivers. The source was read as a complete 28-line file.

## Important APIs, Types, and Functions

This is a Kconfig fragment rather than C code. It declares `TEGRA_SOCTHERM`, `TEGRA_BPMP_THERMAL`, and `TEGRA30_TSENSOR` under the "NVIDIA Tegra thermal drivers" menu. The menu is available when `ARCH_TEGRA` or `COMPILE_TEST` is enabled.

## Control Flow

There is no runtime control flow. The configuration choices control whether the common SOCTHERM platform driver, BPMP firmware-backed thermal driver, or Tegra30 TSENSOR driver is compiled. `TEGRA_BPMP_THERMAL` depends on `TEGRA_BPMP || COMPILE_TEST`; `TEGRA30_TSENSOR` depends on `ARCH_TEGRA_3x_SOC || COMPILE_TEST`.

## State and Persistence Behavior

Kconfig selections persist only in the kernel build configuration. They affect object inclusion and module availability, not runtime state.

## Dependencies and Integration Points

The file integrates with the parent thermal Kconfig and the Tegra architecture symbols. Its selections are consumed by `drivers/thermal/tegra/Makefile` and by conditional declarations/match entries in the SOCTHERM C sources.

## Risks and Edge Cases

Broad `COMPILE_TEST` coverage is useful but can hide missing runtime dependencies if dependencies are too weak. `TEGRA_SOCTHERM` has no explicit per-SoC dependency here, so the linked descriptor objects depend on architecture-specific symbols in the Makefile and C preprocessor.

## Test Signals

Build matrix coverage for `ARCH_TEGRA`, `COMPILE_TEST`, modular builds, and per-driver disabled/enabled combinations verifies this file. `make oldconfig` and `make menuconfig` should expose help text and dependencies as expected.
