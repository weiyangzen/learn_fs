# sources/distributed-fs/ceph-client/sound/soc/samsung/pcm.c

## Purpose
Implements the Samsung S3C PCM controller ASoC DAI driver for two possible PCM instances. It configures DSP_A/DSP_B framing, serial clock source/dividers, DMA FIFO control, and platform-data GPIO/DMA integration.

## Important APIs, Types, And Functions
- `struct s3c_pcm_info` stores lock, device, MMIO base, SCLK-per-FS, idle clock mode, pclk/cclk, and DMA descriptors.
- `s3c_pcm_snd_txctrl()` and `s3c_pcm_snd_rxctrl()` enable/disable TX/RX DMA, FIFO, controller, dipstick thresholds, and serial clock.
- `s3c_pcm_trigger()` dispatches trigger commands to TX/RX control under lock.
- `s3c_pcm_hw_params()` supports only 16-bit samples and computes SCLK/SYNC dividers.
- `s3c_pcm_set_fmt()`, `s3c_pcm_set_clkdiv()`, and `s3c_pcm_set_sysclk()` implement format and clock APIs.
- `s3c_pcm_dev_probe()` validates platform ID, maps registers, enables clocks, fills DMA addresses, registers dmaengine PCM, enables runtime PM, and registers the DAI.

## Control Flow
Probe uses `pdev->id` to select static per-instance state and DMA arrays, optionally calls platform GPIO config, maps MMIO, enables audio-bus and PCM clocks, stores DMA FIFO addresses, registers DMA PCM, then registers one DAI. `hw_params` calculates dividers from chosen source clock and `sclk_per_fs`. `set_fmt` accepts only master DSP_A/DSP_B with inverted bit clock and normal frame, and records continuous/gated idle clock behavior. Trigger toggles DMA/FIFO enable bits for playback or capture.

## State And Persistence
Two static `s3c_pcm_info` entries and static DMA descriptor arrays persist for module lifetime. Per-instance state includes `sclk_per_fs` and `idleclk`. Hardware register state is not explicitly saved by PM despite runtime PM being enabled.

## Dependencies And Integration Points
Depends on platform data `s3c_audio_pdata`, Samsung DMA helper, clocks named `audio-bus` and `pcm`, ASoC DAI APIs, and `pcm.h` constants used by machine drivers.

## Risks And Edge Cases
- Only platform-data style probe is supported; no OF match table appears here.
- Runtime PM is enabled but no PM ops are defined, so clock gating is manual only at remove.
- `s3c_pcm_snd_txctrl()` and RX stop paths set `SERCLK_EN` when `!idleclk`, which looks counterintuitive and should be checked against hardware docs.
- Only 16-bit stereo rates are supported.
- Static instance arrays limit supported IDs to 0 and 1.

## Test Signals
Probe for ids 0/1, invalid id failure, DSP_A/DSP_B format setup, 8-96 kHz 16-bit playback/capture, clock source switching, DMA channel acquisition, and trigger start/stop register traces.
