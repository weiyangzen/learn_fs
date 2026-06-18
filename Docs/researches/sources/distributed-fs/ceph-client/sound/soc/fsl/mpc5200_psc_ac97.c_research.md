# sources/distributed-fs/ceph-client/sound/soc/fsl/mpc5200_psc_ac97.c

## Purpose
MPC5200 PSC AC97 CPU DAI driver. It configures the PSC into AC97 mode, exposes analog and IEC958 DAIs, implements AC97 bus read/write/reset operations, and uses the shared MPC5200 BestComm DMA backend.

## APIs, Types, and Functions
Global `psc_dma` stores the single AC97 PSC instance required by ALSA AC97 ops. Key functions are `psc_ac97_read()`, `psc_ac97_write()`, `psc_ac97_warm_reset()`, `psc_ac97_cold_reset()`, `psc_ac97_hw_analog_params()`, `psc_ac97_hw_digital_params()`, `psc_ac97_trigger()`, `psc_ac97_probe()`, `psc_ac97_of_probe()`, and `psc_ac97_of_remove()`. Two DAIs are registered: analog `mpc5200-psc-ac97.0` and SPDIF `mpc5200-psc-ac97.1`.

## Control Flow, State, and Persistence
OF probe creates DMA state, installs AC97 bus ops, registers DAIs, configures PSC SICR for AC97, and clears active slots. AC97 read/write serialize on `psc_dma->mutex`, poll PSC command/data-valid status bits, and access AC97 command/data registers. Analog hw_params computes AC97 slot enable bits based on stream direction and channel count. Trigger START/STOP updates `psc_dma->slots` and writes `ac97_slots`. Cold reset toggles board GPIO reset through `mpc5200_psc_ac97_gpio_reset()`, notifies PSC, enables RX/TX, waits, then warm-resets.

## Dependencies and Integration
Depends on ALSA AC97 bus ops, MPC52xx PSC register access, platform OF matching, `mpc5200_dma.h`, and board support for AC97 GPIO reset. Integrates with machine fabric such as `pcm030-audio-fabric.c` and WM9712-style AC97 codecs.

## Risks and Test Signals
Risks include the static single-instance `psc_dma`, polling timeouts on a wedged AC97 bus, no cleanup of DMA state if component registration fails after DMA creation, global AC97 ops conflicts, and slot-bit mistakes for multichannel analog playback. Test signals are AC97 codec reset/read/write, analog playback/capture slot activation, IEC958 playback, PSC AC97 SICR setup, and remove restoring AC97 ops and DMA resources.
