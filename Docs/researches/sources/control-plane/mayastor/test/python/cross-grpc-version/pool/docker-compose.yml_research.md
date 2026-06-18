# sources/control-plane/mayastor/test/python/cross-grpc-version/pool/docker-compose.yml

## Purpose
Single-node Docker Compose environment for cross-version pool API tests.

## Important APIs, Types, And Functions
Defines service `ms0` at `10.1.0.2`, enabling ANA/reservations and running io-engine with `--env-context=--iova-mode=pa`.

## Control Flow
pytest brings up `ms0`; legacy and v1 fixtures connect to the same service for mixed API operations.

## State And Persistence
Runtime state is in the container, with source tree, `/nix`, hugepages, `/tmp`, and `/var/tmp` mounted from the host.

## Dependencies And Integration Points
Requires host hugepages and Docker capabilities. Used by `test_bdd_pool.py`.

## Risks
Static network and shared host tmp can conflict with concurrent tests. The PA IOVA mode is a test-specific runtime assumption.

## Test Signals
Container readiness indicates both v0 and v1 pool APIs can target the same io-engine instance.
