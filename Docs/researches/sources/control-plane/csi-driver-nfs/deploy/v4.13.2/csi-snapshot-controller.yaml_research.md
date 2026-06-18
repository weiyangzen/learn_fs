## sources/control-plane/csi-driver-nfs/deploy/v4.13.2/csi-snapshot-controller.yaml

Purpose: Deploys the external snapshot-controller v8.4.0 as a two-replica control-plane Deployment in `kube-system`. It reconciles CSI snapshot custom resources independently of the NFS CSI controller pod.

Important APIs and types: The Deployment uses `replicas: 2`, label `app: snapshot-controller`, `minReadySeconds: 15`, rolling update `maxSurge: 0`/`maxUnavailable: 1`, ServiceAccount `snapshot-controller`, Linux node selector, `system-cluster-critical` priority, `RuntimeDefault` seccomp, and control-plane tolerations. The container image is `registry.k8s.io/sig-storage/snapshot-controller:v8.4.0`, with `--v=2`, `--leader-election=true`, and `--leader-election-namespace=$(POD_NAMESPACE)` from downward API. Resource limit is memory 300Mi with small requests.

Control flow: Replicas contend for leader election in their own namespace. The leader watches `VolumeSnapshot`, `VolumeSnapshotClass`, `VolumeSnapshotContent`, PVC, and PV resources, then writes binding/status changes. CSI driver-specific work is delegated to snapshotter sidecars in controller deployments such as `csi-nfs-controller`.

State and persistence behavior: Snapshot objects and content persist in the Kubernetes API; leader election persists as a Lease. The pod has no local persistent storage. Using `POD_NAMESPACE` makes namespace relocation safer than the v4.3.0 hard-coded arg, provided RBAC also moves.

Dependencies and integration points: Requires CRDs, `rbac-snapshot-controller.yaml`, and a CSI snapshotter sidecar for the target driver. It integrates with `snapshotclass.yaml` and the NFS CSI driver name.

Risks: Missing CRDs prevent readiness. RBAC must grant leases in the runtime namespace. Memory limit increased from v4.3.0 but can still matter for very large clusters. Controller version must stay compatible with the installed CRD schema and sidecar versions.

Test signals: Verify two replicas, one leader lease in the pod namespace, readiness after CRDs, and snapshot lifecycle status updates. Test deployment namespace changes only with matching RBAC, and inspect logs for CRD/version compatibility warnings.
