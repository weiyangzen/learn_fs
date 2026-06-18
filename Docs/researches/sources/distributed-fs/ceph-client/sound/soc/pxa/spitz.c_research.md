# sources/distributed-fs/ceph-client/sound/soc/pxa/spitz.c

Purpose: implements the Sharp Zaurus Spitz/Borzoi/Akita machine driver using PXA2xx I2S and WM8750 codec, with GPIO-controlled jack/speaker/mic routing.

Important APIs/types/functions: global state stores selected jack and speaker functions plus mic and mute GPIO descriptors. Key functions are `spitz_ext_control`, `spitz_startup`, `spitz_hw_params`, user controls `spitz_get/set_jack` and `spitz_get/set_spk`, `spitz_mic_bias`, and `spitz_probe`.

Control flow: probe rejects non-Spitz/Borzoi/Akita machines, gets GPIOs, initializes default jack/speaker states, and registers a static ASoC card. Startup prevents capture when headphone-only mode is selected. hw_params sets WM8750 and PXA I2S sysclk to `SPITZ_AUDIO_CLOCK`. User mixer controls update DAPM pins and GPIO mute/mic-bias state.

State and persistence: jack/speaker mode is global static process state. GPIO outputs persist hardware mute and mic-bias control. ASoC DAPM pins reflect current route selection.

Dependencies and integration: depends on mach type checks, GPIO consumer API, WM8750 codec, PXA2xx I2S sysclk ID, and legacy platform alias `spitz-audio`.

Risks: global static card/state prevents multiple instances. Board detection uses legacy `machine_is_*` macros. GPIO polarity must match board wiring or audio routes mute incorrectly. Capture is mode-dependent and can return `-EINVAL`.

Test signals: probe on each supported Zaurus model, mixer controls for jack/speaker modes, headphone/speaker mute GPIO behavior, mic bias event behavior, and playback/capture routing through WM8750.
