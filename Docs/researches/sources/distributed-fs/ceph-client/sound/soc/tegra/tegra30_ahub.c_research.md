# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_ahub.c

## Purpose
Implements the Tegra30/Tegra114/Tegra124 AHUB/APBIF platform driver and exported helper API for FIFO allocation, FIFO enable/disable, XBAR source routing, CIF configuration, runtime PM, clocks, resets, and child device population.

## Important APIs, Types, And Functions
Exports `tegra30_ahub_allocate_rx_fifo()`, `enable/disable/free_rx_fifo()`, equivalent TX functions, `tegra30_ahub_set_rx_cif_source()`, `tegra30_ahub_unset_rx_cif_source()`, `tegra30_ahub_set_cif()`, and `tegra124_ahub_set_cif()`. Probe initializes a singleton `static struct tegra30_ahub *ahub`, APBIF and AHUB regmaps, bulk clocks, and resets. Regmap callbacks classify APBIF FIFO/status/control registers and AHUB route registers.

## Control Flow
Probe matches SoC data, allocates the singleton, copies reset descriptors, gets clocks and resets, maps APBIF and AHUB MMIO resources, creates cache-only regmaps, enables runtime PM, and populates child devices. Runtime resume asserts resets, enables clocks, waits briefly, deasserts resets, marks regmaps dirty, and syncs caches; suspend cache-disables regmaps and disables clocks. FIFO allocation finds a free bit, records DMA channel name and FIFO register address, configures APBIF channel packing/threshold and CIF format under runtime PM, and returns the selected CIF enum. Routing writes one TX bit into the selected `AUDIO_RX` register.

## State And Persistence
The driver uses a global singleton pointer and bitmaps for RX/TX FIFO allocation state. Regmap cache preserves APBIF/AHUB register programming across runtime PM. FIFO allocation bitmaps live only in memory and reset on driver reprobe.

## Dependencies And Integration Points
Depends on common clock, reset, regmap, runtime PM, OF platform population, and ASoC header definitions. Exported symbols are consumed by Tegra PCM/I2S/SPDIF-style drivers to allocate DMA-facing APBIF FIFOs and route AHUB CIF sources. SoC data selects reset count and CIF bit layout for Tegra30/114 versus Tegra124.

## Risks
Global singleton state prevents multiple independent AHUB instances and requires callers to run only after probe. Bitmap allocation/free is not protected by a lock, so concurrent FIFO allocation could race. FIFO free does not disable the FIFO or clear routing, so callers must sequence disable/unroute/free correctly. The implementation supports a deliberately limited 16-bit stereo APBIF configuration despite broader hardware capability. Error paths after `of_platform_populate()` are minimal because populate return is ignored.

## Test Signals
Test probe on all compatible strings, runtime PM suspend/resume with active routes, concurrent or repeated FIFO allocation until `-EBUSY`, FIFO enable/disable bit changes, RX route set/unset register values, and Tegra124 CIF field positioning versus Tegra30 field positioning.
