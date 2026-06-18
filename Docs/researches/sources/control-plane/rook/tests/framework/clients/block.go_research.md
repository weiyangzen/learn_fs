# sources/control-plane/rook/tests/framework/clients/block.go

Purpose: `BlockOperation` is the integration-test wrapper for Rook/Ceph block storage operations. It creates block pools, storage classes, PVCs, pods, snapshots, restores, clones, and lists or deletes RBD images through Ceph clients.

Important APIs/types/functions: `BlockOperation` stores a `*utils.K8sHelper` and `installer.CephManifests`. `BlockImage` is a test DTO for image name, pool, size, device, and mount point. Key methods include `Create`, `CreatePoolAndStorageClass`, `CreatePVC`, `CreatePod`, snapshot class/snapshot helpers, `ListAllImages`, `ListImagesInPool`, and `DeleteBlockImage`.

Control flow: most mutating methods render YAML through `installer` manifest helpers and call `K8sHelper.ResourceOperation` or `KubectlWithStdin`. Listing methods use `client.ListPoolSummaries` followed by `client.ListImagesInPool` per pool. Deletion paths use typed Kubernetes clients for PVCs/storage classes and Ceph client calls for RBD images.

State and persistence behavior: Kubernetes resources and Ceph RBD images are persistent external state. The wrapper itself holds no durable state.

Dependencies and integration points: depends on Rook Ceph client APIs, test manifests, Kubernetes storage APIs, and the shared test logger from `object.go`.

Risks: several parameters are unused (`size`, `csi`, `namespace` in some methods), which can mislead callers. Delete helpers differ in not-found handling: storage class deletion ignores not found, PVC deletion does not. Raw Ceph image deletion bypasses Kubernetes ownership and can be destructive if pool/image names are wrong.

Test signals: strong signals are PVC bound/deleted checks, pod mount read/write checks, snapshot ready/restore behavior, and post-cleanup RBD image enumeration.
