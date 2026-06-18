# sources/control-plane/longhorn-engine/integration/core/conftest.py

## Purpose
Defines pytest fixtures for core integration tests: process-manager clients, default controller client, and default replica clients.

## Important APIs, Types, and Functions
- `process_manager_client`, `engine_manager_client`.
- `grpc_controller_client`.
- `grpc_replica_client`, `grpc_replica_client2`.

## Control Flow
Fixtures create process-manager clients with cleanup finalizers. Controller fixture starts an engine process, constructs a `ControllerClient`, and waits for version detail. Replica fixtures start replica processes, construct `ReplicaClient`, and clean them to initial state.

## State and Persistence Behavior
Creates and deletes engine/replica processes through instance managers and initializes replica directories. Cleanup is finalizer-driven.

## Dependencies and Integration Points
Depends on `common.core` process creation/cleanup helpers, constants, generated clients, and pytest. Used by core tests.

## Risks and Edge Cases
Fixture cleanup depends on process-manager reliability. Default fixture names and ports are shared, so tests rely on cleanup isolation and `TESTPREFIX`.

## Test Signals
All `integration/core` tests use these fixtures; fixture failures block test collection/execution.
