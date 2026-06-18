<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume_test.go

### Purpose
`volume_test.go` validates JuiceFS PV/PVC discovery from pod volumes against fake Kubernetes resources.

### Important APIs, Types, And Functions
The file tests `GetVolumes` and the `PVPair` result contract. It constructs PVCs, PVs, a fake StorageClass name, fake clientset-backed `K8sClient`, and table-driven pod fixtures.

### Control Flow
The test pre-creates four PVCs and four PVs in a fake API server. Each table case builds a pod with one or more PVC volumes, calls `GetVolumes`, checks the `used` flag and result length, then matches each returned pair by PV/PVC name and compares full objects.

### State, Persistence, And Dependencies
State is fake Kubernetes API memory only. Dependencies include fake clientsets, corev1 resource structs, reflection comparison, and the local k8s client wrapper.

### Integration Points
The tests protect admission webhook behavior that relies on `GetVolumes` to decide whether to mutate an app pod. They also confirm that a missing/non-JuiceFS StorageClass does not prevent static PV CSI detection.

### Risks
The test does not create an actual StorageClass for the fake `StorageClassName`, so it mainly exercises fallback-to-PV detection rather than StorageClass provisioner detection. It does not cover unbound PVCs, missing resources, namespace override, or API errors. Full-object `DeepEqual` can be sensitive to fake client defaulting if client-go behavior changes.

### Test Signals
Covered signals include a single JuiceFS CSI PV, a non-CSI HostPath PV skip, two JuiceFS volumes in one pod, and a PVC with an unknown StorageClass still being recognized by bound PV CSI driver.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume_test.go -->
