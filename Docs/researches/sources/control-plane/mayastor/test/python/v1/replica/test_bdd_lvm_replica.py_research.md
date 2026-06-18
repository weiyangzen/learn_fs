# sources/control-plane/mayastor/test/python/v1/replica/test_bdd_lvm_replica.py

Purpose: v1 pytest-bdd tests for replicas backed by LVM pools and mixed listing of LVM/LVS replicas.

Important APIs and control flow: fixtures create replicas through `replica_rpc.CreateReplica`, find replicas with `ListReplicaOptions(pooltypes=[...])`, create pools with explicit pooltype, and provision/reuse an LVM VG `lvmpool` using loop setup and LVM commands. Scenarios create an LVM pool from a VG, create an LVM-backed replica using the VG UUID as pool UUID, destroy it, create an LVS pool with a replica, and list both pool types. Then steps assert LVM replica existence/removal and pooltype/size fields.

State, dependencies, and integration: state includes loop device, VG UUID, LVM and LVS pools, and replica records. It depends on `nix-sudo`, LVM tools, loop devices, pool/replica/common protobufs, and v1 fixtures.

Risks and test signals: `find_replica` returns `None` after inspecting the first non-matching replica, which can miss later matches. `create_replica` ignores its `pooltype` argument. Cleanup catches broad exceptions. Signals still cover basic LVM-backed creation/destruction and list metadata.
