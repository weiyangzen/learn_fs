# sources/distributed-fs/ceph-client/sound/soc/sunxi/sun50i-dmic.c

## Purpose
This is the platform ASoC CPU-DAI driver for the Allwinner H6 `sun50i` digital microphone controller. It exposes a capture-only DAI named `dmic`, programs the DMIC sample rate/channel/FIFO registers, registers DMA engine PCM support, and manages the controller's bus/module clocks and optional reset line through runtime PM.

## Important APIs, types, and functions
The central state is `struct sun50i_dmic_dev`, which holds the `dmic_clk`, `bus_clk`, optional reset, MMIO regmap, and RX DMA descriptor. `dmic_rate_s` maps ALSA rates to the controller's sample-rate field. The ASoC operations are `sun50i_dmic_startup()`, `sun50i_dmic_hw_params()`, `sun50i_dmic_trigger()`, and `sun50i_dmic_soc_dai_probe()`. `sun50i_dmic_probe()` maps registers, creates a 32-bit uncached MMIO regmap, acquires clocks, initializes DMA parameters at `SUN50I_DMIC_DATA`, deasserts reset, registers the component/DAI, enables runtime PM, and registers DMAengine PCM. Mixer controls expose four stereo channel volume controls using `SOC_DOUBLE_TLV`.

## Control flow
Probe allocates state, maps resources, initializes regmap and clocks, sets `dma_params_rx.addr` and `maxburst`, deasserts reset, registers the component, enables PM, and registers DMAengine PCM. On stream startup, non-capture streams are rejected, RX FIFO is flushed, and the counter register is reset. `hw_params()` programs channel count, HPF enable mask, channel enable mask, FIFO sample size and MSB mode, module-clock rate (`22.5792 MHz` for 44.1 kHz family, `24.576 MHz` for 48 kHz family), the hardware rate selector, DMA bus width, and oversampling mode. `trigger()` enables/disables DMA request generation and global DMIC enable for START/STOP-style commands.

## State and persistence
Hardware state lives in DMIC registers and is not cached (`REGCACHE_NONE`). Runtime suspend disables both clocks; runtime resume prepares the module and bus clocks. There is no explicit reprogramming after suspend beyond normal stream setup, so correctness depends on stream lifecycle and PM not losing configured registers while active. The DMA address width is mutable per `hw_params()`.

## Dependencies and integration points
The driver integrates with platform DT matching for `allwinner,sun50i-h6-dmic`, Linux clocks named `bus` and `mod`, optional reset controller, regmap MMIO, ASoC component/DAI registration, and `snd_dmaengine_pcm`. It exports capture formats `S16_LE` and `S24_LE`, rates from 8 kHz to 48 kHz, and up to 8 channels.

## Risks and edge cases
Unsupported playback, rates outside the hardcoded table, sample formats other than 16/24-bit, or physical widths other than 16/32 bits are rejected. `chan_en = (1 << channels) - 1` assumes validated channel counts. Clock rate failures become `-EINVAL`, losing the lower-level error code. Runtime PM has no register cache, so suspend during configured-but-inactive periods could require subsequent full stream setup. The code exposes only four stereo volume controls although capture supports eight channels.

## Test signals
Useful checks include DT probe with required clocks, capture open rejecting playback, 8/44.1/48 kHz families selecting the expected module clock and rate bits, S16/S24 DMA width selection, trigger toggling DRQ/global enable, runtime suspend/resume clock balancing, and DMA capture smoke tests at 1, 2, and 8 channels.
