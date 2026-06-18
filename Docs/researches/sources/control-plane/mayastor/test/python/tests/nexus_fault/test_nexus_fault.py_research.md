# sources/control-plane/mayastor/test/python/tests/nexus_fault/test_nexus_fault.py

## Purpose
BDD tests ensuring a temporary nexus fault or path replacement does not cause the initiator filesystem workload to fail.

## Important APIs, Types, And Functions
Scenarios cover remote Mayastor restart and recreating/replacing a faulted nexus. Fixtures create pool/replica/nexus, publish NVMf, connect kernel NVMe, mount ext4, run fio, republish on same or alternate node, find controllers, and check remote readiness.

## Control Flow
The test creates a single-replica remote nexus, connects and mounts it, starts fio on a file, restarts or recreates the remote backing resources, optionally connects a replacement nexus and disconnects the old controller, then waits for fio and verifies the filesystem is still mounted.

## State And Persistence
State includes aio backing files, pool, replica, nexus, kernel NVMe controller, mounted filesystem, and a running fio process. Cleanup unmounts, disconnects, and destroys/recreates Mayastor resources.

## Dependencies And Integration Points
Depends on pytest-bdd, retrying, `nix-sudo` mount/mkfs commands, fio, NVMe helper functions, Docker restart, and v2 nexus creation.

## Risks
Filesystem and NVMe recovery timing is highly environment-dependent. Reusing the same replica UUID during recreate paths requires careful teardown.

## Test Signals
fio exit code zero and a still-mounted filesystem are the primary evidence that temporary nexus fault/replacement did not surface as application IO failure.
