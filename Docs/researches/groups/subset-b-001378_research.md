# subset-b-001378 research

This grouped report covers the AMDGPU Display Manager header plus CRTC, CRC, and color-management implementation files. Each file section is wrapped with the requested source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.h

## Purpose
`amdgpu_dm.h` is the central private Display Manager contract between the AMDGPU DRM/KMS driver and AMD Display Core. It defines the main `amdgpu_display_manager` device state, connector/plane/CRTC state wrappers, color-management enums and limits, DMUB/IRQ/workqueue structures, and exported helper prototypes used by connector, CRTC, color, AUX, memory, and detection code.

## Important APIs, Types, And Functions
Important types include `struct amdgpu_display_manager`, `struct amdgpu_dm_connector`, `struct dm_plane_state`, `struct dm_crtc_state`, `struct dm_atomic_state`, and `struct dm_connector_state`. The display manager owns DC/DMUB pointers, firmware buffers, atomic private object state, DC/audio locks, IRQ handler tables, vblank/vupdate/pageflip parameters, backlight caches, secure-display context, HPD offload queues, MST encoders, DMUB completions, and boot-time CRC buffers. Plane and CRTC state wrappers carry DC objects plus AMD color properties such as degamma/shaper/blend LUT blobs, transfer functions, HDR multiplier, 3x4 CTM, 3D LUT, regamma TF, VRR state, ABM level, CRC skip count, active plane count, and cursor mode. Exported APIs include connector state/property helpers, stream validation creation, color-management validation/update entry points, DMUB AUX/config/fused IO helpers, atomic DM state access, GPU memory allocation hooks, headless detection, idle workqueue creation, and HDMI/CEC helpers.

## Control Flow
This header does not execute logic directly except for small container/status helpers, but it establishes the flow used by the implementation: DRM atomic state is extended into DM-specific state, commit code builds or retains DC streams and planes, color and CRC code mutate DC stream/plane transfer functions and IRQ parameters, and asynchronous work structures defer HPD/vblank/vupdate/idle work outside hard interrupt paths.

## State And Persistence
State is runtime kernel state, not on-disk persistence. Several fields are long-lived caches across hotplug, suspend/resume, and atomic commits: cached DRM/DC state, backlight brightness, MST status, FreeSync/ABM settings, secure-display ROI mapping, DMUB firmware buffer addresses, and connector EDID/sink pointers. DC stream and plane pointers require explicit retain/release discipline in users.

## Dependencies And Integration Points
The file depends on DRM atomic/connector/CRTC/plane/writeback APIs, DP MST helpers, AMD DC link/signal/IRQ types, DM CRC declarations, info packets, and broader AMDGPU mode structures. It is included by most `amdgpu_dm` implementation files and is the shared ABI for CRTC, connector, color, CRC, debugfs, DMUB, MST, PSR, Replay, backlight, and audio integration.

## Risks
The header is a high-blast-radius ownership contract. Risks include stale `dc_stream_state`/`dc_plane_state` references, lock-order bugs between `dc_lock`, `audio_lock`, event locks, and mode-config locks, build-configuration drift around `AMD_PRIVATE_COLOR` and `CONFIG_DRM_AMD_SECURE_DISPLAY`, array size mismatches for CRTC/EDP/DMUB notification limits, and connector sink/MST pointers becoming stale during hotplug. Color property fields must remain consistent with conversion code in `amdgpu_dm_color.c`.

## Test Signals
Useful signals are successful DRM device initialization, atomic modesets with suspend/resume, MST hotplug and payload changes, eDP backlight and PSR/Replay transitions, DMUB AUX/config transactions, CRC debugfs enable/disable, secure-display ROI creation when enabled, and IGT/KMS coverage for color properties, VRR, writeback exclusion, connector state duplication, and plane/CRTC atomic validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_color.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_color.c

## Purpose
`amdgpu_dm_color.c` translates DRM color-management state into AMD DC color-programming structures. It supports legacy DRM CRTC degamma/CTM/gamma properties, optional AMD private plane/CRTC properties, and the newer DRM plane colorop pipeline, mapping each into DC transfer functions, gamut matrices, shaper/blend LUTs, HDR multipliers, and 3D LUT state.

## Important APIs, Types, And Functions
Public entry points are `amdgpu_dm_init_color_mod`, `amdgpu_dm_create_color_properties` under `AMD_PRIVATE_COLOR`, `amdgpu_dm_verify_lut3d_size`, `amdgpu_dm_verify_lut_sizes`, `amdgpu_dm_check_crtc_color_mgmt`, `amdgpu_dm_update_crtc_color_mgmt`, and `amdgpu_dm_update_plane_color_mgmt`. Key helpers extract DRM LUT blobs, detect linear LUT bypasses, convert DRM 16-bit and 32-bit LUT formats into `dc_gamma`, convert DRM signed-magnitude CTMs into DC `fixed31_32`, select DC predefined transfer functions, and pack DRM 17-cube 3D LUT data into DC tetrahedral arrays. Colorop helpers parse the linked color pipeline for degamma curve, multiplier, 3x4 CTM, optional shaper curve/LUT, optional 3D LUT, and blend curve/LUT.

## Control Flow
CRTC validation first checks LUT sizes, decides whether degamma/regamma are meaningful or bypass, computes output transfer parameters, and records whether CRTC degamma must later be mapped onto a plane. CRTC update then configures stream regamma and gamut remap. Plane update validates 3D LUT support and sizes, initializes input transfer bypass, tries AMD private plane degamma, rejects simultaneous plane and CRTC degamma use, maps CRTC degamma to the plane when needed, applies plane CTM, then prefers the DRM colorop pipeline if it can be parsed; otherwise it falls back to AMD private plane properties. Colorop parsing depends on the exact `next` chain created by `amdgpu_dm_colorop.c`.

## State And Persistence
The file consumes immutable DRM blob data from atomic state and writes transient DC state into `dc_stream_state` and `dc_plane_state`. It also updates `dm_crtc_state` flags `cm_has_degamma` and `cm_is_degamma_srgb`. It allocates temporary `dc_gamma` objects and releases them after calculating transfer-function parameters. No data is persisted beyond atomic/DC runtime state.

## Dependencies And Integration Points
It depends on DRM color LUT/CTM/colorop APIs, `amdgpu_dm.h` state definitions, `amdgpu_dm_colorop.h` supported colorop bitmasks, DC color caps, and `modules/color/color_gamma.h` calculation routines. It integrates with CRTC atomic checks, plane atomic programming, DCN color capability reporting, and optional AMD private color-property creation.

## Risks
Color correctness is sensitive to hardware block ordering. Risks include accepting a colorop chain with stale or missing state, rejecting valid userspace because only one pre-blend degamma block exists, loss of CRTC degamma in legacy gamma corner cases, size assumptions for 4096-entry 1D LUTs and 17x17x17 3D LUTs, CTM signed-magnitude conversion mistakes, allocation failure from `dc_create_gamma`, and fallback behavior silently using AMD private properties when colorop parsing returns an error. Some colorop blend-LUT checks also rely on fields that are meaningful for curve operations, so this path needs IGT attention.

## Test Signals
Signals include IGT `kms_color` and colorop pipeline tests for CRTC gamma/degamma/CTM, AMD private property tests when compiled, 4096-entry and legacy 256-entry LUT validation, invalid-size rejection for shaper/3D LUT blobs, HDR multiplier and CTM programming checks, DCN2/DCN3 behavior with simultaneous plane and CRTC CTM, 3D LUT enablement only on capable hardware, and visual or CRC-based tests for sRGB/PQ/BT.709/gamma transfer functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_color.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.c

## Purpose
`amdgpu_dm_colorop.c` advertises and constructs AMD's default DRM plane color pipeline. It exposes the supported transfer-function bitmasks and creates a linked set of `drm_colorop` objects matching the DC color pipeline consumed by `amdgpu_dm_color.c`.

## Important APIs, Types, And Functions
The file exports `amdgpu_dm_supported_degam_tfs`, `amdgpu_dm_supported_shaper_tfs`, and `amdgpu_dm_supported_blnd_tfs`, each as a bitmask of supported `DRM_COLOROP_1D_CURVE_*` values. `amdgpu_dm_initialize_default_pipeline` allocates up to ten colorops, initializes them with DRM helpers, links them with `drm_colorop_set_next_property`, and fills a `drm_prop_enum_list` entry naming the pipeline. `dm_colorop_funcs` uses the generic `drm_colorop_destroy` destructor.

## Control Flow
Pipeline creation always starts with a degamma 1D curve, multiplier, and 3x4 CTM. If DC reports hardware 3D LUT or MPC preblend support, it appends shaper curve, shaper 1D LUT, and 3D LUT. It then appends blend 1D curve and blend 1D LUT. On any allocation or initialization failure, it logs allocation failures and destroys the colorop pipeline for the device.

## State And Persistence
State is DRM object state registered on the plane. The first colorop ID is stored in the enum list as the selectable pipeline type, and the pipeline name is dynamically allocated with `kasprintf`. There is no persistent storage outside the DRM object lifetime.

## Dependencies And Integration Points
The file depends on DRM plane/colorop/property helpers, AMDGPU device lookup, DC color caps, and constants from `amdgpu_dm.h`. It is tightly coupled to `amdgpu_dm_color.c`, whose parser assumes the exact operation order and skips optional shaper/3D-LUT entries based on the same capability predicate.

## Risks
Risks include chain-order drift between initialization and parser code, partial cleanup destroying more pipeline state than intended if multiple planes are being initialized, leaked `list->name` ownership if the DRM property layer does not assume it, and userspace-visible pipeline differences across hardware with and without 3D LUT support. The `MAX_COLOR_PIPELINE_OPS` ceiling must remain above the maximum constructed chain length.

## Test Signals
Useful tests inspect the plane `COLOR_PIPELINE` property, verify the advertised colorop order and supported curve masks, validate bypass behavior for every op, exercise initialization on hardware with and without 3D LUT support, force allocation/init failure paths in fault injection, and run colorop atomic commits that `amdgpu_dm_update_plane_color_mgmt` can parse successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.h

## Purpose
`amdgpu_dm_colorop.h` is the small private header for AMD plane color-pipeline support. It shares supported colorop transfer-function masks and the pipeline initialization entry point with the rest of Display Manager.

## Important APIs, Types, And Functions
It declares the exported `u64` masks `amdgpu_dm_supported_degam_tfs`, `amdgpu_dm_supported_shaper_tfs`, and `amdgpu_dm_supported_blnd_tfs`, plus `amdgpu_dm_initialize_default_pipeline(struct drm_plane *plane, struct drm_prop_enum_list *list)`. The masks are consumed by both colorop construction and colorop atomic-state parsing.

## Control Flow
The header defines no executable control flow. The intended sequence is plane initialization calls `amdgpu_dm_initialize_default_pipeline`, then later atomic plane update code walks the generated pipeline and validates curve types using the shared masks.

## State And Persistence
It owns no state. The declarations expose immutable mask constants and a constructor that creates DRM object lifetime state elsewhere.

## Dependencies And Integration Points
It depends on DRM plane and property enum declarations being visible to consumers. Its main integration points are plane initialization code and `amdgpu_dm_color.c` colorop parsing.

## Risks
Because the masks are global constants rather than per-hardware fields, unsupported curve exposure must be handled by pipeline composition and later DC conversion. Header users must keep the function declaration in sync with DRM helper API changes and avoid including it without the relevant DRM type declarations.

## Test Signals
Compile coverage across colorop-enabled builds, successful link of the mask exports, plane pipeline enumeration, and atomic commits using every advertised mask bit are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.c

## Purpose
`amdgpu_dm_crc.c` implements DRM CRTC CRC capture for AMD display pipes and, when secure display is enabled, ROI/window CRC handling used by secure-display workflows. It parses debugfs CRC source names, configures DC stream CRC generation and dithering, manages vblank references, reads CRC values on IRQ, and coordinates secure-display ROI updates with DMUB/DC and PSP TA work.

## Important APIs, Types, And Functions
Public functions include `amdgpu_dm_crtc_get_crc_sources`, `amdgpu_dm_crtc_verify_crc_source`, `amdgpu_dm_crtc_configure_crc_source`, `amdgpu_dm_crtc_set_crc_source`, `amdgpu_dm_crtc_handle_crc_irq`, and secure-display functions `amdgpu_dm_crc_window_is_activated`, `amdgpu_dm_crtc_handle_crc_window_irq`, and `amdgpu_dm_crtc_secure_display_create_contexts`. Helpers parse sources (`none`, `crtc`, `crtc dither`, `dprx`, `dprx dither`, `auto`), classify CRTC vs DPRX sources, decide dithering, sort connectors into secure-display PHY IDs, map MST ports by RAD/LCT, reset CRC windows, notify PSP TA, and forward ROI windows to DC/DMUB.

## Control Flow
Setting a CRC source takes the CRTC modeset lock, waits for outstanding hardware commits, resolves DP AUX for DPRX capture when needed, obtains or releases a vblank reference, resets secure-display windows, calls DC CRC configuration, starts/stops DP AUX CRC when applicable, updates `acrtc->dm_irq_params.crc_src`, resets skip count, and initializes secure-display PHY mapping for legacy mode. IRQ handling skips the first two frames after enabling, then reads DC stream CRC and submits DRM CRC entries. Secure-display window IRQ handling validates CRC source/window activation, handles ROI update requests, optionally configures CRC windows directly, schedules work to forward ROI or notify PSP, and updates per-window CRC/frame counters under spinlocks.

## State And Persistence
Runtime state lives in `amdgpu_crtc.dm_irq_params`, `dm_crtc_state.crc_skip_count`, secure-display CRTC contexts, and the display manager secure-display context. Work items persist across IRQs until flushed or device teardown. No state is persisted to disk; CRC values are emitted through DRM debugfs/readback and secure-display paths.

## Dependencies And Integration Points
The file depends on DRM CRTC/vblank/DP AUX CRC APIs, AMD DC stream CRC/dither/dynamic-expansion calls, AMDGPU IRQ and reset state, PSR/Replay disable hooks, secure-display PSP TA APIs, connector/MST topology state, and `dc_lock`/event/mode-config synchronization. It integrates with `amdgpu_dm_crtc.c` vblank IRQ enablement and secure-display vline0 interrupt handling.

## Risks
Risks include lock-order regressions among CRTC mutex, commit lock, event lock, mode-config mutex, `dc_lock`, and PSP mutex; vblank reference leaks on partial enable failures; using `source` instead of previous DPRX state in some stop decisions; secure-display PHY mapping staleness after hotplug; MST RAD sorting mistakes; CRC window updates racing with IRQ reads; first-frame skip assumptions hiding hardware readiness issues; and PSR/Replay interactions if CRC is enabled or disabled around panel self-refresh transitions.

## Test Signals
Signals include debugfs CRC source enumeration, invalid source rejection, enabling/disabling CRTC CRC with correct vblank reference counts, DPRX CRC on DP/eDP and rejection on non-DP connectors, dither and no-dither variants changing DC dither configuration, first two CRC frames skipped, PSR/Replay disabled while CRC is active, secure-display ROI updates producing CRC/frame counters, MST secure-display mapping stability, and suspend/hotplug/reset tests while CRC capture is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.h

## Purpose
`amdgpu_dm_crc.h` declares the Display Manager CRC source enum, secure-display CRC data structures, validity helper, and debugfs/secure-display CRC entry points used by CRTC and IRQ code.

## Important APIs, Types, And Functions
`enum amdgpu_dm_pipe_crc_source` models no CRC, CRTC CRC, CRTC CRC with dither, DPRX CRC, DPRX CRC with dither, max, and invalid. Under `CONFIG_DRM_AMD_SECURE_DISPLAY`, it defines `enum secure_display_mode`, `struct phy_id_mapping`, `struct crc_data`, `struct crc_info`, `struct crc_window_param`, `struct secure_display_crtc_context`, and `struct secure_display_context`. `amdgpu_dm_is_valid_crc_source` checks enabled non-`none` sources. Function declarations are conditionally exposed for debugfs CRC control and secure-display ROI CRC handling, with no-op/NULL macros when disabled.

## Control Flow
The header defines the compile-time control surface: debugfs builds wire CRTC funcs to CRC set/verify/source/get/IRQ handlers, while non-debugfs builds replace them with NULL or empty macros. Secure-display builds add ROI activation, window IRQ, and context creation; other builds compile those uses out.

## State And Persistence
Secure-display structures store per-CRTC work items, ROI rectangles, per-window RGB CRC values, frame counts, readiness flags, and PHY mapping metadata for connected SST/MST displays. This is runtime kernel state only.

## Dependencies And Integration Points
It forward declares DRM CRTC and DM CRTC state and expects surrounding AMDGPU/DC headers to provide `MAX_CRC_WINDOW_NUM`, `struct crc_window`, workqueue, spinlock, and device types when secure display is enabled. It is included by `amdgpu_dm.h` and consumed by CRTC functions and CRC implementation.

## Risks
Macro fallbacks must match function-pointer expectations; `amdgpu_dm_crc_window_is_activated(x)` expands to no value when secure display is disabled, so callers must keep uses under matching `#ifdef`s. Secure-display array sizes (`MAX_CRTC`, `MAX_CRC_WINDOW_NUM`) must match hardware and mode-info limits. Structs shared with IRQ code require careful locking around `crc_info` and window parameters.

## Test Signals
Compile matrix coverage for `CONFIG_DEBUG_FS` and `CONFIG_DRM_AMD_SECURE_DISPLAY` on/off combinations is essential. Runtime signals are CRC source callbacks present in DRM CRTC funcs when expected, no unresolved references in disabled builds, secure-display context allocation for every CRTC, and valid per-window CRC data under ROI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.c

## Purpose
`amdgpu_dm_crtc.c` implements AMDGPU Display Manager CRTC lifecycle, vblank/vupdate IRQ control, panel self-refresh coordination, idle optimization work, DM CRTC atomic state management, CRTC property hooks, atomic validation, and CRTC initialization with primary/cursor planes and color-management capabilities.

## Important APIs, Types, And Functions
Public functions include `amdgpu_dm_crtc_handle_vblank`, `amdgpu_dm_crtc_modeset_required`, `amdgpu_dm_crtc_vrr_active_irq`, `amdgpu_dm_crtc_set_vupdate_irq`, `amdgpu_dm_crtc_vrr_active`, `amdgpu_dm_crtc_set_panel_sr_feature`, `amdgpu_dm_is_headless`, `idle_create_workqueue`, `amdgpu_dm_crtc_enable_vblank`, `amdgpu_dm_crtc_disable_vblank`, and `amdgpu_dm_crtc_init`. Static helpers handle idle polling, deferred vblank control, vblank IRQ get/put, state destroy/duplicate/reset, debugfs late registration, optional AMD private regamma property set/get, active-plane counting, helper atomic checks, and ISM defaults.

## Control Flow
Vblank handling notifies DRM and sends pending cursor-only events under the DRM event lock. Vblank enable validates that the CRTC is configured, restores vblank counters when IPS/self-refresh may have hidden interrupts, enables vupdate IRQs for active VRR, gets CRTC/pageflip/vline0 IRQs, and queues deferred work to update active vblank counts and ISM idle state. Disable reverses IRQ references and queues corresponding idle-entry work. Panel self-refresh logic enables Replay or PSR only when VRR is inactive, vblank is disabled, entry is allowed, and secure-display CRC windows are inactive. Atomic check updates active plane counts, requires a primary plane when enabling the CRTC, restricts async flips to fast updates, pulls in the primary plane for VRR handling, and validates DC streams.

## State And Persistence
The file manages runtime DRM object state and retained DC stream references. `amdgpu_dm_crtc_duplicate_state` retains streams and copies VRR/color/CRC/ABM/cursor fields; destroy releases the stream. The idle workqueue tracks `enable` and `running`; vblank deferred work retains a stream until work completion. CRTC initialization records `acrtc` in `adev->mode_info.crtcs`, initializes ISM state, cursor limits, IDs, and DRM color-management sizes.

## Dependencies And Integration Points
It depends on DRM vblank and atomic helpers, AMDGPU IRQ APIs, DC interrupt/stream validation/idle APIs, PSR and Replay helpers, plane initialization, debugfs setup, ISM tracing/events, CRC secure-display activation checks, and color-management constants from `amdgpu_dm.h`. Its CRTC funcs wire in the CRC callbacks declared by `amdgpu_dm_crc.h`.

## Risks
Risks include unbalanced IRQ get/put sequences if later IRQ enablement fails, deferred vblank work running after stream teardown without correct retain/release, event-lock races around cursor-only events, relying on `base.enabled` for vblank enable rejection, async flip classification depending on `update_type`, legacy userspace breakage if primary-plane requirements change, self-refresh enabling while CRC/VRR/replay constraints are stale, and failure paths in CRTC init that may need cleanup if plane initialization partially succeeds.

## Test Signals
Signals include vblank counter/event correctness, cursor-only commits delivering events, VRR enabling vupdate IRQs only when needed, async flip rejection for non-fast updates, CRTC enable rejected without a primary plane, PSR/Replay entry/exit around vblank enable/disable and CRC windows, suspend/resume with IPS vblank restore, DC stream retain/release leak checks, debugfs CRTC registration, and boot/modeset coverage across DCE/DCN/DCN4.01 color-capability differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.h

## Purpose
`amdgpu_dm_crtc.h` declares the CRTC-facing Display Manager helpers used by KMS, IRQ, PSR/Replay, and initialization paths.

## Important APIs, Types, And Functions
The header declares panel self-refresh coordination, vblank handling, modeset-required detection, vupdate IRQ control, VRR active checks for IRQ and atomic state paths, vblank enable/disable callbacks, and `amdgpu_dm_crtc_init`. These functions operate on `amdgpu_display_manager`, `amdgpu_crtc`, `dm_crtc_state`, DRM CRTC state, DC stream state, and DRM planes.

## Control Flow
No logic is implemented in the header. It exposes the flow implemented in `amdgpu_dm_crtc.c`: CRTC objects are initialized, atomic checks classify updates and stream validity, vblank callbacks enable/disable hardware IRQs, IRQ handlers report vblank events, and panel self-refresh policy is evaluated when vblank state changes.

## State And Persistence
The header owns no state. Its function signatures show the state being mutated in implementation: CRTC IRQ params, DM display-manager workqueues, DC stream state, `dm_crtc_state` VRR/color fields, and CRTC object lifetime.

## Dependencies And Integration Points
It relies on surrounding includes for AMDGPU/DRM/DC types and is included by files that need CRTC helper calls, including IRQ and PSR/Replay coordination code. It is the local boundary between CRTC implementation and the rest of Display Manager.

## Risks
Signature drift can break broad parts of the display driver because these helpers are shared across modeset, IRQ, and panel-self-refresh code. `amdgpu_dm_crtc_init` names its last parameter `link_index` in the header while the implementation treats it as `crtc_index`, a naming mismatch that can confuse callers even though the type is identical.

## Test Signals
Compile/link coverage for all CRTC users, successful CRTC creation for each display index, vblank callback registration through DRM CRTC funcs, and PSR/Replay/VRR paths invoking the declared helpers are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_crtc.h -->
