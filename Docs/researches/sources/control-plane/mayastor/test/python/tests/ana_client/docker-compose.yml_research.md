# sources/control-plane/mayastor/test/python/tests/ana_client/docker-compose.yml

## Purpose
Four-node compose topology for ANA/multipath client behavior tests.

## Important APIs, Types, And Functions
Defines `ms0`-`ms3` with static IPs `10.1.0.2`-`10.1.0.5`, ANA/reservations enabled, configurable cores, interrupt/poll/log environment, and `NVME_KATO_MS=1000` on `ms3`.

## Control Flow
pytest starts all services; tests create replicas/nexuses across nodes and connect kernel NVMe paths.

## State And Persistence
State is container runtime, Mayastor pools/replicas/nexuses, and host kernel NVMe connections.

## Dependencies And Integration Points
Requires Docker, hugepages, capabilities, source/Nix mounts, and static `mayastor_net`. Used by `test_ana_client.py`.

## Risks
Multipath tests are sensitive to kernel NVMe behavior, KATO timing, and concurrent use of the static network.

## Test Signals
Ready topology supports ANA path and namespace GUID validation across multiple Mayastor nodes.
