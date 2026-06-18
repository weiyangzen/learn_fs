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
