# sources/control-plane/mayastor/test/python/tests/replica/test_bdd_replica.py

Purpose: legacy pytest-bdd replica coverage for create/destroy/list/stats/share/unshare behavior on a single malloc-backed pool.

Important APIs and control flow: `share_protocol` maps BDD strings to legacy replica share enums. Module fixtures create pool `p0`, define fixed replica UUID and size, and expose `find_replica`, `current_replicas`, and `create_replica`. Steps create unshared or NVMf shared replicas, reject iSCSI sharing, recreate existing replicas, destroy replicas, list replicas, get stats, share with same/different protocols, and unshare by issuing `ShareReplica` with `REPLICA_NONE`.

State, dependencies, and integration: state is pool `p0`, a tracked dict of replicas, live replica bdevs, and share state inside Mayastor. It depends on `mayastor_pb2`, `grpc`, pytest-bdd feature files, and `common.mayastor`.

Risks and test signals: several then steps are no-op markers, and read/write scenarios are skipped with `NotImplementedError` bodies. Duplicate create and missing destroy rely on scenario-level failure behavior except where explicit invalid-argument checks exist. Signals include `find_replica`, list membership by UUID, stats UUID membership, and share enum equality.
