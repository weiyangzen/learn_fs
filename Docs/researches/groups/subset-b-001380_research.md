# subset-b-001380 Research

Grouped source research for subset B work item `subset-b-001380`. Each source file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.c

### Purpose
`amdgpu_dm_mst_types.c` implements AMDGPU Display Manager support for DisplayPort MST connectors, AUX transactions, MST HPD sideband processing, fake MST encoders, remote sink creation, bandwidth/PBN helpers, and DSC-over-MST validation/precomputation. It is the bridge between DRM MST topology helpers and DC link/stream state.

### Important APIs, Types, And Functions
Key exported APIs are `amdgpu_dm_initialize_dp_connector`, `dm_dp_create_fake_mst_encoders`, `dm_handle_mst_sideband_msg_ready_event`, `dm_mst_get_pbn_divider`, `compute_mst_dsc_configs_for_state`, `pre_validate_dsc`, `needs_dsc_aux_workaround`, and `dm_dp_mst_is_port_support_mode`. Important internal paths include `dm_dp_aux_transfer`, MST connector `get_modes`/`detect`/`atomic_check`, `dm_dp_add_mst_connector`, DSC helpers such as `validate_dsc_caps_on_connector`, `compute_mst_dsc_configs_for_link`, `increase_dsc_bpp`, and `try_disable_dsc`, plus Synaptics/Panamera branch workarounds.

### Control Flow
DP connector initialization wires a DRM AUX adapter to DC DDC, initializes the MST topology manager, and registers DP subconnector properties. MST topology callbacks allocate dynamic DRM connectors, attach all fake MST encoders, inherit root connector properties, and retain the topology port. Mode probing reads MST EDID, creates or replaces DC remote sinks, restores HDCP state, updates FreeSync/DSC/downstream-port capability caches, and publishes EDID modes. HPD IRQ handling loops over ESI bits, asks DRM MST helpers to process sideband messages, ACKs handled events, and caps the loop at 30 iterations. Atomic validation releases time slots and separately computes DSC/PBN assignments when required.

### State, Persistence, And Dependencies
State is in `amdgpu_dm_connector` fields such as `dc_sink`, `drm_edid`, `mst_output_port`, `mst_root`, `mst_status`, `dsc_aux`, `mst_local_bw`, `vc_full_pbn`, `branch_ieee_oui`, and topology-manager state. No filesystem persistence exists. It depends on DRM DP MST helpers, DRM atomic state, DC link/sink/DSC APIs, DPCD reads, DM HDCP workqueue state, debugfs hooks, and AMD-specific DPCD branch quirks.

### Integration Points
This file is called from AMDGPU DM connector setup, hotplug handling, atomic check, and stream validation. It integrates with `amdgpu_dm.c` for connector state and DC stream creation, with DRM MST for topology/time-slot accounting, with DC resource allocation for DSC hardware, and with `amdgpu_dm_mst_types.h` declarations consumed by the broader DM atomic pipeline.

### Risks
MST state is highly race-prone: remote sinks can be removed by CSN, connectors can unregister while hotplug work runs, and AUX failures can mimic disconnects. DSC precomputation mutates PBN requests and temporary stream timing; mistakes can leave time-slot state inconsistent or allocate DSC unnecessarily. Bandwidth conversion depends on FEC overhead, 8b/10b versus 128b/132b encoding, and branch-specific throughput limits. Quirk paths for Synaptics hubs and HPD-disconnect AUX errors are hardware-specific and easy to regress.

### Test Signals
Exercise MST hub plug/unplug, cascaded Synaptics docks, HPD IRQ storms, remote EDID failure fallback, HDCP state restoration, multi-monitor atomic modesets, DSC and non-DSC bandwidth exhaustion, DP 1.4 and UHBR link encodings, and debugfs forced DSC settings. Useful signals include DRM MST time-slot validation, `DRM_DEBUG_DRIVER` `MST_DSC` logs, no leaked remote sinks, and successful suspend/resume with MST displays attached.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.h

### Purpose
`amdgpu_dm_mst_types.h` declares the public MST/DSC interface used by AMDGPU DM code and centralizes branch-device constants for Synaptics/Panamera DSC workarounds and PBN FEC overhead factors.

### Important APIs, Types, And Functions
The header defines `DP_BRANCH_DEVICE_ID_90CC24`, Synaptics remote-control and vendor-specific DPCD offsets, `IS_SYNAPTICS_PANAMERA`, `IS_SYNAPTICS_CASCADED_PANAMERA`, FEC overhead multipliers, `enum mst_msg_ready_type`, and `struct dsc_mst_fairness_vars`. It declares MST initialization, sideband handling, fake encoder creation, DSC prevalidation/configuration, PBN divider, and mode-support checks.

### Control Flow
There is no executable flow in the header. It shapes call flow by exposing MST connector setup to connector initialization, sideband processing to HPD paths, and DSC computation/prevalidation to atomic-check paths.

### State, Persistence, And Dependencies
The only state shape defined here is `dsc_mst_fairness_vars`, carrying PBN, DSC enablement, target bpp, and connector association during DSC fairness calculations. It forward-declares AMDGPU DM types and relies on DC and DRM types included by users. No persistent storage exists.

### Integration Points
Consumers include `amdgpu_dm_mst_types.c` and broader DM atomic code that needs to initialize MST-capable DP connectors, precompute DSC, or validate MST port mode support. The macros encode branch-vendor assumptions also used when reading DPCD vendor fields.

### Risks
Changing constants or structure fields affects hardware-specific workarounds and the ABI between MST computation code and atomic validation callers. The macro-style Synaptics detection assumes stable branch-device name layout and vendor data offsets.

### Test Signals
Build coverage should include `CONFIG_DRM_AMD_DC_FP` and non-FP configurations, MST DSC-capable hubs, Synaptics cascaded hubs, and atomic check paths that allocate `dsc_mst_fairness_vars`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_mst_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c

### Purpose
`amdgpu_dm_plane.c` implements AMDGPU DM DRM plane support. It advertises plane formats/modifiers, translates DRM framebuffer and plane state into DC plane attributes, pins/unpins scanout buffers, validates scaling and DCC, handles async cursor updates, initializes plane properties, and manages per-plane color-management state.

### Important APIs, Types, And Functions
Exported helpers include `amdgpu_dm_plane_init`, `amdgpu_dm_plane_fill_plane_buffer_attributes`, `amdgpu_dm_plane_fill_dc_scaling_info`, `amdgpu_dm_plane_helper_check_state`, `amdgpu_dm_plane_get_cursor_position`, `amdgpu_dm_plane_handle_cursor_update`, `amdgpu_dm_plane_fill_blending_from_plane_state`, `amdgpu_dm_plane_get_format_info`, and `amdgpu_dm_plane_is_video_format`. Internal logic covers per-family modifier construction for GFX9/GFX10/GFX11/GFX12, DCC validation, framebuffer prepare/cleanup, atomic check/async check/update, panic flush, state duplicate/destroy, format-modifier filtering, and color property handling.

### Control Flow
Plane initialization builds format and modifier lists from DC plane caps and ASIC family, registers a universal DRM plane, attaches zpos, alpha/blend, YUV color, rotation, damage, helper, and color pipeline properties, then resets the state. Atomic check validates viewport/scaling, rejects incompatible plane color pipeline and CRTC degamma use, fills DC scaling info, and calls `dc_validate_plane`. Prepare-fb reserves and pins the BO, allocates GART backing, calls DRM GEM prepare, records the GPU address, references the BO, and fills DC buffer attributes for newly created DC plane states. Cleanup reverses pin/ref state. Async cursor updates swap framebuffer state and program DC cursor attributes/position under `dc_lock`.

### State, Persistence, And Dependencies
State lives in `dm_plane_state` and referenced `dc_plane_state`, DRM plane state fields, framebuffer `amdgpu_framebuffer` address/tiling/TMZ metadata, BO pin counts, color-management blobs, and CRTC cursor dimensions. There is no filesystem persistence. Dependencies include DRM atomic helpers, GEM/TTM reservation and pinning, AMDGPU tiling/modifier macros, DC plane/cursor/scaling/DCC APIs, tracepoints, and optional private color or DRM color pipeline support.

### Integration Points
The file is used by AMDGPU DM device initialization and atomic commit/check paths. It integrates with framebuffer creation, DC resource validation, cursor programming, panic scanout recovery, color management, and userspace-visible DRM plane capabilities. `amdgpu_dm_plane.h` exposes the helpers to the rest of DM.

### Risks
Modifier lists must match both display hardware and render-driver expectations; incorrect DCC/swizzle restrictions can cause corruption or reject valid buffers. BO pin/unpin/ref paths must stay balanced across prepare failures and cleanup. Scaling validation includes hardware-specific workarounds such as rejecting nonzero NV12 source offsets on DCN1. Cursor updates touch live DC state outside a full modeset and require locking. Color blob duplication/destruction must retain and release blobs correctly.

### Test Signals
Run IGT/KMS atomic plane, cursor, async cursor, format/modifier, framebuffer damage, rotation, scaling, writeback/scanout, and panic-flush scenarios across GFX8 through GFX12. Validate NV12/P010 and FP16 formats, DCC and linear buffers, TMZ surfaces, BO pin failure paths, color pipeline properties, and suspend/resume with pinned scanout buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.h

### Purpose
`amdgpu_dm_plane.h` declares the AMDGPU DM plane helper API used by connector/CRTC/atomic code to initialize planes, validate state, convert buffer/scaling attributes, update cursors, inspect formats, and derive blending state.

### Important APIs, Types, And Functions
The header exposes `amdgpu_dm_plane_init`, `amdgpu_dm_plane_fill_plane_buffer_attributes`, `amdgpu_dm_plane_fill_dc_scaling_info`, `amdgpu_dm_plane_helper_check_state`, `amdgpu_dm_plane_get_cursor_position`, `amdgpu_dm_plane_handle_cursor_update`, `amdgpu_dm_plane_get_format_info`, `amdgpu_dm_plane_fill_blending_from_plane_state`, and `amdgpu_dm_plane_is_video_format`.

### Control Flow
The header has no runtime control flow. It defines the call contract between DRM atomic paths and DC plane conversion/programming code implemented in `amdgpu_dm_plane.c`.

### State, Persistence, And Dependencies
No state is stored in the header. Function signatures pass DRM plane/framebuffer state, AMDGPU framebuffers, DC tiling/size/DCC/address/scaling structures, and DC plane caps. It includes `dc.h` for DC structure definitions and relies on AMDGPU/DRM types being visible to consumers.

### Integration Points
Consumers include atomic check/commit logic, cursor code, framebuffer state conversion, and plane initialization paths elsewhere in AMDGPU DM. The declarations are part of the source-level interface between DM and the DC library.

### Risks
Signature changes ripple through atomic commit code. The buffer-attribute helper has many out-parameters, so mismatched initialization or caller assumptions can create stale DC plane state.

### Test Signals
Build all AMDGPU DM configurations and run KMS atomic plane/cursor/modifier tests that call through these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_plane.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_pp_smu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_pp_smu.c

### Purpose
`amdgpu_dm_pp_smu.c` adapts DC display power-management requests to AMDGPU DPM/SMU APIs. It applies display requirements, exposes clock-level queries, submits clock/voltage/watermark/display-count requests, and populates version-specific `pp_smu_funcs` callback tables for DCN generations.

### Important APIs, Types, And Functions
Important exported APIs are `dm_pp_apply_display_requirements`, `dm_pp_get_clock_levels_by_type`, `dm_pp_get_clock_levels_by_type_with_latency`, `dm_pp_get_clock_levels_by_type_with_voltage`, `dm_pp_notify_wm_clock_changes`, `dm_pp_apply_clock_for_voltage_request`, `dm_pp_get_static_clocks`, and `dm_pp_get_funcs`. Internal helpers translate `dm_pp_clock_type` to `amd_pp_clock_type`, convert PP clock tables to DC tables, map PP power levels, and implement RV/NV/RN SMU callback shims.

### Control Flow
Display requirements are copied into `adev->pm.pm_display_cfg`, converted mostly from kHz to 10 kHz units, then submitted via `amdgpu_dpm_display_configuration_change` followed by `amdgpu_dpm_compute_clocks` when DPM is enabled. Clock queries call DPM, fall back to defaults for simple clock levels, clamp boosted levels using validation clocks, and return DC-shaped arrays. SMU callback setup switches on `ctx->dce_version` and fills RV, NV, or RN function tables with wrappers that convert return codes to `PP_SMU_RESULT_*`.

### State, Persistence, And Dependencies
Persistent runtime state is the device power-management display configuration and SMU/DPM-managed clock/watermark state in the GPU firmware/driver. The file itself has no durable storage. It depends on `amdgpu_dpm_*` APIs, `amdgpu_pm`, DC context versioning, `dm_pp_smu.h` structures, and legacy PP clock units.

### Integration Points
DC resource and clock-management code calls these callbacks to inform SMU of active displays, min clocks, memory-clock switch policy, watermarks, and voltage requests. The file connects display mode validation to power-management constraints and SMU generation differences.

### Risks
Unit conversions between kHz, MHz, and 10 kHz are easy to break. Some callbacks treat `-EOPNOTSUPP` as unsupported but nonfatal while other errors fail, so return-code handling affects mode validation and power behavior. Version dispatch only covers specific DCN versions; unsupported versions get a logged error and no functions. Watermark structure layouts differ between RV and newer SMU paths.

### Test Signals
Exercise multi-display modesets, clock changes, VRR/blanking changes, memory-clock switch policy, suspend/resume, and DCN 1.0/2.0/2.1 hardware. Inspect DPM debugfs/sysfs clock levels, SMU logs, watermark programming, and mode validation under high-bandwidth display configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_pp_smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.c

### Purpose
`amdgpu_dm_psr.c` manages Panel Self Refresh capability discovery, link setup, enable/disable, global disable, and wait-for-exit behavior for embedded DisplayPort panels.

### Important APIs, Types, And Functions
Important functions are `amdgpu_dm_set_psr_caps`, `amdgpu_dm_link_setup_psr`, `amdgpu_dm_psr_enable`, `amdgpu_dm_psr_disable`, `amdgpu_dm_psr_disable_all`, `amdgpu_dm_psr_is_active_allowed`, and `amdgpu_dm_psr_wait_disable`. The internal `link_supports_psrsu` checks PSR-SU capability but currently always returns false after gating due to a temporary disable.

### Control Flow
Capability setup rejects non-eDP, disconnected links, missing PSR DPCD support, and panel instance 1, then marks PSR1 or PSR-SU capability. Link setup computes power PSR config, toggles SMU and multi-display optimization flags, optionally derives PSR-SU DSC slice height, and calls `dc_link_setup_psr`. Enable computes a static-frame delay from refresh rate, programs static-screen triggers, enables PSR active permission, and enables DC idle optimizations when available. Disable clears PSR active permission, and wait-disable polls `dc_link_get_psr_state` until PSR exits or a 500 ms timeout is reached.

### State, Persistence, And Dependencies
State lives in `link->psr_settings`, DC current state, panel DPCD capability caches, and firmware PSR state. No filesystem persistence exists. Dependencies include DC link PSR APIs, DMUB/DMCUB capability, panel power helpers, feature/debug masks, udelay polling, and embedded-panel detection.

### Integration Points
The file is called during eDP connector capability setup, stream/link programming, atomic commit power optimization, and global display-manager disable paths. It interacts with DC idle optimizations and SMU optimization policy.

### Risks
Incorrect capability gating can enable PSR on panels that glitch or disable it on working panels. Refresh-rate-derived static-frame delay depends on valid timing totals. PSR-SU is deliberately disabled despite capability checks, so future re-enablement must retest vstartup/vblank behavior. Busy polling for exit can delay callers up to 500 ms.

### Test Signals
Test eDP panels with and without PSR, PSR1 versus PSR-SU-capable panels, multi-display configurations, static screen entry/exit, cursor and overlay updates, suspend/resume, and forced debug masks. Useful signals include PSR state transitions, visual corruption, vblank event continuity, and timeout logs from wait-disable callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.h

### Purpose
`amdgpu_dm_psr.h` declares the AMDGPU DM Panel Self Refresh interface and defines the page-flip entry-delay constant used by PSR policy.

### Important APIs, Types, And Functions
It defines `AMDGPU_DM_PSR_ENTRY_DELAY` and declares PSR capability setup, link setup, enable, disable, global disable, active-allowed query, and wait-disable helpers.

### Control Flow
There is no executable flow. The header defines the boundary used by connector/link setup and atomic commit code to call the PSR implementation.

### State, Persistence, And Dependencies
No state is stored in the header. It includes `amdgpu.h` and references `dc_link`, `dc_stream_state`, and `amdgpu_display_manager` structures supplied by other DM/DC headers.

### Integration Points
Consumers use these declarations when configuring eDP links, entering or leaving PSR around display updates, and disabling PSR globally during modesets or power events.

### Risks
The entry-delay constant is policy visible; changing it affects PSR entry aggressiveness and flicker/power tradeoffs. Signature changes require coordinated edits in PSR callers.

### Test Signals
Build with PSR enabled, run eDP modeset/page-flip tests, and verify callers can disable and wait for PSR around atomic updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_psr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_quirks.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_quirks.c

### Purpose
`amdgpu_dm_quirks.c` applies DMI-based display-manager quirks for specific systems. It currently flags selected Dell desktops for AUX HPD disconnect behavior and selected HP notebooks/thin clients for eDP0-on-DP1 support.

### Important APIs, Types, And Functions
The file defines `struct amdgpu_dm_quirks`, static `quirk_entries`, DMI callbacks `edp0_on_dp1_callback` and `aux_hpd_discon_callback`, the `dmi_quirk_table`, and the exported `retrieve_dmi_info` function.

### Control Flow
`retrieve_dmi_info` resets quirk flags in `amdgpu_display_manager`, calls `dmi_check_system`, then copies the matching callback-updated global quirk bits into `dm->aux_hpd_discon_quirk` and `dm->edp0_on_dp1_quirk` with informational logs.

### State, Persistence, And Dependencies
State is process-global `quirk_entries` plus per-device flags in `amdgpu_display_manager`. There is no filesystem persistence. It depends on Linux DMI matching, DRM logging, and downstream code that reads the two DM quirk flags.

### Integration Points
`aux_hpd_discon_quirk` is consumed by the DP AUX transfer path to treat specific HPD-disconnect errors during MST sideband writes as successful. `edp0_on_dp1_quirk` is consumed by connector/link detection policy elsewhere in AMDGPU DM.

### Risks
The global `quirk_entries` bits are sticky after the first match, which is acceptable for typical single-system DMI evaluation but should be considered if reused in unusual multi-device scenarios. DMI product strings are exact and can miss BIOS naming variants. Over-broad quirks can hide real AUX disconnects.

### Test Signals
Boot listed Dell/HP systems and nearby non-listed variants, confirm the expected log messages and quirk flags, and retest MST AUX sideband handling and eDP connector assignment on affected platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_quirks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.c

### Purpose
`amdgpu_dm_replay.c` manages AMD eDP Panel Replay capability detection, configuration, enable, disable, and global disable. Replay is a panel power-saving feature gated by FreeSync/adaptive-sync, DPCD, VSDB, and DMUB support.

### Important APIs, Types, And Functions
Important functions are `amdgpu_dm_link_supports_replay`, `amdgpu_dm_set_replay_caps`, `amdgpu_dm_link_setup_replay`, `amdgpu_dm_replay_enable`, `amdgpu_dm_replay_disable`, and `amdgpu_dm_replay_disable_all`. It uses replay configuration fields such as `replay_supported`, `replay_enable_option`, fast resync/coasting support, timing sync support, and debug visual-confirm flags.

### Control Flow
Capability support first requires connector FreeSync capability, VSDB replay mode, eDP 1.3 or later, AUX wake ALPM, adaptive-sync SDP support, and populated pixel-deviation data. Set-caps rejects non-embedded signals, panel replay disallow flags, missing DMUB replay firmware support, then initializes the replay config. Link setup enables static-screen replay options, sets power optimization support, computes fast-resync support from min/max vertical frequency, disables general UI when timing sync is unsupported, and marks the feature enabled. Runtime enable checks connector disallow state, programs replay setup/coasting vtotal through `link_srv`, and allows active replay; disable clears active replay.

### State, Persistence, And Dependencies
State lives in `link->replay_settings`, connector `vsdb_info`, FreeSync range fields, `disallow_edp_enter_replay`, DPCD capability caches, and DMUB feature caps. No filesystem persistence exists. Dependencies include DC link service callbacks, DMUB firmware capability reporting, adaptive-sync DPCD parsing, and power-helper initialization.

### Integration Points
Replay setup is part of embedded-panel link configuration and atomic/display power-management paths. It is mutually adjacent to PSR policy and uses `dc_set_replay_allow_active` for display-manager-wide disabling.

### Risks
Replay gating spans multiple capability sources; stale connector state or missing VSDB parsing can misclassify support. Enabling replay when `disallow_edp_enter_replay` is set is explicitly blocked to avoid known panel issues. Link service callbacks must exist and match firmware support. Timing-sync options are conservative and may limit power savings.

### Test Signals
Test eDP panels with replay-capable VSDB and adaptive-sync data, panels without replay, FreeSync disabled states, DMUB firmware without replay support, fast-resync min/max vfreq cases, runtime disallow flags, suspend/resume, and visual-confirm debug mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.h

### Purpose
`amdgpu_dm_replay.h` declares the AMDGPU DM Panel Replay interface and public enable-option bit definitions used to configure replay behavior.

### Important APIs, Types, And Functions
It defines `enum replay_enable_option` bits for static screen, MPO video, full-screen video, general UI, and their coasting variants. It declares link support, capability setup, link setup, enable, disable, and global disable helpers.

### Control Flow
The header has no runtime control flow. It provides compile-time contracts for embedded-panel replay setup and runtime power-management callers.

### State, Persistence, And Dependencies
No state is stored here. It includes `amdgpu.h` and references DC link/stream and AMDGPU DM connector/display-manager types used by the implementation.

### Integration Points
Used by display-manager link setup, connector capability paths, and runtime commit code that enables or disables replay around updates.

### Risks
Enable-option bit changes affect firmware-facing replay config semantics. Declaration drift would break callers in DM and link setup code.

### Test Signals
Build replay-capable configurations and run panel replay capability, enable/disable, and global disable paths on eDP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_replay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_services.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_services.c

### Purpose
`amdgpu_dm_services.c` provides small service hooks used by DC/DM code for elapsed-time calculation, performance trace emission, and SMU trace stubs.

### Important APIs, Types, And Functions
The file defines `dm_get_elapse_time_in_ns`, `dm_perf_trace_timestamp`, `dm_trace_smu_enter`, and `dm_trace_smu_exit`.

### Control Flow
Elapsed time returns the difference between current and last timestamps. Performance tracing forwards current read/write counters and last-entry pointers from `ctx->perf_trace` to `trace_amdgpu_dc_performance`, which also updates the last counters. SMU enter/exit trace hooks are currently empty.

### State, Persistence, And Dependencies
State is limited to caller-provided timestamps and `dc_context->perf_trace` counters. There is no persistence. It depends on `amdgpu_dm_trace.h` tracepoints and DC context service expectations.

### Integration Points
DC code can call these service hooks for instrumentation without depending directly on Linux tracepoint implementation details. The empty SMU hooks reserve integration points for future SMU tracing.

### Risks
`dm_perf_trace_timestamp` assumes `ctx->perf_trace` is valid. Timestamp subtraction has no wrap handling beyond unsigned arithmetic. Empty SMU hooks may hide expected tracing if callers assume they emit events.

### Test Signals
Enable AMDGPU DM tracepoints and verify performance counter deltas during register-heavy modesets; build with service users enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_services.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_trace.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_trace.h

### Purpose
`amdgpu_dm_trace.h` defines Linux tracepoints for AMDGPU Display Manager and DC instrumentation, covering register access, atomic connector/CRTC/plane state, atomic commit/check lifecycle, DC pipe and clock state, DMUB trace IRQs, refresh-rate tracking, DC FPU begin/end, OPTC lock/unlock state, brightness conversion, and ISM commit/event state.

### Important APIs, Types, And Functions
Trace definitions include `amdgpu_dc_rreg`, `amdgpu_dc_wreg`, `amdgpu_dc_performance`, `amdgpu_dm_connector_atomic_check`, `amdgpu_dm_crtc_atomic_check`, `amdgpu_dm_plane_atomic_check`, `amdgpu_dm_atomic_update_cursor`, `amdgpu_dm_atomic_commit_tail_begin`, `amdgpu_dm_atomic_commit_tail_finish`, `amdgpu_dm_atomic_check_begin`, `amdgpu_dm_atomic_check_finish`, `amdgpu_dm_dc_pipe_state`, `amdgpu_dm_dc_clocks_state`, `amdgpu_dm_dce_clocks_state`, `amdgpu_dmub_trace_high_irq`, `amdgpu_refresh_rate_track`, `dcn_fpu`, `dcn_optc_lock_unlock_state`, `amdgpu_dm_brightness`, `amdgpu_dm_ism_commit`, and `amdgpu_dm_ism_event`.

### Control Flow
The file uses `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` macros to generate tracepoint code when included with `trace/define_trace.h`. Runtime flow is passive until tracepoints are enabled; call sites pass DRM/DC state, fields are copied in `TP_fast_assign`, and `TP_printk` formats ftrace output.

### State, Persistence, And Dependencies
Tracepoints do not persist driver state beyond ring-buffer trace records. They depend on Linux tracepoint infrastructure, DRM atomic structures, DC core types, OPTC state, and string lifetime rules for trace strings. Register trace events increment caller-provided counters.

### Integration Points
Trace call sites in DM/DC code use these events for debugging atomic validation, cursor updates, modeset commit sequencing, DC pipe programming, clock programming, FPU sections, brightness, and panel self-refresh/ISM transitions. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` make this header self-defining for trace generation.

### Risks
Trace fields dereference many nested DRM/DC pointers at call time; call sites must pass valid objects. Adding large fields or expensive formatting can perturb timing-sensitive display paths when tracing is enabled. Format strings and field types must stay aligned with structure definitions.

### Test Signals
Build with tracing enabled, enable each event through tracefs during KMS atomic commits, cursor updates, clock changes, brightness updates, and FPU-protected DCN calculations. Check for compile-time trace macro errors and runtime trace output with sensible IDs and dimensions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.c

### Purpose
`amdgpu_dm_wb.c` implements AMDGPU DM DRM writeback connector support for Display Writeback. It validates writeback framebuffer jobs, pins/unpins target buffers, exposes a no-EDID mode set, and registers the writeback connector/encoder helpers.

### Important APIs, Types, And Functions
The public entry point is `amdgpu_dm_wb_connector_init`. Internal callbacks are `amdgpu_dm_wb_encoder_atomic_check`, `amdgpu_dm_wb_connector_get_modes`, `amdgpu_dm_wb_prepare_job`, and `amdgpu_dm_wb_cleanup_job`. The supported writeback format list currently contains `DRM_FORMAT_XRGB2101010`.

### Control Flow
Connector init finds the DC link for the writeback link index, adds connector helpers, calls `drm_writeback_connector_init` with supported formats and CRTC mask, then resets connector state. Atomic check accepts empty jobs, otherwise requires framebuffer dimensions to match the CRTC mode and format to be in the supported list. Prepare-job reserves the BO, reserves move fences, pins it in supported display domains, allocates GART backing, stores the GPU address in the AMDGPU framebuffer, and takes a BO reference. Cleanup reserves the BO, unpins it, unreserves, and drops the reference.

### State, Persistence, And Dependencies
State lives in `amdgpu_dm_wb_connector`, the associated DC link, DRM writeback job/framebuffer, AMDGPU BO pin/ref counts, and framebuffer GPU address. There is no filesystem persistence. Dependencies include DRM writeback helpers, DRM connector state helpers, AMDGPU GEM/TTM/BO APIs, and display domain selection.

### Integration Points
The writeback connector participates in DRM atomic commits and uses the same buffer-management conventions as plane scanout. It connects DC DWB hardware to userspace writeback jobs through DRM's writeback connector abstraction.

### Risks
Only one 10-bit XRGB format is advertised, so userspace format negotiation is narrow. Pin/ref cleanup must match prepare success; cleanup failure to reserve the BO logs and leaves recovery to later paths. Dimension validation prevents scaling through writeback. GART/pin failures need to unwind correctly.

### Test Signals
Run DRM writeback tests with matching and mismatched framebuffer sizes, unsupported formats, BO pin failures where possible, repeated writeback jobs, suspend/resume, and concurrent modesets. Confirm BO pin counts do not leak.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.h

### Purpose
`amdgpu_dm_wb.h` declares the AMDGPU DM writeback connector initialization entry point.

### Important APIs, Types, And Functions
It includes DRM writeback definitions and declares `amdgpu_dm_wb_connector_init(struct amdgpu_display_manager *dm, struct amdgpu_dm_wb_connector *dm_wbcon, uint32_t link_index)`.

### Control Flow
There is no executable flow. The declaration lets display-manager initialization register writeback connectors implemented in `amdgpu_dm_wb.c`.

### State, Persistence, And Dependencies
No state is stored here. Callers provide the display manager, writeback connector storage, and DC link index. It depends on `drm_writeback.h` and AMDGPU DM type definitions.

### Integration Points
Used by AMDGPU DM device/link initialization when DWB/writeback hardware is exposed.

### Risks
Signature drift affects writeback initialization callers. The header does not expose supported formats or job helpers, so callers must treat initialization as the only public contract.

### Test Signals
Build writeback-enabled DM configurations and confirm writeback connector registration succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_wb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.c

### Purpose
`dc_fpu.c` provides AMD DC wrappers around Linux kernel FPU sections. DCN calculations use floating point in selected paths, so this file tracks per-CPU recursion depth, calls `kernel_fpu_begin/end`, disables preemption while active, and emits trace events.

### Important APIs, Types, And Functions
The file defines per-CPU `fpu_recursion_depth` and implements `dc_assert_fp_enabled`, `dc_is_fp_enabled`, `dc_fpu_begin`, and `dc_fpu_end`.

### Control Flow
`dc_fpu_begin` warns if not in task context, disables preemption, increments the per-CPU depth, starts the kernel FPU section only for the outermost depth, and traces begin. `dc_fpu_end` decrements depth, ends the kernel FPU section when returning to zero, warns on negative depth, traces end, and reenables preemption. Assertion/query helpers read the per-CPU depth.

### State, Persistence, And Dependencies
Runtime state is per-CPU recursion depth and the kernel FPU ownership state. There is no persistence. Dependencies include Linux FPU APIs, preemption control, `ASSERT`, `WARN_ON_ONCE`, and `TRACE_DCN_FPU` from DC tracing.

### Integration Points
Macros in `dc_fpu.h` wrap these functions for DC code that uses floating point. Trace events are defined in `amdgpu_dm_trace.h`. The wrapper allows nested DC floating-point callers without repeated `kernel_fpu_begin`.

### Risks
Unbalanced begin/end calls leave preemption disabled or FPU state active/inactive incorrectly. Calls outside task context warn and may be unsafe. Per-CPU depth requires preemption to remain disabled while active. Negative depth indicates serious caller imbalance.

### Test Signals
Build with `CONFIG_DRM_AMD_DC_FP`, exercise DCN bandwidth/color calculations, enable `dcn_fpu` tracepoints, and run lockdep/preempt debugging to catch unbalanced or invalid-context FPU sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.h

### Purpose
`dc_fpu.h` declares DC FPU wrapper functions and provides macros that enforce the intended call pattern for floating-point sections in AMD display code.

### Important APIs, Types, And Functions
It declares `dc_assert_fp_enabled`, `dc_is_fp_enabled`, `dc_fpu_begin`, and `dc_fpu_end`. Public macros are `DC_FP_START`, `DC_FP_END`, and `DC_RUN_WITH_PREEMPTION_ENABLED`.

### Control Flow
Normal compilation maps `DC_FP_START/END` to begin/end calls with function and line metadata. When `CONFIG_DRM_AMD_DC_FP` is enabled, `DC_RUN_WITH_PREEMPTION_ENABLED` temporarily exits an active FPU section around code that needs preemption enabled, then reenters it. For `_LINUX_FPU_COMPILATION_UNIT`, direct macro use is blocked with `BUILD_BUG()` to keep low-level FPU implementation code from recursively using its own wrappers.

### State, Persistence, And Dependencies
The header stores no state. It depends on the implementation's per-CPU recursion tracking and on `CONFIG_DRM_AMD_DC_FP` build configuration. No persistence exists.

### Integration Points
Used throughout DCN code around floating-point calculations and by code that needs to query/assert FPU protection. It is paired with `dc_fpu.c` and `amdgpu_dm_trace.h` FPU trace events.

### Risks
Incorrect macro use can break preemption/FPU balance. `DC_RUN_WITH_PREEMPTION_ENABLED` only preserves an existing FPU section when configured for DC FP, so callers must understand behavior in non-FP builds.

### Test Signals
Compile FP and non-FP configurations, verify `_LINUX_FPU_COMPILATION_UNIT` guard behavior, and exercise nested `DC_FP_START/END` plus `DC_RUN_WITH_PREEMPTION_ENABLED` call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/dc_fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/Makefile

### Purpose
`dc/Makefile` assembles the AMD Display Core component by selecting DC subdirectory Makefiles and core DC object files into `AMD_DISPLAY_FILES`.

### Important APIs, Types, And Functions
The main variables are `DC_LIBS`, `AMD_DC`, `FILES`, and `AMD_DISPLAY_FILES`. `DC_LIBS` lists DC subcomponents such as basics, bios, dml, clk_mgr, dce, gpio, hwss, irq, link, dsc, resource, optc, dpp, hubbub, hubp, dio, dwb, mpc, and others. `FILES` adds core objects including `dc_dmub_srv.o`, EDID/fused I/O/helper files, and `core/dc*.o` modules.

### Control Flow
The Makefile starts with a base subcomponent list, conditionally adds DCN and floating-point-heavy libraries under `CONFIG_DRM_AMD_DC_FP`, always adds DCE generations and HDCP, conditionally adds DCE6 for SI, builds the list of child Makefiles, includes them, then appends root DC objects with the `$(AMDDALPATH)/dc/` prefix.

### State, Persistence, And Dependencies
Build state is make variables only. It depends on parent definitions of `AMDDALPATH`, `FULL_AMD_DISPLAY_PATH`, `CONFIG_DRM_AMD_DC_FP`, `CONFIG_DRM_AMD_DC_SI`, and the child Makefiles for each subcomponent.

### Integration Points
Included by the AMDGPU display build system to compile DC into the driver. It coordinates source inclusion across DC generations and optional FP-enabled DCN support.

### Risks
Missing or misordered subcomponent entries can omit required objects or duplicate DML inclusion. FP gating affects KCOV instrumentation and DCN libraries; wrong config guards can break non-FP or SI builds. Child Makefile include paths depend on parent variables being set correctly.

### Test Signals
Build AMDGPU with `CONFIG_DRM_AMD_DC_FP` on/off and `CONFIG_DRM_AMD_DC_SI` on/off, check that expected DCN/DCE objects are present, and run incremental builds after touching child Makefiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/Makefile

### Purpose
`dc/basics/Makefile` contributes the DAL/DC basics utility objects to the AMD display build.

### Important APIs, Types, And Functions
It defines `BASICS` with `conversion.o`, `fixpt31_32.o`, `vector.o`, `dc_common.o`, `dce_calcs.o`, `custom_float.o`, and `bw_fixed.o`; derives `AMD_DAL_BASICS`; and appends those objects to `AMD_DISPLAY_FILES`.

### Control Flow
Make expands the basics object list, prefixes each object with `$(AMDDALPATH)/dc/basics/`, and appends the result to the global AMD display object list used by the parent build.

### State, Persistence, And Dependencies
State is limited to make variables. It depends on `AMDDALPATH` and on the listed source files existing in the basics directory.

### Integration Points
Included by `dc/Makefile` through the `DC_LIBS` subcomponent include list. It ensures common math, vector, fixed-point, and conversion utilities are linked into AMDGPU DC.

### Risks
Removing `bw_fixed.o` or related utility objects breaks consumers in bandwidth and display calculations. Adding files here affects all DC builds, so build-time dependencies and optional config guards must be considered.

### Test Signals
Build AMDGPU display code and verify all basics objects compile and link; specifically validate consumers of fixed-point and bandwidth helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/bw_fixed.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/bw_fixed.c

### Purpose
`bw_fixed.c` implements a small signed fixed-point arithmetic helper for bandwidth calculations. It converts integers and fractions into `struct bw_fixed`, rounds to a significance, and multiplies fixed-point values with overflow assertions.

### Important APIs, Types, And Functions
The file defines internal macros for `MAX_I64`, `MIN_I64`, the fractional mask, and fractional extraction. It implements `bw_int_to_fixed_nonconst`, `bw_frc_to_fixed`, `bw_floor2`, `bw_ceil2`, and `bw_mul`; `abs_i64` is a local helper.

### Control Flow
Integer conversion left-shifts by `BW_FIXED_BITS_PER_FRACTIONAL_PART` after range assertions. Fraction conversion divides absolute numerator by denominator to get the integer part, iteratively shifts/reduces the remainder to build fractional bits, rounds the least significant bit, then reapplies sign. Floor and ceil divide by absolute significance and multiply back, with ceil stepping one significance unit away from zero when needed. Multiplication decomposes both operands into integer and fractional parts, accumulates integer-integer, integer-fraction, and rounded fraction-fraction products, then reapplies sign.

### State, Persistence, And Dependencies
All state is stack-local and returned by value. There is no persistence. Dependencies include `bw_fixed.h` constants/macros, `dm_services.h` for `ASSERT`, and kernel 64-bit division helpers `div64_u64_rem` and `div64_s64`.

### Integration Points
The file is built through `dc/basics/Makefile` and supports display bandwidth/math calculations that use the older `bw_fixed` format rather than newer fixed-point helpers.

### Risks
Overflow behavior is guarded by assertions rather than graceful error returns. `abs_i64(MIN_I64)` is mathematically problematic in C signed arithmetic because `-arg` overflows before conversion. Division by zero is asserted, not handled. Rounding in multiplication recomputes `bw_frc_to_fixed(1, 2)` and assumes fractional scaling constants remain stable.

### Test Signals
Unit-style tests should cover positive/negative fractions, denominator sign, zero denominator assertion, floor/ceil around zero and negative values, multiplication with fractional rounding, max-range assertion boundaries, and comparison against high-precision expected bandwidth values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/basics/bw_fixed.c -->
