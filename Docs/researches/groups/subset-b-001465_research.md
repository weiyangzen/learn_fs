# subset-b-001465 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp1_transition.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp1_transition.c

Purpose: implements the HDCP 1.x transition layer for HDMI/DVI-style links and DisplayPort links. It consumes execution results in `struct mod_hdcp_transition_input_hdcp1`, examines the current HDCP state through `current_state(hdcp)`, and fills `struct mod_hdcp_output` with callback/watchdog/auth-complete requests while mutating state through helpers from `hdcp.h`.

Important APIs: `mod_hdcp_hdcp1_transition()` handles states `H1_A0_WAIT_FOR_ACTIVE_RX` through `H1_A9_READ_KSV_LIST`; `mod_hdcp_hdcp1_dp_transition()` handles `D1_*` states. Both return `enum mod_hdcp_status` and use helpers such as `callback_in_ms`, `set_watchdog_in_ms`, `set_state_id`, `set_auth_complete`, `fail_and_restart_in_ms`, and `increment_stay_counter`.

Control flow: HDMI waits for BKSV/BCAPS, exchanges KSVs, validates R0 and receiver state, then either enables encryption directly or waits for repeater readiness and validates KSV list/V'. DP first checks HDCP capability in BCAPS, waits for R0' availability with a 100 ms watchdog, retries some validation failures up to the stay-count policy, then authenticates direct receivers or validates repeater topology. MST adds stream encryption checks after link encryption.

State and persistence: this file does not persist external data but updates `hdcp->state`, `hdcp->state.stay_count`, `conn->is_repeater`, retry-related link adjustments, and auth-complete output flags. Workarounds are encoded in `conn->link.adjust.hdcp1`, including `disable`, `postpone_encryption`, and `min_auth_retries_wa`.

Dependencies and integration: depends on the HDCP execution layer to pre-populate the input fields, on PSP-backed validation/encryption helpers, and on event routing for callback/watchdog behavior. It is called by the top-level HDCP event processor after DDC/PSP work has been attempted.

Risks: timeout constants and retry decisions are interoperability-sensitive. A bad PASS/FAIL mapping can cause black screens, endless reauthentication, or accepting invalid topology. DP MST stream encryption and revocation-specific retry suppression are high-risk branches.

Test signals: exercise direct and repeater HDMI/DP, DP MST, invalid BKSV/R0/V', KSV READY timeout, CP reauth/integrity failure, device-count mismatch, and slow receiver timing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp1_transition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_execution.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_execution.c

Purpose: executes HDCP 2.2 protocol actions for the current state and records granular PASS/FAIL/PENDING inputs consumed by the transition layer. It bridges state-machine events to DDC reads/writes, PSP cryptographic preparation/validation, receiver status polling, and DP stream operations.

Important APIs: exported entry points are `mod_hdcp_hdcp2_execution()` for HDMI/DVI-style HDCP 2.2 and `mod_hdcp_hdcp2_dp_execution()` for DisplayPort. Static helpers implement each state: `send_ake_init`, `validate_ake_cert`, `read_h_prime`, `locality_check`, `exchange_ks_and_test_for_repeater`, `enable_encryption`, `verify_rx_id_list_and_send_ack`, `send_stream_management`, and `validate_stream_ready`. `process_rxstatus()` centralizes RxStatus, reauth, link-integrity, and receiver-id-list-ready handling.

Control flow: each state validates expected event types, sets `event_ctx->unexpected_event` for invalid stimuli, then calls `mod_hdcp_execute_and_set()` around lower-level operations. HDMI uses RxStatus message-size checks for AKE cert, H', pairing info, L', receiver-id list, and stream-ready availability. DP reads capability from RxCaps and uses DP-specific RxStatus bits for H', pairing, reauth, link failure, and receiver-id readiness.

State and persistence: stores received messages under `hdcp->auth.msg.hdcp2`, increments `trace->hdcp2.attempt_count`, populates `event_ctx->rx_id_list_ready`, updates `rx_id_list_size`, and records downstream device count / legacy-device flags. Locality check may sleep or use firmware atomic write-poll-read depending on link adjustment flags.

Dependencies and integration: depends on `hdcp_ddc.c` for message transport and `hdcp_psp.c` for cryptographic message generation/validation. It integrates with transition files through `struct mod_hdcp_transition_input_hdcp2`, making each state side-effect visible without embedding transition decisions here.

Risks: RxStatus parsing is protocol- and transport-specific; wrong sizes can stall authentication. `poll_l_prime_available()` sleeps in small intervals and is HDMI-only. `check_device_count()` intentionally allows one extra display for MST internal-panel behavior, so regressions can reject valid MST topologies or accept inconsistent ones.

Test signals: cover HDMI/DP capability reads, callback versus CPIRQ events, watchdog paths, stored and no-stored KM, firmware and software locality paths, repeater receiver-id list validation, stream management retry count, DP link-integrity failure, and MST stream encryption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_execution.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_transition.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_transition.c

Purpose: implements HDCP 2.2 transition decisions for HDMI/DVI and DisplayPort. It interprets the execution input structure, controls timers, retries, and fallback policy, and decides when authentication is complete.

Important APIs: `mod_hdcp_hdcp2_transition()` handles `H2_*` states; `mod_hdcp_hdcp2_dp_transition()` handles `D2_*` states. Both use `struct mod_hdcp_transition_input_hdcp2`, `struct mod_hdcp_event_context`, and `struct mod_hdcp_output`.

Control flow: both paths check receiver capability, create PSP sessions, prepare/write AKE Init, validate AKE cert, select stored or no-stored KM, validate H', run locality check, exchange KS/EKS, and either authenticate direct receivers or run repeater receiver-id-list and stream-management states. HDMI polls several messages with callbacks and watchdogs; DP has explicit content-stream-type signaling before encryption and DP link-integrity checks during authentication.

State and persistence: state is carried in `hdcp->state.id`, `stay_count`, `hdcp->auth.count.stream_management_retry_count`, `conn->is_km_stored`, `conn->is_repeater`, and link adjustment flags. The transition can disable HDCP2 capability, force no stored KM after H' validation failure, switch from firmware to software locality check, or force Type 0 on repeated DP Type 1 link-integrity failures.

Dependencies and integration: depends on `hdcp2_execution.c` to set each input field and on top-level HDCP scheduling to honor callback/watchdog requests. It is tightly coupled to HDCP 2.2 CTS timing, including 100 ms, 200 ms, 1000 ms, 2000 ms, and 3000 ms watchdogs/callbacks.

Risks: retry counters and timer durations are security and compatibility boundaries. HDMI repeater flows can be interrupted by CPIRQ receiver-id-ready events at multiple states. DP content type and MST stream-encryption failures can require fallback to Type 0, so errors can look like policy rather than transport failures.

Test signals: test invalid cert/H'/L'/M'/V', revoked receiver IDs, stored-KM fallback, firmware locality fallback, receiver-id-list timeout, stream-ready retry limit, DP CPIRQ arrival in authenticated states, direct versus repeater, and Type 1 to Type 0 fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp2_transition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_ddc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_ddc.c

Purpose: provides the HDCP DDC/AUX transport implementation for HDCP 1.x and 2.2 messages. It maps logical HDCP message IDs to HDMI I2C offsets or DP DPCD addresses, chunks DP AUX transfers to 16 bytes, and copies protocol data into `hdcp->auth.msg`.

Important APIs: exported functions include HDCP1 reads/writes (`mod_hdcp_read_bksv`, `mod_hdcp_read_bcaps`, `mod_hdcp_read_bstatus`, `mod_hdcp_read_r0p`, `mod_hdcp_read_ksvlist`, `mod_hdcp_read_vp`, `mod_hdcp_write_aksv`, `mod_hdcp_write_ainfo`, `mod_hdcp_write_an`) and HDCP2 operations (`mod_hdcp_read_hdcp2version`, `mod_hdcp_read_rxcaps`, `mod_hdcp_read_rxstatus`, `mod_hdcp_read_ake_cert`, `mod_hdcp_write_ake_init`, `mod_hdcp_write_no_stored_km`, `mod_hdcp_write_stored_km`, `mod_hdcp_write_lc_init`, `mod_hdcp_write_eks`, `mod_hdcp_read_rx_id_list`, `mod_hdcp_write_stream_manage`, `mod_hdcp_write_content_type`, `mod_hdcp_clear_cp_irq_status`, `mod_hdcp_write_poll_read_lc_fw`).

Control flow: common `read()` and `write()` validate message IDs, select DP DPCD or HDMI I2C based on `is_dp_hdcp(hdcp)`, and call function pointers in `hdcp->config.ddc.funcs`. DP HDCP2 messages skip the message ID byte for writes and synthesize it for reads. Receiver-id-list reads are special: DP reads an initial block, derives device count, and reads the remaining aligned portion.

State and persistence: mutates `hdcp->auth.msg.hdcp1`, `hdcp->auth.msg.hdcp2`, and scratch buffer `hdcp->buf`. It does not own authentication state but its byte layout directly feeds PSP validation and logging.

Dependencies and integration: depends on DDC callbacks supplied by the display manager and on HDCP bitfield macros from included headers. Atomic locality helpers use `atomic_write_poll_read_i2c` or `atomic_write_poll_read_aux`.

Risks: offset/address tables are protocol-critical. Buffer sizing, the DP receiver-id-list second-part length expression, and I2C write staging in `hdcp->buf` are sensitive to overflow and off-by-one mistakes. CP_IRQ clear chooses ESI0 for DP 1.4+ links.

Test signals: mock DDC callbacks for HDMI and DP, verify byte offsets, chunked AUX transactions, message-ID inclusion/exclusion, locality combo failures, CP_IRQ clear address selection, and error propagation on failed reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_ddc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.c

Purpose: implements HDCP diagnostic formatting for binary DDC messages, status names, and state names. It supports macros in `hdcp_log.h` and gives state-machine logs readable string values.

Important APIs: `mod_hdcp_dump_binary_message()` formats a byte array as newline-prefixed hex bytes into a caller-supplied buffer. `mod_hdcp_log_ddc_trace()` logs known HDCP1 or HDCP2 message buffers from `hdcp->auth.msg`. `mod_hdcp_status_to_str()` expands `MOD_HDCP_STATUS_LIST`; `mod_hdcp_state_id_to_str()` maps every known HDCP state ID to a string.

Control flow: binary dump calculates required buffer size and only writes when the provided buffer is large enough. DDC trace branches by `is_hdcp1()` and `is_hdcp2()` and emits read/write trace macros for all message classes. State conversion is a large switch covering uninitialized, initialized, HDCP1 HDMI/DP, and HDCP2 HDMI/DP states.

State and persistence: uses `hdcp->buf` as the text-formatting scratch area through the logging macros. It reads authentication message buffers but does not change protocol state.

Dependencies and integration: integrated by `HDCP_AUTH_COMPLETE_TRACE`, DDC trace macros, and error/state logging. It depends on state/status enum definitions being kept in sync with strings.

Risks: `sprintf` is safe only because the target-size guard accounts for fixed three-byte hex tokens, newline, and terminator. If new states are added without updating this file, logs degrade to `UNKNOWN_STATE_ID`. Full DDC dumps can expose sensitive authentication material in debug logs.

Test signals: verify formatting for exact-size and undersized buffers, status string coverage from `MOD_HDCP_STATUS_LIST`, newly added state IDs, and that HDCP1/HDCP2 traces use correct buffer lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.h

Purpose: defines the HDCP logging macro surface used by the state machine, topology updates, DDC tracing, and authentication-complete hooks.

Important APIs/types: macros include `HDCP_ERROR_TRACE`, `HDCP_HDCP1_ENABLED_TRACE`, `HDCP_HDCP2_ENABLED_TRACE`, display add/remove topology traces, state transition traces, callback event traces, `HDCP_DDC_READ_TRACE`, `HDCP_DDC_WRITE_TRACE`, and `HDCP_AUTH_COMPLETE_TRACE`.

Control flow: most macros expand to `DRM_DEBUG_KMS` or `pr_debug` calls. `HDCP_NEXT_STATE_TRACE` checks `output->watchdog_timer_needed` to include watchdog timing. `HDCP_EVENT_TRACE` logs only watchdog timeout and CPIRQ events. `HDCP_AUTH_COMPLETE_TRACE` currently dumps DDC trace and invokes a disabled `HDCP_LOG_TRA` hook.

State and persistence: no persistent state, but macros read `hdcp->config.index`, `hdcp->state`, `output`, and protocol buffers through `mod_hdcp_log_ddc_trace()`.

Dependencies and integration: depends on `mod_hdcp_status_to_str`, `mod_hdcp_state_id_to_str`, and `mod_hdcp_dump_binary_message()` implemented in `hdcp_log.c`, plus kernel DRM/pr_debug logging APIs.

Risks: macro arguments may be evaluated multiple times in future edits if not kept simple. DDC trace macros format into `hdcp->buf`, so concurrent tracing on the same object could overwrite scratch data. Debug logs may include HDCP authentication bytes.

Test signals: compile coverage with logging enabled, transition log strings for states with and without watchdogs, event logs for timeout/CPIRQ, and DDC traces on buffers near `hdcp->buf` capacity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.c

Purpose: implements the HDCP and DTM PSP firmware boundary. It adds/removes displays from secure topology, creates/destroys HDCP sessions, asks firmware to generate transmitter messages, validates receiver messages, and enables link or stream encryption.

Important APIs: topology functions are `mod_hdcp_add_display_to_topology()` and `mod_hdcp_remove_display_from_topology()` with v2/v3 fallback. HDCP1 functions cover create/destroy session, validate receiver, enable encryption, validate KSV list/V', enable DP stream encryption, and link maintenance. HDCP2 functions cover create/destroy session, prepare AKE Init, validate AKE cert/H'/L'/receiver-id-list/stream-ready, prepare LC Init/EKS/stream management, enable encryption, and DP stream encryption.

Control flow: each PSP operation obtains `psp->dtm_context.mutex` or `psp->hdcp_context.mutex`, zeros the shared memory command, fills command-specific input, invokes `psp_dtm_invoke()` or `psp_hdcp_invoke()`, then translates firmware status and output fields into `enum mod_hdcp_status` and module state. DTM v3 falls back to v2 if unsupported at runtime.

State and persistence: persists `hdcp->auth.id`, generated HDCP1/2 messages under `hdcp->auth.msg`, connection flags (`is_repeater`, `is_km_stored`, revocation flags), trace events, and per-display state transitions between active and encryption-enabled.

Dependencies and integration: depends on AMDGPU PSP context, trusted-application command structures in `hdcp_psp.h`, display helper accessors, and DDC/execution layers that send or receive the prepared messages.

Risks: shared-memory layout must exactly match firmware ABI. Mutex coverage is mandatory because one shared buffer is reused. Some remove-display success paths set display state to `ACTIVE` rather than inactive, so callers must understand topology versus display lifecycle. Stream-encryption loops partially update display state if later displays fail.

Test signals: PSP mock tests for every command status, DTM v3 fallback, uninitialized TA contexts, no active display, revocation handling, forced content type negotiation, MST stream encryption with disabled displays, and state rollback after failed topology updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.h

Purpose: declares the firmware ABI data structures, enums, command IDs, status values, and message sizes used by `hdcp_psp.c` to communicate with the PSP HDCP and DTM trusted applications.

Important APIs/types: DTM command IDs include topology update v2/v3 and ASSR enable; DTM inputs carry display handle, controller/DDC/encoder identifiers, MST VCID, ASSR, PHY, link capability, and DPIA/direct output metadata. HDCP command IDs cover HDCP1 sessions/auth/encryption, HDCP2 session/messages/encryption, destroy-all, and SRM get/set. Message ID enums define all HDCP2 AKE, LC, SKE, repeater-auth, and DP content-type messages.

Control flow role: this header has no executable control flow but defines the layout consumed by PSP shared memory. `ta_hdcp_shared_memory` and `ta_dtm_shared_memory` wrap command ID, status, and input/output unions.

State and persistence: structures carry session handles, SRM buffers, generated transmitter messages, receiver messages, authentication status, HDCP version, KM-stored flag, repeater flag, content type, and encryption protection level.

Dependencies and integration: includes PSP/amdgpu-facing declarations such as `psp_cmd_submit_buf` and expects `struct psp_context` / firmware command definitions from the AMDGPU driver. `hdcp_psp.c` treats these definitions as packed firmware contracts.

Risks: any enum renumbering, field-size change, or union change can break firmware compatibility. Buffer maxima (`TA_HDCP__HDCP2_TX_BUF_MAX_SIZE`, `TA_HDCP__HDCP2_RX_BUF_MAX_SIZE`, SRM max size) bound `memcpy` operations elsewhere. The header intentionally mirrors PSP requirements, so cleanup refactors are dangerous.

Test signals: compile-time size/layout assertions against firmware documentation, command serialization tests, HDCP2 max-message buffer tests, SRM size boundary tests, and DTM v2/v3 topology command compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_freesync.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_freesync.h

Purpose: declares the FreeSync/VRR module interface and the shared VRR parameter structures used by AMD display code.

Important APIs/types: `struct mod_freesync` is opaque. `struct mod_freesync_caps` reports support and min/max refresh in microhertz. `enum mod_vrr_state` models unsupported, disabled, inactive, active variable, and active fixed states. `struct mod_freesync_config` is the input policy surface. `struct mod_vrr_params` stores computed timing adjustment, fixed-refresh, BTR, flip-interval workaround, and info-frame state.

Control flow role: the header declares lifecycle (`mod_freesync_create`, `mod_freesync_destroy`), packet construction (`mod_freesync_build_vrr_infopacket`), parameter calculation (`mod_freesync_build_vrr_params`), preflip/vupdate handlers, nominal field-rate and vtotal calculation helpers, and `mod_freesync_get_freesync_enabled`.

State and persistence: module state is external/opaque; callers persist `mod_vrr_params` across flips and vupdates. Counters in BTR/fixed/flip-interval substructures track frame insertion, ramping, and workaround detection.

Dependencies and integration: includes `mod_shared.h` and references DC stream/plane/timing types and `dc_info_packet`. It integrates FreeSync with info-packet building, timing adjustment, and display-manager update cadence.

Risks: units are mixed but explicit (`uhz`, `us`); wrong conversions can break VRR range, BTR, or fixed refresh. The legacy `mod_freesync_caps` TODO indicates compatibility debt.

Test signals: VRR state transitions, BTR frame insertion, ramp completion, flip-interval workaround cleanup, info-packet generation for each packet type, and refresh/vtotal conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_freesync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_hdcp.h

Purpose: public HDCP module contract for AMD display code. It defines statuses, display/link/config structures, DDC/PSP callback interfaces, adjustment policy, event/output plumbing, query results, and lifecycle/process APIs.

Important APIs/types: `enum mod_hdcp_status` is generated from `MOD_HDCP_STATUS_LIST` and covers generic, topology, DDC, HDCP1, and HDCP2 failures. Core types include `mod_hdcp_display`, `mod_hdcp_link`, `mod_hdcp_config`, `mod_hdcp_output`, `mod_hdcp_trace`, `mod_hdcp_display_query`, and DDC atomic op structures. Public functions include `mod_hdcp_get_memory_size`, `mod_hdcp_setup`, `mod_hdcp_teardown`, `mod_hdcp_add_display`, `mod_hdcp_remove_display`, `mod_hdcp_update_display`, `mod_hdcp_query_display`, `mod_hdcp_reset_connection`, `mod_hdcp_process_event`, and string/signal helpers.

Control flow role: callers allocate one `mod_hdcp` per link, set up DDC/PSP callbacks, add/remove/update displays, and drive the module with callback/watchdog/CPIRQ events. The module returns timer requests through `mod_hdcp_output`.

State and persistence: display slots are bounded by `MAX_NUM_OF_DISPLAYS`. Link adjustments persist retry limits, disable flags, forced content type, stored-KM fallback, H' timeout increase, and locality-check mode. Trace state records error history and downstream counts.

Dependencies and integration: includes OS and signal types and references DC/DDC/PSP concepts without exposing internals. It is the main boundary between display manager policy and HDCP implementation files.

Risks: bitfield widths constrain policy values; exceeding display count or retry assumptions can silently truncate. Function-pointer DDC contracts must be valid for the lifetime of the HDCP object. Status list changes require logging/string updates.

Test signals: API lifecycle, display bounds, link mode conversion, callback/watchdog outputs, DDC callback failures, adjustment updates, query encryption status, and all status string conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_info_packet.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_info_packet.h

Purpose: declares helpers for building DisplayPort/HDMI secondary-data and info-frame packets used for VSC colorimetry, HDMI Forum VSIF, and Adaptive Sync signaling.

Important APIs/types: functions include `set_vsc_packet_colorimetry_data`, `mod_build_vsc_infopacket`, `mod_build_hf_vsif_infopacket`, `mod_build_adaptive_sync_infopacket`, and version-specific Adaptive Sync builders. `enum adaptive_sync_type` distinguishes none, DP, PCON whitelisted/non-whitelisted FreeSync, and eDP. `enum adaptive_sync_sdp_version`, `struct frame_duration_op`, and `struct AS_Df_params` describe Adaptive Sync SDP payload details.

Control flow role: callers supply stream timing/color state and receive a populated `dc_info_packet`. The implementation chooses the packet revision and payload based on stream/link capabilities.

State and persistence: no owned module state; packets are filled into caller-provided buffers and marked valid/invalid.

Dependencies and integration: includes `dm_services.h` and `mod_shared.h`, forward-declares DC stream/info-packet/VRR types, and is consumed by display update code and FreeSync/VRR packet generation.

Risks: packet byte positions and enum values are spec-bound. Null stream handling differs by packet type; Adaptive Sync dispatch guards some but not all fields in the implementation.

Test signals: VSC colorimetry for RGB/YCbCr/color-depth/range combinations, PSR/Replay packet revisions, HDMI 3D and HDMI VIC VSIF checksums, Adaptive Sync v1/v2 headers, and null/unsupported type behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_info_packet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_shared.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_shared.h

Purpose: provides small shared enums and structs used by multiple display modules, especially color transfer functions, VRR packet types, and 3D LUT control metadata.

Important APIs/types: `enum color_transfer_func` covers SRGB, BT709, PQ, linear, and gamma encodings. `enum vrr_packet_type` identifies VRR, FreeSync versions, and VTEM packet generation. `union lut3d_control_flags` exposes a raw 32-bit value plus bitfields for gamut, chroma, black handling, shaper, gamma, and 3D LUT usage. `struct lut3d_settings` combines flags, luminance limits, gamut-map mode, and rotation mode.

Control flow role: header-only data contract; implementation files inspect these values when building packets or programming display color behavior.

State and persistence: callers persist `lut3d_settings` and pass transfer/packet enums through module APIs. The bitfield union is a serialization-sensitive state container.

Dependencies and integration: included by FreeSync and info-packet interfaces. It avoids heavyweight DC includes, making it a common module-level contract.

Risks: bitfield ordering can be compiler/ABI sensitive if serialized externally. The `reseved` typo is part of the field name and should not be casually changed if code references it. Enum expansion must be coordinated with packet builders.

Test signals: compile coverage for all includes, raw bitfield round-trip tests where serialized, transfer-function selection in VSC packet generation, and LUT settings compatibility across modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_stats.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_stats.h

Purpose: declares an opaque statistics module interface for display events, flips, vupdates, and FreeSync metrics.

Important APIs/types: `struct mod_stats` is opaque; `struct mod_stats_caps` is currently a dummy capability structure; `struct mod_stats_init_params` carries enable and entry-count configuration. Functions include create/destroy, init, dump, reset, event update, flip/vupdate timestamp update, and FreeSync metric update.

Control flow role: display code creates the module with a DC pointer and initialization parameters, then records events over time and optionally dumps or resets collected data.

State and persistence: actual storage is implementation-owned. Inputs include event strings, timestamps in ns, vtotal min/max, event trigger flags, window bounds, LFC midpoint, inserted frame count, and inserted frame duration.

Dependencies and integration: includes `dm_services.h` for DC/service types. It is designed as a low-friction telemetry hook for display timing and FreeSync behavior.

Risks: header exposes lengths and raw string pointers, so implementation must validate input length and lifetime. Timestamp units must stay consistent. Dummy caps may hide missing feature negotiation.

Test signals: create/init/destroy lifecycle, disabled stats behavior, event length boundaries, monotonic timestamp handling, reset after updates, and FreeSync metric formatting/dump output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_vmid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_vmid.h

Purpose: declares the virtual memory ID helper module used to map page table bases to limited VMID slots for display use.

Important APIs/types: `MAX_VMID` is 16. `struct mod_vmid` is opaque. Public functions are `mod_vmid_get_for_ptb(struct mod_vmid *, uint64_t ptb)`, `mod_vmid_reset`, `mod_vmid_create`, and `mod_vmid_destroy`.

Control flow role: callers create the module with `struct dc`, number of VMIDs, and virtual-address-space config, request a VMID for a PTB, and reset/destroy when address-space state changes or the device is torn down.

State and persistence: implementation owns the mapping cache between PTB values and VMID identifiers. Reset clears that mapping.

Dependencies and integration: includes `dc.h` and references `dc_virtual_addr_space_config`, tying it to core display virtual memory setup.

Risks: VMID exhaustion, stale PTB mappings after reset-sensitive events, and incorrect `num_vmid` bounds can affect GPU memory addressing. Header does not expose error signaling beyond an 8-bit return value.

Test signals: PTB reuse returns stable VMIDs, reset clears mappings, `num_vmid` boundary behavior including `MAX_VMID`, and destroy after partial create failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/inc/mod_vmid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/Makefile

Purpose: adds the info-packet module object to the AMD display build.

Important APIs/build variables: defines `INFO_PACKET = info_packet.o`, builds `AMD_DAL_INFO_PACKET` by prefixing `$(AMDDALPATH)/modules/info_packet/`, and appends it to `AMD_DISPLAY_FILES`.

Control flow: no runtime control flow. At build time, the display make hierarchy includes this fragment so `info_packet.c` is compiled and linked into the AMD display module.

State and persistence: no runtime state. The file participates in persistent build configuration through `AMD_DISPLAY_FILES`.

Dependencies and integration: depends on the parent make environment defining `AMDDALPATH` and `AMD_DISPLAY_FILES`. The object provides implementations declared in `modules/inc/mod_info_packet.h`.

Risks: path prefix errors or missing inclusion from parent makefiles would silently omit packet builders. Adding new source files in this directory requires updating this list.

Test signals: kernel/display build includes `modules/info_packet/info_packet.o`; clean builds and incremental builds after editing `info_packet.c`; parent makefile variable expansion for `AMDDALPATH`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/info_packet.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/info_packet.c

Purpose: builds DisplayPort VSC SDPs, HDMI vendor-specific infoframes, and Adaptive Sync SDPs from stream/link/timing/color inputs.

Important APIs: `set_vsc_packet_colorimetry_data()` encodes DP colorimetry, pixel encoding, color depth, range, and content type into VSC payload bytes. `mod_build_vsc_infopacket()` chooses VSC revisions for 3D stereo, PSR, Panel Replay, and colorimetry. `mod_build_hf_vsif_infopacket()` builds HDMI VSIF for 3D and HDMI VIC modes with checksum. `mod_build_adaptive_sync_infopacket()` dispatches to v1/v2 builders.

Control flow: VSC revision starts undefined, then is promoted by stereo, PSR, Replay, colorimetry, and Panel Replay priority. Revision-specific blocks set packet headers/payload length and validity. Adaptive Sync clears the packet, selects DP/eDP/PCON behavior, and writes v1 or v2 SDP headers. VSIF returns early unless 3D or HDMI VIC mode is required.

State and persistence: no owned state; all output is written into caller-provided `struct dc_info_packet`. The code sets `valid` only for generated packets.

Dependencies and integration: depends on DC stream/link/timing structures, color-space and pixel-encoding enums, Replay/PSR settings, and `mod_shared.h` transfer-function definitions. FreeSync and display update paths consume these packets.

Risks: packet byte offsets are spec-bound. `mod_build_vsc_infopacket()` does not fully clear payload for all revisions, so callers should provide clean packet storage. `mod_build_adaptive_sync_infopacket()` sets `valid = false` before `memset`, which is harmless but redundant. Checksum and length errors can cause sinks to ignore HDMI VSIF.

Test signals: VSC revision selection matrix for PSR1, PSR-SU, Replay, Panel Replay, colorimetry, and 3D; DP colorimetry for RGB/YCbCr/BT2020/gamma fallback; VSIF checksum for all 3D formats and HDMI VIC; Adaptive Sync v1/v2 payload bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/info_packet/info_packet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/Makefile

Purpose: adds the power-helper module object to the AMD display build.

Important APIs/build variables: defines `MOD_POWER = power_helpers.o`, builds `AMD_DAL_MOD_POWER` with the `$(AMDDALPATH)/modules/power/` prefix, and appends it to `AMD_DISPLAY_FILES`.

Control flow: build-only fragment; it ensures `power_helpers.c` is compiled into the display driver when the parent make hierarchy includes this module.

State and persistence: no runtime state. Persistent effect is the build object list contribution.

Dependencies and integration: relies on parent make variables and provides the implementation for declarations in `modules/power/power_helpers.h`.

Risks: new power module sources require manual list updates. Incorrect `AMDDALPATH` or missing inclusion will omit ABM/PSR/Replay helper implementations.

Test signals: full AMD display build includes `modules/power/power_helpers.o`, incremental rebuild after helper edits, and parent makefile expansion validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.c

Purpose: implements ABM/DMCU/DMUB backlight configuration helpers, PSR/Replay configuration helpers, eDP panel capability workarounds, DSC slice-height checks, and custom backlight capability export.

Important APIs: exported functions include `dmub_init_abm_config`, `dmcu_load_iram`, `is_psr_su_specific_panel`, `mod_power_calc_psr_configs`, `init_replay_config`, `mod_power_only_edp`, `psr_su_set_dsc_slice_height`, Replay coasting/frame-skip setters, `calculate_replay_link_off_frame_count`, `fill_custom_backlight_caps`, and `reset_replay_dsync_error_count`.

Control flow: ABM paths build 256-byte IRAM/config tables from fixed reduction tables, aggressiveness sets, gamma curves, and caller backlight LUTs. Version-specific fillers handle ABM 2.0, 2.2, and 2.3/2.4 layouts and endian selection. DMUB config copies packed table fields into a 32-bit-aligned config struct before calling ABM functions. PSR config computes vblank and line time from stream timing, converts DPCD setup time into microseconds, and decides frame-capture indication and SDP deadline.

State and persistence: mutates `link->psr_settings`, `link->replay_settings`, `psr_config`, ABM firmware/config buffers, and caller-provided ACPI backlight caps. Static tables encode persistent policy curves and panel workarounds.

Dependencies and integration: depends on DMCU/ABM hardware function tables, `resource_pool`, DC stream/link/core types, DPCD caps, Replay and PSR config structures, and ACPI backlight caps.

Risks: IRAM layouts are fixed-size firmware contracts; endian mistakes or reserve-area writes can break firmware behavior. Backlight LUT size is assumed valid and indexed without explicit zero-size guards. Timing arithmetic divides by pixel clock-derived values. Panel-specific PSR-SU workarounds are fragile and sink-ID dependent.

Test signals: ABM config for all versions/sets/endian modes, LUT boundary sizes and monotonic curves, DMCU uninitialized behavior, PSR timing deadline arithmetic, eDP DSC slice granularity, Replay frame-skip divide-by-zero guards, panel workaround IDs, and custom backlight caps size calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.h

Purpose: declares power-related helper interfaces for ABM firmware configuration, PSR/Replay calculations, eDP-only checks, DSC/PSR-SU validation, and custom backlight capability reporting.

Important APIs/types: `enum abm_defines` defines four ABM levels and four config sets. `struct dmcu_iram_parameters` carries caller backlight LUT, ramping override, min backlight, and ABM set. Public functions mirror the implementation in `power_helpers.c`, including `dmcu_load_iram`, `dmub_init_abm_config`, Replay coasting/frame-skip helpers, PSR config helpers, `fill_custom_backlight_caps`, and mode-conversion declarations `change_replay_to_psr` / `change_psr_to_replay`.

Control flow role: this header is the contract used by DC/link management code to invoke firmware-table generation and PSR/Replay helper logic.

State and persistence: callers pass mutable `dc_link`, `psr_config`, `replay_config`, and backlight caps structures that the implementation updates in place.

Dependencies and integration: includes DMCU, ABM, and core DC type headers. It forward-declares `struct resource_pool` to avoid broader inclusion in consumers.

Risks: `dmcu_iram_parameters` has raw pointer plus size with no static enforcement; callers must guarantee the LUT remains valid and non-empty. Function declarations for `change_replay_to_psr` and `change_psr_to_replay` require matching definitions elsewhere.

Test signals: compile consumers against this header, validate null/resource-pool behavior in implementation, LUT parameter validation, Replay table updates, PSR config updates, and link mode conversion symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/power/power_helpers.h -->
