# sources/cloud-native/containerd/plugins/services/warning/service.go

## Purpose
This file implements the warning service used to collect last-seen deprecation warnings.

## Important APIs, Types, And Functions
`Service` exposes `Emit` and `Warnings`. The plugin type is `plugins.WarningPlugin`, ID `plugins.DeprecationsPlugin`. `Warning` includes ID, last occurrence time, and message. The private `service` stores a map from `deprecation.Warning` to `time.Time` guarded by an RW mutex.

## Control Flow
`Emit` validates warning IDs, logs invalid IDs, and records `time.Now()` for valid warnings. `Warnings` snapshots the map into a slice and resolves messages through the deprecation package, skipping unknown messages.

## State And Persistence
Warnings are in-memory only and reset on daemon restart. Only the most recent occurrence per warning ID is stored.

## Dependencies And Integration Points
The task service emits deprecated runc option warnings through this service. It depends on `pkg/deprecation`, logging, plugin registration, and synchronization primitives.

## Risks
There is no persistence, count, or ordering guarantee in the returned slice. Time uses wall clock, so clock jumps affect last occurrence values.

## Test Signals
No direct tests are in this subset. Task creation paths that consume deprecated options provide indirect coverage.
