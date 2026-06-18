# sources/distributed-fs/ceph-client/sound/soc/codecs/cpcap.c

## Purpose
This file is the ALSA SoC codec driver for the Motorola CPCAP PMIC audio block. It exposes two DAIs, `cpcap-hifi` for stereo playback and `cpcap-voice` for mono voice playback plus mono/stereo capture, and maps the PMIC register-level audio routing into ASoC controls, DAPM widgets, DAPM routes, jack detection, and headset button reporting.

## Important APIs, types, and functions
The central private type is `struct cpcap_audio`, which holds the component, parent MFD regmap, vendor ID, cached voice codec clock/format settings, the `VAUDIO` regulator, headset and mic-bias IRQ numbers, and the `snd_soc_jack` object. `struct cpcap_reg_info` plus `cpcap_default_regs[]` define reset/default register programming.

Important helpers include the custom mux accessors `cpcap_output_mux_get_enum()`, `cpcap_output_mux_put_enum()`, `cpcap_input_right_mux_get_enum()`, `cpcap_input_right_mux_put_enum()`, `cpcap_input_left_mux_get_enum()`, and `cpcap_input_left_mux_put_enum()`. Clock and stream setup are handled by `cpcap_set_sysclk()`, `cpcap_set_samprate()`, `cpcap_hifi_hw_params()`, `cpcap_hifi_set_dai_fmt()`, `cpcap_voice_hw_params()`, `cpcap_voice_set_dai_fmt()`, and `cpcap_voice_set_tdm_slot()`. `cpcap_voice_call()` programs modem-to-codec routing for a special voice-call mode inferred from TDM slot arguments. Probe/remove and power hooks are `cpcap_soc_probe()`, `cpcap_soc_remove()`, `cpcap_codec_probe()`, and `cpcap_set_bias_level()`. Headset state is handled by `cpcap_hs_irq_thread()` and `cpcap_mb2_irq_thread()`.

## Control flow
The platform probe locates the parent device-tree `audio-codec` child and registers the component with two DAI drivers. Component probe allocates private state, gets `VAUDIO`, creates an ALSA jack, initializes the component regmap from the parent CPCAP MFD regmap, reads the vendor, requests threaded `hs` and `mb2` IRQs, resets audio registers, performs an initial headset-detection pass, and enables IRQ wake.

Audio reset writes the default register table, selects the default DAI mux mapping, sets HiFi and Voice clocks to 26 MHz, and programs both sample-rate generators to 48 kHz. HiFi `hw_params` updates sample rate; HiFi format setup enforces codec bit/frame provider mode and accepts I2S specially, falling back to 4-slot network mode. Voice `hw_params` updates sample rate and capture time slots. Voice TDM setup writes TX/RX slot masks, derives a sample rate from `slot_width * 1000`, and toggles modem voice-call routing if the slot pattern matches the driver heuristic.

DAPM controls power VAUDIO, DAI clocks, microphone bias, ADCs, DACs, PGAs, output amplifiers, headset charge pump, loopback, mono mixers, and playback/capture muxes. Output mux changes update three separate register banks so only one source among Off/Voice/HiFi/Ext is enabled for each physical output.

## State and persistence behavior
Runtime state is in CPCAP hardware registers, the parent MFD regmap cache, `struct cpcap_audio`, regulator mode, and ALSA jack status. The driver does not persist settings across reboots. Bias-level transitions switch `VAUDIO` between normal and standby unless a microphone is present, because mic/PTT detection needs `VAUDIO` in normal mode. IRQ wake enables headset and mic-bias events to wake the system.

## Dependencies and integration points
This file depends on the CPCAP MFD interface, parent regmap, `cpcap_get_vendor()`, Linux regulators, threaded IRQs, input key reporting, ALSA jack support, and ASoC component/DAI/DAPM APIs. Machine drivers integrate through DAI names `cpcap-hifi` and `cpcap-voice`, component/platform name `cpcap-codec`, device-tree child node `audio-codec`, and platform IRQ names `hs` and `mb2`.

## Risks and test signals
Key risks are custom mux setters touching multiple registers, voice-call detection based on a primitive TDM-slot heuristic, sample-rate reset self-clear failures, ST-vendor-specific DAC workaround sequencing, and headset/PTT detection races while bias and charge pump settle. The HiFi DAI format mask includes `SNDRV_PCM_FORMAT_S24_LE` rather than the usual `SNDRV_PCM_FMTBIT_S24_LE`, which is worth checking because `.formats` expects a bitmask. The voice format function logs unsupported provider/inversion cases but does not always return `-EINVAL`.

Useful test signals are successful component registration from a CPCAP MFD parent, `VAUDIO` regulator mode transitions, working 8 kHz through 48 kHz HiFi and Voice streams, correct output source selection, voice capture in one- and two-channel modes, modem-call TDM mode toggling expected register bits, headset/headphone/mic/button reports, wake from headset IRQs, and no register update errors when the ST workaround runs.
