# sources/control-plane/rook/tests/framework/clients/nfs.go

Purpose: `NFSOperation` wraps creation, deletion, and CSI class setup for Rook CephNFS integration tests.

Important APIs/types/functions: constructor `CreateNFSOperation`; `Create`, `Delete`, `CreateStorageClass`, `CreateSnapshotClass`, and `DeleteSnapshotClass`.

Control flow: `Create` first applies an internal `.nfs` block pool, then applies the `CephNFS` CR, waits for labeled NFS pods, and asserts expected pod count/state. `Delete` removes the `CephNFS` CR, waits for deletion, deletes the `dot-nfs` block pool CR, then waits for pool deletion. Storage and snapshot class methods render manifests and apply/delete them through `ResourceOperation`.

State and persistence behavior: persistent state includes the `.nfs` CephBlockPool, CephNFS CR, NFS daemon pods, and CSI storage/snapshot classes.

Dependencies and integration points: uses installer manifests, Rook typed CephV1 clients, K8s helper waiting primitives, and test assertions.

Risks: `Delete` passes `name` to `WaitForCustomResourceDeletion` for the `dot-nfs` pool checker even though the pool name is `dot-nfs`, which can make logs misleading. Assertions inside `Create` fail tests directly. The generated NFS storage class hard-codes service DNS format and expects the first active daemon service suffix.

Test signals: successful NFS pod readiness, correct daemon count, storage class provisioning, snapshot class lifecycle, and absence of CephNFS/pool CRs after cleanup.
