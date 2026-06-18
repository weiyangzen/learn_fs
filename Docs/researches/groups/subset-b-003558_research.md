# subset-b-003558

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dsc_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dsc_helper.c

Purpose: provides common DRM helpers for VESA Display Stream Compression. It packs DSC Picture Parameter Set payloads, initializes DisplayPort PPS SDP headers, calculates DP RC buffer sizes, supplies standardized rate-control tables for DSC 1.1/1.2 operating modes, derives RC timing fields, and dumps DSC configuration for debug output.

Important APIs/types/functions: exports `drm_dsc_dp_pps_header_init`, `drm_dsc_dp_rc_buffer_size`, `drm_dsc_pps_payload_pack`, `drm_dsc_set_const_params`, `drm_dsc_set_rc_buf_thresh`, `drm_dsc_setup_rc_params`, `drm_dsc_compute_rc_parameters`, `drm_dsc_get_bpp_int`, `drm_dsc_initial_scale_value`, `drm_dsc_flatness_det_thresh`, and `drm_dsc_dump_config`. It works primarily on `struct drm_dsc_config`, `struct drm_dsc_picture_parameter_set`, `struct dp_sdp_header`, `struct drm_dsc_rc_range_parameters`, and local `rc_parameters`/`rc_parameters_data` tables.

Control flow: setup is normally staged by callers: fill base mode fields, call `drm_dsc_set_const_params`, `drm_dsc_set_rc_buf_thresh`, select a rate-control table through `drm_dsc_setup_rc_params`, compute derived RC fields with `drm_dsc_compute_rc_parameters`, and finally pack the PPS with `drm_dsc_pps_payload_pack`. The packer zeroes the 128-byte payload, lays out DSC PPS bytes in spec order, converts multi-byte fields to big endian, masks two's-complement BPG offsets into six-bit fields, and copies all RC thresholds/ranges. `drm_dsc_setup_rc_params` dispatches by `enum drm_dsc_params_type` to pre-SCR, 4:4:4, 4:2:2, or 4:2:0 tables and rejects unsupported bpp/bpc pairs. `drm_dsc_compute_rc_parameters` calculates groups-per-line, chunk size, mux padding, scale intervals, final offset, BPG offsets, HRD delay, and decoder delay, returning `-ERANGE` if final offset violates the RC model.

State and persistence: no global mutable state exists. Large static const tables encode specification/C-model defaults. All persistent effects are writes into caller-owned `drm_dsc_config` or packed PPS memory; debug dumps are transient through `struct drm_printer`.

Dependencies and integration: depends on DRM DP helper constants, DSC public headers, fixed-point formatting, endian conversion, and DRM print utilities. Callers include DisplayPort, eDP, MIPI DSI, i915, MSM DSI, and AMD DC paths that need common DSC programming data.

Risks: many inputs are assumed prevalidated by drivers. Unsupported bpp/bpc combinations return `-EINVAL`; missing `bits_per_pixel` or `bits_per_component` triggers `WARN_ON_ONCE`. Integer arithmetic is dense and mostly unsigned long, so slice dimensions, bpp units, native 4:2:0/4:2:2 half-width handling, and mux alignment are key regression points. PPS packing must preserve byte layout and endian conversions exactly, or sinks will reject the stream.

Test signals: look for KUnit or driver tests around DSC config helpers plus integration coverage from i915, MSM DSI, AMD DC, and DP/eDP modesets. Useful checks include PPS byte golden vectors, unsupported table entries, native 420/422 chunk-size paths, 6 bpp threshold overrides, `final_offset >= rc_model_size`, and debug dump stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dsc_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdcp_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdcp_helper.c

Purpose: centralizes DRM HDCP content-protection property creation, HDCP SRM firmware parsing, KSV revocation checks, and kernel-originated content protection state notifications.

Important APIs/types/functions: exports `drm_hdcp_check_ksvs_revoked`, `drm_connector_attach_content_protection_property`, and `drm_hdcp_update_content_protection`. Internal helpers parse HDCP 1.4 and HDCP 2.x SRM blobs, read big-endian 24-bit VRL lengths, count/copy revoked KSVs, and expose enum-name helpers through `DRM_ENUM_NAME_FN` for content protection and HDCP content type values.

Control flow: `drm_hdcp_check_ksvs_revoked` calls `drm_hdcp_request_srm`, which requests `display_hdcp_srm.bin` with `request_firmware_direct`. If no firmware is present, it treats the revocation list as empty. If firmware exists, `drm_hdcp_srm_update` identifies HDCP 1.4 or 2.x by the SRM ID byte and dispatches to the matching parser. HDCP 1.4 parsing walks VRL records containing a count byte followed by 5-byte KSVs and validates total parsed length; HDCP 2.x parsing derives the KSV count from the HDCP 2 count/reserved fields and copies one contiguous KSV array. The exported checker then compares each caller KSV with each revoked KSV and returns the number of matches. Property attachment lazily creates global mode_config enum properties and attaches them to the connector with default values. `drm_hdcp_update_content_protection` updates the live connector state and emits a sysfs property event.

State and persistence: SRM data is loaded per call from firmware and freed immediately. Created DRM properties persist in `dev->mode_config`. Connector state fields `content_protection` and `hdcp_content_type` persist through atomic state; update notification requires the connection mutex to be held.

Dependencies and integration: uses Linux firmware loading, allocation, DRM property/mode object helpers, sysfs connector property events, and HDCP constants from DRM display headers. Display drivers call these helpers when exposing HDCP support and when authentication transitions between desired/enabled states.

Risks: SRM parsing is security-sensitive binary parsing of firmware-provided data. Length checks must prevent malformed VRLs from causing out-of-bounds reads; HDCP 2 parsing relies on SRM length constraints before copying. A missing firmware file intentionally means no revoked KSVs, which is operationally permissive. Property updates warn if modeset locking is missing and can desynchronize userspace if drivers call them outside the documented state transitions.

Test signals: useful tests include malformed/short SRM blobs, reserved bit handling, zero KSV lists, duplicate matches, firmware-not-found behavior, property attachment with and without HDCP content type, and sysfs uevent emission after kernel-triggered content protection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdcp_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_audio_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_audio_helper.c

Purpose: adapts a DRM HDMI connector to the ALSA `hdmi-codec` platform-device interface so display drivers can expose audio callbacks, ELD data, DAI routing, stream mute, and plugged-state notifications through a common connector-owned helper.

Important APIs/types/functions: exports `drm_connector_hdmi_audio_init` and `drm_connector_hdmi_audio_plugged_notify`. It builds a static `struct hdmi_codec_ops` bridge around `struct drm_connector_hdmi_audio_funcs`, stores state in `connector->hdmi_audio`, and uses `struct hdmi_codec_pdata` to instantiate `HDMI_CODEC_DRV_NAME`.

Control flow: `drm_connector_hdmi_audio_init` validates required `prepare` and `shutdown` callbacks, stores callback and DAI-port metadata on the connector, prepares `hdmi_codec_pdata`, and registers a platform device under the supplied parent. Codec callbacks unwrap the connector from opaque `data`: startup is optional, prepare/shutdown call driver hooks, mute is optional and returns `-ENOTSUPP` when absent, ELD copies the connector ELD under `eld_mutex`, DAI ID parses OF graph endpoint and matches the configured port, and plugged callback registration stores a callback/device pair then immediately reports the last known state. `drm_connector_hdmi_audio_plugged_notify` updates `last_state` and invokes the registered callback under the HDMI audio lock.

State and persistence: persistent connector fields include callback pointers, platform device pointer, DAI port, plugged callback, callback device, last plugged state, and the ELD buffer owned by the connector. Locks protect ELD copying and plugged callback state. The helper does not unregister the codec device itself in this file, so lifecycle integration is expected from connector/device teardown paths.

Dependencies and integration: depends on `sound/hdmi-codec.h`, platform device registration, OF graph parsing, DRM connector/device structures, and connector hotplug code. `drm_bridge_connector.c` and VC4 HDMI paths use this helper to bind HDMI audio to DRM connector state.

Risks: required callback validation is minimal; driver hooks must tolerate codec timing and connector lifetime. Plugged callbacks are invoked while holding `hdmi_audio.lock`, so callback implementations must avoid lock inversions. `get_eld` silently truncates to the caller buffer length. DAI routing fails with `-ENOTSUPP` when disabled and `-EINVAL` when endpoint ports do not match.

Test signals: cover platform-device registration failures, missing required callbacks, ELD copy/truncation, OF endpoint DAI selection, plugged callback immediate replay, hotplug notify ordering, and optional mute/startup fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_audio_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_helper.c

Purpose: registers a real CEC adapter for an HDMI DRM connector and bridges CEC framework operations to driver-provided HDMI CEC callbacks.

Important APIs/types/functions: exports `drmm_connector_hdmi_cec_register`, `drm_connector_hdmi_cec_received_msg`, `drm_connector_hdmi_cec_transmit_attempt_done`, and `drm_connector_hdmi_cec_transmit_done`. It defines `struct drm_connector_hdmi_cec_data` holding a `cec_adapter` and driver `drm_connector_hdmi_cec_funcs`, plus `cec_adap_ops` and `drm_connector_cec_funcs` adapters.

Control flow: registration validates mandatory driver callbacks (`init`, `enable`, `log_addr`, `transmit`), allocates connector CEC data, allocates a CEC adapter with connector-info capability, fills connector info from DRM metadata, stores data/functions under `connector->cec.mutex`, calls the driver `init`, registers the adapter with the CEC framework, and attaches a DRM-managed cleanup action. Adapter operations fetch the connector with `cec_get_drvdata` and forward enable/log-address/transmit calls to driver hooks. HDMI connector physical-address updates call `cec_s_phys_addr` or `cec_phys_addr_invalidate`. Receive/transmit completion exports forward low-level hardware notifications back into the CEC framework.

State and persistence: `connector->cec.data` points to allocated helper data until DRM-managed cleanup unregisters the adapter, calls optional driver `uninit`, frees memory, and clears the connector pointer. The CEC adapter can outlive DRM cleanup until userspace closes descriptors, but the CEC framework short-circuits operations after unregister.

Dependencies and integration: uses Linux CEC core, DRM managed actions, connector CEC hooks, connector info helpers, and HDMI hotplug paths that update CEC physical addresses. It is for drivers with native CEC hardware rather than only a notifier.

Risks: callback lifetime and locking are central. The code holds `connector->cec.mutex` across driver `init` and adapter registration; driver callbacks must avoid reentrant CEC connector locking. Exported receive/transmit notification helpers assume registration has succeeded and `connector->cec.data` is valid. Cleanup must pair `cec_unregister_adapter` with the CEC framework lifetime rules.

Test signals: cover mandatory callback validation, allocation/register failures, cleanup action rollback, physical address set/invalidate propagation, transmit completion forwarding, userspace-open adapter lifetime after DRM unbind, and hotplug integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_notifier_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_notifier_helper.c

Purpose: registers a CEC notifier for an HDMI DRM connector when a separate CEC adapter driver consumes connector identity and physical-address changes.

Important APIs/types/functions: exports `drmm_connector_hdmi_cec_notifier_register`. Internal `drm_connector_cec_funcs` implementations forward physical address set/invalidate operations to `cec_notifier_set_phys_addr` and `cec_notifier_phys_addr_invalidate`.

Control flow: registration fills a `cec_connector_info` from the DRM connector, calls `cec_notifier_conn_register` for the supplied parent device and port name, stores the notifier pointer and connector CEC ops under `connector->cec.mutex`, and registers a DRM-managed cleanup action. Cleanup unregisters the notifier and clears `connector->cec.data`.

State and persistence: `connector->cec.data` persists as a `struct cec_notifier *` while the DRM device is alive. Physical address state is held by the media CEC notifier framework and updated by HDMI hotplug/EDID parsing through the connector CEC callbacks.

Dependencies and integration: depends on DRM connector metadata, DRM managed cleanup, Linux CEC notifier APIs, and HDMI hotplug helpers that call `drm_connector_cec_phys_addr_set` or invalidate. It complements `drm_hdmi_cec_helper.c`; drivers should use one model depending on whether they own a full CEC adapter or only publish notifier data.

Risks: registration failure returns `-ENOMEM` for a null notifier. The helper assumes no competing CEC data is already installed on the connector. Consumers must keep port names and connector info stable enough for CEC routing. Physical address callbacks assume `connector->cec.data` remains valid until managed cleanup.

Test signals: cover successful notifier registration, managed-action rollback, unregister cleanup, physical address update propagation, invalidation on disconnect, and behavior when notifier allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_cec_notifier_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_helper.c

Purpose: provides HDMI specification helper routines for HDR DRM infoframe construction, AVI infoframe colorimetry/bar/content-type fields, TMDS character-rate calculation, and HDMI audio clock regeneration N/CTS values.

Important APIs/types/functions: exports `drm_hdmi_infoframe_set_hdr_metadata`, `drm_hdmi_avi_infoframe_colorimetry`, `drm_hdmi_avi_infoframe_bars`, `drm_hdmi_avi_infoframe_content_type`, `drm_hdmi_compute_mode_clock`, and `drm_hdmi_acr_get_n_cts`. Internal data includes DRM-to-HDMI colorimetry encoding tables and a table of standard TMDS clocks with N/CTS values for 32 kHz, 44.1 kHz, and 48 kHz families.

Control flow: HDR metadata setup validates frame/state/blob/connector pointers, warns when the requested EOTF is not advertised by the sink, initializes the HDMI DRM infoframe, and copies type-1 metadata fields. AVI helpers translate DRM connector state fields directly into HDMI infoframe fields. `drm_hdmi_compute_mode_clock` starts from pixel clock in Hz, rejects non-8bpc VIC 1, normalizes YCbCr 4:2:2 to 8 bpc with a 12 bpc cap, halves the rate for YCbCr 4:2:0, doubles for double-clocked modes, and scales by `bpc / 8`. `drm_hdmi_acr_get_n_cts` rounds TMDS to kHz, finds an exact standard table entry or the "other" entry, chooses the sample-rate family in 48/44.1/32 kHz priority order, multiplies N for higher rates, and computes CTS when the table leaves it zero.

State and persistence: all state is caller-owned. Static const tables persist for lookup only. Infoframe structures are filled in memory supplied by callers and later packed/written by HDMI state helpers or drivers.

Dependencies and integration: relies on Linux HDMI infoframe helpers, DRM connector state, EDID/display info, CEA mode matching, and DRM mode flags. HDMI state helpers use TMDS and infoframe helpers during atomic checks; audio drivers use ACR helpers for hardware programming.

Risks: spec corner cases are important: VIC 1 deep color rejection, YCbCr 4:2:2 deep-color semantics, double-clock modes, 4:2:0 half-rate behavior, and sample rates divisible by multiple base families. HDR EOTF mismatch is only debug-logged, not rejected. Unsupported colorimetry indexes become "No Data".

Test signals: `drivers/gpu/drm/tests/drm_connector_test.c` covers TMDS clock calculations across RGB, YUV420, YUV422, deep color, double clock, and VIC 1 cases. Additional useful signals are N/CTS golden values, HDR infoframe validation, invalid metadata blobs, and AVI colorimetry/content type mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_state_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_state_helper.c

Purpose: implements HDMI-specific atomic connector state helpers: reset defaults, sink/mode format and bpc selection, TMDS validation, infoframe generation and writing, audio infoframe updates, hotplug EDID refresh, audio plugged notifications, and CEC physical-address maintenance.

Important APIs/types/functions: exports `__drm_atomic_helper_connector_hdmi_reset`, `drm_atomic_helper_connector_hdmi_check`, `drm_hdmi_connector_mode_valid`, `drm_atomic_helper_connector_hdmi_update_infoframes`, `drm_atomic_helper_connector_hdmi_update_audio_infoframe`, `drm_atomic_helper_connector_hdmi_clear_audio_infoframe`, `drm_atomic_helper_connector_hdmi_hotplug`, and `drm_atomic_helper_connector_hdmi_force`. It manipulates `struct drm_connector_state::hdmi`, `struct drm_connector_hdmi_infoframe`, connector HDMI callback tables, and display info parsed from EDID.

Control flow: reset seeds max bpc fields and broadcast RGB auto. Atomic check exits for disconnected/inactive connectors, computes a valid HDMI configuration by trying RGB first and YCbCr 4:2:0 fallback if allowed, updates limited/full range, generates AVI/SPD/HDR/vendor infoframes, and marks the CRTC `mode_changed` if broadcast RGB, bpc, or format changed. Format selection validates DVI restrictions, connector-supported formats, 4:2:0-only modes, EDID deep-color bits, max TMDS clock, and optional driver TMDS validation. Infoframe update locks `connector->hdmi.infoframes.lock`, packs/writes new frames or clears old frames via driver callbacks, handles the global audio infoframe separately, and only emits HDMI vendor frames when EDID indicates one is needed. Audio update/clear APIs update the connector's persistent audio frame under the same lock. Hotplug/force update EDID via a driver callback or generic read, refresh connector display info, notify HDMI audio, and set/invalidate CEC physical addresses.

State and persistence: derived HDMI state lives in atomic connector states: output bpc, output format, TMDS character rate, quantization range, and generated infoframe payloads. The audio infoframe is connector-global because ALSA updates it outside normal atomic state. EDID/display info, ELD, plugged state, and CEC physical address persist on the connector.

Dependencies and integration: integrates DRM atomic state, EDID parsing, HDMI infoframe packing, HDMI helper routines, connector HDMI callbacks, audio helper notifications, and CEC helper callbacks. Drivers typically call check from connector atomic check, update infoframes during atomic enable/commit, and hotplug/force from detect paths.

Risks: the selection policy currently only tries RGB and optional YCbCr 4:2:0, not every supported format, so YCbCr 4:2:2/4:4:4 behavior depends on future expansion. Missing write/clear callbacks return errors during update. Audio infoframe state is global and must be synchronized with atomic infoframe writes. Hotplug has TODOs for SCDC scrambler handling, so HDMI 2.0 link recovery remains driver-specific.

Test signals: the file documents KUnit execution with `./tools/testing/kunit/kunit.py run --kunitconfig=drivers/gpu/drm/tests drm_atomic_helper_connector_hdmi_*`. `drm_hdmi_state_helper_test.c` covers reset, mode valid, format/bpc selection, max TMDS rejection, infoframe success/failure, HDR bpc gating, and audio infoframe paths. `edid-decode` against debugfs infoframes is an integration compliance signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_hdmi_state_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_scdc_helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_scdc_helper.c

Purpose: implements HDMI 2.0 Status and Control Data Channel helpers over the DDC I2C adapter, covering raw SCDC read/write operations, scrambling status, scrambling enable, and high TMDS clock ratio control.

Important APIs/types/functions: exports `drm_scdc_read`, `drm_scdc_write`, `drm_scdc_get_scrambling_status`, `drm_scdc_set_scrambling`, and `drm_scdc_set_high_tmds_clock_ratio`. It uses SCDC register constants and bit definitions from `drm_scdc_helper.h` and connector DDC access through `connector->ddc`.

Control flow: `drm_scdc_read` performs a two-message I2C transaction to slave address `0x54`, first writing the offset and then reading the requested block, returning `-EPROTO` on short transfer. `drm_scdc_write` allocates a temporary buffer containing offset plus payload and sends one I2C write message. Scrambling and clock-ratio helpers read `SCDC_TMDS_CONFIG`, set or clear the relevant bit, write it back, and log connector-scoped debug errors on failure. Scrambling status reads `SCDC_SCRAMBLER_STATUS`. High TMDS ratio waits 1-2 ms after a successful write as required by the spec.

State and persistence: no kernel-side state is retained. Persistent state lives in the sink's SCDC registers and is lost on disconnect or some sink power transitions. The file documentation explicitly notes drivers may need detect/hotplug logic or empty modesets to restore SCDC state after reconnect.

Dependencies and integration: uses Linux I2C transfers, memory allocation, microsecond sleeps, DRM connector/device debug logging, and HDMI 2.0 link training paths in drivers such as VC4, i915, Tegra, Mediatek, and Synopsys DW-HDMI.

Risks: SCDC operations fail if the DDC adapter is absent, the sink is disconnected, or transfer counts are short. The read-modify-write sequence can race with external link management if drivers do not serialize HDMI enable/disable. Losing SCDC state on hotplug can leave high-rate HDMI links unsynchronized until the driver reprograms scrambling and clock ratio.

Test signals: hardware/integration tests should exercise >340 MHz HDMI 2.0 modes, scrambling enable/disable, reconnect restoration, DDC error handling, and clock-ratio timing. Unit-style tests can mock I2C transfer counts and verify `-EPROTO`/`-ENOMEM` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_scdc_helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic.c

Purpose: implements the DRM atomic modesetting core state container, object state acquisition, core validation, commit entry points, legacy set_config translation, private-object state tracking, state dumping, and debugfs state exposure.

Important APIs/types/functions: exports atomic state lifecycle helpers (`drm_atomic_state_init`, alloc/clear/free/release), commit waiting (`drm_crtc_commit_wait`), object acquisition helpers for CRTCs, planes, colorops, connectors, bridges, and private objects, affected-object expansion helpers, `drm_atomic_check_only`, `drm_atomic_commit`, `drm_atomic_nonblocking_commit`, `__drm_atomic_helper_disable_plane`, `__drm_atomic_helper_set_config`, `drm_atomic_print_new_state`, and `drm_state_dump`. It coordinates `struct drm_atomic_state`, per-object old/new state arrays, `struct drm_private_obj`, `struct drm_crtc_commit`, modeset locks, and driver atomic hooks.

Control flow: state allocation initializes arrays sized from mode_config, takes a DRM device reference, and defaults `allow_modeset` true. `drm_atomic_get_*_state` helpers lock the relevant modeset object with the acquire context, duplicate current state through object callbacks, store old/new pointers in the global state, and link duplicated state back to the atomic state. Private objects grow a dynamic array and use driver private state callbacks. `drm_atomic_check_only` runs core plane checks, CRTC checks, connector/writeback checks, driver `atomic_check`, non-modeset restrictions, and records `state->checked`. Commit wrappers optionally print state, call check, and delegate blocking/nonblocking execution to `mode_config.funcs->atomic_commit`. Legacy `__drm_atomic_helper_set_config` translates setCrtc into CRTC, primary plane, and connector state updates before commit. Dump helpers iterate live or new state and call per-object print callbacks.

State and persistence: atomic state objects hold duplicated transient state until committed or freed; successful driver commits install new object states outside this file through driver/helper commit paths. Reference counts protect async state and CRTC commit completion. `drm_atomic_state_clear` destroys duplicated states, drops connector and commit references, clears private state arrays, and resets `checked`. Private objects persist on `mode_config.privobj_list` until finalized.

Dependencies and integration: this is the core integration point for DRM atomic UAPI, drm_atomic_helper, drm_client_modeset, framebuffer helpers, bridge helpers, writeback, color management, color pipeline/colorop support, debugfs, and driver `atomic_duplicate_state`/`atomic_destroy_state`/`atomic_check`/`atomic_commit` implementations.

Risks: locking and lifetime are the main hazards. Callers must supply an acquire context, handle `-EDEADLK` by backing off and retrying, avoid adding state after `checked`, and release state references. Core checks prevent common invalid states but leave many hardware constraints to drivers. Plane coordinate overflow, invalid damage clips, writeback out-fence without framebuffer, off CRTC events, and direct active plane CRTC switching are explicitly rejected. Debug state dumping without all modeset locks is unsafe except for deliberate diagnostic use.

Test signals: KUnit coverage includes `drm_atomic_state_test.c`, `drm_bridge_test.c`, HDMI state-helper tests that call `drm_atomic_check_only`/`drm_atomic_commit`, VC4 atomic routing tests, and helper tests using `drm_kunit_helper_atomic_state_alloc`. Useful additional tests cover EDEADLK retry paths, private-object state duplication, connector array growth, colorop acquisition, writeback validation, nonblocking commit delegation, and debugfs state dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_atomic.c -->
