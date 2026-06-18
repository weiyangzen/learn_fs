## sources/control-plane/csi-driver-nfs/deploy/v4.3.0/csi-snapshot-controller.yaml

Purpose: Deploys the external snapshot-controller v6.2.2 as a two-replica control-plane Deployment in `kube-system`. It reconciles the Kubernetes `VolumeSnapshot` and `VolumeSnapshotContent` API objects defined by the snapshot CRDs.

Important APIs and types: The Deployment has `replicas: 2`, selector/label `app: snapshot-controller`, `minReadySeconds: 15`, rolling strategy `maxSurge: 0` and `maxUnavailable: 1`, ServiceAccount `snapshot-controller`, Linux node selector, `system-cluster-critical` priority, `RuntimeDefault` seccomp, and control-plane tolerations. The container runs `registry.k8s.io/sig-storage/snapshot-controller:v6.2.2` with `--v=2`, `--leader-election=true`, and `--leader-election-namespace=kube-system`, with memory limit 100Mi and tiny CPU/memory requests.

Control flow: Both replicas start, but leader election makes one active reconciler. The controller watches snapshot CRDs, PVCs, PVs, and classes; it creates/binds content objects, updates status, and coordinates with CSI snapshotter sidecars. `minReadySeconds` is set to exceed the startup failure window when v1 CRDs are absent.

State and persistence behavior: Snapshot API state persists in etcd; leader-election state persists as Leases in `kube-system`. The Deployment has no local persistent storage. Rolling update settings keep at most one unavailable replica and avoid surge.

Dependencies and integration points: Requires snapshot CRDs and `rbac-snapshot-controller.yaml`. It works with the NFS controller's `csi-snapshotter` sidecar and `snapshotclass.yaml` to complete CSI snapshot lifecycle. It is intentionally separate from the CSI driver controller deployment.

Risks: If CRDs are missing, the controller will not become ready or will exit. Memory limit 100Mi may be tight in large clusters. Leader-election namespace is hard-coded to `kube-system`; moving the deployment needs RBAC/arg changes. Tolerations use `Equal value true` for control-plane taints, which may not match all taint forms.

Test signals: Confirm two replicas with one lease holder, readiness after CRDs are installed, successful VolumeSnapshot create/delete reconciliation, and status updates. Test CRD absence during startup and rolling updates with no control-plane outage.
