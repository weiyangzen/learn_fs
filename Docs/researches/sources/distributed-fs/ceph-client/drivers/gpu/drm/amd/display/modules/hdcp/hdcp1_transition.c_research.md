# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp1_transition.c

Purpose: implements the HDCP 1.x transition layer for HDMI/DVI-style links and DisplayPort links. It consumes execution results in `struct mod_hdcp_transition_input_hdcp1`, examines the current HDCP state through `current_state(hdcp)`, and fills `struct mod_hdcp_output` with callback/watchdog/auth-complete requests while mutating state through helpers from `hdcp.h`.

Important APIs: `mod_hdcp_hdcp1_transition()` handles states `H1_A0_WAIT_FOR_ACTIVE_RX` through `H1_A9_READ_KSV_LIST`; `mod_hdcp_hdcp1_dp_transition()` handles `D1_*` states. Both return `enum mod_hdcp_status` and use helpers such as `callback_in_ms`, `set_watchdog_in_ms`, `set_state_id`, `set_auth_complete`, `fail_and_restart_in_ms`, and `increment_stay_counter`.

Control flow: HDMI waits for BKSV/BCAPS, exchanges KSVs, validates R0 and receiver state, then either enables encryption directly or waits for repeater readiness and validates KSV list/V'. DP first checks HDCP capability in BCAPS, waits for R0' availability with a 100 ms watchdog, retries some validation failures up to the stay-count policy, then authenticates direct receivers or validates repeater topology. MST adds stream encryption checks after link encryption.

State and persistence: this file does not persist external data but updates `hdcp->state`, `hdcp->state.stay_count`, `conn->is_repeater`, retry-related link adjustments, and auth-complete output flags. Workarounds are encoded in `conn->link.adjust.hdcp1`, including `disable`, `postpone_encryption`, and `min_auth_retries_wa`.

Dependencies and integration: depends on the HDCP execution layer to pre-populate the input fields, on PSP-backed validation/encryption helpers, and on event routing for callback/watchdog behavior. It is called by the top-level HDCP event processor after DDC/PSP work has been attempted.

Risks: timeout constants and retry decisions are interoperability-sensitive. A bad PASS/FAIL mapping can cause black screens, endless reauthentication, or accepting invalid topology. DP MST stream encryption and revocation-specific retry suppression are high-risk branches.

Test signals: exercise direct and repeater HDMI/DP, DP MST, invalid BKSV/R0/V', KSV READY timeout, CP reauth/integrity failure, device-count mismatch, and slow receiver timing paths.
