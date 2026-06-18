# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bdw_rt286.c

## Purpose
This is the Broadwell Wildcat Point machine driver for Realtek RT286. It defines a richer Broadwell DPCM card with system, offload, and loopback FEs plus one SSP0 codec BE.

## Important APIs, Types, and Functions
The driver defines static DAPM pins for speaker, headphone, headset mic, line jack, and two DMICs. `codec_link_init()` creates a headset jack supporting microphone, headphone, and button 0, then passes it to the RT286 component with `snd_soc_component_set_jack()`. `codec_link_exit()` clears jack detection. `codec_link_hw_params_fixup()` enforces 48 kHz stereo S16_LE on SSP0. `codec_link_hw_params()` sets codec sysclk to RT286 PLL at 24 MHz. Card suspend/resume callbacks detach and restore jack detection.

## Control Flow and Integration
DAI links include dynamic FE links for `System Pin`, `Offload0 Pin`, `Offload1 Pin`, and `Loopback Pin`, all using `haswell-pcm-audio`, plus a no-PCM BE from `ssp0-port` to `i2c-INT343A:00`/`rt286-aif1`. Probe fixes platform names from ACPI machine data, switches to SOF names when applicable, and registers the card.

## State, Persistence, and Dependencies
State is mostly static: the global `card_headset` jack and the card definition. Runtime persistent effects are codec jack registration and RT286 sysclk setup. Dependencies include ASoC DPCM, Broadwell/Haswell PCM platform support, RT286 codec support, and ACPI machine data.

## Risks and Test Signals
Risks include global jack state, hard-coded codec HID, and loss of offload/loopback routes if DAI names drift. The suspend callbacks tolerate missing codec DAI, but that also hides registration defects. Test signals include all four FE PCMs appearing, headset events through the codec, 48 kHz stereo BE constraints, offload playback working, loopback capture working, and suspend/resume maintaining jack reporting.
