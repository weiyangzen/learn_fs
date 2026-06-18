<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/events.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/events.go

## Purpose
Provides structured plugin manager events and subscription filtering for create, remove, disable, and enable operations.

## Important APIs, Types, And Functions
`Event` requires `matches`. Event types are `EventCreate`, `EventRemove`, `EventDisable`, and `EventEnable`. `Manager.SubscribeEvents` returns a channel and cancellation function.

## Control Flow
Event matchers compare event type and plugin ID; create events optionally filter by capability interface using OR logic. Subscription builds a pubsub topic function that panics on non-Event payloads and evicts the channel on cancel.

## State, Dependencies, And Integration Points
State lives in the manager's pubsub publisher. Events are published by backend lifecycle methods and consumed by subsystems waiting for plugin availability/removal.

## Risks And Test Signals
Subscribers must call cancel to avoid leaks. The type panic enforces internal publisher discipline. No direct tests in this subset cover event matching.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/events.go -->
