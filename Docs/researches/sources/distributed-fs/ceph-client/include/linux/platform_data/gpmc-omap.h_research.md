
# sources/distributed-fs/ceph-client/include/linux/platform_data/gpmc-omap.h

## Purpose
This header defines OMAP General-Purpose Memory Controller platform data. It describes chip-select timing, device timing, bus settings, wait-pin policy, and child devices attached to each GPMC chip select.

## Important APIs And Types
`GPMC_CS_NUM` is 8. `struct gpmc_bool_timings` captures extra delay/granularity booleans. `struct gpmc_timings` stores controller timings in nanoseconds, with `sync_clk` in picoseconds, and embeds boolean timing flags. `struct gpmc_device_timings` stores device datasheet timings in picoseconds/cycles plus extra-delay flags. Constants define burst lengths, device widths, multiplexing modes, wait-pin polarity, and invalid sentinel values. `struct gpmc_settings` describes burst, NAND, sync, wait, width, mux, and wait-pin settings. `struct gpmc_omap_cs_data` binds one chip select to settings, timings, child platform device, and platform-data size. `struct gpmc_omap_platform_data` contains all chip selects.

## Control Flow, State, And Persistence
The GPMC driver computes register values from device timing and settings, programs chip-select registers, and creates child devices. State lives in GPMC registers and child device registration; no persistent storage is managed here.

## Dependencies And Integration Points
It integrates OMAP board data with GPMC, NAND, NOR, FPGA, Ethernet, or other memory-mapped child devices using platform devices and timing translation.

## Risks And Test Signals
Risks include unit confusion between ns/ps/cycles, invalid wait-pin polarity, bad chip-select validity, and incorrect timing causing memory bus failures. Test signals include register timing dumps, child-device probe, NAND/NOR read/write stress, sync/asynchronous mode tests, wait-pin behavior, and multi-CS coexistence.
