# sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.c

Purpose: Shared Intel HDA DSP helper that wires ASoC HDMI front-end PCMs to legacy HDA HDMI codec converter control structures before building HDA codec controls.

Important APIs, types, and functions: When `CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC` is enabled, `hda_dsp_hdmi_pcm_handle()` scans card runtimes, skips BE links and non-playback PCMs, and returns the Nth FE PCM whose id contains `HDMI`. `hda_dsp_hdmi_build_controls()` obtains `struct hdac_hda_priv` from the component drvdata, iterates `hcodec->pcm_list_head`, assigns each `struct hda_pcm` to the corresponding FE PCM/device number or marks it invalid, toggles display power, and invokes `snd_hda_codec_build_controls()`.

Control flow and integration: Machine drivers call `hda_dsp_hdmi_build_controls()` from `late_probe` after HDMI BEs have captured the HDA HDMI component. This bridges the SOF topology's FE PCM numbering to the HDA codec layer so ELD/jack/control nodes bind to the right PCM devices.

State and persistence: The helper mutates in-memory `hda_pcm` entries by setting `pcm` and `device`. It has no persistent state and no private allocations.

Dependencies: ASoC card runtime iteration, HDA codec private structures, HD-audio display power helpers, and `hdac_hda` codec integration.

Risks: The PCM match is name-based using substring `HDMI`; topology naming changes can break mapping. Converter order is assumed to match FE HDMI enumeration order. Missing FE PCMs produce warnings and invalid devices, which may be acceptable for absent converters but indicate topology mismatches. Test signals include HDMI PCM ids, HDMI controls/ELD creation, display-power sequencing in dmesg, and successful imports from drivers using `SND_SOC_INTEL_HDA_DSP_COMMON`.
