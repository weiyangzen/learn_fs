# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/trace.h

## Purpose

`trace.h` defines the ftrace tracepoint interface for the MHI host stack. It turns shared MHI state macro lists into trace enums and records transfer ring elements, interrupt-vector state snapshots, PM state changes, event-ring entries, channel command transitions, and queued device-state transitions.

## Important APIs, Types, And Functions

- Trace enum definitions for MHI device states, internal PM states, execution environments, channel command state types, and device transition work states.
- `TRACE_EVENT(mhi_gen_tre)` records generated transfer ring element pointer and dwords.
- `TRACE_EVENT(mhi_intvec_states)` records local EE/state and device EE/state observed in the BHI interrupt-vector handler.
- `TRACE_EVENT(mhi_tryset_pm_state)` records requested PM state transitions.
- `DECLARE_EVENT_CLASS(mhi_process_event_ring)` with `mhi_data_event` and `mhi_ctrl_event` records event ring entries.
- `DECLARE_EVENT_CLASS(mhi_update_channel_state)` with command start/end events records channel command transitions.
- `TRACE_EVENT(mhi_pm_st_transition)` records worker-handled device transition states.

## Control Flow

This header is included normally by MHI source files for tracepoint declarations and included once with `CREATE_TRACE_POINTS` by `init.c` to instantiate tracepoints. The final `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` settings point the trace generator back to the host trace header.

## State And Persistence Behavior

Tracepoints do not alter MHI state. They sample fields from `struct mhi_controller`, `struct mhi_chan`, and `struct mhi_ring_element` at call sites. `tracepoint_string()` through `TPS()` is used for stable reason strings in channel command traces.

## Dependencies And Integration Points

The file depends on Linux tracepoint infrastructure, byte-order helpers, `../common.h`, and `internal.h`. It is called from `main.c` for TRE/event/channel-command tracing and from `pm.c` for PM and device-transition tracing.

## Risks

Trace field extraction assumes pointers passed by call sites remain valid for the trace fast assignment. Symbolic rendering relies on macro lists staying consistent with enum values. Because `mhi_tryset_pm_state` converts bitmask state with `__fls()`, invalid zero or multi-bit PM values would produce misleading trace output.

## Test Signals

With ftrace enabled, expected events should appear under the `mhi_host` trace system during queueing, event completion, channel start/reset, MHI intvec handling, and PM transitions. Build tests should cover tracepoints enabled and disabled, including header multi-read behavior.
