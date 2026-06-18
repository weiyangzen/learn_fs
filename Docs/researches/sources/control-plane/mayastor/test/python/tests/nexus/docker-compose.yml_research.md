# sources/control-plane/mayastor/test/python/tests/nexus/docker-compose.yml

## Purpose
Four-node compose topology for general nexus integration tests.

## Important APIs, Types, And Functions
Defines `ms0`-`ms3`, static IPs, ANA/reservation env vars, `NEXUS_DONT_READ_LABELS=true` on `ms3`, and source/Nix/hugepages/tmp mounts.

## Control Flow
Tests create pools and replicas on remote nodes and nexuses on `ms0`/`ms3`, then connect kernel or SPDK initiators.

## State And Persistence
State includes pools, replicas, nexuses, NVMf publications, kernel connections, and temporary aio/null devices.

## Dependencies And Integration Points
Used by multiple `tests/nexus/*.py` files. Requires Docker, hugepages, static `mayastor_net`, and local io-engine build.

## Risks
Shared service names and static IPs limit concurrent execution. `NEXUS_DONT_READ_LABELS` is test-specific and can hide label-reading paths.

## Test Signals
Ready services support multi-node nexus data path, fault, shutdown, null-device, and remote-only tests.
