# sources/control-plane/mayastor/test/python/tests/publish/docker-compose.yml

## Purpose
Two-node compose topology for BDD nexus publish/lifecycle tests.

## Important APIs, Types, And Functions
Defines `ms0` and `ms1` with ANA/reservation support, configurable cores, interrupt/poll/log variables, static IPs, and shared source/Nix/hugepages/tmp mounts.

## Control Flow
Tests create local and remote bdevs, create nexuses, and exercise publish/unpublish operations on these two nodes.

## State And Persistence
State is transient bdevs, local files, shared NVMf URI, nexuses, and published device URIs.

## Dependencies And Integration Points
Used by `tests/publish/test_bdd_nexus.py`; requires Docker, hugepages, and local io-engine build.

## Risks
Only two nodes are available, so broader multipath behavior is outside this fixture. Static IP/network conflicts are possible.

## Test Signals
Ready services enable BDD lifecycle coverage for nexus creation, child validation, publish protocol rules, and cleanup.
