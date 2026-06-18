# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/diag/fw_tracer_tracepoint.h

## Purpose

`fw_tracer_tracepoint.h` declares the `mlx5_fw` tracepoint used by firmware tracer decoding to emit human-readable firmware log messages.

## Important APIs, Types, and Functions

- `TRACE_EVENT(mlx5_fw, ...)` records device name, trace timestamp, lost-event flag, event ID, and decoded message string.
- The generated trace helper is called from `mlx5_tracer_print_trace()`.

## Control Flow

Decoded trace strings are formatted by `fw_tracer.c`, then passed to `trace_mlx5_fw()`. The tracepoint snapshots the dev name and message as dynamic strings and prints them with timestamp/lost/event metadata.

## State and Persistence Behavior

No driver state is mutated. Events are transient tracing output.

## Dependencies and Integration Points

Depends on Linux tracepoints and `fw_tracer.h`. The tracepoint is exported by `fw_tracer.c` for tracing tools.

## Risks and Edge Cases

- The tracepoint assumes `tracer->dev->device` is valid when the event is emitted.
- Message contents are firmware-controlled after validation/formatting in `fw_tracer.c`; tooling should not assume stable wording.

## Test Signals

Enable `events/mlx5/mlx5_fw`, trigger firmware traces, and verify dev name, timestamp, lost flag, event ID, and message formatting.
