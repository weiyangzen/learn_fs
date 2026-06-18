# sources/distributed-fs/ceph-client/sound/hda/codecs/hdmi/intelhdmi.c

## Purpose

This file specializes generic HDMI support for Intel display audio codecs. It requires i915 audio-component binding, maps HDA pins to display ports, enables Intel vendor features, fixes shared converter routing, and implements Intel silent-stream behavior.

## Important APIs, types, and functions

Key functions are `intelhdmi_probe`, `alloc_intel_hdmi`, `parse_intel_hdmi`, `intel_hsw_common_init`, platform probes for HSW/GLK/ICL/TGL/ADLP/BYT/CPT, `intel_pin2port`, `intel_port2pin`, `intel_pin_eld_notify`, `register_i915_notifier`, `i915_hsw_setup_stream`, `i915_pin_cvt_fixup`, `i915_hdmi_suspend`, `i915_hdmi_resume`, and `haswell_set_power_state`. Module parameter `enable_silent_stream` controls Kconfig-backed silent stream activation.

## Control flow

Probe first refuses binding without `codec->bus->core.audio_component`, preventing generic fallback. Platform-specific init sets `dp_mst`, vendor NID, port map, device count, power flags, and generic `hdmi_ops` overrides, then parses the codec and registers the i915 notifier. Hotplug arrives through i915 `pin_eld_notify`, which maps port/pipe to pin/device entry and calls generic presence reporting. HSW+ stream setup verifies D0, temporarily disables KAE around real stream programming if needed, and delegates to generic stream setup.

## State and persistence behavior

State is stored in `hdmi_spec`: vendor NID, port map, `intel_hsw_fixup`, `silent_stream_type`, and overridden ops. Suspend records whether KAE silent streams require preserved stream IDs and forced resume; resume restores stream format and DIG3 KAE if hardware lost them.

## Dependencies and integration points

The driver integrates with `sound/hda_i915.h`, DRM audio-component callbacks, Intel vendor verbs `0xf81/0x781`, HDA power management, and generic HDMI helpers. The HDA device table maps many Intel display codec IDs to platform models.

## Risks and test signals

Risks include i915 binding absence, deadlocks around silent streams, port-map errors on newer display generations, converter sharing after resume, vendor verb failures, and KAE power-reference leaks. Test with i915-bound HDMI/DP, DP MST, ADL-P KAE, GLK silent-stream-disabled path, runtime PM, S3 resume, and port-to-pin ELD notifications.
