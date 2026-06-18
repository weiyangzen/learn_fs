# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/nvhdmi.c

## Purpose

This file binds modern and transitional NVIDIA HDMI/DP codecs to the generic HDMI implementation, adding NVIDIA-specific channel-map validation, DisplayPort infoframe workaround behavior, audio-component integration, and model selection.

## Important APIs, types, and functions

Key functions are `nvhdmi_probe`, `probe_generic`, `probe_legacy`, `nvhdmi_chmap_cea_alloc_validate_get_type`, `nvhdmi_chmap_validate`, `nvhdmi_pin2port`, and `nvhdmi_port2pin`. `nvhdmi_audio_ops` wires generic audio-component bind/unbind and ELD notify callbacks.

## Control flow

Generic models allocate generic HDMI state, enable `dp_mst`, parse the codec, initialize pins, set dynamic pin output, install NVIDIA channel-map callbacks, enable the DP infoframe layout workaround, mark link-down-at-suspend, and initialize DRM audio-component binding. Legacy models use `snd_hda_hdmi_generic_probe` and the same NVIDIA post-configuration except audio-component setup.

## State and persistence behavior

Runtime state lives in `hdmi_spec`: `dyn_pin_out`, `nv_dp_workaround`, channel-map callbacks, `port2pin`, and audio-component registration for generic models. No persistent storage is used.

## Dependencies and integration points

It relies on `hdmi.c` generic exports, HDA channel-map APIs, DRM audio-component callbacks, and a large NVIDIA HDA device ID table. Pin-to-port mapping assumes contiguous pin NIDs beginning at 4.

## Risks and test signals

Risks include the contiguous pin mapping assumption, channel-map rejection for CA 0x00 stereo, DP infoframe compatibility, and generic-vs-legacy model classification. Test modern NVIDIA HDMI/DP hotplug, audio-component ELD callbacks, stereo and multi-channel channel-map controls, DP MST, suspend link-down behavior, and representative IDs from both model classes.
