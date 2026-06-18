# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace.c

## Purpose
Instantiates iwlwifi tracepoints and implements conditional RX tracing that splits RX packet header tracing from payload tracing.

## Important APIs, Types, and Functions
Defines `CREATE_TRACE_POINTS`, exports ucode tracepoint symbols, and implements `__trace_iwlwifi_dev_rx()`.

## Control Flow
`__trace_iwlwifi_dev_rx()` computes a trace length and header offset using `iwl_rx_trace_len()`, emits `trace_iwlwifi_dev_rx()`, and emits `trace_iwlwifi_dev_rx_data()` only when payload bytes were omitted from the first event.

## State and Persistence Behavior
No persistent driver state. It writes trace records.

## Dependencies and Integration Points
Depends on `iwl-devtrace.h`, `iwl-trans.h`, Linux module tracepoint export, and sparse/`__CHECKER__` guards.

## Risks
RX length calculation must avoid reading beyond packets. Tracepoint symbol export is needed for split modules; missing exports break consumers.

## Test Signals
Device tracing enabled, sparse builds, RX MPDU data/header split, non-MPDU full RX tracing, and module consumers of exported ucode tracepoints are relevant.
