<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-sc.yaml -->
# sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-sc.yaml

Purpose: StorageClass for standalone generic ephemeral BeeGFS demo volumes.

Important APIs and flow: uses `beegfs.csi.netapp.com`, `sysMgmtdHost`, `volDirBasePath: k8s/name/ge`, optional string-valued stripe/permission parameters, `Delete` reclaim policy, immediate binding, and expansion disabled.

State and persistence: creates Pod-scoped storage through generated PVCs and deletes it with reclaim lifecycle.

Dependencies and integration points: consumed by `ge-app.yaml`; depends on CSI provisioner and BeeGFS management path uniqueness.

Risks and test signals: generic ephemeral volumes can leave storage behind if finalizers or deletion fail. Test cleanup after Pod removal and watch provisioner logs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/examples/k8s/ge/ge-sc.yaml -->
