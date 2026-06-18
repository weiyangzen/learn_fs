<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pvc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pvc.yaml

Purpose: standalone PVC for the static read-only BeeGFS example.

Important APIs and flow: requests `ReadOnlyMany`, `5Gi`, sets `storageClassName: ""`, and binds to `csi-beegfs-static-ro-pv`.

State and persistence: stores only binding intent; BeeGFS content remains externally managed.

Dependencies and integration points: requires the matching PV and a consuming Pod that mounts read-only.

Risks and test signals: Kubernetes requires the storage request even though the comment notes it is otherwise meaningless for read-only static volumes. Test `Bound` status and read-only mount behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/static-ro/static-ro-pvc.yaml -->
