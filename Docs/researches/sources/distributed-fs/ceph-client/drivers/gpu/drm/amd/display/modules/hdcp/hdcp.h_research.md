# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp.h

Purpose: Defines the internal HDCP module state, state IDs, message buffers, transition-input flags, helper predicates, and cross-object prototypes used by HDCP top-level, transition, execution, DDC, PSP, and log files.

Important APIs and types: Transition input structures track pass/fail/unknown for each HDCP1/2 action. Message structures store HDCP1 values (`an`, `aksv`, `bksv`, `r0p`, `bcaps`, `bstatus`, KSV list, V prime, DP BINFO) and HDCP2 values (AKE, LC, SKE, repeater, RX status, content stream type). `struct mod_hdcp` aggregates config, connection, displays, authentication, state, and reserved buffer. State enums cover initial, HDCP1 HDMI/DVI, HDCP1 DP, HDCP2 HDMI/DVI, and HDCP2 DP state ranges.

Control flow: Execution files set transition input flags via `mod_hdcp_execute_and_set`; transition files inspect those flags and event context to advance state and output timers. Inline helpers classify current state family, authenticated states, link mode, display activity/encryption state, active display lookup, and retry reset. Output helpers set callbacks, watchdogs, state IDs, and authentication completion.

State and persistence: This header defines all in-memory state persisted across HDCP events. `auth.id` identifies authentication cycles, `state.stay_count` tracks repeated transition stays, connection tracks repeater/revocation/KM/retry data, and displays track per-output state/adjustments. Message buffers have fixed maximum sizes based on HDCP specs.

Dependencies and integration points: Includes public `mod_hdcp.h`, `hdcp_log.h`, DRM DP helper, and DRM HDCP helper. Prototypes connect to `hdcp_psp.c`, `hdcp_ddc.c`, `hdcp_log.c`, and all execution/transition files.

Risks: Fixed buffer sizes must match HDCP maximum message sizes and device counts; overflow would be security-sensitive. State enum ranges are used by inline predicates, so insertion/reordering must preserve range relationships. Helpers set output timer stop flags on state change, so missed calls can leave stale timers. `set_state_id` zeroes state and traces; callers must not expect `stay_count` to survive transitions.

Test signals: State-family predicate tests, state transition range tests, max KSV/RX ID list sizing, display container lookup, callback/watchdog output side effects, and message buffer fill bounds in DDC/PSP operations.
