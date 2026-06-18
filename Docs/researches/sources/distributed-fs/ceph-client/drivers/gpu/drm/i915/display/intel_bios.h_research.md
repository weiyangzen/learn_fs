# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_bios.h

## Purpose
`intel_bios.h` declares the public VBT/BIOS parsing interface for i915 display code. It exposes parsed VBT queries while keeping raw VBT structures private to `intel_bios.c` and `intel_vbt_defs.h`.

## Important APIs, Types, and Functions
The header defines `enum intel_backlight_type` values used by parsed VBT backlight data. It declares VBT lifecycle functions, early/late panel initialization and finalization, VBT validation, display presence queries, DSC parameter lookup, encoder data lookup/iteration, encoder capability predicates, lane/HPD properties, DP AUX/link/boost helpers, HDMI DDC/boost/level-shift/TMDS helpers, and debugfs registration.

## Control Flow
Display initialization calls `intel_bios_init()`, connector/panel setup calls early and late panel init around EDID availability, encoder setup queries `intel_bios_encoder_data_lookup()` and capability helpers, and driver removal calls panel/display cleanup functions. Debugfs registration exposes raw VBT reads.

## State and Persistence
The header owns no state. It references opaque `intel_bios_encoder_data` objects stored in `display->vbt.display_devices` and panel data stored in `panel->vbt`.

## Dependencies and Integration Points
It depends on `linux/types.h` and forward declarations for DRM EDID, display, encoder, CRTC state, panel, `enum port`, and `enum aux_ch`. It is consumed broadly by display connector/encoder initialization, panel code, backlight code, DP/HDMI setup, and debugfs.

## Risks
The API returns parsed firmware data that may be absent or sanitized. Callers must handle zero, false, `PORT_NONE`, `AUX_CH_NONE`, and null encoder data returns. Version-dependent behavior is hidden in the implementation, so new users should not infer that every helper is meaningful on every platform.

## Test Signals
Compile coverage catches signature changes. Runtime coverage comes from connector initialization across VBT/no-VBT systems, eDP/DSI panels, HDMI/DP ports, debugfs `i915_vbt`, and module parameter firmware override cases.
