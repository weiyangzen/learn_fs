# sources/cloud-native/moby/daemon/stats_collector.go

## Purpose
`stats_collector.go` constructs and starts the daemon's stats collector.

## Important APIs, Types, And Functions
`newStatsCollector` reads machine memory on Linux, stores it in `daemon.machineMemory`, creates a `stats.Collector`, starts `Run` in a goroutine, and returns it.

## Control Flow
On Linux, meminfo is read best-effort and ignored on error. The collector starts immediately and waits until subscriptions exist.

## State And Persistence
Updates in-memory `daemon.machineMemory`; starts a long-lived goroutine. No durable state is persisted.

## Dependencies And Integration Points
Integrates the daemon with `daemon/stats.Collector` and `pkg/meminfo`.

## Risks
The collector goroutine has no stop path in this file. Incorrect machine memory affects reported memory limit clamping.

## Test Signals
Stats integration tests indirectly validate collector startup and memory limit reporting.
