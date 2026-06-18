# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.c

## Purpose

`intel_hdcp.c` is the generic i915 display HDCP coordinator. It owns the connector-facing content protection property flow, HDCP 1.4 authentication, HDCP 2.2 authentication, link checking, DP MST stream accounting, firmware/GSC/MEI arbitration, debugfs reporting, and connector cleanup. Bus-specific operations are deliberately abstracted through `struct intel_hdcp_shim`, so the same core state machine can drive HDMI DDC, DP AUX, SST, and MST transports.

## Important APIs, Types, And Functions

The exported entry points are `intel_hdcp_init()`, `intel_hdcp_enable()`, `intel_hdcp_disable()`, `intel_hdcp_update_pipe()`, `intel_hdcp_atomic_check()`, `intel_hdcp_cancel_works()`, `intel_hdcp_cleanup()`, `intel_hdcp_handle_cp_irq()`, `intel_hdcp_component_init()`, `intel_hdcp_component_fini()`, `is_hdcp_supported()`, `intel_hdcp_info()`, and `intel_hdcp_connector_debugfs_add()`. These are called by connector initialization, atomic commit paths, IRQ handlers, driver/component init/fini, and debugfs setup.

The core state is split between `connector->hdcp` and `dig_port->hdcp`. Connector state includes `value`, `content_type`, `force_hdcp14`, `hdcp_encrypted`, `hdcp2_encrypted`, `hdcp2_supported`, `is_repeater`, pairing state, sequence counters, `cpu_transcoder`, `stream_transcoder`, the delayed link-check work, property work, and CP IRQ waitqueue/counter. Port state tracks shared MST data such as `port_data`, `auth_status`, `num_streams`, stream descriptors, and `mst_type1_capable`.

HDCP 1.4 is built from `intel_hdcp1_enable()`, `intel_hdcp_auth()`, `intel_hdcp_auth_downstream()`, `intel_hdcp_validate_v_prime()`, `_intel_hdcp_disable()`, and `intel_hdcp_check_link()`. HDCP 2.2 is built from wrapper calls into `display->hdcp.arbiter->ops`, then protocol stages including `hdcp2_authentication_key_exchange()`, `hdcp2_locality_check()`, `hdcp2_session_key_exchange()`, `hdcp2_authenticate_repeater_topology()`, `hdcp2_propagate_stream_management_info()`, `hdcp2_authenticate_and_encrypt()`, `_intel_hdcp2_enable()`, `_intel_hdcp2_disable()`, and `intel_hdcp2_check_link()`.

## Control Flow

Initialization starts with `intel_hdcp_component_init()`, which registers either the MEI component or a GSC-backed arbiter on display version 14 and newer. `intel_hdcp_init()` initializes per-connector HDCP state, allocates HDCP 2.2 stream data if supported, attaches the DRM content protection property, stores the transport shim, initializes mutexes, work items, and the CP IRQ waitqueue.

Enable requests come from atomic commit through `intel_hdcp_enable()` or `intel_hdcp_update_pipe()`. `_intel_hdcp_enable()` locks connector and shared port HDCP mutexes, records content type and transcoder mapping, then prefers HDCP 2.2 when not forced to 1.4 and both platform and sink capability checks pass. HDCP 2.2 performs AKE, locality, session-key exchange, optional repeater topology validation, stream management, firmware port authentication, then hardware encryption enable. If HDCP 2.2 fails and the requested content is not Type 1, the code falls back to HDCP 1.4.

HDCP 1.4 loads hardware keys, captures An, sends An/Aksv through the shim, validates BKSV and revocation status, configures repeater bits, enables signalling and hardware auth/encryption, verifies R0/Ri, enables MST stream encryption if needed, and validates downstream repeater topology through SHA-1 V prime comparison. Failures trigger cleanup and limited retries.

After a successful enable, the file schedules `check_work`. The delayed worker prefers `intel_hdcp2_check_link()` unless HDCP 1.4 is forced, otherwise calls `intel_hdcp_check_link()`. Protected links reschedule the worker; topology change on HDCP 2.2 runs repeater topology authentication. Link failure disables encryption, sets content protection back to `DESIRED`, and lets userspace or later commits retry.

## State And Persistence Behavior

The file persists no data to disk, but it maintains long-lived in-kernel state across commits and workqueue runs. `hdcp->value` mirrors the desired DRM property state and is updated asynchronously to userspace via `prop_work`. `dig_port->hdcp.num_streams` prevents shared MST link encryption from being torn down while other streams still need protection. HDCP 2.2 pairing information is delegated to firmware through the arbiter interface. `seq_num_v` and `seq_num_m` protect repeater topology and stream-management ordering, and rollover forces reauthentication. `force_hdcp14` is runtime debugfs state that changes protocol selection.

Locking is central: connector HDCP state is protected by `hdcp->mutex`, shared port/MST state by `dig_port->hdcp.mutex`, and firmware arbiter presence by `display->hdcp.hdcp_mutex`. Work items also hold connector references around asynchronous property updates.

## Dependencies And Integration Points

The file depends on DRM HDCP helpers for KSV validation/revocation and content protection property updates, i915 display register access through `intel_de_*`, runtime power helpers, pcode key loading, DP MST payload state, platform stepping helpers, HDCP register definitions, the transport shim, and the GSC/MEI HDCP arbiter interface.

It integrates with HDMI through `intel_hdmi.c`'s shim, with DP through corresponding DP shims outside this subset, with atomic modeset through atomic check and enable/update hooks, with CP IRQ handling through `intel_hdcp_handle_cp_irq()`, with debugfs through capability and force-HDCP-1.4 files, and with display version 14+ GSC firmware through `intel_hdcp_gsc_message.c`.

## Risks And Edge Cases

The highest-risk areas are authentication timing, shared MST state, and failure recovery. HDCP 1.4 has several spec-driven retry loops and carefully ordered register writes; regressions can cause false authentication failures or leave signalling enabled. HDCP 2.2 depends on external firmware availability and correct `hdcp_port_data`; missing arbiter state or stale GSC/MEI status blocks capability. MST uses a single link policy for all active streams, so Type 1 content can be downgraded or rejected when any downstream sink is not Type 1 capable.

Other hazards include key-load power-well requirements, platform-specific line rekey workarounds, DP dock resume retry behavior, topology sequence rollover, revocation checks, and cleanup races during connector unregister. Authentication changes should be tested on both repeater and non-repeater topologies.

## Test Signals

Useful test signals include successful attach of the DRM content protection property, HDCP 1.4 and HDCP 2.2 enable/disable cycles, fallback from HDCP 2.2 to 1.4 for Type 0 content, rejection of Type 1 when only HDCP 1.4 is available, CP IRQ-triggered rechecks, repeater topology changes, MST multi-stream accounting, suspend/resume with DP docks, GSC/MEI component bind/unbind, debugfs capability output, and `i915_force_hdcp14` behavior. Kernel logs should be checked for timeouts around An/Ri/SHA-1/encryption status and firmware command failures.
