# sources/distributed-fs/ceph-client/drivers/s390/cio/ccwreq.c

Purpose: implements the common internal CCW request engine for CIO device procedures, including path selection, retry, timeout, cancellation, interrupt status interpretation, and callback completion.

Important APIs/types/functions: exports/defines `lpm_adjust`, `ccw_request_start`, `ccw_request_cancel`, `ccw_request_handler`, `ccw_request_timeout`, and `ccw_request_notoper`; internal helpers include `ccwreq_next_path`, `ccwreq_stop`, `ccwreq_do`, `ccwreq_status`, and `ccwreq_log_status`.

Control flow: start initializes mask/retry/done/cancel state, adjusts the logical path mask, and calls `ccwreq_do`. The executor tries paths until retries are exhausted, starts I/O through `cio_start`, clears temporary improper status, moves to next path on access/path errors, and stops with callback on terminal errors. Interrupt handler accumulates/senses status, applies optional request filter and driver unit-check handler, optionally calls request check callback, then completes, restarts, or moves to another path. Timeout logs missing-interrupt details per channel path, clears the subchannel, and may record a final `-ETIME`.

State and persistence: state lives in `cdev->private->req` plus accumulated IRB in the ccw device DMA area. No persistent state; timeouts are configured through ccw device timeout machinery.

Dependencies and integration: uses low-level CIO `cio_start`, `cio_clear`, `cio_update_schib`, ccw device timeout and sense accumulation helpers, per-cpu `cio_irb`, subchannel data, CIO tracing, and optional ccw driver `uc_handler`.

Risks: path-mask and retry semantics are subtle, especially singlepath mode using `0x8080` to try all paths twice; cancellation maps killed I/O to `-EIO`; `drc` can override non-ENODEV errors after timeout; status filters/check callbacks can redirect restart/path decisions.

Test signals: no-path start, successful request, channel/device status errors, command reject/unit-check handler decisions, retry exhaustion, singlepath path rotation, cancellation before completion, timeout logging/clear, and not-oper completion.
