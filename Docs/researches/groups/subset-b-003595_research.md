# subset-b-003595 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.c

## Purpose

`intel_hdcp.c` is the generic i915 display HDCP coordinator. It owns the connector-facing content protection property flow, HDCP 1.4 authentication, HDCP 2.2 authentication, link checking, DP MST stream accounting, firmware/GSC/MEI arbitration, debugfs reporting, and connector cleanup. Bus-specific operations are deliberately abstracted through `struct intel_hdcp_shim`, so the same core state machine can drive HDMI DDC, DP AUX, SST, and MST transports.

## Important APIs, Types, And Functions

The exported entry points are `intel_hdcp_init()`, `intel_hdcp_enable()`, `intel_hdcp_disable()`, `intel_hdcp_update_pipe()`, `intel_hdcp_atomic_check()`, `intel_hdcp_cancel_works()`, `intel_hdcp_cleanup()`, `intel_hdcp_handle_cp_irq()`, `intel_hdcp_component_init()`, `intel_hdcp_component_fini()`, `is_hdcp_supported()`, `intel_hdcp_info()`, and `intel_hdcp_connector_debugfs_add()`. These are called by connector initialization, atomic commit paths, IRQ handlers, driver/component init/fini, and debugfs setup.

The core state is split between `connector->hdcp` and `dig_port->hdcp`. Connector state includes `value`, `content_type`, `force_hdcp14`, `hdcp_encrypted`, `hdcp2_encrypted`, `hdcp2_supported`, `is_repeater`, pairing state, sequence counters, `cpu_transcoder`, `stream_transcoder`, the delayed link-check work, property work, and CP IRQ waitqueue/counter. Port state tracks shared MST data such as `port_data`, `auth_status`, `num_streams`, stream descriptors, and `mst_type1_capable`.

HDCP 1.4 is built from `intel_hdcp1_enable()`, `intel_hdcp_auth()`, `intel_hdcp_auth_downstream()`, `intel_hdcp_validate_v_prime()`, `_intel_hdcp_disable()`, and `intel_hdcp_check_link()`. HDCP 2.2 is built from the wrapper calls into `display->hdcp.arbiter->ops`, then the protocol stages `hdcp2_authentication_key_exchange()`, `hdcp2_locality_check()`, `hdcp2_session_key_exchange()`, `hdcp2_authenticate_repeater_topology()`, `hdcp2_propagate_stream_management_info()`, `hdcp2_authenticate_and_encrypt()`, `_intel_hdcp2_enable()`, `_intel_hdcp2_disable()`, and `intel_hdcp2_check_link()`.

## Control Flow

Initialization starts with `intel_hdcp_component_init()`, which registers either the MEI component or a GSC-backed arbiter on display version 14 and newer. `intel_hdcp_init()` initializes per-connector HDCP state, allocates HDCP 2.2 stream data if the platform supports it, attaches the DRM content protection property, stores the transport shim, initializes mutexes, work items, and the CP IRQ waitqueue.

Enable requests come from atomic commit through `intel_hdcp_enable()` or `intel_hdcp_update_pipe()`. `_intel_hdcp_enable()` locks the connector HDCP mutex and the shared port HDCP mutex, records the requested content type and transcoder mapping, then prefers HDCP 2.2 when not forced to 1.4 and both platform and sink capability checks pass. HDCP 2.2 performs AKE, locality, session-key exchange, optional repeater topology validation, stream management, firmware port authentication, then hardware encryption enable. If HDCP 2.2 fails and the requested content is not Type 1, the code falls back to HDCP 1.4.

HDCP 1.4 loads hardware keys, captures An, sends An/Aksv through the shim, validates BKSV and revocation status, configures repeater bits, enables signalling and hardware auth/encryption, verifies R0/Ri, enables MST stream encryption if needed, and validates downstream repeater topology through SHA-1 V prime comparison. Failures trigger cleanup and limited retries.

After a successful enable, the file schedules `check_work`. The delayed worker prefers `intel_hdcp2_check_link()` unless HDCP 1.4 is forced, otherwise calls `intel_hdcp_check_link()`. A protected link reschedules the worker at the protocol-specific period. A topology change on HDCP 2.2 runs repeater topology authentication. Link failure disables the current encryption path, sets the DRM content protection value back to `DESIRED`, and lets userspace or later commits retry.

Disable paths set the internal value to `UNDESIRED`, disable stream encryption first for MST, then disable link encryption/signalling and close firmware sessions when needed. `intel_hdcp_cleanup()` cancels outstanding work and clears the shim only after connector unregistration.

## State And Persistence Behavior

The file persists no data to disk, but it maintains long-lived in-kernel state across commits and workqueue runs. `hdcp->value` mirrors the desired DRM property state and is updated asynchronously to userspace via `prop_work`. `dig_port->hdcp.num_streams` prevents shared MST link encryption from being torn down while other streams still need protection. HDCP 2.2 pairing information is delegated to firmware through the arbiter interface rather than stored in this file. `seq_num_v` and `seq_num_m` protect repeater topology and stream-management ordering, and rollover forces reauthentication. `force_hdcp14` is runtime debugfs state that changes protocol selection.

Locking is central: connector HDCP state is protected by `hdcp->mutex`, shared port/MST state by `dig_port->hdcp.mutex`, and firmware arbiter presence by `display->hdcp.hdcp_mutex`. Work items also hold connector references around asynchronous property updates.

## Dependencies And Integration Points

The file depends on DRM HDCP helpers for KSV validation/revocation and content protection property updates, i915 display register access through `intel_de_*`, runtime power helpers, pcode key loading, DP MST payload state, platform stepping helpers, the HDCP register definitions, the transport shim, and the GSC/MEI HDCP arbiter interface from `drm/intel/i915_hdcp_interface.h`.

It integrates with HDMI through `intel_hdmi.c`'s shim, with DP through corresponding DP shims outside this subset, with atomic modeset through `intel_hdcp_atomic_check()` and enable/update hooks, with CP IRQ handling through `intel_hdcp_handle_cp_irq()`, with debugfs through capability and force-HDCP-1.4 files, and with display version 14+ GSC firmware through `intel_hdcp_gsc_message.c`.

## Risks And Edge Cases

The highest-risk areas are authentication timing, shared MST state, and failure recovery. HDCP 1.4 has several spec-driven retry loops and carefully ordered register writes; regressions can cause false authentication failures or leave signalling enabled. HDCP 2.2 depends on external firmware availability and correct `hdcp_port_data`; missing arbiter state or stale GSC/MEI status blocks capability. MST uses a single link policy for all active streams, so Type 1 content can be downgraded or rejected when any downstream sink is not Type 1 capable. The property worker intentionally avoids updating userspace when the state is already `UNDESIRED`; incorrect value transitions can leave userspace seeing stale content protection state.

Other hazards include key-load power-well requirements, platform-specific line rekey workarounds, DP dock resume retry behavior, topology sequence rollover, revocation checks, and cleanup races during connector unregister. The code uses warnings and reference counting to reduce these risks, but authentication changes should be tested on both repeater and non-repeater topologies.

## Test Signals

Useful test signals include successful attach of the DRM content protection property, HDCP 1.4 and HDCP 2.2 enable/disable cycles, fallback from HDCP 2.2 to 1.4 for Type 0 content, rejection of Type 1 when only HDCP 1.4 is available, CP IRQ-triggered rechecks, repeater topology changes, MST multi-stream enable/disable accounting, suspend/resume with DP docks, GSC/MEI component bind/unbind, debugfs capability output, and `i915_force_hdcp14` behavior. Kernel logs should be checked for timeout messages around An/Ri/SHA-1/encryption status and for firmware command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.h

## Purpose

`intel_hdcp.h` is the public display-local HDCP interface used by HDMI, DP, atomic modeset, IRQ, debugfs, and driver lifecycle code. It hides the implementation in `intel_hdcp.c` behind a small set of initialization, state transition, cleanup, and reporting functions.

## Important APIs, Types, And Functions

The header forward declares DRM and i915 display types rather than including large internal headers. Its key constant is `HDCP_ENCRYPT_STATUS_CHANGE_TIMEOUT_MS`, shared by encryption enable/disable wait paths. The API surface includes `intel_hdcp_init()`, `intel_hdcp_enable()`, `intel_hdcp_disable()`, `intel_hdcp_update_pipe()`, `intel_hdcp_atomic_check()`, `intel_hdcp_cancel_works()`, `intel_hdcp_cleanup()`, `intel_hdcp_handle_cp_irq()`, `is_hdcp_supported()`, `intel_hdcp_component_init()`, `intel_hdcp_component_fini()`, `intel_hdcp_info()`, and `intel_hdcp_connector_debugfs_add()`.

## Control Flow

Connector setup calls `intel_hdcp_init()` after selecting a bus-specific shim. Atomic check and commit paths call `intel_hdcp_atomic_check()`, `intel_hdcp_enable()`, and `intel_hdcp_update_pipe()` to convert DRM content protection property changes into protocol enable/disable work. Hotplug/teardown paths call cancel and cleanup helpers. Driver/component setup calls the component init/fini functions to prepare firmware-backed HDCP 2.2 services. DP CP IRQ handling calls `intel_hdcp_handle_cp_irq()`.

## State And Persistence Behavior

The header itself stores no state. It defines the contract for functions that mutate `struct intel_connector`, `struct intel_digital_port`, and `struct intel_display` HDCP fields. Callers must respect connector and display lifecycle ordering: initialize before exposing HDCP properties, cancel work before teardown, and do not use the API after cleanup has cleared the shim.

## Dependencies And Integration Points

The header integrates with DRM connector state, i915 atomic state, encoder/CRTC state, the shim abstraction, debugfs `seq_file`, and display port identifiers. It is included by `intel_hdcp.c`, HDMI/DP connector code, and other display lifecycle files.

## Risks And Edge Cases

Because this is a narrow declaration header, risks come from API misuse: calling enable without an initialized shim, failing to cancel delayed work before connector destruction, or exposing HDCP support on unsupported ports. Signature changes here affect multiple display subsystems.

## Test Signals

Build coverage is the primary signal for this header. Runtime signals are successful connector initialization with content protection properties, clean unload without pending work warnings, and correct CP IRQ handling for DP/HDMI paths that include this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.c

## Purpose

`intel_hdcp_gsc_message.c` implements the HDCP 2.2 firmware arbiter for platforms that use the Graphics Security Controller instead of the legacy MEI HDCP component. It translates the generic `i915_hdcp_ops` callbacks used by `intel_hdcp.c` into wired GSC command messages, sends them through `intel_parent_hdcp_gsc_msg_send()`, validates firmware status, and copies firmware outputs back into DRM HDCP protocol message structs.

## Important APIs, Types, And Functions

The exported lifecycle functions are `intel_hdcp_gsc_init()` and `intel_hdcp_gsc_fini()`. Initialization allocates an `i915_hdcp_arbiter`, obtains an `intel_hdcp_gsc_context`, assigns `gsc_hdcp_ops`, and stores both on `display->hdcp`. Fini frees the context and arbiter and clears display pointers.

The static callback set `gsc_hdcp_ops` implements every operation needed by the HDCP 2.2 core: initiating sessions, verifying receiver certificates, verifying H prime and L prime, storing pairing info, initiating locality checks, getting session keys, verifying repeater topology, verifying stream management M prime, enabling authentication, and closing sessions. Each function uses command structs from `i915_hdcp_interface.h`, fills the common command header with `HDCP_API_VERSION`, command id, success status, and command-specific buffer length, then sends the request.

## Control Flow

`intel_hdcp_component_init()` in the HDCP core calls `intel_hdcp_gsc_init()` on display version 14 and newer. Once initialized, the generic HDCP 2.2 authentication flow calls `display->hdcp.arbiter->ops`. For each stage, this file validates input pointers, derives `struct intel_display` from the provided device, reads the stored GSC context, populates port fields from `hdcp_port_data`, sends the GSC command, checks transport return value and firmware status, and maps output data into the next HDCP protocol message.

The AKE flow starts with `intel_hdcp_gsc_initiate_session()`, which returns AKE_INIT data. `intel_hdcp_gsc_verify_receiver_cert_prepare_km()` consumes the receiver certificate and returns either stored-Km or no-stored-Km message data plus the actual message size. Locality and session-key callbacks produce LC_INIT and SKE_SEND_EKS data. Repeater callbacks verify receiver ID lists and stream-ready M prime. `intel_hdcp_gsc_enable_authentication()` asks firmware to enable authenticated port state, while `intel_hdcp_gsc_close_session()` closes firmware session state.

## State And Persistence Behavior

The file stores only display-lifetime pointers: `display->hdcp.gsc_context` and `display->hdcp.arbiter`. Per-authentication state lives in firmware and in the caller's `hdcp_port_data`. Pairing material is handed to firmware with `intel_hdcp_gsc_store_pairing_info()` rather than persisted by the driver. Variable-sized stream-management verification allocates a request sized by `data->k` and frees it immediately after sending.

## Dependencies And Integration Points

The file depends on `drm/intel/i915_hdcp_interface.h` for command and protocol structs, `intel_parent_hdcp_gsc_context_alloc/free()` and `intel_parent_hdcp_gsc_msg_send()` for transport, and `intel_display_types.h` for display HDCP storage. It plugs into `intel_hdcp.c` through the generic `i915_hdcp_arbiter` interface, allowing the same authentication core to use either GSC or MEI.

## Risks And Edge Cases

The main risks are ABI mismatch with firmware command layouts, incorrect buffer lengths, missing or stale GSC contexts, and incomplete error propagation. Each command treats non-success firmware status as `-EIO`, which is useful but collapses detailed firmware reasons unless logs are inspected. `intel_hdcp_gsc_verify_mprime()` must size the flexible request correctly with `struct_size()` and `array_size()` because `data->k` comes from active stream management. Fini assumes no concurrent authentication users; lifecycle ordering must ensure HDCP work is stopped before context free.

## Test Signals

Strong signals include successful HDCP 2.2 authentication on GSC platforms, command failure logs with command IDs on injected firmware errors, clean init/fini across driver unload, repeater and MST stream-management authentication, Type 0/Type 1 content negotiation, and suspend/resume with GSC reinitialization. Memory instrumentation should cover the variable-size M prime request path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.h

## Purpose

`intel_hdcp_gsc_message.h` exposes the minimal GSC-backed HDCP lifecycle API to the generic HDCP core. It keeps the command translation implementation private to `intel_hdcp_gsc_message.c`.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display` and declares `intel_hdcp_gsc_init(struct intel_display *display)` plus `intel_hdcp_gsc_fini(struct intel_display *display)`. No command structs or GSC internals are exposed here.

## Control Flow

`intel_hdcp_component_init()` calls `intel_hdcp_gsc_init()` when the platform routes HDCP 2.2 through GSC. `intel_hdcp_component_fini()` calls `intel_hdcp_gsc_fini()` on teardown. All authentication-stage calls then go through the `i915_hdcp_arbiter` installed by init rather than through this header.

## State And Persistence Behavior

The header stores no state. The implementation behind it allocates and frees display-level GSC HDCP context and arbiter pointers.

## Dependencies And Integration Points

This header integrates the GSC message implementation with `intel_hdcp.c` while avoiding broader dependency exposure. It depends only on a forward-declared display object.

## Risks And Edge Cases

API misuse risk is lifecycle ordering: fini must not run while HDCP authentication work can still dereference the arbiter or GSC context. Any signature change affects the generic component init/fini path.

## Test Signals

Build coverage plus runtime init/fini on GSC-capable platforms are the main signals. Successful HDCP 2.2 capability checks after init and clean unload after fini validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_regs.h

## Purpose

`intel_hdcp_regs.h` centralizes HDCP-related i915 display MMIO register definitions and bit fields. It supports both older port-addressed HDCP registers and display version 12+ transcoder-addressed registers through selection macros.

## Important APIs, Types, And Functions

The header defines no functions. Its important macro groups are HDCP key registers (`HDCP_KEY_CONF`, `HDCP_KEY_STATUS`, Aksv registers and key/fuse bits), repeater SHA-1 registers (`HDCP_REP_CTL`, `HDCP_SHA_V_PRIME()`, `HDCP_SHA_TEXT`, repeater-present and SHA state bits), HDCP 1.4 auth registers (`HDCP_CONF()`, `HDCP_ANINIT()`, `HDCP_ANLO/HI()`, `HDCP_BKSVLO/HI()`, `HDCP_RPRIME()`, `HDCP_STATUS()`), and HDCP 2.2 registers (`HDCP2_AUTH()`, `HDCP2_CTL()`, `HDCP2_STATUS()`, `HDCP2_STREAM_STATUS()`, `HDCP2_AUTH_STREAM()`).

`TRANS_HDCP(display)` selects transcoder-based register addressing for display version 12 and newer; otherwise macros pick per-port register bases. Status bits such as `HDCP_STATUS_ENC`, `HDCP_STATUS_RI_MATCH`, `LINK_AUTH_STATUS`, and `LINK_ENCRYPTION_STATUS` are consumed directly by enable, disable, and link-check paths.

## Control Flow

The register macros are used by `intel_hdcp.c` to load/clear keys, capture An, program BKSV/Ri, drive repeater SHA-1 validation, enable/disable encryption, and poll hardware status. They are also used by HDMI HDCP link checks to write Ri prime and test hardware match status. The macros themselves are pure compile-time address and bit definitions.

## State And Persistence Behavior

State represented here is hardware state, not software persistence. Register bits reflect key-load completion, fuse status, active encryption, authentication status, stream encryption, and SHA engine progress. These values persist in display hardware until changed by driver writes, hardware reset, or power transitions.

## Dependencies And Integration Points

The header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_TRANS`, `_MMIO_PORT`, `_PICK`, and bit helpers. It is tightly coupled to `intel_hdcp.c`, `intel_hdmi.c`, and DDI/DP code that manipulates HDCP signalling and stream state.

## Risks And Edge Cases

Incorrect register selection across port/transcoder generations is the core risk. A wrong base address or bit mask can break authentication, leave encryption enabled, or misreport link status. The comment on `HDCP_DDIE_SHA1_M0` notes a possible bspec inconsistency, which makes repeater validation for that port sensitive. Register definitions must be kept in sync with platform display version behavior.

## Test Signals

Signals include successful HDCP 1.4 and 2.2 enable/disable on pre-Gen12 and Gen12+ platforms, repeater SHA-1 validation, status polling without timeout, correct stream encryption status for MST, and no register access warnings on unsupported transcoders or ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_shim.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_shim.h

## Purpose

`intel_hdcp_shim.h` defines the transport abstraction between generic HDCP logic and bus-specific receiver access. HDMI uses DDC register offsets and message mailboxes; DP uses AUX and different register naming/semantics. The shim lets `intel_hdcp.c` run the same HDCP 1.4 and HDCP 2.2 state machines over both.

## Important APIs, Types, And Functions

`enum check_link_response` defines link-check outcomes: protected, topology change, integrity failure, and reauth request. `struct intel_hdcp_shim` is the central type. HDCP 1.4 callbacks cover An/Aksv write, BKSV/BSTATUS/repeater/Ri/KSV FIFO/V prime reads, signalling enable, MST stream encryption, link checks, optional sink capability, and protocol identity.

HDCP 2.2 callbacks cover sink capability, message write/read, DP stream type configuration, MST stream encryption, link integrity checks, and optional remote HDCP capability for MST hubs. The `protocol` field maps the bus to `enum hdcp_wired_protocol` for firmware.

## Control Flow

Connector initialization passes a concrete shim to `intel_hdcp_init()`. The HDCP core stores it in `connector->hdcp.shim` and calls only through this table during authentication and link checks. HDMI populates the table in `intel_hdmi.c`; DP code provides its own implementation outside this subset.

## State And Persistence Behavior

The shim itself is static function-pointer configuration. Runtime state lives in the connector, digital port, sink, hardware registers, and firmware. Optional callbacks are checked by the core before use, allowing HDMI and DP to differ in capability detection, stream encryption, and stream-type configuration.

## Dependencies And Integration Points

The header depends on Linux integer types and `drm/intel/i915_hdcp_interface.h` for the wired protocol enum. It forward declares Intel display connector and port types and is included by both the generic HDCP core and transport implementations.

## Risks And Edge Cases

The primary risk is an incomplete or semantically mismatched shim. For example, a transport that reports capability but cannot reliably read/write protocol messages will fail mid-authentication. Optional callbacks must be genuinely optional in the core. MST-specific stream callbacks also require shared port accounting to avoid disabling encryption for other streams.

## Test Signals

Test each concrete shim with HDCP 1.4, HDCP 2.2, repeater topologies, link checks, capability queries, and disable paths. Compile-time coverage catches signature drift; runtime coverage catches offset, timing, and transport-specific behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_shim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.c

## Purpose

`intel_hdmi.c` implements i915 HDMI connector support. It covers HDMI mode validation and atomic configuration, TMDS clock and bits-per-component selection, RGB/YCbCr output format decisions, SCDC scrambling, infoframe packing/programming across platform register generations, EDID/DDC/dual-mode adapter detection, connector registration, CEC notifier setup, HDMI DSC helper calculations, and the HDMI implementation of the HDCP shim used by `intel_hdcp.c`.

## Important APIs, Types, And Functions

Externally used functions include `intel_hdmi_init_connector()`, `intel_hdmi_compute_has_hdmi_sink()`, `intel_hdmi_compute_config()`, `intel_hdmi_encoder_shutdown()`, `intel_hdmi_handle_sink_scrambling()`, `intel_dp_dual_mode_set_tmds_output()`, `intel_infoframe_init()`, `intel_hdmi_infoframes_enabled()`, `intel_hdmi_infoframe_enable()`, `intel_hdmi_read_gcp_infoframe()`, `intel_hdmi_fastset_infoframes()`, `intel_read_infoframe()`, `hsw_write_infoframe()`, `hsw_read_infoframe()`, `intel_hdmi_limited_color_range()`, `intel_hdmi_bpc_possible()`, `intel_hdmi_tmds_clock()`, `intel_hdmi_dsc_get_bpp()`, `intel_hdmi_dsc_get_num_slices()`, `intel_hdmi_dsc_get_slice_height()`, and `intel_hdmi_is_frl()`.

Important internal groups include platform-specific DIP/infoframe functions for G4X, IBX, CPT, VLV/CHV, HSW+ DDI, and LSPCON; HDMI HDCP DDC helpers; mode validation helpers for TMDS limits and color depth; connector funcs/helper funcs; and platform-specific DDC pin mapping.

## Control Flow

Connector setup runs through `intel_hdmi_init_connector()`. It validates port/lane suitability, selects a DDC pin from VBT or platform defaults, initializes the DRM connector with DDC, attaches helper funcs and HDMI properties, attaches the encoder, initializes HDCP when the port supports it, and registers a CEC notifier. `intel_infoframe_init()` separately installs the correct infoframe function pointers on the digital port based on platform generation and LSPCON presence.

Detection uses `intel_hdmi_detect()`: it checks display access, obtains GMBUS power, optionally checks digital port connection on newer platforms, clears old EDID/dual-mode state, reads EDID over DDC with a bit-banging fallback, updates connector display info, detects DP dual-mode adapters, updates CEC physical address, and returns connected only for digital EDID. Forced detection refreshes EDID only when the connector is already connected.

Atomic mode setup enters `intel_hdmi_compute_config()`. The function rejects dblescan and disallowed interlace, sets default RGB output, determines HDMI sink/infoframe/audio state, computes pipe bpp, chooses output format and TMDS clock while first respecting downstream limits and then allowing forced out-of-spec user modes at 8 bpc, handles YCbCr 4:2:0 pfit, computes limited RGB range, aspect ratio, lane count, HDMI 2.0 scrambling/high TMDS ratio, VRR, GCP, AVI, SPD, vendor, and HDR DRM infoframes.

Infoframe programming is split by hardware generation. The common pack path inserts the hardware-specific DIP data hole, then calls the selected `write_infoframe` callback. Set functions assert the HDMI port/transcoder is disabled, clear enable bits, program GCP where available, and write enabled infoframes. `intel_hdmi_fastset_infoframes()` updates HDR DRM infoframes during fastset without full mode programming.

HDCP-over-HDMI is exposed through `intel_hdmi_hdcp_shim`. HDCP 1.4 callbacks read and write DDC registers at `DRM_HDCP_DDC_*`, output Aksv through GMBUS, toggle DDI HDCP signalling, and check Ri matches. HDCP 2.2 callbacks use HDMI message offsets, poll RxStatus for message size/ready state with per-message timeouts, read/write HDCP 2.2 messages, detect reauth/topology-change status, and query sink version capability.

## State And Persistence Behavior

Persistent connector state includes `intel_hdmi->attached_connector`, DP dual-mode adapter type and max TMDS clock, CEC notifier pointer, connector EDID (`detect_edid`), display info, and connector properties. Atomic configuration state is stored in `intel_crtc_state`: `has_hdmi_sink`, `has_infoframe`, `has_audio`, `sink_format`, `output_format`, `port_clock`, `pipe_bpp`, `limited_color_range`, `hdmi_scrambling`, `hdmi_high_tmds_clock_ratio`, and packed infoframe payloads. HDCP state is owned by the generic HDCP core, while this file supplies transport operations through DDC and DDI signalling.

No file-backed persistence exists. Hardware state persists in DIP registers, SCDC sink registers, DDI signalling bits, and connected sink state until changed or reset. EDID and dual-mode data are refreshed on detection and cleared before new reads.

## Dependencies And Integration Points

The file depends on DRM HDMI, EDID, SCDC, HDCP, atomic, CEC, and probe helpers; i915 display register access; DDI, GMBUS, audio, VRR, pfit, LSPCON, panel, PHY, DPLL, and BIOS/VBT helpers. It integrates with the generic HDCP core through `intel_hdcp_init()` and the HDMI shim, with atomic modeset through connector helper funcs and encoder compute hooks, with userspace through connector properties, with sink devices through DDC/SCDC, and with CEC through notifier registration.

## Risks And Edge Cases

Risk is spread across platform differences. Infoframe register layouts differ substantially by generation; writing while ports are enabled or failing to clear enable bits can produce bad packets. TMDS and bpc selection must respect source, sink, dual-mode adapter, VBT, and PLL holes; mistakes reject valid modes or allow unstable modes. YCbCr 4:2:0 fallback and limited RGB range must avoid contradictory color state. SCDC scrambling must be programmed before enabling HDMI 2.0 links or sinks can time out.

HDCP DDC operations are sensitive to I2C errors, sink timing, message size validation, and Kaby Lake signalling workaround timing. Detection relies on EDID being digital and can fall back to bit-banged GMBUS. DDC pin selection must avoid duplicate pin ownership. DSC helper math must obey HDMI 2.1 slice width, throughput, and chunk byte limits.

## Test Signals

Useful signals include mode validation across HDMI 1.4/2.0 limits, RGB and YCbCr 4:2:0 modes, 8/10/12 bpc selection, SCDC scrambling at high TMDS rates, HDR metadata fastset updates, infoframe readback on each platform path, EDID read fallback, DP dual-mode adapter detection and max clock handling, CEC notifier address updates, HDCP 1.4 and 2.2 authentication over HDMI, Kaby Lake HDCP signalling workaround coverage, DDC pin conflict logging, and HDMI DSC slice/bpp helper unit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.h

## Purpose

`intel_hdmi.h` declares the display-local HDMI API used by encoder setup, atomic modeset, infoframe handling, scrambling control, DSC calculations, and connector initialization. It keeps the large HDMI implementation private to `intel_hdmi.c` while exposing the operations needed by the rest of i915 display code.

## Important APIs, Types, And Functions

The header forward declares HDMI, DRM, and Intel display types, then declares connector and compute functions (`intel_hdmi_init_connector()`, `intel_hdmi_compute_has_hdmi_sink()`, `intel_hdmi_compute_config()`), lifecycle and sink programming functions (`intel_hdmi_encoder_shutdown()`, `intel_hdmi_handle_sink_scrambling()`, `intel_dp_dual_mode_set_tmds_output()`), infoframe operations (`intel_infoframe_init()`, `intel_hdmi_infoframes_enabled()`, `intel_hdmi_infoframe_enable()`, `intel_hdmi_read_gcp_infoframe()`, `intel_hdmi_fastset_infoframes()`, `intel_read_infoframe()`, `hsw_write_infoframe()`, `hsw_read_infoframe()`), color/clock helpers (`intel_hdmi_limited_color_range()`, `intel_hdmi_bpc_possible()`, `intel_hdmi_tmds_clock()`), DSC helpers, and `intel_hdmi_is_frl()`.

## Control Flow

Other display code calls `intel_hdmi_init_connector()` during digital port setup, `intel_infoframe_init()` to install platform callbacks, `intel_hdmi_compute_has_hdmi_sink()` and `intel_hdmi_compute_config()` during atomic state construction, infoframe functions during enable/fastset/readout, scrambling control before HDMI 2.0 port enable, and DSC helpers when configuring PCON/HDMI DSC paths.

## State And Persistence Behavior

The header stores no state. Its functions read and mutate `struct intel_hdmi`, `struct intel_digital_port`, `struct intel_connector`, and `struct intel_crtc_state` fields in the implementation. Callers are responsible for using the APIs in the proper modeset phase, especially for infoframe programming and SCDC scrambling.

## Dependencies And Integration Points

This header is included by DDI, encoder, connector, and readout code that needs HDMI-specific behavior. It bridges DRM connector state, Intel CRTC state, HDMI infoframe structs, output format enums, and the digital port object.

## Risks And Edge Cases

Header risk is API drift: signature changes affect multiple modeset paths. Misusing the APIs outside their intended enable/disable/readout phase can lead to stale infoframes, bad scrambling state, or inconsistent CRTC state. The direct exposure of HSW read/write infoframe helpers means non-HDMI paths that share DIP registers must preserve expected buffer layout.

## Test Signals

Build coverage, successful HDMI connector bring-up, valid atomic HDMI modes, correct infoframe programming/readback, SCDC scrambling toggles, and DSC helper results all validate this header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdmi.h -->
