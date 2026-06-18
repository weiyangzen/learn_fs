# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp.c

Purpose: Implements the top-level HDCP module lifecycle, display topology management, event processing, authentication reset logic, retry/error handling, query API, and signal-to-operation-mode mapping.

Important APIs and functions: Public functions include `mod_hdcp_get_memory_size`, `mod_hdcp_setup`, `mod_hdcp_teardown`, `mod_hdcp_add_display`, `mod_hdcp_remove_display`, `mod_hdcp_update_display`, `mod_hdcp_query_display`, `mod_hdcp_reset_connection`, `mod_hdcp_process_event`, and `mod_hdcp_signal_type_to_operation_mode`. Internal helpers include `push_error_status`, `is_cp_desired_hdcp1`, `is_cp_desired_hdcp2`, `execution`, `transition`, `reset_authentication`, `reset_connection`, and `update_display_adjustments`.

Control flow: Setup stores config and resets connection state. Adding/removing/updating displays resets authentication as needed, updates topology through PSP helpers, resets retry/trace state, and schedules callback authentication. `mod_hdcp_process_event` runs execution for the current state, then transition logic, converts execution/transition failures into public status, resets authentication on `RESET_NEEDED`, and clears CP_IRQ status after CPIRQ events. `transition` chooses HDCP2 before HDCP1 when content protection is desired and the link mode supports it, branching separately for DP and HDMI/DVI.

State and persistence: All persistent runtime state lives in `struct mod_hdcp`: config, connection/link data, display containers, authentication messages/transition inputs/counters, current state, and reserved buffer. Error trace is capped by `MAX_NUM_OF_ERROR_TRACE`; retry counters can disable HDCP1/HDCP2 when link retry limit is reached. No disk persistence.

Dependencies and integration points: Includes `hdcp.h`, which brings public mod HDCP types, DRM HDCP helpers, PSP function prototypes, DDC functions, logging, and transition/execution state machines. Integrates with display manager callbacks/watchdogs, topology updates, CPIRQ handling, and signal classification from `signal_types.h`.

Risks: Event handling is state-machine sensitive; unexpected events are ignored via `unexpected_event` and can leave authentication waiting for callbacks. Reset paths must destroy PSP sessions correctly; HDCP1 destroy behavior is TODO-noted as less unified than HDCP2. Retry-limit auto-disable changes link adjustment state after repeated failures. `update_display_adjustments` only handles a narrow MST authenticated disable->enable case and otherwise reports not implemented to force full reset.

Test signals: Add/remove/update display sequences, retry limit disablement, CP desired selection with revoked/disabled displays, reset during each HDCP1/2 state family, query encryption status for HDCP1/HDCP2 type0/type1, CPIRQ processing, unexpected events, and signal-to-mode mapping for DVI/HDMI/DP/eDP/MST/unsupported signals.
