# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra20_ac97.c

## Purpose
This is the Tegra20 AC97 ASoC controller driver. It exposes a stereo 16-bit playback/capture DAI, provides global AC97 bus read/write/reset operations, controls AC97 FIFOs for DMA playback/capture, and registers the Tegra PCM platform.

## Important APIs, types, and functions
Global `workdata` bridges the old ASoC AC97 bus callbacks to the active device. AC97 bus operations are `tegra20_ac97_codec_read()`, `tegra20_ac97_codec_write()`, `tegra20_ac97_codec_reset()`, and `tegra20_ac97_codec_warm_reset()`. Stream operations include trigger helpers for playback/capture and `tegra20_ac97_probe()` to attach DMA data. Regmap callbacks mark control, command, status, FIFO control, and FIFO registers as readable/writeable/volatile/precious. Platform probe configures reset, clock, regmap, codec reset/sync GPIOs, DMA addresses, hardware reset sequencing, AC97 ops, component, and PCM.

## Control flow
Probe gets the AC97 reset control and clock, maps registers, creates regmap, obtains codec reset and sync GPIOs, sets DMA FIFO addresses, asserts controller reset, enables the clock, deasserts reset, registers global AC97 ops, registers the component/DAI, registers PCM, then assigns `workdata`. Codec reads issue a command with read bit and poll `STATUS1_STA_VALID1`. Codec writes issue command/data and poll `CMD_BUSY`. Cold and warm resets toggle GPIO lines and poll codec ready. PCM triggers enable FIFO attention interrupts and controller DAC/stream bits for playback or capture FIFO full signaling for capture.

## State and persistence
The driver uses a cached regmap but has no runtime PM. Hardware stays clocked after probe until remove. AC97 bus state is effectively global through `workdata` and `snd_soc_set_ac97_ops()`, matching the old ASoC AC97 API's single-codec limitation.

## Dependencies and integration points
It depends on Tegra PCM helpers, DMAengine PCM data structures, GPIO descriptors named `nvidia,codec-reset` and `nvidia,codec-sync`, a reset control named `ac97`, a controller clock, regmap MMIO, and compatible `nvidia,tegra20-ac97`. Kconfig selects `SND_SOC_AC97_BUS` and DAS.

## Risks and edge cases
The global `workdata` means only one AC97 controller/codecs path is supported and callback use before assignment would be unsafe. Poll loops time out silently and may return stale readback rather than an error. Probe error handling calls `snd_soc_set_ac97_ops(NULL)` even for early failures. The driver uses non-devm component/PCM registration and manual cleanup. No PM support means idle power may be higher.

## Test signals
Verify AC97 codec reset/warm reset timing, register read/write operations with timeout instrumentation, stereo playback/capture DMA, FIFO underrun/overrun handling, remove cleanup, and failure paths for missing GPIOs/reset/clock.
