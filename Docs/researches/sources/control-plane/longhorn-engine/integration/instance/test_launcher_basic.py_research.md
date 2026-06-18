# sources/control-plane/longhorn-engine/integration/instance/test_launcher_basic.py

## Purpose
This module validates instance-manager process launch, listing, deletion, error handling, engine/replica wiring, engine upgrade basics, and revision-counter compatibility checks at the process-management layer.

## Important APIs, types, and functions
- Test entry points: `test_start_stop_replicas`, `test_process_creation_failure`, `test_one_volume`, `test_multiple_volumes`, skipped `test_engine_upgrade`, and `test_engine_replica_revision_counter_mismatch`.
- Helper: `engine_replica_mismatch`.
- Uses process helpers from `common.core`: `create_replica_process`, `create_engine_process`, `delete_process`, process/deletion waiters, device existence waiters, `upgrade_engine`, `get_process_address`, `cleanup_process`, and delayed replica client construction.
- Uses `ProcessManagerClient`, `ReplicaClient`, and `ControllerClient` wrappers.
- Constants define process states, base names, binary paths, size strings, and the replica instance manager address.

## Control flow
Replica process tests create ten temporary replica directories, create replica processes, verify each can be fetched and listed, then delete them in order and wait for process disappearance. Failure tests create processes with a nonexistent binary and assert all land in `PROC_STATE_ERROR`.

Volume tests create replica processes, derive `tcp://localhost:<port>` replica URLs from process status, create engine processes, assert frontend devices exist, and then delete engines and replicas while checking process list counts. The multiple-volume test repeats this for five volumes and verifies device deletion after engine removal.

The skipped upgrade test covers a process-manager-level upgrade path using an upgrade binary and old/new replica processes. The active revision-counter mismatch test runs two cases: engine revision counter enabled and disabled. Each case creates two replica processes with opposite revision-counter settings, creates replica data, starts an engine with matching setting, starts a volume with both URLs, and asserts the mismatched replica is `ERR` while the matched replica is `RW`.

## State and persistence behavior
The tests manage process-manager state maps, process specs/statuses, assigned port ranges, frontend device nodes, temporary replica directories, replica-created volume state, and controller replica mode state. Cleanup calls remove engine and replica processes after mismatch scenarios.

## Dependencies and integration points
The module integrates instance-manager process-manager gRPC clients, engine manager and replica manager fixtures, Longhorn process binaries, controller and replica RPC clients, local device path checks, and temporary filesystem directories.

## Risks and edge cases
- Process-list count assertions assume a clean process manager at test start.
- Device existence/deletion waits rely on frontend attach/detach timing.
- The skipped upgrade test is not a live safety net unless unskipped.
- Revision-counter mismatch checks rely on correct pairing between engine flag and replica flag, and clean teardown through `cleanup_process`.
- `test_process_creation_failure` expects process records to remain visible in error state rather than being removed immediately.

## Test signals
Signals include process spec names, `PROC_STATE_RUNNING`/`STOPPING`/`STOPPED`/`ERROR`, list lengths, device node existence/deletion, idempotent engine delete behavior, upgrade process state in skipped coverage, and controller replica modes `RW` versus `ERR` for revision-counter mismatch.
