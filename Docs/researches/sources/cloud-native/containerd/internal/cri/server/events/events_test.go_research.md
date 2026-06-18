
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events_test.go -->
# sources/cloud-native/containerd/internal/cri/server/events/events_test.go

## Purpose

This test file covers the generic event monitor backoff queue behavior and verifies that a monitor can handle pre-enqueued backoff events without a real subscriber.

## Important APIs, Types, and Functions

It defines `noopEventHandler` with `HandleEvent`, `TestEventMonitor_SubscribeNothing`, and `TestBackOff`. The tests use `eventtypes.TaskOOM`, `typeurl.MarshalAny`, `convertEvent`, fake clocks, and protobuf comparison helpers.

## Control Flow

`TestEventMonitor_SubscribeNothing` creates a monitor, starts it without subscribing to containerd, manually enqueues a TaskOOM event into backoff, waits for it to be delivered to the noop handler, stops the monitor, and expects a clean error-channel close. `TestBackOff` uses a fake clock to enqueue two queues, assert their initial state, verify `isInBackOff`, advance time, drain expired queues, prove second drain is nil, and verify `reBackOff` doubles duration and keeps only a suffix.

## State and Persistence Behavior

The tests manipulate only in-memory monitor state. Fake clock control makes backoff expiration deterministic. No containerd event stream, CRI store, or filesystem state is used.

## Dependencies and Integration Points

Dependencies include containerd API event types, `typeurl`, `prototestutil.Compare`, `go-cmp`, `testify/assert`, and `testingclock`. The tests protect behavior used by `criService` event handling but do not exercise the CRI-specific handler.

## Risks and Edge Cases

`TestEventMonitor_SubscribeNothing` has long timeout ceilings and depends on the real backoff ticker interval. The tests do not cover subscriber errors, namespace filtering, unsupported events, or handler failures during drain.

## Test Signals

Passing tests show that backoff queues preserve event contents, report membership correctly, expire based on the configured clock, can be drained once, and can be requeued with doubled duration after partial failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events_test.go -->
