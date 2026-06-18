# sources/control-plane/csi-lib-utils/slowset/slowset.go

## Purpose

`slowset` implements an in-memory, concurrency-safe set of API object keys that should be retried or synchronized at a slower rate until a retention period expires.

## Important APIs and Flow

`SlowSet` embeds an RWMutex and stores `retentionTime`, `resyncPeriod`, and `workSet map[string]ObjectData`. `ObjectData` records a timestamp and storage class UID. `NewSlowSet` initializes the map and a default 100 ms resync period. `Add` inserts only if absent and returns whether it added. `Get`, `Contains`, `Remove`, and `TimeRemaining` provide map access under locks. `Contains` returns false for expired entries even before cleanup. `removeAllExpired` deletes expired keys. `Run` starts a ticker and repeatedly removes expired entries until `stopCh` closes.

## State, Dependencies, and Integration

All state is process-local memory. There is no persistence. Dependencies are Go `sync` and `time`. The package is intended for controllers or sidecars that need temporary throttling keyed by namespace/name or similar object identifiers.

## Risks and Test Signals

`TimeRemaining` can return a negative duration for expired-but-not-cleaned entries. `Run` depends on callers to provide and close a stop channel. Tests cover idempotent add behavior, expiration, pre-expiration contains, time remaining, and contains behavior for expired entries.
