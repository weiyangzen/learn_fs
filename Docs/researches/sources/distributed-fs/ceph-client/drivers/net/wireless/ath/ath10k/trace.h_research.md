# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/trace.h

Purpose: Defines ath10k trace events for logs, WMI commands/events/dbglog/diag, HTT stats/pktlog/TX, TX completion unref, frame headers/payloads, and HTT RX descriptors, with no-op stubs when ath10k tracing is disabled.

Important APIs and definitions: Provides `ath10k_frm_hdr_len()`, `TRACE_SYSTEM ath10k`, `ATH10K_MSG_MAX`, `DECLARE_EVENT_CLASS` templates for log/header/payload events, and `TRACE_EVENT`/`DEFINE_EVENT` instances such as `ath10k_log_err`, `ath10k_log_warn`, `ath10k_log_info`, `ath10k_log_dbg`, `ath10k_log_dbg_dump`, `ath10k_wmi_cmd`, `ath10k_wmi_event`, `ath10k_htt_stats`, `ath10k_wmi_dbglog`, `ath10k_htt_pktlog`, `ath10k_htt_tx`, `ath10k_txrx_tx_unref`, `ath10k_tx_hdr`, `ath10k_tx_payload`, `ath10k_rx_hdr`, `ath10k_rx_payload`, `ath10k_htt_rx_desc`, `ath10k_wmi_diag_container`, and `ath10k_wmi_diag`.

Control flow, state, and persistence: No persistent driver state. When tracing is disabled, macro overrides create inline no-op trace functions and `trace_*_enabled()` false helpers. When enabled, the header generates tracepoint metadata and dynamic-array copies for buffers.

Dependencies and integration points: Includes Linux tracepoint support and `core.h`; must be paired with `trace.c` for definition. It integrates with debug logging, WMI/HTT instrumentation, TX/RX paths, and tracefs consumers.

Risks: Dynamic array sizes use packet/buffer lengths, so callers must pass valid buffers. `ath10k_frm_hdr_len()` intentionally clamps header length to avoid short-frame overreads. Trace ABI changes can affect tooling that parses tracefs output. The custom `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` must remain correct for kernel trace generation.

Test signals: Build tracing enabled/disabled, enable each trace event class, send WMI/HTT traffic, trace short or FCS-error RX frames, verify payload/header splitting, and confirm no-op builds do not evaluate trace side effects unexpectedly.
