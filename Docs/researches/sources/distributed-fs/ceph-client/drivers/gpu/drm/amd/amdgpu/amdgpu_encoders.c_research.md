# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_encoders.c

## Purpose
`amdgpu_encoders.c` contains legacy/non-DC display encoder helper logic. It links connectors to compatible encoders, tracks the active connector device mask, finds related connectors and external DP bridge encoders, adjusts panel modes to native timing, and decides when digital outputs need dual-link DVI/HDMI-style behavior.

## Important APIs, types, and functions
Important functions are `amdgpu_link_encoder_connector()`, `amdgpu_encoder_set_active_device()`, `amdgpu_get_connector_for_encoder()`, `amdgpu_get_connector_for_encoder_init()`, `amdgpu_get_external_encoder()`, `amdgpu_encoder_get_dp_bridge_encoder_id()`, `amdgpu_panel_mode_fixup()`, and `amdgpu_dig_monitor_is_duallink()`.

## Control flow
Connector/encoder setup walks DRM connector and encoder lists, compares AMDGPU ATOM device bitmasks, attaches compatible encoders, and initializes LCD backlight state for LCD-capable encoders. Active-device selection scans connectors for the current encoder and stores the intersection of encoder and connector device masks. Lookup helpers either use the active device mask or the initialization-time possible device mask. External encoder discovery scans for another encoder marked `is_ext_encoder` with overlapping device masks, and bridge ID reporting only exposes known Travis/Nutmeg bridge IDs. Panel fixup copies native mode timings while preserving blanking/sync offsets. Dual-link detection switches on connector type, HDMI information, DP sink type, and pixel-clock thresholds.

## State and persistence behavior
The file updates runtime DRM mode objects and AMDGPU encoder fields such as `active_device`, `native_mode`, and `adev->mode_info.bl_encoder`. It does not persist state outside the kernel mode configuration.

## Dependencies and integration points
It depends on DRM connector/encoder iteration, AMDGPU connector and encoder private structures, ATOM device masks, ATOM bridge encoder IDs, backlight initialization, and display mode helpers. It integrates with legacy KMS display bring-up paths rather than the newer DC-specific helpers.

## Risks and edge cases
Connector lookup assumes a connector is found before dereferencing in `amdgpu_dig_monitor_is_duallink()`. Device-mask mismatches can attach wrong encoders or miss valid ones. Pixel-clock thresholds encode single-link HDMI/DVI limits and must stay aligned with connector semantics. External bridge detection is limited to known encoder IDs. Mode fixup assumes the native panel mode is valid and initialized.

## Test signals
Signals include connector-to-encoder attachments, backlight setup for LCD/eDP panels, active-device changes during modesets, DP bridge ID detection, native panel mode timing in adjusted modes, single-link versus dual-link decisions across DVI/HDMI/DP connectors, and hotplug/modeset testing on legacy display hardware.
