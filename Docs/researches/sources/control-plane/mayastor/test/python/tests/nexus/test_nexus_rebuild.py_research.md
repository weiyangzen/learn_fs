# sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_rebuild.py

## Purpose
Tests nexus rebuild behavior in the Python integration suite.

## Important APIs, Types, And Functions
Uses Mayastor handles, pool/replica/nexus fixtures, child add/remove, rebuild state/stat APIs, fio or command helpers, and assertions over child/nexus states.

## Control Flow
The test creates a degraded nexus, adds or replaces a child, starts rebuild or waits for automatic rebuild, polls states/statistics, and verifies the target child returns online or the expected rebuild state is observed.

## State And Persistence
State is remote pools, replicas, nexus children, and rebuild tasks. Cleanup removes children, destroys nexuses/replicas/pools, and disconnects any devices.

## Dependencies And Integration Points
Depends on `tests/nexus/docker-compose.yml`, common Mayastor/NVMe/fio helpers, and legacy protobuf state enums.

## Risks
Rebuild timing is asynchronous and data-size dependent. Polling windows and child ordering assumptions can introduce flakes.

## Test Signals
Passing tests signal that adding/rebuilding children restores mirrored nexus health and exposes correct rebuild progress.
