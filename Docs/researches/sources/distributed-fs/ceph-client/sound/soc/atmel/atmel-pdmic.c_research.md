# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-pdmic.c

## Purpose
This driver exposes the Atmel SAMA5D2 PDMIC as a capture-only ASoC component and simple sound card using the dummy codec. It configures PDM microphone clocking, oversampling, sample size, gain, offset, filters, DMAengine capture, and overrun interrupt handling.

## Important APIs, Types, And Functions
State is `struct atmel_pdmic` and DT-derived `struct atmel_pdmic_pdata`. Important functions are `atmel_pdmic_dt_init()`, `atmel_pdmic_cpu_dai_startup()`, `atmel_pdmic_cpu_dai_prepare()`, `atmel_pdmic_platform_configure_dma()`, `pdmic_get_mic_volsw()`, `pdmic_put_mic_volsw()`, `atmel_pdmic_component_probe()`, `atmel_pdmic_cpu_dai_hw_params()`, `atmel_pdmic_cpu_dai_trigger()`, `atmel_pdmic_get_sample_rate()`, `atmel_pdmic_interrupt()`, and `atmel_pdmic_probe()`.

## Control Flow
Probe parses required mic frequency bounds and optional card name/offset, gets clocks, sets `gclk` to one third of `pclk`, maps regmap, requests IRQ, computes supported sample-rate bounds, registers the capture DAI, DMAengine PCM, and a one-link card. Startup enables clocks, clears control state, stores the active substream, and enables overrun interrupts. `hw_params` enforces mono, 16/32-bit formats, chooses OSR 64 or 128, selects pclk or gclk prescaler, and updates mode/DSPR registers. Trigger enables/disables PDM capture. Interrupt on overrun disables capture and stops the substream with xrun.

## State And Persistence
Software state includes clocks, regmap, active substream, physical DMA source, IRQ, and pdata. Hardware state includes PDM enable, clock source/prescaler, converted data register, DSP filter/gain/offset registers, and overrun interrupt state.

## Dependencies And Integration Points
It depends on OF properties `atmel,mic-min-freq`, `atmel,mic-max-freq`, optional `atmel,mic-offset` and `atmel,model`, clocks `pclk`/`gclk`, regmap MMIO, DMAengine PCM, dummy codec, and register definitions in `atmel-pdmic.h`.

## Risks And Test Signals
Risk areas include prescaler division assumptions, global static DAI rate fields modified at probe, substream pointer validity in IRQ, and gain table mapping. Test signals are card registration, mono capture at min/max computed rates, gain/filter controls updating registers, DMA source address correctness, and clean xrun handling on forced overrun.
