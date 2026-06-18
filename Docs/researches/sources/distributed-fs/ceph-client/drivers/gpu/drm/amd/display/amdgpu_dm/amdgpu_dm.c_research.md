# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-001376`: lines 1-8707, `Docs/researches/chunks/subset-b-001376_research.md`
- `subset-b-001377`: lines 8708-13717, `Docs/researches/chunks/subset-b-001377_research.md`

## Chunk Research

### subset-b-001376: lines 1-8707

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c lines 1-8707

## Scope

This chunk covers the first 8,707 lines of `amdgpu_dm.c`, the AMDGPU Display Manager bridge between DRM/KMS and AMD Display Core (DC). It includes module firmware declarations, DM/DC initialization and teardown, DMUB/DMCU firmware and memory setup, interrupt registration and interrupt handlers, hotplug and HPD RX work, suspend/resume and GPU reset recovery, DRM mode config private state, connector detection/update paths, backlight/sysfs support, plane and stream conversion helpers, FreeSync video mode helpers, DSC policy for SST/eDP streams, mode validation, HDR info packet setup, connector atomic checks, and the beginning of encoder/MST helper logic.

## Purpose

`amdgpu_dm.c` is the top-level KMS display integration file for AMD DC. In this chunk it:

- Registers the DM IP block hooks used by the core amdgpu device lifecycle.
- Converts DRM display objects, modes, connector state, plane state, and atomic private state into DC objects.
- Owns global display manager state inside `adev->dm`, including `dc`, DMUB services, workqueues, connector/sink references, backlight data, cached suspend state, and interrupt parameter arrays.
- Handles asynchronous hardware events from vblank, vupdate, pageflip, HPD, HPD RX, and DMUB outbox notifications.
- Creates DRM CRTCs, planes, encoders, connectors, writeback connectors, and private atomic state from DC link and capability data.
- Manages firmware-assisted features such as DMUB notifications, DMCU/ABM, PSR, Replay, DSC, FreeSync, HDCP callbacks, AUX/SET_CONFIG completion, and fused I/O completion.

## Important APIs, Types, and Functions

- `amdgpu_dm_init()` builds `dc_init_data`, sets ASIC/debug/feature flags, creates `adev->dm.dc`, initializes DMUB hardware, DC hardware, HPD RX workqueues, FreeSync, color modules, vblank/HDCP/idle/outbox work, DRM display objects, MST fake encoders, and vblank support.
- `amdgpu_dm_fini()`, `dm_hw_fini()`, `dm_sw_fini()`, and `amdgpu_dm_early_fini()` unwind workqueues, secure-display contexts, HDCP, DMUB outbox state, BOs, HPD RX queues, DC, CGS, FreeSync, mutexes, firmware references, and DMUB software objects.
- `dm_early_init()`, `dm_sw_init()`, `dm_hw_init()`, `dm_late_init()`, `dm_suspend()`, and `dm_resume()` are wired into `amdgpu_dm_funcs` and exported through `dm_ip_block`.
- `dm_init_microcode()`, `load_dmcu_fw()`, `dm_dmub_sw_init()`, `dm_dmub_hw_init()`, and `dm_dmub_hw_resume()` select firmware by DCE/DCN IP version, register PSP-loadable firmware records, allocate DMUB framebuffer windows, copy firmware/VBIOS/BSS/mailbox regions, initialize DMUB hardware, and recover it after resume.
- `dm_allocate_gpu_mem()` and `dm_free_gpu_mem()` expose DC GPU memory allocation through kernel BOs tracked in `adev->dm.da_list`.
- `dm_dmub_outbox1_low_irq()`, `register_dmub_notify_callback()`, `dmub_aux_setconfig_callback()`, `dmub_aux_fused_io_callback()`, `dmub_hpd_callback()`, and `dm_handle_hpd_work()` process DMUB traces and notifications, optionally offloading HPD work to `adev->dm.delayed_hpd_wq`.
- `dm_pflip_high_irq()`, `dm_vupdate_high_irq()`, `dm_crtc_high_irq()`, and optional `dm_dcn_vertical_interrupt0_high_irq()` handle pageflip completion, VRR vupdate, vblank/CRC/writeback completion, FreeSync BTR vmin/vmax updates, and secure-display CRC window interrupts.
- `register_hpd_handlers()`, `dce110_register_irq_handlers()`, `dcn10_register_irq_handlers()`, and `register_outbox_irq_handlers()` map DC IRQ sources to amdgpu IRQ IDs and DM callbacks.
- `handle_hpd_irq_helper()`, `handle_hpd_rx_irq()`, `dm_handle_hpd_rx_offload_work()`, `hdmi_hpd_debounce_work()`, and `schedule_hpd_rx_offload_work()` implement full hotplug, short-pulse, MST message-ready, link-loss, automated-test, CP IRQ, CEC IRQ, and HDMI debounce behavior.
- `amdgpu_dm_update_connector_after_detect()`, `amdgpu_dm_connector_detect()`, `amdgpu_dm_connector_poll()`, `emulated_link_detect()`, `create_eml_sink()`, and `handle_edid_mgmt()` keep DRM connector state, DC sink state, EDID, CEC, FreeSync caps, subconnector properties, and forced/headless detection in sync.
- `amdgpu_dm_mode_config_init()`, `dm_atomic_create_state()`, `dm_atomic_duplicate_state()`, `dm_atomic_destroy_state()`, `dm_atomic_get_state()`, and `dm_atomic_get_new_state()` create and manage the DM private atomic object that owns a `dc_state` copy.
- `amdgpu_dm_initialize_drm_device()` creates primary and overlay planes, CRTCs, connectors, encoders, writeback connectors, outbox IRQs, PSR/Replay defaults, backlight setup, and IRQ registration based on DC caps and ASIC/IP version.
- Backlight support is centered on `amdgpu_dm_update_backlight_caps()`, `convert_brightness_from_user()`, `convert_brightness_to_user()`, `amdgpu_dm_backlight_set_level()`, `amdgpu_dm_backlight_get_level()`, `amdgpu_dm_register_backlight_device()`, and `setup_backlight_device()`. It supports ACPI caps, panel quirks, AUX nits control, PWM control, custom luminance curves, scratch-register persistence for eDP0, and idle-optimization suppression during hardware access.
- Plane and stream conversion uses `fill_plane_color_attributes()`, `fill_dc_plane_info_and_addr()`, `fill_dc_plane_attributes()`, `fill_dc_dirty_rects()`, `update_stream_scaling_settings()`, `convert_color_depth_from_display_info()`, `get_output_color_space()`, `fill_stream_properties_from_drm_display_mode()`, `fill_audio_info()`, `create_stream_for_sink()`, `create_validate_stream_for_sink()`, and `dm_validate_stream_and_context()`.
- Connector/encoder DRM hooks in this chunk include `amdgpu_dm_connector_funcs`, `amdgpu_dm_connector_helper_funcs`, `amdgpu_dm_connector_atomic_set_property()`, `amdgpu_dm_connector_atomic_get_property()`, `amdgpu_dm_connector_atomic_check()`, `amdgpu_dm_connector_mode_valid()`, `dm_encoder_helper_atomic_check()`, and `dm_update_mst_vcpi_slots_for_dsc()`.

## Control Flow

Initialization starts in `dm_early_init()`, which verifies the AtomBIOS object header, sets legacy CRTC/HPD/DIG counts by ASIC or DCE IP version, installs `dm_display_funcs`, marks DC enabled, and requests DMUB firmware if supported. `dm_sw_init()` creates the CGS device, initializes the DAL allocation list, builds the DMUB software service and framebuffer metadata, and loads DMCU firmware if needed. `dm_hw_init()` calls `amdgpu_dm_init()`, initializes HPD, and adds an OEM I2C adapter if DC exposes one.

`amdgpu_dm_init()` is the main constructor. It initializes mutexes and IRQ support, fills DC init flags from module masks, ASIC/IP versions, DMI quirks, seamless boot, GPU VM support, FBC, LTTPR, IPS policy, DCN42 DPIA features, and optional DMUB-provided bounding-box data. After `dc_create()`, it applies debug masks, initializes DMUB hardware, calls `dc_hardware_init()`, creates HPD RX offload queues, initializes APUs' system aperture context, creates FreeSync/color/idle/HDCP/outbox support, initializes DRM objects, creates MST fake encoders, sets cursor caps, initializes vblank, and optionally secure-display contexts.

Runtime IRQ flow is split by event type. High-priority pageflip IRQs validate `pflip_status`, send or defer DRM vblank events depending on VRR front-porch timing, update `last_flip_vblank`, and clear flip state. Vblank/vupdate IRQs update DRM vblank, CRC, writeback completion, FreeSync BTR parameters, and offload vmin/vmax DC updates to workqueue context. Low-priority DMUB outbox IRQs drain trace entries, pull DMUB notifications, validate notification type and handler, then either call handlers directly or queue HPD work.

Hotplug flow starts from legacy HPD IRQs or DMUB HPD notifications. `handle_hpd_irq_helper()` checks forced state, HDCP reset needs, connection type, HDMI debounce conditions, DC detection, connector/sink update, DRM state restore, and KMS hotplug events. HPD RX short-pulse handling first asks DC to parse HPD RX data, then offloads MST sideband readiness, automated-test handling, and link-loss handling as needed; otherwise it may detect downstream status changes, update connector state, handle CP IRQ, and signal DP CEC.

Suspend/resume has two distinct paths. In GPU reset, `dm_suspend()` disables ISM and idle optimizations, copies `dc->current_state`, disables interrupts for streams with planes, commits zero streams, suspends IRQs, and flushes HPD RX work. GPU-reset `dm_resume()` reinitializes DMUB, powers DC to D0, resumes DC and IRQs, marks streams and planes for full update, reenables outbox, commits cached streams, reapplies plane state, reenables interrupts, releases cached DC state, and restores backlight. In normal S3/S4/S0ix, suspend caches DRM atomic state, suspends HDMI CEC and MST, suspends IRQs, disables ISM, flushes HPD RX work, powers DC/DMUB to D3, and optionally allows IPS idle. Resume recreates the DM private `dc_state`, resumes DMUB/outbox/DC/ISM/IRQ, restores CEC and MST, redetects connectors, updates sinks, resumes cached DRM state, probes MST topology, resumes late IRQs, writes SMU watermarks, and emits a hotplug event.

Mode validation and stream creation flow from DRM connector helpers into `amdgpu_dm_connector_mode_valid()`, which duplicates the mode, computes CRTC timings, and calls `create_validate_stream_for_sink()`. That function creates a DC stream, validates it, retries lower BPC down to an output-specific floor, optionally checks MST port support, validates a temporary stream+plane+global DC context, and on bandwidth/encoder failures recursively retries YUV422 then YUV420. `create_stream_for_sink()` handles fake sinks for writeback/headless cases, FreeSync video timing substitution, native timing/scaling decisions, HDMI/DP info packets, DSC policy, audio info, stream signal, VSC SDP colorimetry, and scaling rectangles.

## State and Persistence Behavior

Persistent driver state is concentrated in `struct amdgpu_display_manager` (`adev->dm`). This chunk initializes and mutates `dm.dc`, `dm.dmub_srv`, `dm.dmub_fb_info`, `dm.dmub_bo*`, `dm.dmub_notify`, `dm.fused_io[]`, workqueue pointers, `dm.hpd_rx_offload_wq`, `dm.freesync_module`, `dm.hdcp_workqueue`, `dm.atomic_obj`, `dm.cached_state`, `dm.cached_dc_state`, `dm.backlight_caps[]`, `dm.backlight_link[]`, `dm.backlight_dev[]`, `dm.brightness[]`, `dm.actual_brightness[]`, `dm.num_of_edps`, `dm.boot_time_crc_info`, `dm.bb_from_dmub`, and `dm.da_list`.

Connector state is split between DRM state and DM/DC references. `struct amdgpu_dm_connector` owns `dc_link`, `dc_sink`, `dc_em_sink`, `drm_edid`, `timing_requested`, `mst_mgr`, `mst_root`, `mst_output_port`, `bl_idx`, HDMI debounce cached sink state, and per-connector force/format flags. `amdgpu_dm_update_connector_after_detect()` carefully retains/releases DC sinks and replaces EDID/CEC/FreeSync state under DRM mode config locking. Connector atomic private fields in `struct dm_connector_state` persist scaling, underscan, ABM state, FreeSync capability, MST PBN, and VCPI slot counts across atomic duplicate/reset paths.

Firmware and memory persistence include DMUB firmware retained in `adev->dm.dmub_fw`, DMCU firmware in `adev->dm.fw_dmcu`, PSP firmware accounting in `adev->firmware.ucode[]`/`fw_size`, DMUB framebuffer windows in one kernel BO, boot-time CRC BOs, FBC compressor BOs, and temporary DAL allocations tracked in `da_list`. Backlight brightness is cached in `dm->brightness[]`, `actual_brightness[]`, and for index 0 also written to ATOMBIOS scratch registers.

Concurrency state is guarded by a mix of `dm.dc_lock`, per-connector `hpd_lock`, `audio_lock`, `dpia_aux_lock`, DRM mode config locks, DRM event locks, writeback job locks, offload workqueue spinlocks, completions for DMUB replies, and workqueue flushing/cancellation during teardown/suspend. IRQ handlers use atomic/GFP_ATOMIC contexts where necessary and offload slow paths like HPD handling and vmin/vmax updates.

## Dependencies and Integration Points

This code depends heavily on AMD DC (`dc_create`, `dc_destroy`, `dc_commit_streams`, `dc_link_detect`, `dc_validate_*`, `dc_state_*`, `dc_stream_*`, DSC helpers, PSR/Replay helpers, DMCU/ABM, DMUB service wrappers), amdgpu core services (`amdgpu_ip_block`, IRQ registration, BO allocation, firmware loading, CGS, SMU/DPM watermarks, ATOMBIOS scratch, reset/suspend flags), DRM/KMS (`drm_atomic`, connector/encoder/helper funcs, MST topology manager, EDID, HDMI infoframes, writeback, vblank, color properties, privacy screen state), Linux platform APIs (`workqueue`, `component`, `backlight`, `power_supply`, `ACPI video`, `firmware`, `i2c`, `sysfs`), HDCP helpers, DP CEC, and optional secure display/debugfs/color feature blocks.

Important outward integration surfaces are:

- `dm_ip_block` for amdgpu device lifecycle.
- `dm_display_funcs` for legacy amdgpu display callbacks.
- `amdgpu_dm_mode_funcs` and `amdgpu_dm_mode_config_helperfuncs` for DRM atomic commit/check integration.
- `amdgpu_dm_connector_funcs`, `amdgpu_dm_connector_helper_funcs`, and `amdgpu_dm_encoder_helper_funcs` for KMS object behavior.
- DMUB notification callback arrays and outbox IRQ handlers for firmware-to-driver event delivery.
- Backlight class devices and `/sys/class/drm/.../amdgpu/panel_power_savings` for user-visible panel controls.
- Audio component binding for HDA ELD notification.

## Risks and Edge Cases

- Sink and stream lifetime is subtle. HPD, resume, forced detection, and mode validation all retain/release `dc_sink` and `dc_stream_state`; missed releases or stale references can cause leaks or use-after-free. The code contains many explicit retain/release calls and warnings around refcounts.
- IRQ paths are timing-sensitive. Pageflip completion under VRR front-porch timing deliberately defers events to vblank handling; changing this can break timestamps, throttling, or userspace pageflip completion.
- HPD RX work has duplicate suppression for MST sideband and link-loss handling. Failure to clear `is_handling_mst_msg_rdy_event` or `is_handling_link_loss` on all paths could suppress later events.
- Suspend/resume and GPU reset paths diverge. Reset resume assumes `dm->cached_dc_state` is valid and unlocks `dm->dc_lock` after successful recovery; error paths around zero-stream commit or DMUB init are high risk.
- DMUB firmware setup depends on IP-version tables, PSP load type, firmware header layout, framebuffer window sizing, and VBIOS copying. New ASIC support requires updating firmware declarations, `dm_init_microcode()`, `dm_dmub_sw_init()`, `dm_dmub_hw_init()` quirks, and init feature flags consistently.
- Backlight conversion mixes ACPI caps, AUX nits, PWM 16-bit scaling, user brightness ranges, panel quirks, custom luminance curves, and IPS idle gating. Off-by-one or invalid cap handling can cause unusable brightness ranges.
- Mode validation can recurse through YUV fallback flags on the connector. The flags are cleared after recursion, but failures inside recursion should be reviewed carefully when changing validation paths.
- MST bandwidth accounting is distributed between connector atomic check, stream validation, and later DSC VCPI adjustment. PBN/VCPI mismatches can break MST multi-monitor allocation.
- HDMI HPD debounce caches a sink reference and may emit only internal reenable if sinks match. This behavior is useful for spurious toggles but risky for monitors that change capabilities without EDID difference.
- `dm_allocate_gpu_mem()` assigns `*addr = da->gpu_addr` before checking `amdgpu_bo_create_kernel()` return, so callers must treat a NULL CPU pointer as failure and ignore the address.
- Some functions are intentional stubs/TODOs (`dm_is_idle`, `dm_wait_for_idle`, `dm_soft_reset`, `dm_bandwidth_update`, empty encoder disable), so tests should not assume full behavior there.

## Test Signals

Useful validation signals for this chunk include:

- Boot logs: `Display Core v... initialized`, DMUB firmware version/init logs, DCN/IP unsupported errors, outbox IRQ registration errors, PSR/Replay capability messages, backlight registration messages, and link/sink debug dumps.
- KMS and IGT coverage: atomic modeset, pageflip/vblank, VRR/FreeSync, writeback, connector hotplug, MST topology, DP/HDMI mode validation, HDR metadata, privacy screen, scaling/underscan, overlay/MPO, damage clips, PSR selective update, and suspend/resume tests.
- Firmware and platform coverage: PSP-loaded vs backdoor-loaded DMUB, DMCU-supported ASICs, DCN 3.x/4.x IP-version matrices, USB4/DPIA links, eDP PSR/Replay/DSC panels, DP-HDMI PCON paths, and APU system aperture setup.
- Runtime events: HPD plug/unplug, HPD RX short pulse, MST sideband ready, link loss, CP IRQ/HDCP, HDMI debounce reconnect, CEC EDID attach/unset, DMUB AUX/SET_CONFIG/fused I/O completion, and DMUB trace/outbox draining.
- Power management: S3/S4/S0ix suspend/resume, GPU reset recovery, IPS idle enable/disable around register/backlight access, MST resume after suspend, and backlight restore after reset.
- Sysfs/user controls: backlight brightness reads/writes, ACPI native backlight fallback, panel power savings read/write and hotplug-triggered update, connector scaling/underscan/ABM atomic property round trips, and forced connector EDID management.

### subset-b-001377: lines 8708-13717

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm.c lines 8708-13717

## Scope And Purpose

This chunk is the second and final chunk of AMDGPU Display Manager's main DRM/DC bridge file. It covers connector mode enumeration and property setup, DDC/I2C adapter plumbing, encoder/connector construction, the display atomic check and commit path, VRR/FreeSync capability parsing, cursor mode selection, Display Core stream/plane validation, writeback programming, HDCP/audio notifications, DMUB AUX/fused-I/O synchronization, and low-level register access hooks.

The code is the runtime integration layer between Linux DRM atomic modesetting objects and AMD Display Core (`dc`) objects. DRM connector, CRTC, plane, framebuffer, writeback, MST, HDCP, and color-management state are translated into `dc_stream_state`, `dc_plane_state`, `dc_state`, stream updates, surface updates, and DMUB commands. Most of the chunk is safety-critical modeset code: atomic check builds and validates a prospective DC state without programming hardware, while atomic commit consumes that checked state to program streams, planes, interrupts, cursor state, VRR packets, self-refresh, writeback, audio, and runtime PM references.

The chunk begins immediately after native-mode discovery logic from the previous chunk and starts with helpers that clone native panel timings into common panel modes. It ends at the last functions in the file, including DMUB command execution wrappers and a stub for ACPI PHY transition interlock.

## Connector Modes, Properties, And DDC

`amdgpu_dm_create_common_mode()`, `amdgpu_dm_connector_add_common_modes()`, and `common_modes[]` synthesize lower-resolution eDP/LVDS modes by duplicating the native mode and replacing only visible width/height/name. This keeps timings derived from the native panel mode while exposing common scaled modes to userspace. `amdgpu_set_panel_orientation()` probes modes under `mode_config.mutex`, reads the native mode cached in `amdgpu_encoder`, and lets DRM apply panel-orientation quirks.

`amdgpu_dm_connector_ddc_get_modes()` refreshes `connector->probed_modes` from a cached `struct drm_edid`, sorts modes before selecting the native mode, and restores FreeSync capability state because `drm_edid_connector_add_modes()` resets display-info properties. When no EDID is present, `amdgpu_dm_connector_get_modes()` falls back to no-EDID modes, adds 1920x1080 for DP 128b/132b links, and adds common analog modes for DAC-load-detected analog sinks. With EDID, it adds EDID modes, panel common modes, synthetic FreeSync video modes, and initializes FBC.

`add_fs_modes()` creates driver-only modes at common video refresh rates by increasing vertical totals on the highest-refresh mode at the preferred resolution. It rejects rates outside the connector's FreeSync min/max range and avoids illegal timing ordering. `amdgpu_dm_connector_add_freesync_modes()` gates these synthetic modes behind the `amdgpu_freesync_vid_mode` module parameter, valid EDID/DC sink/link objects, DC VRR support, non-analog sinks, and a FreeSync range wider than 10 Hz.

`amdgpu_dm_connector_init_helper()` fills the connector runtime state and attaches DRM properties: scaling, underscan, max bpc, broadcast RGB, HDMI content type, HDMI/DP colorspace, HDR output metadata, VRR capable, content protection, panel type, and privacy-screen provider. It also configures HPD polling, ycbcr420 support from link encoder features, HDMI HPD debounce delayed work, connector IDs, audio instance, adaptive-sync metadata, and synchronization locks. This helper assumes connector state has been reset first because several properties depend on initialized atomic connector state.

`amdgpu_dm_i2c_xfer()`, `amdgpu_dm_i2c_func()`, `amdgpu_dm_i2c_algo`, and `create_i2c()` expose DC DDC services as Linux I2C adapters. Transfers are translated into `struct i2c_command` payloads and routed either through `dc_submit_i2c_oem()` or `dc_submit_i2c()` for the link index. `amdgpu_dm_connector_init()` creates the hardware I2C adapter, registers the DRM connector with DDC, adds helper funcs, attaches the encoder, initializes HDMI CEC notifiers, and performs DP-specific connector initialization. Failure after I2C allocation frees the adapter data and clears `aconnector->i2c`.

`amdgpu_dm_initialize_hdmi_connector()` registers a CEC notifier unless disabled by `DC_DISABLE_HDMI_CEC`. `amdgpu_dm_encoder_init()` initializes a DRM TMDS encoder, assigns possible CRTCs from `amdgpu_dm_get_encoder_crtc_mask()`, and installs encoder helper funcs.

## Atomic Commit Control Flow

`amdgpu_dm_atomic_setup_commit()` first lets DRM MST prepare commit state, then updates CRTC color-management state when the CRTC is active and either color properties, regamma transfer function, or modeset state require it.

`amdgpu_dm_atomic_commit_tail()` is the commit tail called after atomic check has succeeded. Its high-level order is:

1. Update legacy modeset bookkeeping and wait for MST dependency commits.
2. Retrieve the DM private `dc_state` and call `amdgpu_dm_commit_streams()` to commit DC streams.
3. Update HDCP state through `amdgpu_dm_update_hdcp()`.
4. Apply stream-only updates for non-modeset connector changes: scaling/underscan, broadcast RGB output colorspace, ABM level, HDR metadata, and privacy-screen state. Because DC requires at least one surface update, dummy updates are built from current stream status planes.
5. Enable IRQ/vblank handling for newly active or modeset CRTCs, retain stream references in IRQ params, update VRR IRQ parameters, handle VRR transition vblank refs, and reapply debugfs CRC configuration when enabled.
6. Commit planes per CRTC with `amdgpu_dm_commit_planes()`.
7. Enable writeback jobs, notify audio ELD changes, restore panel backlight levels, send leftover DRM events, mark hardware programming done, wait for flip completion when appropriate, clean up planes, release reserved VGA VRAM outside suspend, and drop runtime PM refs for newly disabled CRTCs.

`amdgpu_dm_commit_streams()` disables existing writeback capture, turns off interrupts and releases old streams for inactive or modeset CRTCs, updates timestamping constants, decides which CRTCs need set/reset operations, manages runtime PM gets for enabled CRTCs, disables PSR/Replay before modesets, performs `dc_commit_streams()` under `dm->dc_lock`, records OTG instances from DC stream status, and restores eDP brightness after modesets/resume.

`amdgpu_dm_commit_planes()` builds one heap-allocated bundle containing `dc_surface_update`, `dc_plane_info`, `dc_scaling_info`, `dc_flip_addrs`, and a `dc_stream_update`. It handles cursor-native and cursor-overlay transitions, walks old/new planes for the target CRTC, fills scaling and color update pointers, fills plane info and addresses for flips, computes dirty rects for PSR/Replay, enforces async flip restrictions, updates FreeSync preflip state for the primary plane, prepares flip events under `event_lock`, optionally attaches VRR info-packet updates, flushes vblank-control work before hardware programming, disables PSR/Replay around full or VRR updates, adjusts DC vmin/vmax if FreeSync timing changed, calls `update_planes_and_stream_adapter()`, refreshes pageflip IRQ state when active plane counts change, and re-enables self refresh if conditions allow.

`prepare_flip_isr()` consumes the DRM event from CRTC state into `amdgpu_crtc->event` and marks `pflip_status` as submitted. The pageflip interrupt later completes the event. Cursor-only updates can also consume the event and rely on vblank completion.

`manage_dm_interrupts()` is the stream on/off interrupt gate. On enable, it configures DRM vblank offdelay based on ASIC generation and APU/dGPU class, enables vblank, and gets pageflip/vline0 IRQs on specific DCN 3.x dGPUs. On disable, it puts those IRQs and calls `drm_crtc_vblank_off()`. `dm_update_pflip_irq_state()` forces hardware reapplication of current pageflip IRQ state after pipe power gating can have lost interrupt enablement.

## Atomic Check And DC State Construction

`amdgpu_dm_atomic_check()` validates the prospective atomic state and builds a detached DC state when full validation is required. It starts with DRM modeset checks, marks connector-driven ABM/scaling changes as connector changes, adds affected CRTCs for MST DSC fairness, verifies LUT sizes, adds affected connectors and planes for modesets or color/VRR/DSC changes, pulls all primary/overlay planes for any modified CRTC so z-order can be reconstructed, normalizes zpos, selects cursor modes, removes changed planes, disables changed CRTCs, enables changed CRTCs, adds new/modified planes, pre-validates DSC, checks planes, applies native cursor restrictions, optionally short-circuits legacy cursor async updates, updates MST slot info for link encoding format, and then either performs full DC/MST validation or frees the private DM state for fast updates.

The full-validation branch acquires all modeset locks with `do_aquire_global_lock()`, waits for pending commit `hw_done` and `flip_done`, computes MST DSC configs, updates VCPI slots, runs `drm_dp_mst_atomic_check()`, and calls `dc_validate_global_state()`. The fast-update branch destroys the transient DM private object so no stale detached DC context can be used later. At the end, async flips are allowed only for fast updates that do not change framebuffer memory type, and each CRTC records `UPDATE_TYPE_FULL` or `UPDATE_TYPE_FAST`.

`dm_update_crtc_state()` owns stream creation/removal in atomic check. For enable paths it finds the connector, creates and validates a stream for the sink, fills HDR metadata, optionally suppresses unnecessary modesets when the new and old DC streams/scaling are unchanged, handles FreeSync video fixed-refresh front-porch-only timing changes, adds streams to the DM atomic DC context, and updates scaling, ABM, color-management checks, and FreeSync config. For disable paths it removes the old stream from the DC context, releases it, clears `dm_new_crtc_state->stream`, resets VRR state, and requests full lock/validation.

`should_reset_plane()` decides whether a plane must be removed/recreated in DC instead of fast-updated. Reset is required for older ASIC modeset-allowed paths, writeback jobs, GPU reset, CRTC movement, cursor mode changes, CRTC color-management changes, zpos changes, modesets, adding/removing primary/overlay planes on the same CRTC, scaling/rotation/blend/alpha/colorspace changes, plane HDR/color-pipeline changes, pixel format changes, and tiling/modifier changes. `dm_update_plane_state()` applies that decision by removing old DC planes on disable, creating/filling/adding new `dc_plane_state` objects on enable, marking MPO requests, and falling back from overlay cursor to native cursor validation on `-EINVAL`.

Cursor behavior is a major policy point. `dm_crtc_get_cursor_mode()` chooses native or overlay cursor mode after zpos normalization. Native mode is forced on DCN401/DCN420, while earlier DCN uses overlay mode when the cursor would be blended over YUV planes, differently scaled planes, active plane color pipelines, or holes in CRTC coverage. `dm_check_cursor_fb()` enforces native cursor size, no cropping, pitch of 64/128/256 pixels, and linear tiling when no DRM modifier is present. The native cursor is also rejected on DCN401/DCN420 if rotated or scaled.

## VRR, FreeSync, PSR, Replay, And Timing Sync

The chunk maintains FreeSync and VRR state at connector, CRTC, stream, IRQ, and info-packet levels. `get_freesync_config_for_crtc()` maps connector FreeSync capability and mode refresh into `mod_freesync_config`, using fixed, variable, inactive, or unsupported states. `reset_freesync_config_for_crtc()`, `is_timing_unchanged_for_freesync()`, and `set_freesync_fixed_config()` support FreeSync video mode where only vertical totals/front porch change and a full modeset may be skipped.

`update_stream_irq_parameters()` rebuilds `mod_vrr_params` from CRTC FreeSync config and stores the config, active plane count, and VRR params into `amdgpu_crtc->dm_irq_params` under `event_lock` for IRQ handlers. `update_freesync_state_on_stream()` handles preflip updates, legacy vupdate handling on pre-AI ASICs, PCON/replay adaptive-sync info-packet construction, VRR info-packet comparison, and stream `allow_freesync` state. `amdgpu_dm_handle_vrr_transition()` keeps vblank and vupdate IRQs held while VRR is active to avoid bogus timestamps and releases them when returning to fixed refresh.

`amdgpu_dm_enable_self_refresh()` coordinates PSR and Panel Replay. It sets up PSR/Replay on non-fast updates, decrements connector self-refresh skip counts on fast updates, toggles `allow_sr_entry`, and enables Replay or PSR-SU only when not in VRR, CRC capture is not active, dirty-rect changes have been stable long enough, and the connector does not disallow eDP PSR entry.

`amdgpu_dm_update_freesync_caps()` updates connector FreeSync capability from EDID, DisplayID dynamic timing blocks, DP/HDMI AMD VSDB data, PCON whitelist adaptive-sync type, and optional MCCS DDC transactions. It updates connector monitor ranges, `amdgpu_dm_connector` min/max vfreq, VSDB fields, SDP packing, sink MCCS/FreeSync VCP code, DRM `vrr_capable` property, and disables Replay support if FreeSync is no longer capable. `amdgpu_dm_trigger_timing_sync()` toggles triggered CRTC reset on current DC streams and calls DC per-frame master-sync helpers under `dc_lock`.

## EDID Parsing And DMUB/DMCU Interfaces

`dm_edid_parser_send_cea()`, `parse_edid_cea_dmub()`, and `parse_edid_cea_dmcu()` send CEA extension chunks to DMUB or DMCU firmware to parse AMD VSDB data. DMUB uses `DMUB_CMD__EDID_CEA` commands with replies that either acknowledge chunks or return AMD VSDB fields. DMCU sends eight-byte chunks and receives ACK/result through DC parser APIs. `parse_edid_cea()` selects DMUB or DMCU under `dc_lock`. `parse_edid_displayid_vrr()` locally scans DisplayID extension block `0x25` for dynamic video timing range when base DRM monitor range data is absent. `parse_hdmi_amd_vsdb()` locates the CEA extension and delegates AMD VSDB parsing.

The tail exposes synchronous DMUB/DPIA transaction helpers. `amdgpu_dm_process_dmub_aux_transfer_sync()` serializes through `dpia_aux_lock`, starts an async DMUB AUX transfer, waits up to 10 seconds for `dmub_aux_transfer_done`, copies reply command/data into the AUX payload, maps DMUB notification status to `operation_result`, and reinitializes the completion. `amdgpu_dm_process_dmub_set_config_sync()` does the same for set-config commands.

`execute_fused_io()` and `amdgpu_dm_execute_fused_io()` support fused DMUB I/O command lists keyed by DDC line. They execute a command list with reply, wait on the per-line `fused_io_sync.replied` completion for a matching identifier, copy the reply into the first request, and abort on timeout via `abort_fused_io()`. `dm_execute_dmub_cmd()` and `dm_execute_dmub_cmd_list()` are thin wrappers over DC DMUB service command runners.

`dm_write_reg_func()` and `dm_read_reg_func()` are DC register access callbacks. They optionally reject address zero, exit idle power state before hardware access, route through CGS read/write helpers, and trace register access counts. Reads additionally reject invalid use during DMUB reg-helper offload gather mode.

## HDCP, Audio, Writeback, And Hotplug Recovery

`is_content_protection_different()` encodes HDCP state transitions across connector and CRTC state. It handles HDCP content-type changes, re-enable requests from enabled to desired, S3 resume where restored enabled becomes desired, stream removal/re-enable, HPD/headless S3/DPMS cases via `update_hdcp`, mode-change reauthentication, and no-op desired/enabled transitions. `amdgpu_dm_update_hdcp()` iterates connector changes, resets HDCP for lost streams, persists MST connector HDCP properties in the per-link workqueue arrays, and calls `hdcp_update_display()` with content type and encryption enable/disable intent.

`amdgpu_dm_commit_audio()` notifies audio ELD removal when connectors change CRTCs or modeset, clears `aconnector->audio_inst` under `audio_lock`, then notifies additions from new stream status audio instances after modesets. Writeback support is split between `dm_clear_writeback()` and `dm_set_writeback()`: commit streams remove old writeback capture, while commit tail adds a `dc_writeback_info` configured from CRTC mode and writeback framebuffer pitch/address, attaches it to the DC stream, marks CRTC writeback pending state, and queues the DRM writeback job.

`dm_force_atomic_commit()` constructs an internal atomic state that marks the disconnected CRTC's mode as changed and commits it. `dm_restore_drm_connector_state()` uses this to recover cases where hotplug does not produce a userspace modeset, including unplug/replug on the same port or systems without a userspace desktop manager. It only acts when the connector has a current DC sink, state, encoder, CRTC stream, and the stream sink differs from the connector sink.

## State And Persistence Behavior

Persistent state lives across multiple layers:

- DRM object state: connector properties, CRTC active/modeset flags, plane state, writeback jobs, MST topology state, colorop state, privacy-screen state, vblank/event state, and atomic private objects.
- AMD DM state: `amdgpu_dm_connector` caches DDC/EDID-derived FreeSync ranges, VSDB/replay metadata, DC link/sink pointers, HPD debounce state, audio instance, self-refresh skip count, and I2C adapter state. `amdgpu_crtc` stores OTG instance, enable state, hardware mode, cursor size, pageflip status, event pointer, writeback state, and IRQ parameters.
- DC state: `dc_state` streams/planes are created during atomic check, retained/released around commit and IRQ usage, validated globally for full updates, and discarded for fast updates.
- Firmware synchronization state: DMUB AUX completions, fused-I/O per-DDC-line completion slots, `dmub_notify`, and replay/PSR settings on links.
- Power-management state: runtime PM refs are acquired when CRTCs are enabled and released for newly disabled CRTCs; idle optimizations are explicitly exited before DC programming and register access; PSR/Replay may be disabled and later re-enabled depending on commit type.

The most important persistence invariant is ownership of DC object references. Atomic check may create `dc_stream_state` and `dc_plane_state` objects, attach them to the detached DC context, and transfer lifetime to the atomic state. Commit retains active streams for IRQ handler access and releases old streams after disabling. Fast updates deliberately remove the DM private object from the atomic state to avoid a stale detached context.

## Dependencies And Integration Points

This chunk integrates with Linux DRM core APIs for connectors, encoders, EDID, modes, atomic states, vblank, events, MST, DSC, writeback, color management, color pipelines, privacy screens, CEC, I2C, and runtime PM. It depends on AMDGPU core objects (`amdgpu_device`, `amdgpu_crtc`, `amdgpu_framebuffer`, BO memory type, IRQ helpers, TTM VRAM reservation helpers, IP-version checks, and family-specific tiling fields). It also relies heavily on AMD Display Core and firmware APIs: `dc_commit_streams`, `dc_validate_global_state`, `dc_state_add/remove_stream`, `dc_state_add/remove_plane`, `dc_stream_update`, `dc_stream_set_cursor_*`, FreeSync module helpers, PSR/Replay helpers, MST/DSC helpers, DMUB command runners, DMCU/DMUB EDID parsers, and AUX/set-config async paths.

Conditional integration points include `CONFIG_DRM_AMD_SECURE_DISPLAY` CRC/vline0 handling, `CONFIG_DEBUG_FS` CRC reconfiguration, `CONFIG_DRM_AMD_DC_FP` DSC pre-validation, HDMI CEC, HDCP workqueues, DisplayPort MST topology managers, panel privacy screens, and writeback connectors.

## Risks And Edge Cases

The atomic path is sensitive to ordering. Interrupts are disabled before old streams are released and re-enabled only after stream programming so IRQ handlers do not observe stale DRM/DC state. Pending commits are drained under global modeset locks before full validation because IRQ handlers still reference DRM state directly. Any change that skips this synchronization can create pageflip timeouts, use-after-free of DC streams/planes, or incorrect validation against concurrent commits.

Fast versus full update classification is high risk. Under-classifying a bandwidth-affecting plane, stream, DSC, MST, color, tiling, memory-type, zpos, scaling, or writeback change as fast would bypass global DC validation. Over-classifying fast updates as full can cause unnecessary modesets, flicker, latency, and PSR/Replay churn. Async flips are explicitly restricted to fast updates without framebuffer memory type changes.

VRR/FreeSync/PSR/Replay interactions are fragile. VRR requires held vblank/vupdate IRQs for timestamp correctness, FreeSync video mode may suppress a full modeset for vertical-total-only timing changes, PSR-SU must be disabled around dirty-rect changes and re-enabled only after stability, and Panel Replay/PCON paths use different info-packet variants. Bugs here can show up as stutter, black screens, timestamp regressions, or panel self-refresh artifacts.

Cursor mode selection has multiple hardware-generation constraints. Native cursor can be invalid over YUV/scaled/color-managed planes or incomplete CRTC coverage; overlay cursor needs a DC plane and is unavailable on DCE. Fallback and validation must remain consistent between atomic check and commit to avoid cursor disappearance or accidental transformation by an underlying plane.

EDID and firmware paths depend on synchronized command/reply protocols. DMUB AUX, set-config, fused-I/O, and EDID parsing serialize on `dpia_aux_lock` or `dc_lock` and rely on completion reinitialization after success and timeout. Missing reinit, wrong reply matching, or incorrect timeout handling can break later AUX/I2C transactions.

HDCP state transitions intentionally rewrite connector content-protection values in several resume, HPD, and mode-change cases. Regressions could leave userspace seeing enabled protection while encryption is not active, or repeatedly reauthenticate displays. MST HDCP properties must survive connector destruction/recreation.

## Test Signals

Useful test signals include DRM atomic KMS tests that exercise modeset, fast plane update, async pageflip, cursor update, zpos, scaling, color management, writeback, and MST/DSC paths. Failures generally appear as `atomic_check` `-EINVAL`, pageflip timeout, missing vblank event, DC global validation failure, black screen, or incorrect writeback output.

Hardware and integration coverage should include eDP/LVDS common-mode enumeration, HDMI/DP EDID and no-EDID fallbacks, analog no-EDID mode addition, HDMI CEC notifier creation, privacy-screen provider detection, content-protection property changes, audio ELD notifications across modesets, and hotplug restore without a userspace modeset.

VRR-specific signals include `vrr_capable` property state, generated FreeSync video modes, fixed-refresh FreeSync video timing changes that avoid unnecessary modesets, VRR on/off vblank reference handling, PCON/replay info-packet selection, and PSR/Replay disable/re-enable behavior during flips and dirty-rect changes.

DMUB/AUX test signals include successful and timed-out DPIA AUX transfers, protocol-error warning paths, set-config status propagation, fused-I/O timeout aborts, and repeated transfers after completion reinitialization. Register read/write trace counters and idle-exit behavior are additional low-level observability points.

## Cross-Chunk Notes

This chunk depends on types, helpers, globals, and module parameters defined earlier in `amdgpu_dm.c` and adjacent AMD display files, including connector/CRTC/plane state structs, `amdgpu_dm_connector_funcs`, `amdgpu_dm_connector_helper_funcs`, plane attribute filling, stream creation/validation, MST/DSC helpers, PSR/Replay helpers, HDCP workqueue definitions, and FreeSync module setup. The merge lane should combine this with chunk `subset-b-001376` to describe whole-file initialization, IRQ registration, suspend/resume, connector detection, property creation, and helper definitions that this tail chunk calls.
