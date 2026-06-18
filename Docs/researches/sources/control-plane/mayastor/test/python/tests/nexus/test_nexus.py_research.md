# sources/control-plane/mayastor/test/python/tests/nexus/test_nexus.py

## Purpose
Core Python integration tests for two-replica nexuses, v2 nexus fields, reservation keys, controller IDs, and failure/degraded behavior under IO.

## Important APIs, Types, And Functions
Fixtures create pools, replicas, v1-style and v2-style nexuses, UUID/name/controller/reservation-key values. Tests cover ENOSPC via `Volume`, killing one or all replica containers during fio/SPDK IO, controller ID support, Dataset Management/Write Zeroes bits, reservation reports, and skipped preempt-key behavior.

## Control Flow
Most tests create pools on `ms1`/`ms2`, create replicas, create/publish nexus on `ms3` or `ms0`, connect kernel NVMe or run SPDK fio, induce container failure, and assert nexus/child states or NVMe metadata.

## State And Persistence
State includes pools, replicas, nexuses, NVMf connections, reservation registrations, fio IO, and Docker container lifecycle. Fixtures destroy resources after each test.

## Dependencies And Integration Points
Depends on common fixtures, `Volume`, `Fio`, `FioSpdk`, NVMe helpers, legacy `mayastor_pb2`, gRPC status codes, and Docker restart/kill behavior.

## Risks
Failure timing and fio completion are race-prone. Reservation/preempt coverage is partly skipped, and assertions depend on kernel NVMe CLI JSON formats and Mayastor state propagation.

## Test Signals
Passing tests show nexus creation/publish, degraded/faulted state transitions, NVMe identify/reservation behavior, and IO continuity/failure behavior across replica failures.
