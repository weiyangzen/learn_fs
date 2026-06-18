# sources/control-plane/mayastor/test/python/tests/nexus_fault/docker-compose.yml

## Purpose
Two-node compose topology for nexus fault and replacement tests.

## Important APIs, Types, And Functions
Defines `ms0` and `ms1` with ANA/reservation support, configurable cores, interrupt/poll/log variables, static IPs `10.1.0.2` and `10.1.0.3`, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
Tests use one node as local nexus and one as remote replica, then restart/recreate resources to force fault handling.

## State And Persistence
State is transient pools, replicas, nexuses, kernel NVMe controllers, mounted filesystems, and host `/tmp` backing files.

## Dependencies And Integration Points
Used by `test_nexus_fault.py`. Requires Docker, hugepages, capabilities, and local fio/NVMe tooling on the host.

## Risks
Container restart timing and KATO/fault detection can vary by host load.

## Test Signals
Ready topology enables filesystem-over-NVMe tests during temporary nexus faults and path replacement.
