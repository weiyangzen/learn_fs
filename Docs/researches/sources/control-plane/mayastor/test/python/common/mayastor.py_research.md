# sources/control-plane/mayastor/test/python/common/mayastor.py

## Purpose
Reusable pytest fixtures for Docker Compose based Mayastor integration tests.

## Important APIs, Types, And Functions
Exports `check_size`, function-scoped fixtures `containers`, `mayastors`, `create_temp_files`, and module-scoped fixtures `container_mod`, `mayastor_mod`.

## Control Flow
Container fixtures enumerate `docker_project.compose.ps()` and map names to container objects. Mayastor fixtures turn container IPs on `mayastor_net` into `MayastorHandle` instances. `create_temp_files` removes and recreates `/tmp/<container>.img` files.

## State And Persistence
State is fixture-scoped dictionaries of Docker containers and gRPC handles plus temporary host image files. The fixtures do not commit any state; test cases create and destroy remote Mayastor resources.

## Dependencies And Integration Points
Depends on `pytest`, pytest-docker-compose, `MayastorHandle`, and `run_cmd`. It binds compose service names such as `ms0`-`ms3` to test code.

## Risks
Fixture correctness depends on compose network names and static service naming. `check_size` subtracts current from previous pool usage, so callers must pass snapshots in the expected order.

## Test Signals
Most Python test failures begin here when containers are not reachable, gRPC readiness fails, or temporary backing files cannot be prepared.
