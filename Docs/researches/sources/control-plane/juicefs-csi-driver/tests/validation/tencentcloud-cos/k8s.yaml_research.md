<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/tencentcloud-cos/k8s.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/tencentcloud-cos/k8s.yaml

### Purpose
This manifest defines a Tencent Cloud COS validation workload for JuiceFS CSI dynamic provisioning.

### Important APIs, Types, And Functions
It creates StorageClass `juicefs-sc` with provisioner `csi.juicefs.com` and fixed secret name/namespace `juicefs-secret/default`, PVC `juicefs-pvc` requesting RWX `10Pi`, and pod `juicefs-app` running CentOS to append UTC timestamps to `/data/out.txt`.

### Control Flow
Applying the StorageClass and PVC triggers provisioning using the pre-existing secret. The pod mounts the PVC at `/data` and writes a timestamp every five seconds.

### State, Persistence, And Dependencies
Persistent state includes StorageClass, PVC/PV, pod, and JuiceFS data backed by Tencent COS configuration in the secret. Dependencies include the CSI driver, correct `juicefs-secret`, COS credentials/config, and the CentOS image.

### Integration Points
This is a provider-specific validation fixture for Tencent COS storage, checking the same CSI dynamic provisioning/node publish path with COS-backed JuiceFS settings.

### Risks
Credentials are external and not represented here. `10Pi` capacity has the same quota/thin-provisioning concerns as other validation fixtures. The pod has no restart policy override, probes, or resource requests. CentOS image availability can affect validation unrelated to CSI.

### Test Signals
Signals include PVC binding, pod running, timestamp writes under `/data`, successful readback/log inspection, and cleanup of COS-backed JuiceFS resources.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/tencentcloud-cos/k8s.yaml -->
