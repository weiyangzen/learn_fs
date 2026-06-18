# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_i2s.h

## Purpose
This header defines Tegra20 I2S register offsets, control/status/timing/FIFO bit fields, and the private driver state structure used by the Tegra20 I2S ASoC driver.

## Important APIs, types, and functions
Offsets cover control, status, timing, FIFO scratch/control, PCM/network/TDM controls, and two FIFO data registers. Macros define FIFO enables, loopback/master mode, LRCK polarity, I2S/right/left/DSP bit formats, sample sizes, FIFO packing modes, interrupt/query bits, timing non-symmetric mode, channel bit count, FIFO clear, and FIFO attention levels. `struct tegra20_i2s` stores mutable DAI metadata, clock, DMA descriptors, regmap, and reset.

## Control flow
There is no executable flow. The `.c` file uses these macros in `set_fmt()`, `hw_params()`, trigger helpers, DMA setup, and regmap classification.

## State and persistence
The state struct persists per-controller resources and DMA configuration for the platform-device lifetime. Register persistence is maintained by the implementation's regcache during runtime PM.

## Dependencies and integration points
The header includes `tegra_pcm.h` for Tegra PCM integration and is private to the Tegra20 I2S implementation. The register definitions must align with Tegra20 hardware and DAS routing expectations.

## Risks and edge cases
The header exposes definitions for TDM/PCM/network registers not currently programmed by the driver, so future feature work must validate unused macros. Enum-like bit macros are directly written to hardware fields; bad values would affect serial format and FIFO operation.

## Test signals
Compile the I2S driver, compare register field encodings with hardware documentation, and use register traces from `set_fmt()`/`hw_params()` to validate bit-format, sample-size, and FIFO threshold macros.
