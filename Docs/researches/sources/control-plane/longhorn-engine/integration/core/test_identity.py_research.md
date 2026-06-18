# sources/control-plane/longhorn-engine/integration/core/test_identity.py

## Purpose
Validates identity metadata enforcement for controller, replica, sync-agent, and CLI operations.

## Important APIs, Types, and Functions
- `test_validation_fails_with_client`.
- `test_validation_fails_with_cli`.
- Uses controller, replica, sync-agent clients and Longhorn CLI subprocesses.

## Control Flow
The client test starts an engine and replica with expected identities, then constructs clients with wrong volume or instance names and asserts `FAILED_PRECONDITION`. It also tests a correct engine/sync-agent trying to communicate with a replica created for a different volume. The CLI test performs analogous checks through `longhorn --volume-name/--engine-instance-name` and `add-replica`.

## State and Persistence Behavior
Creates multiple engine/replica processes with distinct volume and instance identities. Mutates controller replica membership in the setup path. No persistent data validation beyond process state.

## Dependencies and Integration Points
Uses `common.core` process helpers, generated clients, sync-agent client, CLI binary fixture from `core.test_cli`, and gRPC status codes. Directly validates metadata added by Go and Python interceptors.

## Risks and Edge Cases
Asserts exact stderr/details fragments, so error wording changes are breaking. Relies on sync-agent address derivation from replica process port layout.

## Test Signals
Strong security/identity signal that wrong volume or instance metadata prevents cross-volume/cross-instance RPCs and CLI operations.
