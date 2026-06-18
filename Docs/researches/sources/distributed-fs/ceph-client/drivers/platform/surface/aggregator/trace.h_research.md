# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/trace.h

## Purpose
Defines ftrace tracepoints for SSAM/SSH protocol activity, packet/request state transitions, allocation/free events, pending counts, and error-injection events. It gives maintainers observability into the highly asynchronous packet and request transport layers.

## Important APIs, Types, And Functions
The header defines trace enums for SSH frame types, packet/request flags, and SSH target categories. Helper functions derive display-safe fields from packets: pointer UIDs, sequence IDs, request IDs, TID/SID/TC, CID, and IID. Event classes cover frames, commands, packets, packet status, requests, request status, allocation, free, pending counts, and data lengths. Concrete events include `ssam_rx_frame_received`, `ssam_rx_response_received`, `ssam_packet_submit`, `ssam_packet_complete`, `ssam_request_submit`, `ssam_request_complete`, timeout reap events, error-injection events, and cache/event-item allocation/free events.

## Control Flow
Transport code calls tracepoints at packet submit/resubmit/cancel/timeout/complete/release, request submit/cancel/timeout/complete, RX frame/command reception, timeout reaper execution, and error-injection branches. Trace event formatting converts raw bitfields and protocol IDs into compact symbolic strings for debugging.

## State And Persistence Behavior
Tracepoints persist no driver state. The only local transformation is `ssam_trace_ptr_uid()`, which derives a short non-address UID string from `%p` output to correlate events without exposing full kernel pointers. Trace output is consumed by ftrace/perf infrastructure depending on runtime tracing configuration.

## Dependencies And Integration Points
Depends on Linux tracepoint infrastructure, unaligned access helpers, and protocol definitions in `linux/surface_aggregator/serial_hub.h`. It must be included in exactly one trace-definition context with `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` outside the include guard, following kernel tracepoint conventions.

## Risks
Trace helpers inspect packet data lengths before reading protocol fields, but any mismatch in `SSH_COMMAND_MESSAGE_LENGTH()` offsets would produce misleading traces. The symbolic table for target categories must be kept in sync with protocol enum additions. Tracepoint format changes can break external scripts that parse trace output.

## Test Signals
Build with tracepoints enabled, enable each event class under `/sys/kernel/tracing/events/surface_aggregator`, run packet/request traffic, verify symbolic formatting for known TID/TC/flag combinations, and use error injection to confirm diagnostic tracepoints fire.
