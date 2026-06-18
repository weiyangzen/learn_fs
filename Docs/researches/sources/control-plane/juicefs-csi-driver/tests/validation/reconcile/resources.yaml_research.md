<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/resources.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/resources.yaml

### Purpose
`resources.yaml` defines the dynamic-provisioning validation workload for JuiceFS CSI reconcile testing: a StorageClass, a large RWX PVC, and writer/reader deployments sharing it.

### Important APIs, Types, And Functions
The StorageClass `juicefs-sc` uses provisioner `csi.juicefs.com` and four CSI secret parameter keys. PVC `juicefs-pvc` requests `ReadWriteMany` and `10Pi`. Deployment `juicefs-writer` appends UTC timestamps to `/jfs/out.txt`; deployment `juicefs-reader` tails that file.

### Control Flow
When applied, the StorageClass references the generated Secret, the PVC triggers dynamic provisioning, the writer mounts the PVC and writes once per second, and the reader mounts the same PVC and follows the output file.

### State, Persistence, And Dependencies
State includes Kubernetes StorageClass/PVC/Deployments and data written to the JuiceFS volume. It depends on JuiceFS CSI driver, secret values, dynamic provisioning, RWX support, and BusyBox images.

### Integration Points
This fixture validates that controller provisioning, node publishing, and workload reconciliation produce a shared filesystem visible across deployments.

### Risks
`10Pi` is intentionally huge and relies on thin/quota behavior; clusters or quota settings that enforce real capacity may reject it. `tail -f /jfs/out.txt` can fail until the writer creates the file because the shell uses `errexit`. No resource requests or readiness probes are present.

### Test Signals
Signals include PVC bound to a JuiceFS PV, both deployments available, writer file growth, reader logs showing appended timestamps, and successful cleanup/reconcile after pod restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/resources.yaml -->
