# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.c

Purpose: implements HDCP diagnostic formatting for binary DDC messages, status names, and state names. It supports macros in `hdcp_log.h` and gives state-machine logs readable string values.

Important APIs: `mod_hdcp_dump_binary_message()` formats a byte array as newline-prefixed hex bytes into a caller-supplied buffer. `mod_hdcp_log_ddc_trace()` logs known HDCP1 or HDCP2 message buffers from `hdcp->auth.msg`. `mod_hdcp_status_to_str()` expands `MOD_HDCP_STATUS_LIST`; `mod_hdcp_state_id_to_str()` maps every known HDCP state ID to a string.

Control flow: binary dump calculates required buffer size and only writes when the provided buffer is large enough. DDC trace branches by `is_hdcp1()` and `is_hdcp2()` and emits read/write trace macros for all message classes. State conversion is a large switch covering uninitialized, initialized, HDCP1 HDMI/DP, and HDCP2 HDMI/DP states.

State and persistence: uses `hdcp->buf` as the text-formatting scratch area through the logging macros. It reads authentication message buffers but does not change protocol state.

Dependencies and integration: integrated by `HDCP_AUTH_COMPLETE_TRACE`, DDC trace macros, and error/state logging. It depends on state/status enum definitions being kept in sync with strings.

Risks: `sprintf` is safe only because the target-size guard accounts for fixed three-byte hex tokens, newline, and terminator. If new states are added without updating this file, logs degrade to `UNKNOWN_STATE_ID`. Full DDC dumps can expose sensitive authentication material in debug logs.

Test signals: verify formatting for exact-size and undersized buffers, status string coverage from `MOD_HDCP_STATUS_LIST`, newly added state IDs, and that HDCP1/HDCP2 traces use correct buffer lengths.
