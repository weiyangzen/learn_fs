# sources/control-plane/mayastor/test/python/cross-grpc-version/rebuild/docker-compose.yml

## Purpose
Single-node Docker Compose environment for cross-version rebuild BDD tests.

## Important APIs, Types, And Functions
Defines `ms0` at `10.1.0.2`, with ANA/reservation environment and io-engine cores `1,2`.

## Control Flow
The container runs one io-engine instance; tests create aio-backed nexus children on host-mounted `/tmp` and issue mixed v0/v1 rebuild commands.

## State And Persistence
State resides in the container and host `/tmp` image files created by tests.

## Dependencies And Integration Points
Used by `test_bdd_rebuild.py`, with mounted source tree, `/nix`, hugepages, and relaxed capabilities/seccomp.

## Risks
Shared `/tmp` and static network can interfere with parallel jobs. Rebuild tests need enough time and IO resources for state transitions.

## Test Signals
Container startup enables the same Mayastor instance to expose legacy nexus creation and v1 rebuild operations.
