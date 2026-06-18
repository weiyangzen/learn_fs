# sources/cloud-native/moby/daemon/stats/collector.go

## Purpose
`collector.go` manages periodic container stats polling and fan-out to subscribers.

## Important APIs, Types, And Functions
`Collector` stores a mutex/condition variable, supervisor, interval, and map from containers to pubsub publishers. Methods include `NewCollector`, `Collect`, `StopCollection`, `Unsubscribe`, and `Run`. `supervisor` requires `GetContainerStats`.

## Control Flow
`Collect` creates or reuses a publisher, broadcasts the condition, and returns a subscription channel. `Run` waits until publishers exist, snapshots container/publisher pairs under lock, unlocks, polls stats for each container, publishes empty stats on error, then sleeps for the configured interval. `Unsubscribe` evicts a channel and removes empty publishers.

## State And Persistence
All state is in-memory subscription/publisher state. No persistent state is written.

## Dependencies And Integration Points
Used by daemon stats APIs through `newStatsCollector`. Depends on Moby `pubsub` and API container stats types.

## Risks
Containers are map keys by pointer, so lifecycle code must pass the same container object. `Run` never exits. Polling is serialized across active containers, so many subscribers/containers can increase interval latency.

## Test Signals
No direct tests here; Docker stats integration tests exercise collector behavior.
