# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_connectors.c

## Purpose

`radeon_connectors.c` implements Radeon DRM connector behavior for VGA, DVI/HDMI, DisplayPort/eDP/LVDS, TV, DP bridges, and legacy connectors. It owns connector initialization, detect callbacks, mode enumeration, mode validation, property handling, EDID retrieval, HPD handling, scratch-register updates, and connector destruction for both AtomBIOS and COMBIOS topology paths.

## Important APIs, Types, and Functions

- `radeon_connector_hotplug()` handles HPD polarity and DisplayPort retraining for already-enabled DP sinks.
- `radeon_get_monitor_bpc()` derives effective BPC from EDID, connector type, ASIC generation, HDMI deep-color rules, TMDS clock limits, and module policy.
- EDID/mode helpers include `radeon_connector_get_edid()`, `radeon_connector_free_edid()`, `radeon_ddc_get_modes()`, `radeon_get_native_mode()`, `radeon_fp_native_mode()`, and `radeon_add_common_modes()`.
- `radeon_connector_set_property()` handles coherent mode, audio, dither, underscan, TV standard, load detect, TMDS PLL source, scaling mode, and output CSC; `radeon_lvds_set_property()` handles panel scaling.
- Family-specific callbacks cover LVDS, VGA, TV, DVI/HDMI, and DP/eDP: `radeon_lvds_detect()`, `radeon_vga_detect()`, `radeon_tv_detect()`, `radeon_dvi_detect()`, `radeon_dp_detect()`, their get-modes functions, and their mode-valid functions.
- `radeon_connector_analog_encoder_conflict_solve()` prevents two analog connectors from simultaneously claiming a shared DAC/TVDAC.
- DP helpers include `radeon_connector_encoder_get_dp_bridge_encoder_id()`, `radeon_connector_is_dp12_capable()`, AUX late registration, and AUX unregister.
- `radeon_add_atom_connector()` and `radeon_add_legacy_connector()` allocate and register DRM connectors, attach helpers/properties, wire DDC/AUX/router data, set polling behavior, and record Radeon connector-private state.

## Control Flow

Firmware parsing calls one of the connector constructors. The constructors skip unknown or disabled-TV connectors, merge duplicate connector IDs, detect shared DDC lines, look up DDC buses, allocate digital private data where needed, choose connector funcs/helpers by connector type, attach user-visible properties, set interlace/doublescan and polling flags, register the connector, and initialize DP AUX when applicable.

Detect callbacks acquire runtime PM unless called from the poll worker. LVDS/eDP checks native panel validity and EDID/DPCD. VGA prefers DDC and optionally performs DAC load detect on forced probes. DVI/HDMI handles DDC, broken EDID, analog/digital selection, shared DDC filtering, HPD-without-DDC retry scheduling, DAC load detection, BIOS EDID fallback, and audio detection. DP handles eDP panel power, DP bridges, native DP sinks, passive adapters, HPD, DPCD, AUX, and DDC probing.

Mode enumeration prefers EDID. Panels repair or synthesize native modes, then add scaled common modes. TV exposes common modes on newer ASICs or 800x600 on older ones. Mode validation applies panel bounds, scaling policy, max pixel clock, TMDS/DVI/HDMI limits, RV100 DVI clock concerns, and DP bandwidth checks.

## State and Persistence Behavior

`struct radeon_connector` persists EDID cache, DDC bus, AUX status, HPD record, router state, supported device mask, connector object ID, shared-DDC state, DAC load-detect state, analog/digital selection, audio/dither properties, and digital connector-private data. Connector status is mirrored into AtomBIOS or COMBIOS scratch registers for every possible encoder. User property changes persist in connector/encoder private fields and are applied on later modesets.

## Dependencies and Integration Points

The file integrates with DRM connector helpers, EDID, DP AUX/MST helpers, runtime PM, switcheroo DDC, Radeon DDC/router/HPD/DP/audio helpers, Atom/COMBIOS scratch register code, external encoder setup, module parameters such as `radeon_audio` and `radeon_deep_color`, and firmware-derived encoder capabilities.

## Risks and Edge Cases

- HPD hotplug uses unprotected `connector->dpms` state.
- Shared DDC and analog/digital inference are heuristic and board-layout dependent.
- DAC load detection is intentionally avoided unless forced but can still perturb analog outputs.
- BIOS EDID fallback can force virtual server/KVM outputs connected.
- Some property paths assume `best_encoder()` is available when no current encoder exists.
- DVI HPD-without-DDC retry introduces timing-sensitive delayed work state.
- AUX late registration assumes DDC bus setup was completed for AUX-capable connectors.

## Test Signals

Test connector creation for every connector type, property attachment, shared DDC, DP bridge and AUX setup, duplicate connector merging, and polling flags. Test detection for DDC success/failure, invalid EDID, HPD-only DVI retry, load detect, BIOS EDID fallback, shared DDC digital/analog conflicts, DP/eDP DPCD and panel power, runtime-PM failures, and audio detection. Test mode validation for panel bounds, scaling, HDMI deep color clock degradation, DVI dual-link limits, max pixel clock, and DP bandwidth.
