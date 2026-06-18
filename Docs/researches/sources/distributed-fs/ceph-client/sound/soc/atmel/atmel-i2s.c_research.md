# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-i2s.c

## Purpose
This is the Atmel SAMA5D2 I2S controller ASoC CPU DAI driver. It supports playback and capture through DMAengine PCM, handles I2S master/slave clocking, configures sample formats and mono mode, reports underrun/overrun interrupts, and registers DMA addresses for transmit/receive holding registers.

## Important APIs, Types, And Functions
Core state is `struct atmel_i2s_dev`, `struct atmel_i2s_gck_param`, and optional capability hooks in `struct atmel_i2s_caps`. Important functions are `atmel_i2s_interrupt()`, `atmel_i2s_set_dai_fmt()`, `atmel_i2s_get_gck_param()`, `atmel_i2s_hw_params()`, `atmel_i2s_switch_mck_generator()`, `atmel_i2s_trigger()`, `atmel_i2s_dai_probe()`, `atmel_i2s_sama5d2_mck_init()`, and `atmel_i2s_probe()`.

## Control Flow
Probe maps registers, initializes regmap, requests IRQ, gets `pclk` and optional `gclk`, applies clock mux capability, enables `pclk`, enables error interrupts, registers the DAI/component, fills DMA addresses, and registers DMAengine PCM. `set_fmt` records the DAI format. `hw_params` validates I2S format, master/slave mode, channel count, and PCM format, then updates `ATMEL_I2SC_MR`. Trigger starts/stops RX or TX and reference-counts master-clock generator enablement in master mode.

## State And Persistence
Persistent state includes regmap, clocks, DMA data, saved DAI format, selected GCK parameters, capabilities, and `clk_use_no`. Hardware state includes mode register fields, control register commands, interrupt masks/status, holding registers, and version register.

## Dependencies And Integration Points
It depends on OF compatible `atmel,sama5d2-i2s`, clocks `pclk`, `gclk`, optional `muxclk`, regmap MMIO, DMAengine PCM, and `dma-names`; a `rx-tx` DMA name marks half-duplex operation.

## Risks And Test Signals
Risks include only supporting I2S format, clock generator reference counting across simultaneous streams, nearest GCK rate selection, and cleanup after component registration failures. Test signals are probe version logging, playback/capture for all listed formats/rates, overrun/underrun interrupt logs when forced, master and slave clock modes, and half-duplex behavior when DT requests it.
