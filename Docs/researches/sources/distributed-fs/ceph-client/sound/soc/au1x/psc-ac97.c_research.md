# sources/distributed-fs/ceph-client/sound/soc/au1x/psc-ac97.c

## Purpose
ASoC CPU DAI for Au12x0/Au1550 PSC in AC97 mode. It implements PSC-specific AC97 codec read/write/reset, configures sample width and AC97 slots, starts/stops direction FIFOs, and registers a DAI instance named after the platform device.

## Important APIs, Types, And Functions
- Global `au1xpsc_ac97_workdata` backs AC97 bus ops.
- `au1xpsc_ac97_read/write/warm_reset/cold_reset` implement `snd_ac97_bus_ops` using PSC AC97 CDC/EVNT/RST registers.
- `au1xpsc_ac97_hw_params()` programs length and front L/R AC97 slots, rejecting mismatches while TX/RX are busy.
- `au1xpsc_ac97_trigger()` clears FIFO and starts/stops TX or RX.
- Probe selects PSC AC97 mode, records DMA IDs, clones the DAI template, and registers AC97 ops/component.

## Control Flow
Probe maps PSC registers, reads DMA resources, sets FIFO thresholds and device enable bits in `cfg`, preserves platform clock selection, switches PSC into AC97 mode, registers bus ops and DAI. Cold reset disables the PSC, asserts reset, enables PSC, waits for ready bits, and enables AC97. `hw_params` either validates an active configuration or disables/re-enables AC97 to apply new width/slot settings. Trigger start/stop manipulates PSC PCR and waits for busy clear on stop.

## State And Persistence
Configuration, rate, PM save registers, mutex, and DMA IDs live in `au1xpsc_audio_data`. The global workdata restricts practical use to one active AC97 PSC. Suspend saves `PSC_SEL` and disables PSC; resume restores selection and expects AC97 core reset to reinitialize.

## Dependencies And Integration Points
Depends on Alchemy PSC register definitions, ASoC AC97 bus, PSC DBDMA PCM, and platform DMA resources. Platform driver name is `au1xpsc_ac97`.

## Risks
Global AC97 bus context is not multi-instance safe despite DAI naming by device instance. Polling waits use busy loops and msleeps and can stall on broken hardware. Only front L/R slots are enabled. Resume relies on later AC97 reset rather than fully restoring hardware.

## Test Signals
Codec read/write retries, cold/warm reset on real PSC hardware, active-stream `hw_params` rejection, suspend/resume with codec rediscovery, and playback/capture FIFO stop wait.
