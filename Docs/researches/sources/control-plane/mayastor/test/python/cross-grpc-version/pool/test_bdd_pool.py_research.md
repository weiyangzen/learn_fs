# sources/control-plane/mayastor/test/python/cross-grpc-version/pool/test_bdd_pool.py

## Purpose
BDD tests for v1 pool operations against pools created by the legacy API.

## Important APIs, Types, And Functions
Scenarios cover duplicate name creation, same-name/different-disk failure, list all, list by name, list non-existent name, and destroy. Fixtures include `create_v0_pool`, `create_v1_pool`, cleanup maps, `find_pool`, and v1 `ListPools` filters.

## Control Flow
A legacy pool is created with malloc disk URIs, v1 pool RPCs are attempted or used to list/destroy, and assertions compare gRPC status codes or list contents.

## State And Persistence
Fixture dictionaries track v0 and v1-created pools for teardown. Pool state itself is remote in `ms0`.

## Dependencies And Integration Points
Depends on `pytest_bdd`, legacy `mayastor_pb2`, v1 `pool_pb2`, common/v1 Mayastor fixtures, and gRPC status codes.

## Risks
Cleanup must reconcile resources created by either API version. Name/disk semantics are tightly coupled to current v1 error mapping.

## Test Signals
Passing tests prove v1 can list and destroy legacy pools and preserves expected conflict behavior.
