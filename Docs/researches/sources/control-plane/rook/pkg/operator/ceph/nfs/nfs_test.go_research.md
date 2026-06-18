<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs_test.go -->
# sources/control-plane/rook/pkg/operator/ceph/nfs/nfs_test.go

## Purpose
This file tests lower-level NFS daemon lifecycle helpers, particularly config map hashing, multi-instance resource creation, and skip-reconcile handling.

## Important APIs and control flow
`TestReconcileCephNFS_createConfigMap` verifies repeated generation gives stable hashes, different daemon IDs produce different hashes, and different NFS names/configs produce different hashes. `TestReconcileCephNFS_upCephNFS` calls `upCephNFS` for two active servers and verifies two Deployments and Services with config-hash annotations. `TestUpCephNFS_SkipsReconcile` verifies a daemon deployment labeled with `ceph.rook.io/do-not-reconcile` is skipped. `TestUpCephNFS_SkipReconcileFails` verifies list failures from the Kubernetes clientset surface as errors.

## State and persistence
The tests use fake Kubernetes clientsets and fake controller-runtime clients. Created Deployments, Services, and ConfigMaps are in-memory only. Ceph auth is mocked through `exectest.MockExecutor`.

## Dependencies and integration points
The tests depend on Rook scheme, fake Kubernetes reactors, Rook config labels, Ceph version fixtures, and executor mocks. They validate integration among generated ConfigMaps, Deployment annotations, Services, and skip-reconcile label discovery.

## Risks and test signals
The tests do not exercise RADOS config object creation, Kerberos config mutation, grace database calls, or deployment update fallback in depth. They are good regression signals for deterministic config hashes and basic resource fan-out.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nfs/nfs_test.go -->
