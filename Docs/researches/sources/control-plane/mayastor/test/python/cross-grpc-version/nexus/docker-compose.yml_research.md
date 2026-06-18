# sources/control-plane/mayastor/test/python/cross-grpc-version/nexus/docker-compose.yml

## Purpose
Docker Compose environment for cross-version nexus tests.

## Important APIs, Types, And Functions
Defines two services, `ms0` and `ms1`, running `${SRCDIR}/${IO_ENGINE_DIR}/io-engine` with static IPs `10.1.0.2` and `10.1.0.3`, ANA and reservation support enabled, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
pytest-docker-compose starts both containers on `mayastor_net`; fixtures map them to legacy and v1 gRPC handles.

## State And Persistence
State is container-local Mayastor runtime plus host-mounted `/tmp` and hugepages. No named volumes are declared.

## Dependencies And Integration Points
Requires Docker, rust image, mounted build tree, `/nix`, hugepages, and seccomp/capability relaxations. Used by cross-version nexus BDD tests.

## Risks
Static IPs and shared network names can conflict with other compose runs. Host `/tmp` sharing means stale test files can affect runs.

## Test Signals
Successful container startup enables v0-created nexus resources to be operated through v1 gRPC.
