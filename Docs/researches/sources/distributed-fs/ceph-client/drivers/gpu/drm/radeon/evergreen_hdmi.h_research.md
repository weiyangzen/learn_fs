# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_hdmi.h

## Purpose
`evergreen_hdmi.h` is the private Radeon header that exposes DCE4/Evergreen HDMI and DisplayPort audio/video-infoframe helper functions to the rest of the driver. It contains no implementation logic; it defines the cross-file API contract implemented by `evergreen_hdmi.c`.

## Important APIs, Types, And Functions
The header forward-declares DRM and Radeon types used by the prototypes: `struct drm_encoder`, `struct drm_connector`, `struct drm_display_mode`, `struct radeon_device`, `struct radeon_crtc`, `struct radeon_hdmi_acr`, `struct r600_audio_pin`, and CEA audio descriptor types. Declared functions include HDMI/DP enable hooks (`evergreen_hdmi_enable()`, `evergreen_dp_enable()`), audio pin control (`dce4_audio_enable()`), ACR programming (`evergreen_hdmi_update_acr()`), AVI packet writing (`evergreen_set_avi_packet()`), SAD/speaker/latency programming, DTO setup, VBI/audio packet setup, color depth selection, and mute control.

## Control Flow
As a header, it contributes compile-time linkage only. Source files include it to get type-checked prototypes before calling into `evergreen_hdmi.c`. Include guards prevent multiple declaration in one translation unit.

## State And Persistence Behavior
No runtime state is stored here. The declarations describe routines that mutate Radeon display/audio hardware state and AFMT software state in their implementation file.

## Dependencies And Integration Points
The header is private to the Radeon driver and intentionally uses forward declarations instead of including all DRM/Radeon definitions. This reduces include coupling while allowing mode-setting, audio, and encoder code to call the DCE4 HDMI/DP helpers.

## Risks
Prototype drift is the main risk: if implementation signatures change without updating this header or vice versa, callers may fail to build or call with wrong assumptions. Because it exposes low-level hardware hooks, unclear parameter units such as `offset`, `clock`, and `bpc` can lead to misuse by call sites.

## Test Signals
Build coverage is the primary signal. Runtime coverage comes indirectly from the functions declared here: HDMI/DP audio enablement, infoframe emission, DTO programming, mute control, and hotplug/modeset paths.
