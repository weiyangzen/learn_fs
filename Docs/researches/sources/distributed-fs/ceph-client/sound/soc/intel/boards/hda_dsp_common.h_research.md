# sources/distributed-fs/ceph-client/sound/soc/intel/boards/hda_dsp_common.h

Purpose: Header for shared Intel HDA DSP HDMI helpers consumed by machine drivers that need to expose HDA HDMI codec controls from SOF/ASoC topologies.

Important APIs, types, and functions: The header declares `hda_dsp_hdmi_build_controls(struct snd_soc_card *card, struct snd_soc_component *comp)` when `CONFIG_SND_SOC_SOF_HDA_AUDIO_CODEC` is enabled. Otherwise it provides a static inline stub returning `-EINVAL`, allowing callers to compile while still failing predictably when HDA audio codec support is absent.

Control flow and integration: Drivers include this header and call the helper during card `late_probe`. It imports HDA codec and display-power definitions plus `hdac_hda` private types needed by the implementation.

State and persistence: The header defines no state. Its only behavioral impact is compile-time gating of HDMI control support.

Dependencies: ASoC, HDA codec core, HDA i915/display helpers, and `../../codecs/hdac_hda.h`.

Risks: Callers must handle the `-EINVAL` stub path, especially in builds without HDA audio codec support. Test signals include build coverage for both config branches and module namespace imports in callers that use the exported implementation.
