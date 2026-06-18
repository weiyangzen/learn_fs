# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/trace.h

## Purpose

`trace.h` declares iwlmei tracepoints for SAP command messages and MEI doorbell messages. It provides no-op stubs when device tracing is disabled and full tracepoint definitions when enabled.

## Important APIs, Types, and Functions

The callable tracing hooks are `trace_iwlmei_sap_cmd(const struct iwl_sap_hdr *, bool tx)` and `trace_iwlmei_me_msg(const struct iwl_sap_me_msg_hdr *, bool tx)`. `iwlmei_sap_cmd` records a dynamic copy of the SAP command plus direction, type, length, and sequence. `iwlmei_me_msg` records ME message type, sequence, and direction.

## Control Flow

Instrumented code in `main.c` calls these hooks before sending commands and after receiving ME/SAP messages. Tracepoint metadata is included through `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` so `trace.c` can instantiate it.

## State and Persistence Behavior

No state is stored in the driver. Trace events are transient records in ftrace/perf buffers. SAP command tracing copies the full command payload, so it observes the command as it was at trace time.

## Dependencies and Integration Points

It depends on Linux tracepoint macros and SAP protocol structures. The include path uses `"mei/sap.h"` and a local `TRACE_INCLUDE_PATH .`, so build include paths must match the iwlwifi directory layout.

## Risks and Edge Cases

Tracing command payloads can expose firmware-control data. Any new SAP command structure can be traced without header-specific decoding, but the length field must be validated by callers before they hand a pointer to this tracepoint. Stub parity must be maintained when adding new trace hooks.

## Test Signals

Compile both tracing-disabled and tracing-enabled configurations, enable trace events during SAP startup/ownership/NVM flows, and verify printed type/length/sequence values match driver logs.
