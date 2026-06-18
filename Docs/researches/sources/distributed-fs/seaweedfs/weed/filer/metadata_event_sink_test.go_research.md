# sources/distributed-fs/seaweedfs/weed/filer/metadata_event_sink_test.go

## Purpose

`metadata_event_sink_test.go` verifies that `Filer.NotifyUpdateEvent` records a request metadata event into a context-attached `MetadataEventSink`.

## Important APIs, Types, and Functions

The test uses `WithMetadataEventSink`, constructs a minimal `Filer` with signature and local log buffer, calls `NotifyUpdateEvent`, and inspects `sink.Last()`.

## Control Flow

The test creates a delete-like event for `/dir/file.txt`, then asserts the sink captured an event with directory `/dir`, old entry name `file.txt`, signatures containing the caller-provided signature and filer signature, and a non-zero timestamp.

## State and Persistence Behavior

The log buffer is in-memory and configured with a no-op flush callback. The captured sink event is request-local; no store writes are involved.

## Dependencies and Integration Points

The test depends on `log_buffer.NewLogBuffer`, SeaweedFS path utilities, and `Filer.NotifyUpdateEvent`. It validates the integration between event emission and the sink helper.

## Risks and Edge Cases

The test covers one old-entry event shape, not create/update, multiple events, nil sink, or suppression context interactions. Signature order is asserted and could break if notify semantics intentionally change.

## Test Signals

The key signals are non-nil captured event, correct directory/name, signature propagation, and non-zero event timestamp.
