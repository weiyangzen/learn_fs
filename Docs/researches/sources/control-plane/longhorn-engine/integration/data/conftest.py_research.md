# sources/control-plane/longhorn-engine/integration/data/conftest.py

## Purpose
Defines pytest fixtures for data-path integration tests, including controllers with/without frontends, backing-file replicas, fixed-directory replicas, and shared process-manager clients.

## Important APIs, Types, and Functions
- Controller fixtures: `grpc_controller`, `grpc_controller_no_frontend`, `grpc_controller_device_name_test`, `grpc_backing_controller`.
- Replica fixtures: `grpc_replica1/2`, backing qcow2/raw replicas, fixed-dir replicas, extra replicas.
- Process fixtures: `process_manager_client`, `engine_manager_client`, generator fixtures `grpc_replica_client`, `grpc_controller_client`.
- `first_available_device` fixture and `dev` fixture.

## Control Flow
Generator fixtures create process-manager clients and return closures that start named engine/replica processes. Backing fixtures pass `--backing-file` args. Device-name fixture hard-links `/dev/null` to an available `/dev/sd*` name and removes it after test. `dev` starts a two-replica volume and returns a block device wrapper.

## State and Persistence Behavior
Creates and deletes processes, replica directories, backing-file-based replicas, fixed directories under `/tmp`, Longhorn block devices, and a temporary `/dev/sd*` hard link. Finalizers clean process and replica directory state.

## Dependencies and Integration Points
Depends on `common.core`, constants, generated clients, pytest, `tempfile`, and OS filesystem behavior. Feeds all `integration/data` tests.

## Risks and Edge Cases
Manipulating `/dev/sd*` requires privileged/test-isolated environment and careful cleanup. Fixed directories are shared constants; cleanup finalizers are essential. Fixture closures default mutable `args=[]`, but they do not mutate it directly here.

## Test Signals
Fixture correctness is transitively verified by data tests for frontend, backup, and basic IO behavior.
