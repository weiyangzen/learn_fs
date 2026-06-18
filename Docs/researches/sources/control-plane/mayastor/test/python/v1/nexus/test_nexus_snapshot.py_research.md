# sources/control-plane/mayastor/test/python/v1/nexus/test_nexus_snapshot.py

Purpose: pytest-bdd scenario for creating a nexus snapshot while a published one-replica nexus is under active fio I/O.

Important APIs and control flow: fixtures disconnect stale NVMe sessions, create pools on `ms1` and `ms2`, create one replica on `ms1`, create and publish a nexus on `ms3`, connect the nexus with NVMe, and start fio with `subprocess.Popen`. The snapshot step calls `mayastor_mod["ms3"].nexus_create_snapshot` with entity ID, transaction ID, snapshot name, and replica-to-snapshot UUID descriptors. Then steps validate `replicas_done`, no skipped replicas, snapshot fields from `ms1.list_snapshots()`, and fio exit status.

State, dependencies, and integration: state includes pool/replica/nexus objects, an NVMe host connection, a live fio process, and snapshot metadata. It depends on snapshot, pool, replica, common, and nexus protobufs plus `common.nvme` and `common.fio`.

Risks and test signals: `create_nexus_1` destroys by name through a method expecting UUID, but the primary fixture used for connection returns without teardown. Fio cleanup waits after the snapshot. Signals cover snapshot status fan-out, stored metadata, and no I/O errors.
