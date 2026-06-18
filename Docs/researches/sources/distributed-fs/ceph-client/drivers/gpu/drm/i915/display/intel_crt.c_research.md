# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.c

## Purpose
Implements analog VGA/CRT encoder and connector support for i915. It controls ADPA/PCH_ADPA/VLV_ADPA programming, mode validation, compute config, enable/disable sequencing, hotplug/DDC/load detection, DMI quirks, and connector/encoder initialization.

## Important APIs and functions
Public functions are `intel_crt_port_enabled()`, `intel_crt_init()`, and `intel_crt_reset()`. `struct intel_crt` embeds `struct intel_encoder`, tracks whether forced hotplug is required, and stores the ADPA register. Important internal paths include `intel_crt_get_hw_state()`, `intel_crt_get_config()`, `hsw_crt_get_config()`, `intel_crt_set_dpms()`, enable/disable hooks for native/PCH/HSW, `intel_crt_mode_valid()`, compute-config variants, hotplug detectors (`ilk_crt_detect_hotplug()`, `valleyview_crt_detect_hotplug()`, `intel_crt_detect_hotplug()`), EDID/DDC helpers, legacy `intel_crt_load_detect()`, and `intel_crt_detect()`.

## Control flow
`intel_crt_init()` chooses the ADPA register, probes whether the DAC can be enabled, allocates connector/encoder objects, initializes DRM connector and encoder callbacks, sets pipe masks/hotplug polling, installs DDI or legacy encoder hooks, optionally records LPT FDI polarity state, and resets hotplug bits. Detection first checks display availability/access and DMI skip quirks, powers the CRT domain, tries HPD where available, then analog EDID/DDC, and only uses load detect for forced pre-gen4 cases. Enable/disable sequences differ for simple ADPA programming, PCH split, and HSW DDI/PCH/FDI paths.

## State and persistence behavior
Persistent state includes ADPA register bits for DAC enable, pipe select, sync polarity, DPMS, hotplug configuration, `force_hotplug_required`, connector polling state, FDI RX config, and DRM connector/encoder state. Load detection temporarily mutates border color, vblank, and transcoder config, then restores them.

## Dependencies and integration points
The file depends on connector helpers, CRTC vblank helpers, DDI, FDI, PCH, GMBUS, hotplug IRQ, load detect, VGA sense, underrun reporting, panel fitting, and link bandwidth helpers. It integrates with DRM connector helper callbacks, encoder hooks, power domains, and atomic modeset sequencing.

## Risks and test signals
Risks include false-positive VGA detection, HPD polling loops on VLV, broken DDC behind KVM/DVI-I adapters, load-detect flicker and register restore failures, platform-specific FDI limits, and incorrect underrun reporting order around HSW enable/disable. Tests should include VGA hotplug/DDC, DVI-I shared DDC cases, forced load-detect, DMI skip machines, HSW/BDW FDI CRT modes, suspend/resume reset, and DPMS transitions.
