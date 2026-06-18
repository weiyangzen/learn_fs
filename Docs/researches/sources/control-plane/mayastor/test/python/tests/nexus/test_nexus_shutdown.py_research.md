# sources/control-plane/mayastor/test/python/tests/nexus/test_nexus_shutdown.py

## Purpose
BDD-style tests for the `ShutdownNexus` operation and initiator behavior while a nexus is shut down.

## Important APIs, Types, And Functions
Defines fixtures for published/connected nexus, pools, replicas, and fio workload. Steps verify shutdown state, degraded children, repeated shutdown idempotency, and fio remaining blocked rather than failing.

## Control Flow
The suite creates a two-child nexus, connects it with NVMe, starts fio, issues `nexus_shutdown`, asserts nexus state `NEXUS_SHUTDOWN` and child degraded states, then verifies fio does not exit with IO errors and a second shutdown succeeds.

## State And Persistence
State includes published nexus, kernel NVMe controller, running fio process, pools, replicas, and container resources. Cleanup forcibly deletes NVMe controller and destroys resources.

## Dependencies And Integration Points
Depends on `pytest_bdd`, common NVMe helpers including forced controller deletion, fio, Docker compose fixtures, and legacy Mayastor shutdown RPC.

## Risks
The desired fio behavior is a hang/wait condition, so test timeouts must distinguish success from deadlock. Kernel NVMe controller state may survive failed cleanup.

## Test Signals
Passing scenarios show shutdown is idempotent, visible in gRPC state, and does not cause immediate filesystem/initiator IO failure.
