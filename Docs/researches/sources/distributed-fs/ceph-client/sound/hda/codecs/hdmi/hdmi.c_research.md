# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/hdmi.c

## Purpose

This is the generic ALSA HDA HDMI/DisplayPort codec implementation. It discovers digital audio converters and HDMI/DP pins, builds playback PCM devices, exposes ELD and channel-map controls, handles jack and DRM audio-component notifications, programs HDMI/DP audio infoframes, and manages converter/pin assignment across hotplug and suspend/resume.

## Important APIs, types, and functions

Exported entry points include `snd_hda_hdmi_generic_alloc`, `snd_hda_hdmi_parse_codec`, `snd_hda_hdmi_generic_probe`, `snd_hda_hdmi_generic_build_pcms`, `snd_hda_hdmi_generic_build_controls`, `snd_hda_hdmi_generic_init`, `snd_hda_hdmi_generic_suspend`, `snd_hda_hdmi_generic_resume`, `snd_hda_hdmi_generic_remove`, `snd_hda_hdmi_setup_stream`, `snd_hda_hdmi_setup_audio_infoframe`, `snd_hda_hdmi_generic_pcm_prepare`, `snd_hda_hdmi_generic_pcm_cleanup`, `snd_hda_hdmi_check_presence_and_report`, and the audio-component helpers. The core state is `struct hdmi_spec`, `struct hdmi_spec_per_pin`, `struct hdmi_spec_per_cvt`, and `struct hdmi_pcm` from `hdmi_local.h`.

## Control flow

Probe allocates `codec->spec`, registers channel-map ops, parses AFG child nodes by collecting converters before pins, initializes per-pin locks/work/proc entries, and later builds PCMs and controls. PCM open chooses a free converter, binds it to the pin mux, assigns SPDIF controls, and narrows capabilities from ELD unless `static_hdmi_pcm` is set. Prepare revalidates routing, syncs display audio rate for audio-component users, writes channel mapping and infoframes, enables dynamic pin output, and programs stream format. Hotplug uses unsolicited events or DRM callbacks to refresh ELD, attach or detach PCMs, update controls, and report jack state. Suspend cancels repoll work; resume reinitializes codec state and senses each pin.

## State and persistence behavior

State is per-codec and in-memory: dynamic arrays of pins/converters, `pcm_bitmap`, `pcm_in_use`, ELD buffers, channel maps, pin setup flags, converter assignment flags, delayed repoll work, and audio-component registration flags. Module parameters control static PCM capability policy, audio-component binding, and forced pin connectivity. No disk persistence exists except optional procfs ELD visibility.

## Dependencies and integration points

The file integrates ALSA HDA core, HDA jack tables, HDA controller stream data, HDMI ELD parsing, IEC958/SPDIF controls, `hdac_chmap`, PM runtime, PCI quirks, and DRM audio components through `snd_hdac_acomp_*`. Vendor modules override `hdmi_ops` for Intel, NVIDIA, and Tegra behavior.

## Risks and test signals

Risks include converter sharing races, stale ELD data, MST device-entry mismatches, incorrect infoframe size/checksum, HBR setup regressions, suspend/resume routing loss, silent-stream conflicts, and audio-component notifier lifetime errors. Test signals are HDMI/DP hotplug, DP MST displays, ELD control content, channel-map controls, non-PCM/HBR playback, S3/runtime PM resume, dynamic PCM attach/detach, and systems in the force-connect quirk list.
