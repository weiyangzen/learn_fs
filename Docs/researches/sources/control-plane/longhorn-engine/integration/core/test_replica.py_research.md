# sources/control-plane/longhorn-engine/integration/core/test_replica.py

## Purpose
Validates replica gRPC lifecycle and disk-chain behavior: create, open, close, snapshot, disk removal, reload, and rebuilding state transitions.

## Important APIs, Types, and Functions
- Tests: `test_create`, `test_open`, `test_close`, `test_snapshot`, `test_remove_disk`, `test_remove_last_disk`, `test_reload`, `test_reload_simple`, `test_rebuilding`, `test_not_rebuilding`.
- Local `random_str`/`random_num` fixtures.

## Control Flow
Tests call replica client methods directly and assert returned state fields: `state`, `dirty`, `rebuilding`, `size`, `sector_size`, `parent`, `head`, `chain`, disk labels, and remove operation plans.

## State and Persistence Behavior
Creates replica files and metadata, snapshots disks, marks/removes disks, reloads from disk, and toggles rebuilding flags. These tests verify persistence across close/open/reload transitions.

## Dependencies and Integration Points
Uses fixture-provided `grpc_replica_client`, constants, grpc error assertions, and pytest. Exercises server created by `app/cmd/replica.go`.

## Risks and Edge Cases
Exact chain filenames and states are asserted, so changes in naming or state-machine semantics require test updates. Remove-disk tests cover active-head rejection and idempotent missing-disk preparation.

## Test Signals
Directly validates core replica state machine and persisted disk chain semantics used by snapshot, backup, rebuild, and purge flows.
