# sources/distributed-fs/ceph-client/drivers/soc/amlogic/Kconfig

## Purpose
This file defines Amlogic Meson SoC driver configuration options for canvas, clock measurement, and SoC information drivers.

## Important APIs, Types, And Functions
Configuration symbols are `MESON_CANVAS`, `MESON_CLK_MEASURE`, `MESON_GX_SOCINFO`, and `MESON_MX_SOCINFO`. The clock measurement option selects `REGMAP_MMIO`, while the SoC information options select `SOC_BUS`.

## Control Flow
When the Amlogic menu is parsed, each option becomes available based on architecture and `COMPILE_TEST`. Defaults prefer enabling clock measurement and SoC info on `ARCH_MESON`, while canvas defaults to off.

## State, Persistence, And Dependencies
Chosen values are stored in `.config`. Build-time dependencies are `ARCH_MESON`, ARM/ARM64 for the appropriate SoC info driver, `COMPILE_TEST`, `REGMAP_MMIO`, and `SOC_BUS`.

## Integration Points
The corresponding Amlogic Makefile turns these symbols into `meson-canvas.o`, `meson-clk-measure.o`, `meson-gx-socinfo.o`, and `meson-mx-socinfo.o`.

## Risks
Incorrect dependency constraints can make platform-only code compile on unsupported architectures or hide useful compile-test coverage. Defaulting bool SoC info options on affects boot-time registration paths.

## Test Signals
Use ARM Meson, ARM64 Meson, and COMPILE_TEST configs to confirm symbols appear, select required dependencies, and produce expected objects.
