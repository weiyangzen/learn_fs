<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/audio.h -->
# sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/audio.h

## Purpose
`audio.h` defines the WM8350 codec/audio register map and platform data. It covers clocking, FLL, DAC/ADC controls, input and output mixers, volume registers, anti-pop behavior, audio interface formatting, jack detect status, clock divider IDs, DAI IDs, audio IRQ numbers, and codec platform tuning.

## Important APIs, types, and functions
Public data types are `struct wm8350_audio_platform_data` and `struct wm8350_codec`. Macros define audio register addresses `0x28` through `0x74` plus jack status `0xe7`, field masks for FLL and clocks, DAC/ADC volume and mute bits, input/output mixer routing, AIF format and TDM controls, jack-detect IRQs `WM8350_IRQ_CODEC_*`, platform constants for VMID/discharge/tie-off behavior, and clock divider/source IDs.

## Control flow
The codec driver uses these fields while probing and during ALSA SoC DAI operations: configure VMID and anti-pop timing from platform data, set FLL/clock dividers, route mixers, update volume with VU bits, set AIF format, and service jack IRQs.

## State and persistence behavior
Codec routing, gains, mute state, clocks, FLL configuration, and jack status live in hardware registers. `struct wm8350_codec` stores the platform device and platform data pointer as runtime binding state.

## Dependencies and integration points
The header depends on `platform_device` and is embedded by `core.h`. It integrates with ASoC codec/DAI code, IRQ registration through WM8350 core, board platform data, and power-management register bits declared in `core.h`.

## Risks and test signals
Risks include clock-divider mistakes causing invalid sample rates, volume update bits not being set consistently across stereo channels, pop/click regressions from bad VMID timing, jack IRQ number drift, and routing loops. Test signals include ASoC probe, DAI format/rate tests, mixer control readback, suspend/resume audio path restoration, and jack-detect interrupt tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mfd/wm8350/audio.h -->
