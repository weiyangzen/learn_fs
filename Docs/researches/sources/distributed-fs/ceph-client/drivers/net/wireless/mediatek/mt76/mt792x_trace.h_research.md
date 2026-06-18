# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_trace.h

## Purpose
This header declares the MT792x trace event format for low-power state transitions.

## Important APIs, Types, And Functions
It defines trace system `mt792x`, helper macros for device name fields, and `TRACE_EVENT(lp_event)` with arguments `struct mt792x_dev *dev` and `u8 lp_state`. The printed event includes the wiphy name and either `lp ready` or `lp not ready`.

## Control Flow
Callers invoke `trace_lp_event(dev, state)` generated from this declaration. The tracepoint copies the wiphy name and low-power state into the event record and formats it for trace output.

## State And Persistence
The trace event stores transient event records in the kernel tracing buffers when enabled. It does not mutate driver state.

## Dependencies And Integration Points
It depends on Linux tracepoint macros and `mt792x.h` for device types and `mt76_hw()`. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back at this header.

## Risks
Trace event field names and print format become observable tracing ABI. The helper uses a fixed 32-byte wiphy name buffer and depends on a valid mt76 hw pointer at trace time.

## Test Signals
Successful trace header generation, event enable/disable under ftrace/perf, and correctly formatted low-power PM events validate this header.
