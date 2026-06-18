# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_log.h

Purpose: defines the HDCP logging macro surface used by the state machine, topology updates, DDC tracing, and authentication-complete hooks.

Important APIs/types: macros include `HDCP_ERROR_TRACE`, `HDCP_HDCP1_ENABLED_TRACE`, `HDCP_HDCP2_ENABLED_TRACE`, display add/remove topology traces, state transition traces, callback event traces, `HDCP_DDC_READ_TRACE`, `HDCP_DDC_WRITE_TRACE`, and `HDCP_AUTH_COMPLETE_TRACE`.

Control flow: most macros expand to `DRM_DEBUG_KMS` or `pr_debug` calls. `HDCP_NEXT_STATE_TRACE` checks `output->watchdog_timer_needed` to include watchdog timing. `HDCP_EVENT_TRACE` logs only watchdog timeout and CPIRQ events. `HDCP_AUTH_COMPLETE_TRACE` currently dumps DDC trace and invokes a disabled `HDCP_LOG_TRA` hook.

State and persistence: no persistent state, but macros read `hdcp->config.index`, `hdcp->state`, `output`, and protocol buffers through `mod_hdcp_log_ddc_trace()`.

Dependencies and integration: depends on `mod_hdcp_status_to_str`, `mod_hdcp_state_id_to_str`, and `mod_hdcp_dump_binary_message()` implemented in `hdcp_log.c`, plus kernel DRM/pr_debug logging APIs.

Risks: macro arguments may be evaluated multiple times in future edits if not kept simple. DDC trace macros format into `hdcp->buf`, so concurrent tracing on the same object could overwrite scratch data. Debug logs may include HDCP authentication bytes.

Test signals: compile coverage with logging enabled, transition log strings for states with and without watchdogs, event logs for timeout/CPIRQ, and DDC traces on buffers near `hdcp->buf` capacity.
