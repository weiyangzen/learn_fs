# sources/control-plane/mayastor/test/grpc/test_replica.js

## Purpose
Legacy gRPC tests for pool and replica lifecycle behavior. It covers pool creation/list/destroy, replica create/list/share/unshare/stats/destroy, NVMf exported replica datapath reads/writes, data reset after recreation, and optional uring-backed pools.

## Important APIs, Types, And Functions
Important helpers are `createTestDisk`, `destroyTestDisk`, and `ensureNoTestPool`. The suite drives `createPool`, `listPools`, `destroyPool`, `createReplica`, `shareReplica`, `listReplicas`, `statReplicas`, and `destroyReplica`.

## Control Flow
The suite starts Mayastor when no external endpoint is supplied, creates or uses disk devices, creates an aio pool, validates invalid inputs, exercises replica share-state transitions, creates multiple replicas, destroys the pool, then runs optional `uring` tests and an NVMf datapath section using the `initiator` helper to write/read blocks.

## State And Persistence
State includes a loop-backed `/tmp/mayastor_test_disk`, pool metadata, replica bdevs, exported NVMf URI, and temporary `/tmp/test_block` data. The tests clean up the test pool, loop device, block file, and NBD permissions.

## Dependencies And Integration Points
Depends on Node `grpc`, `async`, `chai`, local root access, `losetup`, `truncate`, `initiator`, Mayastor's legacy gRPC service, and `test_common`. It can point at an externally running Mayastor through `MAYASTOR_ENDPOINT` and `MAYASTOR_DISKS`.

## Risks
The suite is environment-sensitive and has legacy duplicated object keys/lines in the source. It assumes specific capacity accounting, share enum strings, 4 MiB clusters, and root device permissions.

## Test Signals
Passing tests signal compatibility of pool/replica CRUD, share idempotency, NVMf URI formatting, basic replica IO, and pool cleanup through the legacy gRPC interface.
