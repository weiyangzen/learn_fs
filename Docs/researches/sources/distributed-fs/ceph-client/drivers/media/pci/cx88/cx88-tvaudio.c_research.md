# sources/distributed-fs/ceph-client/drivers/media/pci/cx88/cx88-tvaudio.c

## Purpose
`cx88-tvaudio.c` programs the cx2388x audio DSP for analog TV/radio standards and manages stereo/SAP/NICAM mode selection. It converts V4L2 tuner audio mode requests into low-level `AUD_*` register recipes and runs a background monitor for standards that need software stereo follow-up.

## Important APIs, Types, And Functions
Public functions are `cx88_set_tvaudio()`, `cx88_newstation()`, `cx88_get_stereo()`, `cx88_set_stereo()`, and `cx88_audio_thread()`. Register helpers include `set_audio_registers()`, `set_audio_start()`, and `set_audio_finish()`. Standard-specific programming functions are `set_audio_standard_BTSC()`, `set_audio_standard_NICAM()`, `set_audio_standard_A2()`, `set_audio_standard_EIAJ()`, and `set_audio_standard_FM()`. `cx88_detect_nicam()` samples `AUD_NICAM_STATUS2`.

## Control Flow
Audio-standard setup mutes, writes `AUD_INIT`/reset, applies static register sequences, restarts audio DMA to avoid buzz, enables I2S output for blackbird or DAC output for analog, then restores shadowed volume. `cx88_set_tvaudio()` selects recipes from `core->tvaudio`: BTSC, A2/NICAM by world standard, EIAJ, FM, or I2S ADC. For BG/DK/M/I/L, it programs A2 mono first, then NICAM, samples NICAM status, and either keeps NICAM or falls back to A2 mono. `cx88_get_stereo()` reads `AUD_STATUS`, maps hardware mode to V4L2 tuner fields, and may call `cx88_dsp_detect_stereo_sap()`. `cx88_set_stereo()` honors manual override and adjusts standard-specific `AUD_CTL` bits or reprograms BTSC/NICAM recipes. The kthread wakes once per second and auto-switches A2 mono/stereo only when no manual mode is set.

## State, Persistence, And Dependencies
State is in `core->tvaudio`, `audiomode_manual`, `audiomode_current`, `use_nicam`, `astat`, `last_change`, shadow audio registers, and the audio kthread pointer. Dependencies include cx88 register helpers, V4L2 tuner modes, audio DMA helpers, DSP stereo detection, and module parameters `always_analog` and `radio_deemphasis`.

## Integration Points
`cx88-video.c` calls this file during initial setup, input changes, radio open, and frequency changes. V4L2 tuner get/set operations expose its stereo decisions to userspace. Blackbird cards depend on I2S pass-through setup for MPEG encoder audio.

## Risks
The register tables are hardware-specific and sparsely documented. Reprogramming resets audio state and must preserve mute/volume through shadow registers. NICAM detection is timing-sensitive. Manual mode prevents automatic kthread changes, so `cx88_newstation()` must clear it on channel/input changes. The `always_analog` option can alter blackbird pass-through expectations.

## Test Signals
Test BTSC stereo/SAP, PAL BG/DK/I/L with and without NICAM, FM deemphasis settings, I2S ADC audio-route boards, blackbird I2S output, tuner mode get/set via V4L2, channel-change reset behavior, kthread freeze/stop, and audible regressions such as buzz after DMA restart.
