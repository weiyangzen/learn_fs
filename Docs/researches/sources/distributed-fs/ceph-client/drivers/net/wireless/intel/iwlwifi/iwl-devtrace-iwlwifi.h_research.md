# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-iwlwifi.h

## Purpose
Declares primary iwlwifi device trace events for host commands, RX packets, TX frames, and firmware event-log entries.

## Important APIs, Types, and Functions
Trace events include `iwlwifi_dev_hcmd`, `iwlwifi_dev_rx`, `iwlwifi_dev_tx`, and `iwlwifi_dev_ucode_event`. They use host command payload arrays, RX trace lengths, TX TFD/buffer snapshots, and firmware event fields.

## Control Flow
Callers supply command or packet metadata; trace fast-assign handlers copy relevant bytes into dynamic arrays. Host command tracing handles wide and legacy headers, and TX tracing filters payload through `iwl_trace_data()`.

## State and Persistence Behavior
Only trace buffers are populated. No device state is modified.

## Dependencies and Integration Points
Included by `iwl-devtrace.h`, used by transport TX/RX/host-command paths and firmware event log dumping.

## Risks
Dynamic-array lengths must match copied bytes. TX/RX tracing can expose frame data if filtering is wrong. Host-command tracing sits on hot paths and should remain lightweight when disabled.

## Test Signals
Wide and non-wide host command traces, multi-buffer command payloads, RX MPDU header-only tracing, TX data filtering, firmware event-log trace, and disabled tracepoint stubs are useful.
