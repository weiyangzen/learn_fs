# sources/control-plane/mayastor/test/python/tests/replica_uuid/test_replica_uuid.py

Purpose: legacy/v2 compatibility tests for explicit replica names and UUIDs. It verifies replicas created with the newer API keep distinct name and UUID fields and that replicas created by the older API enumerate correctly through the newer listing API.

Important APIs and control flow: constants define pool, replica names, UUID, and size. A module fixture creates `pool0` with `pool_create` and destroys it best-effort. Steps create a v2 replica via `replica_create_v2(pool, name, uuid, size)`, inspect bdevs for name/UUID/size, enumerate with `replica_list_v2`, and create an old API replica with `replica_create(pool, name, size)`.

State, dependencies, and integration: state includes a malloc pool, replica bdev metadata, and v2 replica list responses. It depends on `common.mayastor` helper methods that are not defined in this file, pytest-bdd, and legacy `mayastor_pb2`.

Risks and test signals: the old API test asserts the returned old replica UUID equals the requested name but later asserts v2 enumeration UUID differs from name, making this an explicit compatibility contract. Cleanup only destroys the pool, relying on pool teardown to remove replicas. Assertions cover bdev metadata, enumeration fields, size, and pool name.
