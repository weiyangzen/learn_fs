# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-data.h

## Purpose
Declares trace events that capture TX transfer-buffer payload data and RX payload data for iwlwifi device tracing.

## Important APIs, Types, and Functions
Trace events are `iwlwifi_dev_tx_tb` and `iwlwifi_dev_rx_data`. They use `DEV_ENTRY`, `DEV_ASSIGN`, `iwl_trace_data()`, and dynamic trace arrays.

## Control Flow
TX data is copied only when `iwl_trace_data(skb)` allows it, avoiding selected important/control frames. RX data copies bytes after the supplied start offset if `start < len`.

## State and Persistence Behavior
No driver state is mutated. Captured bytes persist only in tracing buffers.

## Dependencies and Integration Points
Included by `iwl-devtrace.h` and compiled through Linux tracepoint infrastructure.

## Risks
Trace data can expose packet payloads, so filtering is important. Incorrect lengths or offsets could over-copy into trace buffers.

## Test Signals
Trace enabled/disabled builds, TX payload filtering for EAPOL/status-request frames, RX data with `start == len` and `start < len`, and trace output decoding are useful.
