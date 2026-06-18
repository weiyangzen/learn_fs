# sources/cloud-native/moby/daemon/container/view_test.go

## Purpose
Tests the in-memory container view database, name index, health projection, ID-prefix lookup behavior, and benchmark characteristics of prefix lookups at small container counts.

## Important APIs, Types, And Functions
- `newContainer` creates a temporary base container with a UUID ID and root directory.
- `TestViewSaveDelete`, `TestViewAll`, and `TestViewGet` validate basic store/read behavior through `CheckpointTo`.
- `TestNames` verifies name reservation, conflict typing, release/reuse, `GetID`, `GetAllNames`, and cleanup through `Delete`.
- `TestViewWithHealthCheck` checks `Health.Status()` is projected into `Snapshot.Health`.
- `TestTruncIndex` and `assertIndexGet` exercise exact, prefix, ambiguous, missing, and deleted prefix cases.
- `BenchmarkDBAdd100` and `BenchmarkDBGetByPrefix*` measure insert and prefix lookup costs.

## Control Flow
Each test creates a fresh `ViewDB`, writes containers or names, then uses a read `View` to assert snapshot state. The name test deliberately keeps an old read transaction while changing live reservations to prove snapshot isolation. Prefix tests insert overlapping IDs, assert ambiguity for short prefixes, delete one ID, and assert the remaining prefix is unambiguous.

## State And Persistence
State is local to each test's temporary directory and memdb instance. The tests indirectly validate that `CheckpointTo` writes immutable copies into the replica, but no daemon disk checkpoint files are the target of these assertions.

## Dependencies And Integration Points
Uses `gotest.tools`, containerd errdefs predicates, UUIDs, daemon `stringid` helpers for benchmarks, and container checkpoint integration. It is the direct regression suite for `view.go`.

## Risks And Edge Cases
The tests rely on map/slice ordering in expected `GetAllNames` results after deterministic insert order. Benchmarks use random IDs and random prefix lengths, so they are performance signals rather than behavioral gates. The health test only checks status, not failing streak or full health summary projection.

## Test Signals
Failures identify broken transactional isolation, name conflict classification, reservation cleanup, health mapping, or prefix-index semantics. Benchmarks detect gross regressions in add and prefix-resolution cost.
