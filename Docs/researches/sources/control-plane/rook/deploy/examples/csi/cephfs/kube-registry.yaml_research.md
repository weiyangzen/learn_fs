<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/kube-registry.yaml -->
# sources/control-plane/rook/deploy/examples/csi/cephfs/kube-registry.yaml

Purpose: deploys a three-replica Docker registry backed by a shared CephFS PVC in `kube-system`.
Important APIs/types/functions: `PersistentVolumeClaim` named `cephfs-pvc`, `Deployment` `kube-registry`, `registry:2`, `REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY`, HTTP probes, and PVC volume mount `image-store`.
Control flow: Kubernetes binds the RWX PVC through `rook-cephfs`; registry pods mount it at `/var/lib/registry`, expose port 5000, and probes hit `/` on the registry port. State and persistence are container image blobs persisted on CephFS; Deployment replica state is Kubernetes-managed. Dependencies are the CephFS StorageClass, registry image, kube-system placement, and a CephFS volume that supports shared writes. Risks: sample HTTP secret is insecure, registry filesystem backend concurrency requires correct shared storage semantics, no Service is included, and namespace differs from other examples. Test signals: PVC bound, three pods ready, liveness/readiness pass, and pushing/pulling images works across pod restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/examples/csi/cephfs/kube-registry.yaml -->
