<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar_test.go

### Purpose
`sidecar_test.go` verifies focused `SidecarMutate` subroutines: volume injection, sidecar container injection, and deduplication of generated names.

### Important APIs, Types, And Functions
The tests cover `injectVolume`, `injectContainer`, and `Deduplicate`. They use `builder.NewContainerBuilder`, `config.JfsSetting`, `PVPair`, and Kubernetes pod/volume/mount structs.

### Control Flow
`TestSidecarMutate_injectVolume` constructs pods with PVC volumes and expected generated volumes, invokes `injectVolume`, and compares final pod volumes by name. It covers regular and subPath-derived hostPath targets. `TestSidecarMutate_injectContainer` appends a sidecar container to a pod. `TestSidecarMutate_Deduplicate` mutates generated mount pod names and volume names when the app pod already uses those names.

### State, Persistence, And Dependencies
No Kubernetes API calls are made. State is in-memory pod mutation. Dependencies include corev1, metav1, `filepath`, reflection, JuiceFS config, resource PVPair, and builder package behavior.

### Integration Points
The tests guard the lower-level mutation mechanics used by the admission handler before JSON patch generation. They are particularly relevant for pods with multiple JuiceFS PVCs or user containers/volumes that conflict with generated builder names.

### Risks
The tests do not exercise the full `Mutate` path, secret creation, settings parsing, native sidecar init-container behavior, serverless builders, or node metadata. The hostPath comparison condition appears weak when both actual and expected HostPath are non-nil, so path mismatches may not be reported in all cases.

### Test Signals
Signals include generated mount volumes being appended, app PVC volume source being replaced by a hostPath under the mount point, subPath suffix inclusion, appending a sidecar container, suffixing duplicate container names with the volume index, and renaming colliding generated volumes and mounts together.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar_test.go -->
