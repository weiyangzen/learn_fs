# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_ahub.h

## Purpose
Defines Tegra30-family AHUB/APBIF register maps, Audio CIF bitfields, route enum values, exported helper prototypes, CIF configuration structure, SoC-data structure, and private AHUB state.

## Important APIs, Types, And Functions
The header declares TX and RX CIF enums, FIFO allocation/enable/disable/free APIs, route set/unset APIs, and CIF programming helpers. `struct tegra30_ahub_cif_conf` is the common parameter object for CIF bitfield composition. `struct tegra30_ahub_soc_data` selects reset count and CIF writer. `struct tegra30_ahub` stores clocks, resets, MMIO base, regmaps, and FIFO usage bitmaps.

## Control Flow
No executable flow exists. Constants and enums drive APBIF FIFO address arithmetic, XBAR route bit selection, and CIF register packing in `tegra30_ahub.c`.

## State And Persistence
The private state struct defines in-memory FIFO allocation bitmaps and hardware resource handles. Register persistence is implemented by the C file's regmap cache and runtime PM callbacks.

## Dependencies And Integration Points
Included by the AHUB implementation and by other Tegra audio drivers that call exported AHUB APIs. It uses `dma_addr_t`, regmap, reset, clock, device, and bitmap-related kernel types through included headers in the C file/build context.

## Risks
There is a suspicious enum spelling `TEGRA30_AHUB_RXcIF_APBIF_RX2` with lowercase `c`, which may break callers expecting the consistent `RXCIF` name. The header documents that the driver is simplistic and omits many hardware features; callers should not assume support beyond the exposed 16-bit stereo APBIF-oriented paths. Several Tegra124 masks are defined near Tegra30 masks, so field-mapping regressions are easy if macros are copied carelessly.

## Test Signals
Compile all users of the RX/TX CIF enums, validate generated CIF words for Tegra30 and Tegra124 layouts, and run APBIF FIFO allocation/routing tests that touch each enum value used by callers.
