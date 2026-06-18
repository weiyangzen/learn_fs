# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/raw_mode.h

Purpose: This header declares the raw-mode queue IDs and the raw-mode hooks used by the SCMI core and transports to initialize, tear down, and report raw messages.

Important APIs/types/functions: The queue enum defines `SCMI_RAW_REPLY_QUEUE`, `SCMI_RAW_NOTIF_QUEUE`, `SCMI_RAW_ERRS_QUEUE`, and `SCMI_RAW_MAX_QUEUE`. `scmi_raw_mode_init()` creates a raw-mode instance for an SCMI handle, debugfs root, instance ID, transport channels, descriptor, and max in-flight count. `scmi_raw_mode_cleanup()` tears it down. `scmi_raw_message_report()` serializes normal replies/notifications. `scmi_raw_error_report()` serializes unexpected or timed-out replies.

Control flow: Core code can keep the opaque pointer returned by init and pass it back into report/cleanup functions. Queue selection and debugfs behavior are implemented in `raw_mode.c`.

State and persistence: The header has no state; the returned opaque pointer represents runtime state owned by `raw_mode.c`.

Dependencies and integration points: It includes `common.h`, so users see SCMI handle, channel, descriptor, and xfer types. It is an integration boundary between generic core RX/error handling and optional debug raw mode.

Risks and edge cases: Callers must pass the correct queue index and channel ID. The opaque pointer can be NULL only where implementation tolerates it; cleanup and report hooks guard against NULL, but misuse before initialization loses reports.

Test signals: Build tests must cover raw mode enabled/disabled callers. Runtime tests should verify that core RX hooks pass replies to the reply queue and notifications to the notification queue using these declarations.
