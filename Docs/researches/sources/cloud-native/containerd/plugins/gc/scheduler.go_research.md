# sources/cloud-native/containerd/plugins/gc/scheduler.go

## Purpose
Registers and implements the metadata garbage collection scheduler. It turns metadata mutations, deletion counts, startup delay, manual triggers, and pause-threshold heuristics into calls to the metadata collector.

## Important APIs, Types, And Functions
`config` exposes pause, deletion, mutation, schedule, and startup delays. `collector` abstracts metadata GC. `gcScheduler` owns event channel, waiter list, thresholds, and run loop. `ScheduleAndWait`, `wait`, `mutationCallback`, `schedule`, and `run` are the core methods.

## Control Flow
Startup validates/clamps config, registers a mutation callback, exports effective config, and starts `run`. The run loop optionally schedules startup GC, accepts mutation/manual events, counts dirty deletions and mutations, schedules collections when thresholds are met, skips unneeded scheduled runs, runs `GarbageCollect`, notifies waiters, updates metrics, and recalculates the next interval from average GC duration and pause threshold.

## State And Persistence
Scheduler state is in-memory: counters, average GC timing, waiters, and next collection time. Actual persistence cleanup is delegated to metadata DB garbage collection.

## Dependencies And Integration Points
Requires metadata plugin implementing `collector`, uses `pkg/gc.Stats`, `tomlext.Duration`, plugin exports, logging, and metrics from `metrics.go`. Lease and image services use `ScheduleAndWait` for synchronous deletes.

## Risks
Events are sent from goroutines into an unbuffered channel; if the run loop is blocked in GC, senders can accumulate. GC failure closes all waiters and reschedules. Pause threshold is clamped to avoid overscheduling, but very small GC durations are floored to 5ms.

## Test Signals
`scheduler_test.go` covers pause threshold limiting, deletion threshold triggering, manual trigger wait, and startup delay behavior.
