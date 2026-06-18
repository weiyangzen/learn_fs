# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/session-protect.c

Purpose: Implements firmware session protection requests used to reserve medium time for association and TDLS-style exchanges before normal firmware association scheduling is active.

Important APIs and functions: `iwl_mld_schedule_session_protection()` sends a best-effort protection request. `iwl_mld_start_session_protection()` sends a request and waits for a matching start notification. `iwl_mld_cancel_session_protection()` removes a pending or active session. `iwl_mld_handle_session_prot_notif()` updates VIF session state from firmware notifications.

Control flow: Scheduling resolves the target MLD link, rejects redundant requests when current `end_jiffies` covers the requested minimum, sends `SESSION_PROTECTION_CMD` with add action, and marks `session_requested`. The blocking start path installs a notification wait, schedules protection, waits for `SESSION_PROTECTION_NOTIF`, and succeeds only when the matching link reports a start. Cancellation checks active/requested state, sends remove action, and clears local state.

State and persistence: Per-VIF `session_protect` tracks `end_jiffies`, requested duration in milliseconds, and whether a request is awaiting notification. State is runtime-only and cleared on failure, stop, or cancel. `end_jiffies` uses a nonzero sentinel because zero means inactive.

Dependencies and integration points: Depends on MLD VIF/link lookup, firmware MAC context/session protection ABI, notification wait infrastructure, and wiphy locking. It is used by association and TDLS paths that need medium reservation.

Risks: The code warns when more than one active link exists because session protection is not designed for multi-link operation. Link removal before notification can make firmware IDs stale. A firmware status of zero clears state and can cause a blocking start to return `-EIO`. Time conversions between ms, TU, and jiffies must preserve the intended minimum window.

Test signals: Exercise already-protected `-EALREADY`, matching and nonmatching notifications, timeout, firmware reject, cancellation with no active session, cancellation after request, and link removal/error-before-recovery behavior.
