# sources/distributed-fs/seaweedfs/weed/filer/posixlock/reassert_test.go

## Purpose

`posixlock/reassert_test.go` tests lock reassertion, the recovery path used when a mount's lock mirror is sent to a fresh or changed owner filer.

## Important APIs, Types, and Functions

The tests use two `Manager` instances as client mirror and owner authority, plus `Track`, `Snapshot`, `Reassert`, `TryLock`, `Renew`, and `ReapExpired`. `maxEnd` aliases `^uint64(0)` for whole-file locks.

## Control Flow

`TestReassertRebuildsOnFreshOwner` tracks locks in a client manager, snapshots them, reasserts them into a fresh owner, and verifies foreign locks now conflict. `TestReassertIdempotent` reasserts the same list repeatedly and expects no state change. `TestReassertReportsConflict` verifies an incumbent lock acquired during a migration gap blocks reassertion. `TestReassertRenewsLease` verifies reassertion refreshes the session lease.

## State and Persistence Behavior

State is in-memory in manager maps. Reassertion rebuilds transient lock state after restart/ownership changes and does not persist to metadata.

## Dependencies and Integration Points

The tests validate mount keepalive/reassertion behavior expected by distributed lock ownership routing. They depend on reflect equality for lock slices and time-based lease reaping.

## Risks and Edge Cases

The tests cover one-key and multi-key snapshot flows but not partial reassert lists, empty lists on existing sessions, or concurrent reassert while other locks churn.

## Test Signals

Key signals are conflict-free rebuild on fresh owner, idempotent repeated reassertion, incumbent lock conflict reporting, and fresh lease preventing immediate reap.
