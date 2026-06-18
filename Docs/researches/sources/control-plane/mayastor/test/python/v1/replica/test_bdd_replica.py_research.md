# sources/control-plane/mayastor/test/python/v1/replica/test_bdd_replica.py

Purpose: comprehensive v1 pytest-bdd replica behavior tests for create, duplicate name/UUID, destroy error variants, list filtering, share/unshare, and unsupported iSCSI paths.

Important APIs and control flow: fixtures create an LVS pool and expose fixed replica name, UUID, and size. `create_lvs_replica` calls `replica_rpc.CreateReplica`; `find_replica` scans by name and UUID; listing steps use `ListReplicaOptions` by name or pool name. Error steps assert `ALREADY_EXISTS`, `NOT_FOUND`, `FAILED_PRECONDITION`, and `INVALID_ARGUMENT` for unsupported iSCSI or protocol change. Share/unshare calls use `ShareReplica`/`UnshareReplica`.

State, dependencies, and integration: state is the LVS pool, live replicas tracked in `current_replicas`, share state, and list filter responses. It depends on `pool_pb2`, `replica_pb2`, `common_pb2`, `grpc`, pytest-bdd, and v1 fixtures.

Risks and test signals: several then steps are pass-through markers, read/write scenarios are skipped, and duplicate function names for then handlers overwrite Python names though decorators keep registrations. Strong signals include explicit gRPC status codes, list counts by filter, and share enum state.
