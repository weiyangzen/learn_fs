# sources/cloud-native/moby/daemon/stats.go

## Purpose
`stats.go` implements the high-level `ContainerStats` API and bridges daemon callers to the stats collector.

## Important APIs, Types, And Functions
`ContainerStats` streams or returns stats to a configured output stream. `subscribeToContainerStats` registers a container with the collector. `GetContainerStats` collects one platform-specific sample and augments it with system CPU and network stats.

## Control Flow
For non-streaming requests, stopped/restarting containers return an empty stats object. One-shot returns a single sample. Non-streaming non-one-shot consumes one previous sample so `PreRead`/`PreCPUStats` are populated. Streaming loops over collector updates, encodes JSON without HTML escaping, and exits on context cancellation. `GetContainerStats` calls platform `stats`, then `getSystemCPUUsage`, then network stats on non-Windows unless networking is disabled.

## State And Persistence
No durable state is persisted. The stats collector stores subscriptions; responses reflect runtime/container/network state.

## Dependencies And Integration Points
Integrates daemon container lookup, backend stats config streams, platform stats implementations, collector pubsub, containerd error classifiers, runtime GOOS, and libnetwork stats.

## Risks
First-sample semantics differ between one-shot, streaming, and normal non-streaming modes. Stats collection returns empty data for not-found/conflict to preserve API behavior. Slow clients can block encoding but subscriptions are cleaned up with defer.

## Test Signals
Platform stats tests cover CPU parsing; integration tests cover Docker stats streaming and one-shot behavior.
