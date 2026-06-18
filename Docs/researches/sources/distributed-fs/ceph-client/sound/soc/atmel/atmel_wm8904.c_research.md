# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel_wm8904.c

## Purpose
This is an Atmel machine driver for boards using an SSC controller with a WM8904 codec. It parses devicetree, allocates SSC audio support, configures the codec FLL/sysclk during `hw_params`, and registers a one-link ASoC card with DAPM widgets and DT-provided routing.

## Important APIs, Types, And Functions
Important data includes DAPM widgets, `atmel_asoc_wm8904_dailink`, and `atmel_asoc_wm8904_card`. Key functions are `atmel_asoc_wm8904_hw_params()`, `atmel_asoc_wm8904_dt_init()`, `atmel_asoc_wm8904_probe()`, and `atmel_asoc_wm8904_remove()`. It uses `SND_SOC_DAILINK_DEFS()` with empty CPU/platform components filled from DT and a WM8904 codec DAI named `wm8904-hifi`.

## Control Flow
Probe sets the card device, parses `atmel,model` and `atmel,audio-routing`, resolves `atmel,ssc-controller` and `atmel,audio-codec`, obtains the SSC alias ID, calls `atmel_ssc_set_audio(id)`, and registers the card. `hw_params` programs the WM8904 FLL from a 32.768 kHz MCLK to `sample_rate * 256`, then selects FLL as the codec system clock. Remove unregisters the card and releases the SSC.

## State And Persistence
State is mostly static card/dailink data updated with DT nodes. Runtime codec clock state is programmed per stream. SSC ownership persists from probe until remove through `atmel_ssc_set_audio()`/`put_audio()`.

## Dependencies And Integration Points
It depends on OF properties, WM8904 codec support, `atmel_ssc_dai.h`, and the SSC DAI/PCM stack. DAI format is I2S, normal bit/frame polarity, codec bit/frame provider (`SND_SOC_DAIFMT_CBP_CFP`).

## Risks And Test Signals
Risk areas include static global card data for multiple instances, alias ID errors, fixed 32.768 kHz FLL input assumption, and cleanup if card registration fails. Test signals are successful DT parsing, SSC allocation, WM8904 PLL/sysclk programming at stream start, DAPM routes matching board audio, and clean remove/reprobe.
