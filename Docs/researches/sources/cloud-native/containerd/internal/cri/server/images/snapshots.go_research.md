
<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/snapshots.go -->
# sources/cloud-native/containerd/internal/cri/server/images/snapshots.go

## Purpose

This file implements a background snapshot usage syncer that periodically caches snapshot size and inode usage for imagefs and container stats consumers.

## Important APIs, Types, and Functions

The main type is `snapshotsSyncer` with constructor `newSnapshotsSyncer`, methods `start` and `sync`, and helper `calculateEMA`.

## Control Flow

`start` launches a goroutine that repeatedly calls `sync`, logs errors, measures cycle cost, computes a smoothed target sleep with an exponential moving average, enforces a minimum sleep of half the configured period, and sleeps before the next cycle. `sync` uses a namespaced context, records a start timestamp, walks each configured snapshotter to collect snapshot infos, queries usage outside the walk callback, updates existing non-active snapshot timestamps cheaply, fetches usage for new or active snapshots, stores size/inode data, and deletes cached snapshots not updated during the cycle.

## State and Persistence Behavior

The syncer maintains an in-memory `snapshotstore.Store`. It reads live snapshotter metadata and usage, but it does not write containerd snapshot metadata. Stale cache entries are deleted when not observed in the latest sync.

## Dependencies and Integration Points

Dependencies include containerd snapshotter APIs, CRI snapshot store, CRI namespaced context utility, errdefs, and logging. It is started by `NewService` and feeds `ImageFsInfo` plus any stats code reading the snapshot store.

## Risks and Edge Cases

The goroutine has no stop mechanism and can continue until process exit. Usage calls can be expensive and have TODOs for timeouts. Non-active snapshots reuse previous size/inode values and only refresh timestamps, so long-lived committed snapshot usage changes may not be detected. If sync takes longer than the period, minimum sleep still releases CPU but effective frequency drops.

## Test Signals

Useful tests would cover EMA sleep calculation, snapshot walk failure, usage failure and `NotFound` handling, active snapshot usage refresh, non-active timestamp-only update, stale cache deletion, and multiple snapshotter keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/server/images/snapshots.go -->
