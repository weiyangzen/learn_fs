# sources/distributed-fs/ceph-client/include/dt-bindings/clock/tegra20-car.h

## Purpose
Provides Tegra20 Clock and Reset controller clock IDs for device-tree users. It maps older Tegra CAR module and PLL clocks to stable integers.

## Important APIs, Types, and Constants
The file exports `TEGRA20_CLK_*` macros, including CPU, AC97, RTC, timers, UARTs, GPIO, SDMMC, I2C, SPI, display, memory, PLL, audio, and TWD clocks. `TEGRA20_CLK_CLK_MAX` is 133. Some comments document aliases such as `TEGRA20_CLK_COP` as AVP and `TEGRA20_CLK_AUDIO` as `audio_sync_clk`.

## Control Flow and State
No runtime logic exists. The include guard `_DT_BINDINGS_CLOCK_TEGRA20_CAR_H` prevents duplicate expansion. Clock enable/rate state is owned by Tegra20 CAR hardware and the kernel clock driver.

## Dependencies and Integration Points
There are no includes. Integration is through DT source files and the Tegra20 CAR clock provider, which must use the same numbering when resolving clock specifiers.

## Risks and Test Signals
Because this header supports legacy DTs, even comments that explain aliases can be important for maintainers. Renumbering can break old boards silently. Test signals include old Tegra20 DTS builds, schema validation, and runtime probing of devices that depend on module clocks such as SDMMC, UART, display, and audio.
