# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/tegrahdmi.c

## Purpose

This file adapts generic HDMI support for NVIDIA Tegra SoC display audio codecs. Its main addition is notifying the Tegra HDMI driver of active HDA audio format through NVIDIA scratch-register vendor verbs.

## Important APIs, types, and functions

Key functions are `tegrahdmi_probe`, `tegra_hdmi_init`, `tegra_hdmi_build_pcms`, `tegra_hdmi_pcm_prepare`, `tegra_hdmi_pcm_cleanup`, and `tegra_hdmi_set_format`. It also reuses NVIDIA channel-map validation helpers and generic HDMI ops.

## Control flow

Probe allocates generic HDMI state. Tegra234-and-newer models enable DP MST, dynamic pin output, and host interrupt trigger control. Init parses converters and pins, enables digital converters, initializes per-pin state, sets depop delay, installs NVIDIA-style channel-map validation, and enables the DP infoframe workaround. PCM build calls generic PCM build and overrides playback prepare/cleanup so prepare programs generic stream/infoframe state then writes scratch format, while cleanup invalidates scratch format before generic cleanup.

## State and persistence behavior

State is in `hdmi_spec`, especially `hdmi_intr_trig_ctrl`, `dyn_pin_out`, `nv_dp_workaround`, and `dp_mst`. Hardware-visible state is persisted in scratch register bytes until updated: format bits, valid bit, and either toggled trigger bit or host interrupt verb.

## Dependencies and integration points

It depends on generic HDMI exports, NVIDIA vendor-defined scratch verbs, HDA converter control, and the external Tegra HDMI driver that consumes scratch-register/interrupt updates. Device IDs cover Tegra30 through Tegra264 and related SoCs.

## Risks and test signals

Risks include using the wrong NID for scratch access on MST vs non-MST hardware, missed interrupts when trigger semantics differ, stale valid bits after cleanup, duplicate channel-map assignment, and only overriding the first HDMI PCM. Test format changes, stream cleanup, Tegra234+ MST, old trigger-bit SoCs, DP/HDMI infoframes, and suspend/resume playback.
