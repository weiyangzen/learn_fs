# sources/control-plane/mayastor/test/python/tests/nexus_multipath/test_bdd_nexus_multipath.py

## Purpose
BDD tests for ANA NVMe multipath behavior and replacing a failed IO path on demand.

## Important APIs, Types, And Functions
Fixtures create two-replica nexuses, a second nexus over the same replicas, one-replica connected/disconnected nexuses, pools, replicas, controller IDs, and reservation keys. Steps connect clients, verify path states, run fio, degrade a path, add a second path, remove the failed path, and wait for fio completion.

## Control Flow
The first scenario connects two controllers to one namespace, starts fio, and checks IO statistics route through the active nexus. The second scenario starts fio through one path, restarts the serving container to degrade it, connects another nexus as replacement, removes the broken controller, and verifies fio finishes.

## State And Persistence
State includes pools/replicas, multiple v2 nexuses, kernel NVMe controllers, fio processes, and path states. Setup/teardown disconnects all NVMe controllers around the module.

## Dependencies And Integration Points
Depends on pytest-bdd feature files, common Mayastor/NVMe/fio helpers, Docker container restarts, legacy protobuf enums, and Linux multipath sysfs/CLI output.

## Risks
Path states such as `live` and `connecting` are timing-sensitive. The IO stats assertion assumes specific controller selection and may vary with ANA/path policy changes.

## Test Signals
Passing scenarios show multipath namespace merging, IO path preference, live replacement of failed paths, and fio continuity.
