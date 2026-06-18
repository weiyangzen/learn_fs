# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-devtrace-ucode.h

## Purpose
Declares trace events for continued and wrapped firmware event-log output.

## Important APIs, Types, and Functions
Events are `iwlwifi_dev_ucode_cont_event` and `iwlwifi_dev_ucode_wrap_event`, capturing device name, event time/data/id, and wrap counters/entry positions.

## Control Flow
Firmware event-log dump paths call these events while iterating event logs and detecting wrap boundaries.

## State and Persistence Behavior
No driver state is mutated; event-log snapshots persist in trace buffers.

## Dependencies and Integration Points
Included by `iwl-devtrace.h`; tracepoints are exported by `iwl-devtrace.c`.

## Risks
Event log trace volume can be high during firmware failures. Field widths must match firmware event data.

## Test Signals
Continuous event log tracing, wrap tracing, exported tracepoint availability for modules, and disabled tracing builds are key.
