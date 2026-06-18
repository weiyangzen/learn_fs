# Research: subset-b-001379

Grouped research for AMDGPU Display Manager debugfs, HDCP, helper, IRQ, and idle-state-management files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.c

## Purpose
`amdgpu_dm_debugfs.c` builds the Display Manager debugfs surface for connector, CRTC, and device-wide diagnostics and override controls. It exposes DP link and PHY settings, DP test patterns, DSC status and forced parameters, MST status and hotplug simulation, HDCP sink capability, eDP PSR/Replay and backlight state, DMUB trace buffers and trace masks, IPS residency counters, secure-display CRC windows, and low-level DTN/DCC logging.

## Important APIs, types, and functions
- Initialization entry points are `connector_debugfs_init()`, `crtc_debugfs_init()`, and `dtn_debugfs_init()`.
- Common write parsing is centralized in `parse_write_buffer_into_params()`, which copies a debugfs write buffer from userspace and parses hex `long` parameters.
- DP controls include `dp_link_settings_read/write()`, `dp_mst_link_setting()`, `dp_phy_settings_read/write()`, `dp_phy_test_pattern_debugfs_write()`, `dp_lttpr_status_show()`, `dp_sdp_message_debugfs_write()`, `dp_max_bpc_read/write()`, and `edp_ilr_show/write()`.
- DSC controls include `dp_dsc_clock_en_read/write()`, `dp_dsc_slice_width_read/write()`, `dp_dsc_slice_height_read/write()`, `dp_dsc_bits_per_pixel_read/write()`, `dp_dsc_pic_width_read()`, `dp_dsc_pic_height_read()`, `dp_dsc_chunk_size_read()`, `dp_dsc_slice_bpg_offset_read()`, `dp_dsc_passthrough_set()`, and `dp_dsc_fec_support_show()`.
- Power, firmware, and tracing hooks include `dmub_tracebuffer_show()`, `dmub_fw_state_show()`, `dmub_trace_mask_show/set()`, `dmcub_trace_event_state_get/set()`, `ips_status_show()`, `ips_residency_show()`, and `ips_residency_cntl_get/set()`.
- MST/HPD and device debug hooks include `trigger_hotplug()`, `mst_topo_show()`, `trigger_hpd_mst_set/get()`, `force_timing_sync_set/get()`, `disable_hpd_set/get()`, `dp_force_sst_set/get()`, `dp_ignore_cable_id_set/get()`, `visual_confirm_set/get()`, `skip_detection_link_training_set/get()`, and `dcc_en_bits_read()`.
- Under `CONFIG_DRM_AMD_SECURE_DISPLAY`, CRC window debugfs attributes update `amdgpu_crtc.dm_irq_params.window_param[]` and `crc_poly_mode`.

## Control flow
Connector setup selects entries by connector type. DP and eDP connectors get link, PHY, LTTPr, DSC, HDCP capability, SDP, max-BPC, MST-role, DPIA, and MST-link controls. eDP adds Replay, PSR, backlight, ILR, hotplug-detection, and PSR/Replay disallow controls. HDMI-A gets HDCP capability and HDMI-CEC control. Common connector entries are then created for YUV420 forcing, virtual hotplug, internal display reporting, and ODM-combine segment reporting.

Most write paths copy and parse small userspace buffers, validate ranges, then mutate either DC link settings or DRM connector/CRTC state. DP link forcing updates preferred training settings under `adev->dm.dc_lock`; MST link forcing sets preferred training with delayed retrain and synthesizes hotplug by toggling `connector->force`. DSC force writes locate the active `pipe_ctx`, lock mode-config and CRTC state, update `aconnector->dsc_settings`, and mark `dm_crtc_state->dsc_force_changed` so the next modeset evaluates the new settings.

Device-wide setup in `dtn_debugfs_init()` creates root debugfs files for MST topology, DC capabilities, DTN logs, MST/SST workarounds, visual confirmation, detection-link-training skipping, DMUB trace buffer/state/masks, timing sync, MST HPD trigger, DCC bits, HPD disable, and optional IPS status/residency controls. CRTC setup adds current BPC/colorspace and, when secure display is enabled, CRC window controls under the CRTC `crc` directory.

## State and persistence behavior
The file does not persist data across boots. It exposes and mutates live kernel and hardware-facing state: `dc_link` preferred/current link settings, lane drive settings, DPCD state, `amdgpu_dm_connector.dsc_settings`, connector force and content state, `amdgpu_display_manager` debug booleans, DMUB trace buffers in framebuffer windows, DMUB shared IPS state, `amdgpu_crtc.dm_irq_params` CRC fields, and DC debug options. Changes survive only until reset, hotplug, modeset, module unload, or driver teardown, except when they indirectly program sink DPCD or firmware state.

## Dependencies and integration points
This file depends on Linux debugfs, userspace copy helpers, DRM connector/CRTC state locks, DP AUX/DPCD helpers, AMD DC link APIs, DSC hardware state callbacks, DMUB services and GPINT commands, eDP PSR/Replay helpers, CEC notifier support, MST topology manager APIs, and optional secure-display CRC plumbing. It is the user-visible debugging and test-control boundary for AMDGPU DM and is especially tied to IGT/manual validation workflows.

## Risks and edge cases
Debugfs writes are privileged but can still destabilize links: forced link rates, PHY settings, HPD toggles, DSC overrides, and DPCD test patterns can intentionally desynchronize software, hardware, and sink state. Several DSC read paths scan `MAX_PIPES` and then use `pipe_ctx` without an explicit `i == MAX_PIPES` guard, so disconnected or unusual topology states are sensitive. Buffer parsing truncates to fixed parameter counts and treats values as base-16, which can surprise users. Locking spans mode-config, CRTC, HPD, and `dc_lock`; changes in these paths need deadlock testing. Secure-display CRC writes share `event_lock` state with IRQ-driven CRC paths, and PSR is disabled before activating a secure CRC window.

## Test signals
Useful tests include debugfs file creation per connector type, read/write round-trips for link settings and max-BPC, invalid-input rejection, DP test-pattern enable/disable with HPD behavior, MST hotplug and topology dumps, DSC force settings followed by atomic-check/modeset behavior, DMUB trace and mask reads, IPS residency start/stop/query, HDMI-CEC enable/disable, eDP PSR/Replay state/residency reads, ILR forcing on panels with supported link-rate tables, secure-display CRC window programming, and lockdep coverage under concurrent hotplug/modeset/debugfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.h

## Purpose
`amdgpu_dm_debugfs.h` is the small Display Manager debugfs interface header. It declares the three debugfs initialization hooks implemented by `amdgpu_dm_debugfs.c`.

## Important APIs, types, and functions
The exported prototypes are `connector_debugfs_init(struct amdgpu_dm_connector *connector)`, `dtn_debugfs_init(struct amdgpu_device *adev)`, and `crtc_debugfs_init(struct drm_crtc *crtc)`.

## Control flow
The header has no runtime control flow. AMDGPU DM initialization code includes it so connector, device, and CRTC creation paths can attach debugfs files at the right DRM debugfs nodes.

## State and persistence behavior
No state is defined here. The declared functions expose live debugfs state in the C implementation; all persistence behavior belongs to the objects passed into those calls.

## Dependencies and integration points
It includes `amdgpu.h` and `amdgpu_dm.h` for the concrete AMDGPU and DM connector types. It is the compile-time boundary between the broader DM driver and debugfs-specific implementation.

## Risks and edge cases
The main maintenance risk is signature drift between initialization call sites and the implementation. Because this header is unconditional while some debugfs contents are config-gated in the C file, callers should not infer that every individual file exists on every build or device.

## Test signals
Build coverage with `CONFIG_DEBUG_FS` enabled and disabled, plus probe-time validation that connector, CRTC, and device debugfs initialization links successfully, is sufficient for this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.c

## Purpose
`amdgpu_dm_hdcp.c` bridges DRM content-protection properties, AMD DC HDCP state-machine code, DP AUX/I2C DDC operations, PSP/TA secure services, and sysfs SRM handling. It creates one HDCP workqueue context per DC link, tracks connectors on that link, updates authentication policy on atomic commits, handles CPIRQ/watchdog/callback events, and exposes `/sys/class/drm/card*/device/hdcp_srm` so userspace can save and restore HDCP System Renewability Messages.

## Important APIs, types, and functions
- Public lifecycle and event APIs are `hdcp_create_workqueue()`, `hdcp_destroy()`, `hdcp_update_display()`, `hdcp_reset_display()`, and `hdcp_handle_cpirq()`.
- DDC adapter callbacks for `mod_hdcp` are `lp_write_i2c()`, `lp_read_i2c()`, `lp_write_dpcd()`, `lp_read_dpcd()`, `lp_atomic_write_poll_read_i2c()`, and `lp_atomic_write_poll_read_aux()`.
- PSP SRM helpers are `psp_get_srm()` and `psp_set_srm()`, using HDCP TA shared memory commands.
- Work handlers are `event_callback()`, `event_property_update()`, `event_property_validate()`, `event_watchdog_timer()`, and `event_cpirq()`.
- PSP stream integration is provided by `update_config()` through `cp_psp->funcs.update_stream_config`; ASSR enablement is provided by `enable_assr()`.
- Sysfs binary attribute callbacks are `srm_data_write()` and `srm_data_read()`.

## Control flow
`hdcp_create_workqueue()` allocates an array sized to `dc->caps.max_links`, allocates shared SRM buffers, initializes each per-link mutex and work item, binds DDC callbacks to the corresponding DC link, configures PSP capabilities, installs CP PSP callbacks, and creates the `hdcp_srm` binary sysfs file. `update_config()` is called from CP PSP stream configuration: DPMS-off removes the display; active streams populate `mod_hdcp_link` and `mod_hdcp_display` from connector, sink, stream encoder, link encoder, DPCD, and topology fields, add the display to the `mod_hdcp` engine, retain the DRM connector, and process returned scheduling requests.

When DRM asks to enable or disable content protection, `hdcp_update_display()` records the connector, optionally reloads a saved SRM into PSP, sets HDCP type policy, enables firmware or software locality-check options, schedules property validation, and calls `mod_hdcp_update_display()`. `process_output()` then translates `mod_hdcp_output` into delayed callback/watchdog work and property validation. CPIRQ and timer events call `mod_hdcp_process_event()` under the per-link mutex. Property validation queries each active display and schedules `property_update_work` when encryption status changes; property update waits for any pending commit and updates the DRM content-protection property to `ENABLED` or `DESIRED`.

## State and persistence behavior
Runtime state lives in `struct hdcp_workqueue`: work items, connector references indexed by DRM connector index, per-display encryption status, saved DRM content-protection/type values for MST reconnects, one `mod_hdcp` engine plus current link/display/output structs per link, `max_link`, SRM buffers, SRM version/size, and the sysfs binary attribute. Connector references are held with `drm_connector_get()` and released on replacement, reset, removal, and destroy. SRM persistence is delegated to userspace: PSP loses SRM across power transitions, and the sysfs file lets userspace read from PSP to storage and write from storage back to PSP.

## Dependencies and integration points
The file depends on AMD DC HDCP modules (`mod_hdcp`, `hdcp`, `hdcp_psp`), PSP HDCP and DTM trusted applications, DRM HDCP property helpers, DP AUX/DPCD and I2C helper paths, fused I/O locality-check support, workqueues, sysfs binary attributes, and CP PSP stream configuration callbacks. It integrates with atomic commit through connector state and with MST by keeping connector-indexed property snapshots.

## Risks and edge cases
HDCP is concurrency-sensitive: work handlers, commit completion waits, connector unplug, MST connector destruction, and reset all mutate connector references and encryption status. `event_property_update()` can wait up to ten seconds for commit `hw_done` and then forces status to desired on timeout. SRM sysfs writes may be chunked by PAGE_SIZE, so partial writes are intentionally attempted against PSP and only accepted if PSP validates a complete SRM; callers must read back to verify. Buffer sizes rely on `PSP_HDCP_SRM_FIRST_GEN_MAX_SIZE`, and `psp_set_srm()` copies the supplied size into TA shared memory. ASSR and SRM operations fail when PSP TA contexts are uninitialized.

## Test signals
Validation should cover HDCP 1.4 and 2.2 enable/disable for HDMI, DP SST, and DP MST, content type 0/1 policy, CPIRQ and watchdog recovery, connector unplug/reset during authentication, MST display reconnect preserving saved property choices, suspend/resume SRM restore, sysfs SRM chunked read/write and invalid SRM behavior, PSP TA unavailable paths, fused I/O locality-check toggles, and DRM property transitions from `DESIRED` to `ENABLED` and back.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.h

## Purpose
`amdgpu_dm_hdcp.h` defines the AMDGPU DM HDCP workqueue state and declares the HDCP lifecycle and event functions used by the rest of Display Manager.

## Important APIs, types, and functions
The central type is `struct hdcp_workqueue`, which stores work items, a per-link mutex, connector references, `mod_hdcp` state, encryption status arrays, saved content-protection properties, link count, SRM buffers/version/size, and the `hdcp_srm` binary attribute. Public functions are `hdcp_create_workqueue()`, `hdcp_destroy()`, `hdcp_update_display()`, `hdcp_reset_display()`, and `hdcp_handle_cpirq()`.

## Control flow
The header encodes the control contract: DM creates the workqueue array during device setup, CP PSP stream updates add/remove displays, atomic commit paths call `hdcp_update_display()` when content protection changes, IRQ paths call `hdcp_handle_cpirq()`, link reset paths call `hdcp_reset_display()`, and teardown calls `hdcp_destroy()`.

## State and persistence behavior
All state is runtime memory except SRM payloads that userspace can persist externally through the sysfs attribute created by the C file. The connector arrays are indexed by `AMDGPU_DM_MAX_DISPLAY_INDEX`; saved content-protection and content-type values help MST connectors recover property intent after temporary destruction.

## Dependencies and integration points
The header depends on AMD DC HDCP types, PSP CP stream types, `dc.h`, and `amdgpu.h`. It is included by HDCP implementation and by DM code that needs to update or destroy HDCP state.

## Risks and edge cases
The struct combines workqueue objects, reference-counted connectors, security-state buffers, and mod-HDCP engine state; changes to array sizes or connector-indexing assumptions must stay aligned with DRM connector index limits. Callers must pass a valid link index below `max_link` and must not use the workqueue after `hdcp_destroy()`.

## Test signals
Compile coverage plus runtime HDCP creation/destruction, connector reference leak checks, MST reconnect behavior, CPIRQ dispatch, SRM sysfs file creation/removal, and suspend/resume coverage validate the contract represented by this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_helpers.c

## Purpose
`amdgpu_dm_helpers.c` is the AMDGPU Display Manager implementation of helper callbacks expected by the DC core. It translates DC requests into Linux DRM, DP MST, AUX/DPCD, I2C, EDID, DSC, DMUB, ACPI, VBIOS, panel, memory, MCCS, and adaptive-sync operations.

## Important APIs, types, and functions
- EDID and panel helpers include `dm_helpers_parse_edid_caps()`, `dm_helpers_read_local_edid()`, `dm_helpers_init_panel_settings()`, and `dm_helpers_override_panel_settings()`, with local helpers for EDID quirks, ACPI EDID, and VBIOS hardcoded EDID.
- DP MST helpers include `dm_helpers_dp_mst_write_payload_allocation_table()`, `dm_helpers_dp_mst_poll_for_allocation_change_trigger()`, `dm_helpers_dp_mst_send_payload_allocation()`, `dm_helpers_dp_mst_update_mst_mgr_for_deallocation()`, `dm_helpers_dp_mst_start_top_mgr()`, and `dm_helpers_dp_mst_stop_top_mgr()`.
- AUX/I2C and DMUB helpers include `dm_helpers_dp_read_dpcd()`, `dm_helpers_dp_write_dpcd()`, `dm_helpers_submit_i2c()`, `dm_helpers_execute_fused_io()`, `dm_helper_dmub_aux_transfer_sync()`, `dm_helpers_dmub_set_config_sync()`, and `dm_helpers_dmub_outbox_interrupt_control()`.
- DSC and stream helpers include `dm_helpers_dp_write_dsc_enable()`, Synaptics DSC workaround helpers, `dm_helpers_mst_enable_stream_features()`, and `dm_helpers_dp_handle_test_pattern_request()`.
- Logging and memory helpers include `dm_dtn_log_begin()`, `dm_dtn_log_append_v()`, `dm_dtn_log_end()`, `dm_helpers_allocate_gpu_mem()`, and `dm_helpers_free_gpu_mem()`.
- MCCS/adaptive-sync helpers include `dm_helpers_read_mccs_caps()`, `dm_helpers_mccs_vcp_set()`, and `dm_get_adaptive_sync_support_type()`.

## Control flow
EDID reading prepares the DDC engine, repeatedly attempts ACPI EDID for internal panels, VBIOS hardcoded EDID when no DDC exists, or normal DDC reads, updates DRM connector display info, handles DP compliance checksum reporting, copies raw EDID into the DC sink, and parses audio, HDMI, name, and panel quirk data. `dm_helpers_parse_edid_caps()` treats bad checksums as a status while still extracting fields and applies hardcoded panel workarounds for delay, FAMS, FreeSync extension caps, and colorimetry issues.

MST allocation helpers sit between DRM atomic MST state and DC link allocation tables. On enable they call `drm_dp_add_payload_part1()`, mirror the VCPI/time-slot sequence into a DC allocation table, and later send `drm_dp_add_payload_part2()`. On disable they reconstruct the old payload slot count, call the DRM remove payload phases, update DC allocation state, and track connector MST progress bits used by debugfs.

AUX/DPCD and I2C helpers locate the `amdgpu_dm_connector` from `link->priv`, call DRM DP AUX or Linux I2C transfer APIs, and return DC-style booleans. DSC enablement handles SST sinks and DP-HDMI PCONs directly, while MST uses `aconnector->dsc_aux`, optional pass-through AUX, and a Synaptics non-virtual-DPCD workaround that manipulates vendor remote-control registers and resets an SDP FIFO before enabling DSC. DP compliance test-pattern handling may mutate the current stream timing color depth/pixel encoding, update DSC configuration, force memory clock state, and program the test pattern.

## State and persistence behavior
This file mostly mutates live state owned elsewhere: DRM connector display info, `dc_sink.dc_edid` and `edid_caps`, `dc_link.panel_config`, link MST allocation tables, connector MST status bits, DPCD sink registers, DSC enable bits in sinks or branch devices, DC stream timing/test-pattern fields, DMUB command state, GPU memory allocations, idle workqueue flags, and MCCS caps stored on the sink. There is no on-disk persistence.

## Dependencies and integration points
Dependencies include DRM EDID and connector helpers, ACPI video EDID, VBIOS embedded panel info, DRM DP MST topology manager, DP AUX/DPCD, Linux I2C, AMD DC link/core types, DMUB command processing, DC clock manager, DSC and MST connector structures, and MCCS/DDC-over-I2C. This file is a major adapter layer between the OS/DRM object model and AMD DC's platform-agnostic callbacks.

## Risks and edge cases
EDID retry and fallback behavior is sensitive: invalid EDID sizes, too many extensions, ACPI/VBIOS fake EDIDs, compliance checksum paths, and connector force-off all alter results. MST helpers rely on atomic state lifetime guarantees and correct reconstruction of old payload slot counts. DSC programming order differs for SST, MST virtual DPCD, pass-through ports, DP-HDMI converters, and Synaptics branches. Several TODO/stub helpers return false or do nothing, so DC callers must tolerate absent platform support. MCCS operations use retrying raw I2C messages and sink-specific checksums; slow or non-compliant monitors may fail or delay detection.

## Test signals
Strong coverage includes EDID valid/bad/no-response cases, ACPI and VBIOS EDID fallback for internal panels, panel quirk application by encoded panel ID, DP compliance EDID checksum response, MST payload add/remove with multi-stream slot ordering, DP AUX and I2C failure injection, DSC enable/disable across SST, MST virtual DPCD, pass-through, DP-HDMI PCON, and Synaptics hub paths, DP test-pattern compliance modes, DMUB AUX/config commands, idle periodic detection toggling, MCCS FreeSync VCP request/set, and adaptive-sync PCON whitelist behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.c

## Purpose
`amdgpu_dm_irq.c` implements Display Manager's IRQ indirection layer on top of the base AMDGPU IRQ framework. It lets DC subcomponents register high-context handlers that run in interrupt context and low-context handlers that run in workqueues, maps hardware interrupt vectors to DC IRQ sources, controls DC interrupt enablement, and manages HPD/HPDRX, vblank, pageflip, vline, vupdate, and DMUB outbox IRQ sources.

## Important APIs, types, and functions
- Core public APIs are `amdgpu_dm_irq_init()`, `amdgpu_dm_irq_fini()`, `amdgpu_dm_irq_register_interrupt()`, `amdgpu_dm_irq_unregister_interrupt()`, `amdgpu_dm_irq_suspend()`, `amdgpu_dm_irq_resume_early()`, and `amdgpu_dm_irq_resume_late()`.
- Base-driver integration is installed by `amdgpu_dm_set_irq_funcs()`, which assigns `amdgpu_irq_src_funcs` for CRTC, vline0, DMUB outbox, vupdate, DMUB trace, pageflip, and HPD sources.
- HPD lifecycle APIs are `amdgpu_dm_hpd_init()`, `amdgpu_dm_hpd_fini()`, and `amdgpu_dm_outbox_init()`.
- Internal dispatch helpers include `amdgpu_dm_irq_handler()`, `amdgpu_dm_irq_immediate_work()`, `amdgpu_dm_irq_schedule_work()`, `dm_irq_work_func()`, `remove_irq_handler()`, and `unregister_all_irq_handlers()`.
- Interrupt state callbacks include `amdgpu_dm_set_hpd_irq_state()`, `amdgpu_dm_set_pflip_irq_state()`, `amdgpu_dm_set_crtc_irq_state()`, `amdgpu_dm_set_vline0_irq_state()`, `amdgpu_dm_set_vupdate_irq_state()`, `amdgpu_dm_set_dmub_outbox_irq_state()`, and `amdgpu_dm_set_dmub_trace_irq_state()`.

## Control flow
Initialization creates per-DC-IRQ-source list heads for high and low handlers and initializes a spinlock. Registration validates the source and context, allocates handler data, initializes work for low-context handlers, and appends to the chosen list under the table lock. The base AMDGPU IRQ `process` hook calls `amdgpu_dm_irq_handler()`, which maps the IV entry to a DC IRQ source, acknowledges it through DC, runs all high-context handlers immediately, and queues low-context work on `system_highpri_wq`.

Low-context scheduling first tries to queue existing handler work. If all existing work items are already queued, it allocates a duplicate handler data object with `GFP_ATOMIC`, appends it to the list, initializes work, and queues it so repeated interrupts are not silently dropped behind an already-pending work item. Teardown flushes low-context work then unregisters all handlers. Suspend disables HPD and HPDRX sources and flushes HPD low-context work; resume re-enables HPDRX early and HPD late, coordinating DRM polling.

## State and persistence behavior
State is runtime-only in `adev->dm`: high and low handler-list tables indexed by `enum dc_irq_source`, a spinlock, queued `work_struct`s, and handler data containing callback/argument/DM/source. Interrupt enable state is held in hardware/DC through `dc_interrupt_set()` and in base AMDGPU IRQ reference counts through `amdgpu_irq_get()`/`amdgpu_irq_put()` for HPD sources covered by `mode_info.num_hpd`.

## Dependencies and integration points
The file depends on AMDGPU IRQ source infrastructure, DRM polling and connector iteration, AMD DC interrupt mapping/ack/set APIs, HPD source numbering, system workqueues, and DM CRTC state (`otg_inst`). It integrates with DC registration sites that call `amdgpu_dm_irq_register_interrupt()` and with base driver interrupt processing through the `amdgpu_irq_src_funcs` table.

## Risks and edge cases
Handler lifetime and duplicate low-context handler allocation are key risks: duplicate objects are appended to the same list and must be freed by unregister-all paths, while unregister by handler pointer can remove only the first matching entry. High-context handlers run under the IRQ table spinlock and must not sleep. Suspend iterates HPD ranges while repeatedly dropping and reacquiring the table lock, so list stability and flush ordering matter. `dm_irq_state()` disables idle optimizations before enabling/disabling CRTC IRQs, which can affect power behavior. HPD source counts can mismatch BIOS-reported sources, requiring fallback direct DC interrupt control.

## Test signals
Useful tests include registration/unregistration for high and low contexts, duplicate interrupt storms while work is pending, handler teardown with queued work, invalid source/context rejection, HPD and HPDRX enable/disable on init/fini/suspend/resume, base IRQ mapping for vblank/pageflip/vline/vupdate/DMUB outbox, analog connector polling setup, hotplug behavior on devices with more HPD sources than `mode_info.num_hpd`, and lockdep/IRQ context validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.h

## Purpose
`amdgpu_dm_irq.h` declares Display Manager IRQ management interfaces used by DC and the broader AMDGPU DM initialization/teardown paths.

## Important APIs, types, and functions
It declares initialization and teardown (`amdgpu_dm_irq_init()`, `amdgpu_dm_irq_fini()`), handler registration (`amdgpu_dm_irq_register_interrupt()`, `amdgpu_dm_irq_unregister_interrupt()`), base IRQ-function setup (`amdgpu_dm_set_irq_funcs()`), DMUB outbox setup (`amdgpu_dm_outbox_init()`), HPD lifecycle (`amdgpu_dm_hpd_init()`, `amdgpu_dm_hpd_fini()`), and suspend/resume hooks (`amdgpu_dm_irq_suspend()`, `amdgpu_dm_irq_resume_early()`, `amdgpu_dm_irq_resume_late()`).

## Control flow
The header has no executable logic but documents the intended order: initialize DM IRQ tables once during DM setup, register DC subcomponent handlers as display blocks come up, install AMDGPU IRQ source functions, initialize HPD/outbox interrupts, suspend/resume hardware interrupt sources around power transitions, unregister handlers as users go away, and finalize during DM destruction.

## State and persistence behavior
The header defines no state. The state implied by these APIs lives in `amdgpu_display_manager` handler tables and hardware/DC interrupt enablement.

## Dependencies and integration points
It includes `irq_types.h` for DAL/DC IRQ definitions and relies on `struct amdgpu_device`, `struct dc_interrupt_params`, and DC interrupt context enums from included driver headers. It is the call boundary between platform-neutral DC code and AMDGPU's Linux IRQ implementation.

## Risks and edge cases
Callers must preserve the documented context restriction: registration cannot happen from an interrupt handler, and unregistration must use the handler index returned by registration. Resume is split into early HPDRX and late HPD phases, so power-management call ordering matters.

## Test signals
Build coverage, probe/remove, suspend/resume, HPD hotplug, and DC handler registration tests validate this header's interface contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq_params.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq_params.h

## Purpose
`amdgpu_dm_irq_params.h` defines the per-CRTC Display Manager IRQ parameter bundle used by vblank, pageflip, VRR/FreeSync, PSR/Replay, CRC, and secure-display paths.

## Important APIs, types, and functions
The single central type is `struct dm_irq_params`. Its fields include `last_flip_vblank`, `vrr_params`, active `stream`, `active_planes`, `allow_sr_entry`, `freesync_config`, debugfs CRC source and polynomial mode fields, and optional secure-display CRC window parameters plus `crc_window_activated`.

## Control flow
The header has no control flow. Runtime code stores and reads this struct from `struct amdgpu_crtc`, including debugfs CRC controls, IRQ handlers, PSR/Replay state-management code, and FreeSync/vblank logic.

## State and persistence behavior
The struct is runtime state only. It tracks current CRTC/display interrupt-related settings, the active DC stream pointer, CRC capture configuration, and power-management flags. It is reset with CRTC/driver state and is not persisted to disk.

## Dependencies and integration points
It includes `amdgpu_dm_crc.h` for CRC source and secure-display window types. It integrates CRTC IRQ handling with DC stream state, FreeSync module configuration, debugfs pipe CRC controls, and `CONFIG_DRM_AMD_SECURE_DISPLAY` secure CRC windows.

## Risks and edge cases
The `stream` pointer must remain valid only while the owning CRTC state is valid. CRC fields are conditionally compiled, so code touching them must stay under matching config guards. Secure-display window updates are also shared with IRQ and debugfs contexts, requiring correct locking in callers.

## Test signals
Compile coverage across `CONFIG_DEBUG_FS` and `CONFIG_DRM_AMD_SECURE_DISPLAY`, pipe CRC tests, secure-display CRC window tests, VRR/vblank behavior, pageflip tracking, and PSR/Replay self-refresh entry checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.c

## Purpose
`amdgpu_dm_ism.c` implements per-CRTC idle state management for AMDGPU DM. It coordinates OS vblank/cursor activity, DC hardware idle optimizations, and panel static-screen optimizations such as PSR1 and Replay low-Hz behavior using a finite-state machine, hysteresis timers, and recent idle-duration history.

## Important APIs, types, and functions
- Public APIs are `amdgpu_dm_ism_init()`, `amdgpu_dm_ism_fini()`, `amdgpu_dm_ism_commit_event()`, `amdgpu_dm_ism_disable()`, and `amdgpu_dm_ism_enable()`.
- FSM helpers are `dm_ism_next_state()`, `dm_ism_trigger_event()`, and `dm_ism_dispatch_power_state()`.
- Delay/history helpers are `dm_ism_get_idle_allow_delay()`, `dm_ism_get_sso_delay()`, `dm_ism_insert_record()`, and `dm_ism_set_last_idle_ts()`.
- State application is performed by `dm_ism_commit_idle_optimization_state()`.
- Timer callbacks are `dm_ism_delayed_work_func()` and `dm_ism_sso_delayed_work_func()`.

## Control flow
Callers deliver events such as enter-idle request, exit-idle request, cursor-update begin/end, idle timer elapsed, and SSO timer elapsed while holding `dm->dc_lock`. `amdgpu_dm_ism_commit_event()` repeatedly advances the FSM, traces transitions, and lets dispatch return an immediate follow-up event when a delayed state should be collapsed into the next state.

When idle is requested from full-power running, the FSM enters `HYSTERESIS_WAITING`, records the idle start timestamp, computes a frame-based delay from recent short-idle history, and either schedules `delayed_work` or immediately enters optimized idle. Optimized idle may immediately progress to SSO, schedule an SSO timer, or temporarily allow DC idle optimizations before enabling panel static-screen features. Exit-idle or cursor activity cancels timers as needed, inserts a duration record, re-enables full-power/vblank behavior, and disables panel SSO.

## State and persistence behavior
State lives in `struct amdgpu_dm_ism` embedded in each `amdgpu_crtc`: configuration thresholds, current and previous FSM states, circular idle history records, next record index, last idle timestamp, and two delayed work items. The code also mutates global display state through `dc_allow_idle_optimizations()`, `dc_post_update_surfaces_to_stream()`, and `amdgpu_dm_crtc_set_panel_sr_feature()`. There is no persistent storage.

## Dependencies and integration points
The file depends on DRM vblank semantics, AMD DC stream timing, `amdgpu_crtc`, `dm_crtc_state`, DM `dc_lock`, tracepoints, delayed workqueues, and panel self-refresh controls. It integrates with IRQ/vblank management through `dm->active_vblank_irq_count` and with PSR/Replay through `amdgpu_dm_crtc_set_panel_sr_feature()`.

## Risks and edge cases
The FSM assumes callers hold `dc_lock`; missing locking can race timers, state transitions, and DC power calls. Frame-time calculations divide by `stream->timing.pix_clk_100hz`, so valid timing is required. Short-idle filtering relies on correctly initialized history records and timestamp ordering. Disable paths use `disable_delayed_work_sync()` and then commit an exit-idle event, so they must run before DC teardown. If `sso_num_frames` is less than the hysteresis filter window, the implementation intentionally skips early idle allow and waits for the SSO worker to avoid negative power impact.

## Test signals
Important tests include FSM transition coverage for all valid events, ignored invalid transitions, vblank enable/disable sequences, cursor-update begin/end during hysteresis and optimized idle, delayed idle and SSO timer firing, CRTC-disabled immediate-idle behavior, recent short-idle history causing activation delay, suspend/disable and re-enable workqueue behavior, tracepoint output, and verification that DC idle optimizations and PSR/Replay state are toggled at the expected times.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.h

## Purpose
`amdgpu_dm_ism.h` declares the AMDGPU DM idle state-management model: FSM states/events, configuration knobs, idle history records, per-CRTC ISM storage, and lifecycle/event functions.

## Important APIs, types, and functions
Key enums are `enum amdgpu_dm_ism_state` and `enum amdgpu_dm_ism_event`, combined by `STATE_EVENT()`. `struct amdgpu_dm_ism_config` defines short-idle filtering, history size, activation delay, old-history threshold, and static-screen-optimization delay in frame counts. `struct amdgpu_dm_ism_record` stores idle timestamp/duration. `struct amdgpu_dm_ism` stores config, state, history, and delayed work. Public functions are `amdgpu_dm_ism_init()`, `amdgpu_dm_ism_fini()`, `amdgpu_dm_ism_commit_event()`, `amdgpu_dm_ism_disable()`, and `amdgpu_dm_ism_enable()`.

## Control flow
The header defines the event vocabulary used by callers: idle enter/exit requests, cursor update begin/end, timer elapsed, SSO timer elapsed, and immediate internal progression. Implemented control flow lives in the C file's FSM and delayed workers.

## State and persistence behavior
The declared structures are per-CRTC runtime state. They track recent idle windows in a fixed 16-entry circular buffer and scheduled delayed work, but no state is persisted across driver teardown or reboot.

## Dependencies and integration points
It depends on Linux workqueues and forward declares `amdgpu_crtc` and `amdgpu_display_manager`. The `ism_to_amdgpu_crtc()` macro requires the ISM object to be embedded in `struct amdgpu_crtc` as `ism`, coupling this header to the CRTC layout.

## Risks and edge cases
Enum ordering and `DM_ISM_NUM_*` sentinel values are used for string tables and loop termination in the implementation, so additions need coordinated updates. Configuration values are frame counts, not milliseconds, and zero disables several filters or delays. The container macro is unsafe for standalone `struct amdgpu_dm_ism` allocations that are not embedded in an AMDGPU CRTC.

## Test signals
Build coverage with CRTC embedding, initialization/finalization, event delivery from vblank/cursor paths, delayed work enable/disable, and configuration edge cases with zero and nonzero filter values validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_ism.h -->
