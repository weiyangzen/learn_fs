# sources/distributed-fs/ceph-client/sound/soc/atmel/atmel-classd.c

## Purpose
This driver exposes the Atmel SAMA5D2 CLASSD amplifier as both an ASoC CPU DAI/component and a simple self-contained sound card using the dummy codec. It supports playback through DMAengine to the CLASSD transmit holding register and configures PWM, non-overlap timing, sample-rate clocks, mute, volume, mono, swap, deemphasis, and EQ controls.

## Important APIs, Types, And Functions
State is `struct atmel_classd` and DT platform data `struct atmel_classd_pdata`. Important callbacks are `atmel_classd_cpu_dai_startup()`, `atmel_classd_platform_configure_dma()`, `atmel_classd_component_probe()`, `atmel_classd_cpu_dai_hw_params()`, `atmel_classd_cpu_dai_prepare()`, `atmel_classd_cpu_dai_trigger()`, and `atmel_classd_probe()`. The component registers ALSA controls with TLV volume and enum EQ/mono options.

## Control Flow
Probe reads DT properties (`atmel,pwm-type`, `atmel,non-overlap-time`, `atmel,model`), maps MMIO into a cached regmap, gets `pclk`/`gclk`, registers the CPU DAI and DMAengine PCM, builds a one-link card, and registers it. Startup clears `CLASSD_THR` and enables clocks. `hw_params` selects the closest supported sample-rate entry, reprograms `gclk`, and updates `CLASSD_INTPMR`. Trigger enables/disables left/right output bits. Shutdown disables `gclk`.

## State And Persistence
Software state stores regmap, physical base for DMA, clocks, IRQ number, device pointer, and pdata. Hardware state includes CLASSD mode, interpolation/sample-rate register, transmit holding register, mute/output enable bits, and cached defaults. `regcache_sync()` restores cached values on resume.

## Dependencies And Integration Points
It depends on OF, clocks named `pclk` and `gclk`, regmap MMIO, generic DMAengine PCM, dummy codec, ASoC card registration, and register definitions in `atmel-classd.h`.

## Risks And Test Signals
Risk areas include clock-rate selection by nearest match, only accepting 16-bit physical audio, no explicit IRQ use despite requesting an IRQ number, and DT property validation. Test signals are successful card registration, playback at all supported rates, correct DMA slave address/width for mono vs stereo, controls changing registers, and resume restoring regmap state.
