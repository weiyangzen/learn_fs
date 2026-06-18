# sources/control-plane/longhorn-engine/integration/core/test_controller.py

## Purpose
Validates controller gRPC operations for replica lifecycle, volume start/shutdown, and expansion using file backends.

## Important APIs, Types, and Functions
- Tests: `test_replica_list`, `test_replica_create`, `test_replica_delete`, `test_replica_change`, `test_start`, `test_shutdown`, `test_controller_expand`.

## Control Flow
Tests create temporary backend files, call controller client methods directly, assert replica list/mode counts, start volumes with file backends, expand with frontend helper, and verify backend file sizes.

## State and Persistence Behavior
Creates local sparse backend files, mutates controller replica membership/modes, starts/shuts down volume state, expands file sizes, and removes backend files during cleanup.

## Dependencies and Integration Points
Uses `common.core` backend-file helpers and expansion helpers, constants for sizes, generated `ControllerClient`, grpc, and pytest.

## Risks and Edge Cases
Relies on controller accepting only one WO replica at a time, idempotent duplicate create/delete semantics, and filesystem truncation behavior. Cleanup must remove temp backend files even after assertion failures through test framework behavior.

## Test Signals
Direct gRPC-level signal for controller APIs underlying `rm-replica`, `update-replica`, `expand`, and startup flows.
