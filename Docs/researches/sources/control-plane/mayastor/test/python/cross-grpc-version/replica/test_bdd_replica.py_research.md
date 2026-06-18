# sources/control-plane/mayastor/test/python/cross-grpc-version/replica/test_bdd_replica.py

## Purpose
BDD compatibility tests for v1 replica operations against legacy-created pools and replicas.

## Important APIs, Types, And Functions
Scenarios cover duplicate name/UUID create failures, list all/by name/by pool, share NVMf, invalid iSCSI share, same/different protocol share, unshare, idempotent unshare, and destroy. Fixtures create a legacy pool, legacy replicas, v1 replicas, `find_replica`, and share protocol mapping.

## Control Flow
The legacy API creates a pool and v0 replicas. v1 replica RPCs then create/list/share/unshare/destroy or intentionally fail, while assertions inspect v1 `ListReplicas` output and gRPC status codes.

## State And Persistence
Fixture dictionaries track current replicas by UUID and clean them up through legacy or v1 APIs. The pool is module-scoped and destroyed after tests.

## Dependencies And Integration Points
Depends on `replica_pb2`, `common_pb2`, legacy `mayastor_pb2`, pytest-bdd feature files, and common/v1 Mayastor fixtures.

## Risks
The suite assumes stable mapping between legacy `ShareProtocolReplica` and v1 `common_pb` share enums. Duplicate resource cleanup can be fragile if a test fails midway.

## Test Signals
Passing scenarios show v1 replica RPCs can discover, share, unshare, reject invalid operations, and destroy legacy replicas.
