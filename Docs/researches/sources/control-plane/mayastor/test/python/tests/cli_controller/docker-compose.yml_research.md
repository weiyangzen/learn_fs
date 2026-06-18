# sources/control-plane/mayastor/test/python/tests/cli_controller/docker-compose.yml

## Purpose
Three-node compose topology for testing `io-engine-client` controller list/stat commands.

## Important APIs, Types, And Functions
Defines services `ms1`, `ms2`, and `ms3` with static IPs, ANA/reservations, configurable cores, interrupt/poll/log variables, and KATO on `ms3`.

## Control Flow
Tests create replicas on `ms1`/`ms2` and a nexus on `ms3`, then point the CLI at target URLs.

## State And Persistence
State is transient pools, replicas, nexus, and NVMf controllers created during tests.

## Dependencies And Integration Points
Requires Docker, hugepages, source/Nix mounts, `mayastor_net`, and the built `io-engine-client`.

## Risks
CLI tests fail if binary paths or service names differ. Static IPs can collide with other compose suites.

## Test Signals
Ready services allow CLI controller output to be compared with gRPC-created resources.
