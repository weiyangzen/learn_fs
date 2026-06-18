# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_edid.c

## Purpose

`drm_edid.c` is the DRM core EDID and display capability parser. It reads EDID from DDC or driver-supplied callbacks, accepts debugfs or firmware overrides, validates and repairs blocks where possible, exposes allocation-safe `struct drm_edid` wrappers, parses modes and sink capabilities, updates connector properties, and builds HDMI/DP audio ELD data. It is a central integration file for display probing: connector helpers call it to turn a monitor's EDID into `drm_connector.display_info`, connector EDID/non-desktop/tile properties, `connector->probed_modes`, audio metadata, HDR metadata, HDMI infoframe inputs, and legacy `struct edid` compatibility outputs.

The file is also a compatibility layer. New APIs prefer `const struct drm_edid *` with explicit allocation size, while deprecated paths still accept raw `struct edid *`. The wrapper matters because EDID extension counts are untrusted input and can otherwise drive reads beyond allocated memory.

## Important APIs, Types, and Data

The internal `struct drm_edid` stores `size` and `const struct edid *edid`. All block count helpers distinguish the EDID-advertised count from the allocation-limited count, including HDMI Forum EEODB override handling. `drm_edid_alloc()`, `drm_edid_dup()`, `drm_edid_free()`, and `drm_edid_raw()` manage this wrapper. `drm_edid_raw()` intentionally refuses to return a raw pointer if the EDID's advertised size exceeds the stored allocation.

Validation uses `enum edid_block_status`, `edid_block_check()`, `edid_block_status_valid()`, and `drm_edid_block_valid()`. Base block header repair is controlled by the read-only `edid_fixup` module parameter, defaulting to six matching header bytes. CTA extension checksum failures are treated as usable in selected cases, matching long-standing EDID tolerance. `drm_edid_is_valid()` validates a legacy raw EDID; `drm_edid_valid()` validates the size-aware wrapper.

EDID acquisition APIs include `drm_probe_ddc()`, `drm_get_edid()`, `drm_edid_read_custom()`, `drm_edid_read_ddc()`, `drm_edid_read()`, `drm_edid_read_base_block()`, and switcheroo variants. `_drm_do_get_edid()` is the core flow: try override or firmware EDID first, read base block, allocate extension space, handle HF-EEODB extension count increases, read each extension, filter invalid extension blocks if possible, and return a raw EDID plus actual allocation size.

Mode construction relies on static DMT, established timing, CTA VIC, HDMI 1.4 4K, minimode, and stereoscopic timing tables. Key mode helpers include `drm_mode_find_dmt()`, `drm_mode_std()`, `drm_mode_detailed()`, `add_detailed_modes()`, `add_standard_modes()`, `add_established_modes()`, `add_cvt_modes()`, `add_cea_modes()`, `add_displayid_detailed_modes()`, and `add_inferred_modes()`. Exported helpers include `drm_match_cea_mode()`, `drm_display_mode_from_cea_vic()`, and `drm_add_modes_noedid()`.

CTA parsing is built around `struct cea_db_iter` and `struct cea_db`. The iterator covers both top-level CTA extension blocks and CTA data blocks embedded in DisplayID. CTA predicates identify HDMI VSDB, HDMI Forum VSDB/SCDB/EEODB, Microsoft and AMD vendor blocks, VCDB, YCbCr 4:2:0 blocks, HDR static metadata, audio, video, and speaker blocks.

Connector update APIs are `drm_edid_connector_update()` and `drm_edid_connector_add_modes()`. Legacy wrappers `drm_connector_update_edid_property()` and `drm_add_edid_modes()` remain exported. `drm_edid_connector_property_show()` backs sysfs EDID reads.

HDMI helper exports include `drm_default_rgb_quant_range()`, `drm_hdmi_avi_infoframe_from_display_mode()`, `drm_hdmi_avi_infoframe_quant_range()`, and `drm_hdmi_vendor_infoframe_from_display_mode()`. Audio/helper exports include `drm_edid_to_sad()`, `drm_edid_to_speaker_allocation()`, `drm_av_sync_delay()`, `drm_detect_hdmi_monitor()`, `drm_detect_monitor_audio()`, and `drm_edid_is_digital()`.

## Control Flow

DDC reads start with `drm_get_edid()` or `drm_edid_read_ddc()`. Forced-off connectors return no EDID, and unspecified-force connectors must first pass `drm_probe_ddc()`. `_drm_do_get_edid()` first checks `connector->edid_override` under `edid_override_mutex`, then firmware EDID through `drm_edid_load_firmware()`. If no override exists, it reads block 0 through `edid_block_read()`, retries up to four times, optionally repairs weak headers, rejects all-zero or unrecoverable base blocks, and records `edid_corrupt`, `null_edid_counter`, `bad_edid_counter`, and `real_edid_checksum` diagnostics. For extensions, it grows the buffer according to the base block count, then may grow again when block 1 has HDMI Forum EEODB. Invalid extension blocks are logged and compacted out by `edid_filter_invalid_blocks()`, which rewrites the extension count and checksum.

Display update starts in `drm_edid_connector_update()`: `update_display_info()` resets all EDID-derived connector fields, clears ELD under `eld_mutex`, applies quirks, reads physical size, monitor range, CTA/HDMI/DisplayID/MSO information, applies bit-depth and non-desktop quirks, builds ELD, then `_drm_update_tile_info()` parses DisplayID tiled topology and maintains tile group references. `_drm_edid_connector_property_update()` replaces the EDID blob property, increments `epoch_counter` when the EDID blob changes, updates the non-desktop property, and sets tile properties.

Mode addition is intentionally separate. `drm_edid_connector_add_modes()` rewraps the connector EDID property blob and calls `_drm_edid_connector_add_modes()`. That function follows EDID preference order: detailed timings, CVT three-byte codes, standard timings, established timings, CTA/HDMI modes, alternate 59.94/60 Hz CEA variants, DisplayID detailed/formula timings, and range-inferred modes. Preferred mode quirks can then rewrite which mode carries `DRM_MODE_TYPE_PREFERRED`.

HDMI infoframe helpers flow from display modes and connector display info. AVI generation picks CEA or HDMI VICs, handles aspect ratio constraints, suppresses HDMI 2.0 VICs for HDMI 1.4 sinks unless explicitly advertised, and initializes conservative scan/content fields. Quantization range generation respects VCDB selectable quantization and HDMI 2.0 YQ behavior.

## State and Persistence Behavior

The file does not persist state outside the kernel, but it mutates long-lived connector state. It updates `connector->edid_blob_ptr`, `display_info`, `eld`, latency arrays, EDID diagnostic counters, `edid_corrupt`, `epoch_counter`, tile topology fields, and tile group references. It allocates and frees `display_info.vics` every display info reset, manages EDID override storage behind `edid_override_mutex`, and writes ELD under `eld_mutex`. The EDID property blob is the handoff between update and add-modes paths.

Module parameters affect behavior across the driver lifetime: `edid_fixup` controls base header repair threshold, while firmware override selection lives in `drm_edid_load.c`. Static quirk tables are in-memory policy keyed by panel id and optional monitor name.

## Dependencies and Integration Points

This file depends on I2C DDC (`i2c_transfer`, segment address `0x30`), HDMI core infoframe helpers, CEC physical address semantics, VGA switcheroo, DRM connector/mode/property/tile APIs, DisplayID parsing from `drm_displayid_internal.h`, and EDID/ELD public headers. Audio integration is through connector ELD and exported SAD/speaker extraction helpers used by sound drivers. Userspace integration is through connector properties, sysfs EDID show, available modes, and mode infoframes. Driver integration is broad: display drivers call the EDID read/update/add helpers during hotplug probing and mode validation.

## Risks and Edge Cases

Most risks come from malformed EDID input. The file has many guards for header corruption, all-zero blocks, invalid checksums, untrusted extension counts, too-short CTA data blocks, HDMI Forum EEODB count overrides, and variable-length AMD VSDB payloads. Regressions can expose buffer overreads, accepted invalid modes, missing audio/HDR/color capabilities, or userspace-visible EDID property churn. The separation between `drm_edid_connector_update()` and `drm_edid_connector_add_modes()` is another risk: callers must update first or modes will be generated from stale/no property data.

CTA iterator bounds are critical because data block lengths are embedded in untrusted bytes. The file often uses payload-length predicates before indexing fields, but helper conversions still have FIXME comments around raw pointer usage. DisplayID and CTA coexistence can duplicate or reorder capabilities; the iterator deliberately scans CTA extensions before DisplayID CTA blocks. Tile group reference handling must release old groups when EDID loses tile data.

Mode generation is compatibility-heavy. EDID quirks intentionally override clocks, sync polarity, bit depth, preferred mode, DSC bpp, and non-desktop classification. Changing quirk matching or mode ordering can break real monitors. Legacy raw EDID helpers depend on trusted `edid_size(edid)` and are less robust than wrapper APIs.

## Test Signals

Useful tests include EDID corpus tests for valid, all-zero, bad-header, repaired-header, bad-checksum CTA, oversized extension count, HF-EEODB, and invalid-extension filtering cases. Connector tests should verify `epoch_counter` changes only when EDID blobs differ, non-desktop and tile properties follow EDID content, and ELD is cleared on NULL EDID. Mode tests should cover detailed timings, standard timings, established timings, CTA VDB, Y420VDB/Y420CMDB, HDMI VSDB 4K and 3D modes, DisplayID detailed/formula blocks, alternate CEA clocks, and preferred-mode quirks. Capability tests should cover HDR metadata, luminance range calculation, HDMI deep color, SCDC scrambling, FRL/DSC parsing, Microsoft non-desktop VSDB, AMD VSDB v3 minimum and maximum payload lengths, and monitor range/VRR extraction. Runtime probes should inspect KMS debug logs, sysfs EDID bytes, connector properties, and userspace-visible mode lists after hotplug and EDID override changes.
