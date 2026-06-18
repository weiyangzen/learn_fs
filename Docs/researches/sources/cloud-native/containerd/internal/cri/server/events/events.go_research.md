
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events.go -->
# sources/cloud-native/containerd/internal/cri/server/events/events.go

## Purpose

This package implements a generic containerd event monitor used by the CRI server. It subscribes to containerd events, filters to the Kubernetes containerd namespace, converts protobuf events into concrete Go event types, invokes an injected handler, and retries failed events with per-object exponential backoff.

## Important APIs, Types, and Functions

The public surface is `EventHandler`, `EventMonitor`, `NewEventMonitor`, `(*EventMonitor).Subscribe`, `(*EventMonitor).Start`, `(*EventMonitor).Backoff`, and `(*EventMonitor).Stop`. Internal retry machinery is `backOff`, `backOffQueue`, `convertEvent`, `newBackOff`, `enBackOff`, `deBackOff`, `reBackOff`, `getExpiredIDs`, and `isInBackOff`.

## Control Flow

`Subscribe` stores the event and error channels returned by a containerd `events.Subscriber`. `Start` starts the backoff ticker and a goroutine selecting over event channel, subscription error channel, backoff expiration ticker, and monitor context cancellation. Events outside the Kubernetes namespace are ignored. Supported event payloads are unpacked with `typeurl.UnmarshalAny`; unsupported event types are logged and skipped.

If an event ID is already in backoff, the new event is appended to that ID's queue. Otherwise, the handler is called immediately; failures enqueue the event. When a queue expires, the monitor drains events in order. If any event fails, the remaining suffix is requeued with doubled duration capped at five minutes.

## State and Persistence Behavior

All state is in memory: subscribed channels, cancellation context, backoff queues keyed by container/sandbox/image ID, queue expiration times, and ticker. There is no persistence across process restarts.

## Dependencies and Integration Points

The package depends on containerd event envelopes, CRI namespace constants, containerd API event types, `typeurl`, logging, and `k8s.io/utils/clock` for testable timing. The CRI server injects `criEventHandler` to mutate CRI stores and image metadata.

## Risks and Edge Cases

`Start` assumes event channels are initialized; starting before subscribe is only safe if only backoff events are used. A receive from a closed channel can yield nil values, so subscriber lifecycle behavior matters. Backoff queues are per ID, preventing event reordering for one object but not across objects. Handler failures during a retry requeue only the unprocessed suffix.

## Test Signals

Tests should validate namespace filtering, conversion keys for every supported event type, immediate handling, queueing while in backoff, expiration-based drain, duration doubling and max cap, subscription errors, stop behavior, and nil or unsupported event payloads.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/events/events.go -->
