# sources/control-plane/mayastor/test/python/cross-grpc-version/replica/docker-compose.yml

## Purpose
Single-node Docker Compose fixture for cross-version replica API tests.

## Important APIs, Types, And Functions
Defines `ms0` at `10.1.0.2`, io-engine cores `0,1`, ANA/reservation env vars, source/Nix/hugepages/tmp mounts, and `mayastor_net`.

## Control Flow
pytest starts one container and both legacy and v1 fixtures connect to it.

## State And Persistence
Replica and pool state is remote in `ms0`; host-mounted `/tmp` is available for tests.

## Dependencies And Integration Points
Used by `test_bdd_replica.py` and requires Docker, hugepages, and the local io-engine build.

## Risks
Static IP/network and host mounts can conflict with concurrent suites. Resource cleanup is delegated to pytest fixtures.

## Test Signals
Readiness means the same io-engine process can serve legacy replica creation and v1 replica operations.
