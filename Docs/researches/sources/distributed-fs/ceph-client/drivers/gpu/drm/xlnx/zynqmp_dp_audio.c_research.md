# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_dp_audio.c

## Purpose

`zynqmp_dp_audio.c` adds optional ASoC/DMAengine PCM support for ZynqMP DisplayPort audio. It registers a CPU DAI, two DMAengine playback PCMs, a simple card, volume controls, and programs audio clocks/status/registers when playback starts.

## Important APIs, Types, And Functions

State is `struct zynqmp_dpsub_audio`, containing MMIO base, card, DAI/PCM/link names, DAI driver, PCM configs, links, component descriptors, enable mutex, enabled stream count, current rate, and two cached volumes. Public APIs are `zynqmp_audio_init()` and `zynqmp_audio_uninit()`. Runtime callbacks include `dp_dai_hw_params()`, `dp_dai_hw_free()`, `zynqmp_dp_dai_read()`, and `zynqmp_dp_dai_write()`.

## Control Flow

Init exits silently if no audio clock exists, maps `aud`, creates names, registers the CPU DAI, registers two DMAengine PCMs using `aud0`/`aud1`, builds a dummy-codec ASoC card, and restores platform driver data after card registration. `hw_params` accepts only 44.1 kHz or 48 kHz, prevents rate changes while streams are active, programs `aud_clk` to sample rate times 512, enables PM/runtime clocking, writes mixer volume and IEC958 channel status, configures two DP channels, writes audio N/M, and enables DP audio. `hw_free` decrements stream use, disables DP audio and clock on the last stream, and drops runtime PM.

## State And Persistence Behavior

Persistent state includes cached volumes, current sample rate, active stream count, and registered ASoC card/DAI/PCM objects. Hardware state includes audio mixer volume, channel status words, soft reset, DP audio channel count, and audio enable/N/M registers.

## Dependencies And Integration Points

It depends on ASoC core, DMAengine PCM, ALSA IEC958 definitions, clocks, PM runtime, display audio register macros, and DP audio helpers from `zynqmp_dp.c`. It integrates with the platform probe after DRM/display/DP setup.

## Risks And Test Signals

Risks include only S16_LE stereo 44.1/48 kHz support, clock-rate tolerance failures, no audio reset because reset breaks restart, devm card registration overwriting driver data, older DTs missing audio DMA channels, and multi-PCM rate sharing. Test sound-card registration with/without audio DMA nodes, playback on both PCMs, concurrent same-rate streams, rejected rate changes, volume writes while idle/active, suspend/resume, and DP sink audio interoperability.
