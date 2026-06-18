# sources/control-plane/mayastor/test/python/tests/nexus_multipath/docker-compose.yml

## Purpose
Four-node compose topology for nexus multipath and reservation-key tests.

## Important APIs, Types, And Functions
Defines `ms0`-`ms3`, static IPs, ANA/reservation support, configurable cores, KATO on `ms3`, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
Tests create replicas on `ms1`/`ms2` and multiple nexuses on `ms0`/`ms1`/`ms2`/`ms3` to form multiple paths to one namespace.

## State And Persistence
State includes pools, replicas, multiple published nexuses, kernel multipath controllers, and reservation registrations.

## Dependencies And Integration Points
Used by both imperative and BDD multipath test files. Requires Linux NVMe multipath behavior and Docker network stability.

## Risks
Static network/IPs and host kernel multipath state can conflict across parallel tests. KATO/path-state timing can vary.

## Test Signals
Ready topology supports path count, path state, failover, and reservation key validation.
