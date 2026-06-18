# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-i2s-mcc.c

## Purpose
Microchip I2S Multi-Channel Controller CPU DAI driver. It exposes playback and capture DAIs for sam9x60/sama7g5 I2SMCC blocks, configures I2S/left-justified/TDM data framing, selects pclk or gclk clocking, and binds the hardware holding registers to dmaengine PCM.

## Important APIs, Types, And Functions
- `struct mchp_i2s_mcc_soc_data` carries SoC differences: number of data pin pairs and FIFO availability.
- `struct mchp_i2s_mcc_dev` persists regmap, pclk/gclk handles, DMA data, selected DAI format, sysclk/frame settings, TDM slots, channel count, ready wait queues, and gclk state flags.
- DAI ops are `mchp_i2s_mcc_set_sysclk`, `mchp_i2s_mcc_set_bclk_ratio`, `mchp_i2s_mcc_set_dai_fmt`, `mchp_i2s_mcc_set_dai_tdm_slot`, `mchp_i2s_mcc_startup`, `mchp_i2s_mcc_hw_params`, `mchp_i2s_mcc_trigger`, and `mchp_i2s_mcc_hw_free`.
- `mchp_i2s_mcc_config_divs()` searches pclk/gclk rounded rates using an LCM of sysclk and bclk, then programs IMCKDIV/ISCKDIV and source clock bits.
- `mchp_i2s_mcc_interrupt()` acknowledges stop-drain ready interrupts and wakes TX/RX wait queues.
- `mchp_i2s_mcc_probe()` maps registers, creates regmap, requests IRQ, gets clocks, parses OF match data and `microchip,tdm-data-pair`, registers the component/DAI and dmaengine PCM.

## Control Flow
Probe builds the device state, enables the peripheral clock for register access, registers the DAI, and sets DMA addresses to `THR` and `RHR`. Startup resets the IP only when neither direction is running. `hw_params` validates the requested format, clock-provider mode, channel count, sample format, TDM mask, FIFO mode, and DMA burst size; if another stream is already running it rejects mismatched mode registers. Trigger start enables clock and either TX or RX; trigger stop disables the stream and enables ready interrupts so `hw_free` can wait up to 500 ms for final data availability before disabling clocks.

## State And Persistence
Runtime state is in memory only: selected format, requested sysclk/frame length, TDM slots, active channel count, DMA maxburst, and gclk prepare/enable flags. Hardware configuration persists in MRA/MRB until reset or reprogramming. There is no disk persistence. Wait queues bridge interrupt state into stop cleanup.

## Dependencies And Integration Points
Depends on Linux ASoC, dmaengine PCM, regmap MMIO, clocks, IRQs, and OF compatible data. It integrates with machine drivers through standard DAI format/sysclk/TDM callbacks and with DMA via `snd_soc_dai_init_dma_data` and `devm_snd_dmaengine_pcm_register`.

## Risks
Clock-rate selection is central: bad gclk/pclk rounding or missing gclk can reject otherwise valid audio modes. Full-duplex mode is constrained by symmetric rate, sample bits, and channels and by exact MRA/MRB reuse when one stream is already active. TDM masks must be contiguous and identical for RX/TX; nonstandard daisy-chain layouts are rejected. Stop relies on ready interrupts and a timeout fallback; missed interrupts can delay clock shutdown. The optional gclk path logs a warning with a potentially stale `err` value when a non-defer `devm_clk_get("gclk")` fails.

## Test Signals
Useful signals include probe success and hardware version logging, `aplay`/`arecord` at 8 kHz through 192 kHz across S8/S16/S24/S32 formats, TDM slot validation, full-duplex mismatch rejection, runtime stop without ready timeouts, and DMA maxburst alignment across representative period sizes. Device-tree tests should cover both one-pair sam9x60 and FIFO-capable sama7g5 data.
