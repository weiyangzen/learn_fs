# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra30-car.h

## Purpose
Provides Tegra30 CAR clock IDs for device-tree references. It names legacy module clocks, PLL outputs, audio muxes, display, camera, and pad clocks.

## Important APIs, Types, and Constants
The `TEGRA30_CLK_*` namespace starts with `TEGRA30_CLK_CPU` 0, includes peripheral clocks such as UART, I2C, SPI, SDMMC, display, HDMI, USB, and memory, and ends with camera pad IDs `TEGRA30_CLK_CSIA_PAD` and `TEGRA30_CLK_CSIB_PAD` at 309 and 310. No function-like macros are exported.

## Control Flow and State
There is no executable flow. The include guard prevents duplicate definitions. Hardware state is controlled by the Tegra30 CAR driver and reset/clock registers.

## Dependencies and Integration Points
Self-contained header included by Tegra30 DTS/DTSI files and matched by the Tegra30 clock provider implementation.

## Risks and Test Signals
The IDs preserve legacy board ABI and include non-contiguous values. Do not reorder or close gaps. Test signals are DT compilation, schema validation, and runtime probing for display, audio, storage, USB, and camera users.
