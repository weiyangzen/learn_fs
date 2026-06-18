# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.h

## Purpose
Top-level device tracing header for iwlwifi. It provides packet-data filtering helpers, RX trace-length calculation, tracepoint stubs for disabled builds, shared device-field macros, and includes all trace event families.

## Important APIs, Types, and Functions
Key helpers are `iwl_trace_data()`, `iwl_rx_trace_len()`, `maybe_trace_iwlwifi_dev_rx()`, and `__trace_iwlwifi_dev_rx()`. It includes IO, ucode, message, data, and iwlwifi trace headers.

## Control Flow
`iwl_trace_data()` suppresses payload tracing for non-data frames, frames requesting TX status, and likely EAPOL frames. `iwl_rx_trace_len()` trims RX MPDU traces to headers for data frames. `maybe_trace_iwlwifi_dev_rx()` calls the heavy trace helper only if RX tracepoints are enabled.

## State and Persistence Behavior
No state changes. It controls what packet bytes are copied into trace buffers.

## Dependencies and Integration Points
Depends on skb/mac80211/cfg80211 types and `iwl-trans.h`. Used throughout transport RX/TX/IO/debug logging paths.

## Risks
Packet header offset assumptions must match 802.11 header forms and firmware RX command header size. Filtering is privacy-sensitive and can affect trace usefulness.

## Test Signals
QoS/A4/EAPOL TX filtering, RX MPDU header trimming, non-data RX full tracing, disabled tracepoint stub compilation, and tracepoint-enabled gating are important.
