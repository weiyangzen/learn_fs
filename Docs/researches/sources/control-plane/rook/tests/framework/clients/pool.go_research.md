# sources/control-plane/rook/tests/framework/clients/pool.go

Purpose: `PoolOperation` wraps CephBlockPool CR lifecycle, Ceph pool inspection, and pool deletion with RBD image cleanup.

Important APIs/types/functions: constructor `CreatePoolOperation`; `Create`, `Update`, internal `createOrUpdatePool`; inspection methods `ListCephPools`, `GetCephPoolDetails`, `ListPoolCRDs`, `PoolCRDExists`, `CephPoolExists`; cleanup method `DeletePool`.

Control flow: create/update apply a rendered block pool manifest. Ceph inspection uses `client.ListPoolSummaries` and `client.GetPoolDetails` against the admin test cluster. CR inspection uses the Rook typed client. `DeletePool` lists images in the pool, force-deletes each image with retry, deletes the pool CR, and waits for custom resource deletion.

State and persistence behavior: persistent state includes CephBlockPool CRs, Ceph pools, and RBD images. The wrapper keeps no local durable state.

Dependencies and integration points: integrates with `BlockOperation`, Rook Ceph client APIs, Kubernetes CephV1 clientset, and manifest generation.

Risks: `DeletePool` ignores the error returned by `ListImagesInPool`, potentially proceeding to delete the pool despite failing to enumerate images. The deletion retry logs the whole `BlockImage` with `%q`, which may be noisy. Ceph and CR existence checks can diverge during reconciliation and require caller-side waiting.

Test signals: pool CR existence, Ceph pool summary/details, RBD image cleanup, and custom resource deletion completion are primary validation points.
