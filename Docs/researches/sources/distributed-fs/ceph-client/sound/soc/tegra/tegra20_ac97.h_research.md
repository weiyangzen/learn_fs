# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.h

## Purpose
This header defines Tegra20 AC97 controller register offsets, bit fields, FIFO controls, and the private state structure used by the AC97 platform driver.

## Important APIs, types, and functions
Offsets include `CTRL`, `CMD`, `STATUS1`, `FIFO1_SCR`, `FIFO_TX1`, and `FIFO_RX1`. Bit fields describe controller enables, cold/warm reset, command address/data/busy fields, status data/valid/ready bits, and FIFO interrupt/attention/force-empty controls. `struct tegra20_ac97` stores clock, playback/capture DMA descriptors, reset control, regmap, and reset/sync GPIO descriptors.

## Control flow
There is no executable flow. The `.c` file uses these definitions for AC97 command transactions, stream trigger enable/disable, DMA FIFO address calculation, and regmap access policy.

## State and persistence
The struct persists controller handles and DMA parameters for the lifetime of the platform device. Register persistence is implemented by the driver's regmap and always-on clock lifecycle.

## Dependencies and integration points
The header includes `tegra_pcm.h` for Tegra PCM/DMA integration. It is private to the Tegra20 AC97 driver and its ASoC/PCM registration path.

## Risks and edge cases
Macros model only the FIFO/channel subset used by the driver; additional AC97 streams would need new definitions and trigger logic. Register bit values must remain consistent with hardware because command read/write paths directly encode fields.

## Test signals
Build the AC97 driver and validate command field encoding, status decoding, and FIFO address offsets against hardware documentation or known-good register traces.
