## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/interface.go

### Purpose
`interface.go` defines the small sidecar-builder contract used by different JuiceFS injection modes. It also initializes the package logger used by builder implementations.

### Important APIs, Types, And Functions
`SidecarInterface` requires `NewMountSidecar() *corev1.Pod`, `NewSecret() corev1.Secret`, `OverwriteVolumes(*corev1.Volume, string)`, and `OverwriteVolumeMounts(*corev1.VolumeMount)`. `builderLog` is a package-level `klogr` logger named `builder`.

### Control Flow
The file has no runtime control flow beyond interface dispatch. Callers construct a concrete builder, call `NewSecret()` for the JuiceFS credential/script Secret, call `NewMountSidecar()` for the sidecar pod spec, and use the overwrite hooks while mutating application volumes and mounts.

### State, Persistence, And Dependencies
No state is persisted here. The interface couples implementations to Kubernetes `corev1.Pod`, `Secret`, `Volume`, and `VolumeMount` types. Concrete implementations include `ContainerBuilder`, `ServerlessBuilder`, and `VCIBuilder`; all embed `BaseBuilder` through `PodBuilder` to satisfy `NewSecret()`.

### Integration Points
This interface is the abstraction boundary between control-plane sidecar injection logic and environment-specific builders. The overwrite methods allow the caller to handle app pod mutation without knowing whether the backend should use hostPath, emptyDir, or mount propagation tweaks.

### Risks
The interface returns a full `*corev1.Pod` as a sidecar template rather than a narrower container/volume bundle, so callers must understand which fields are meaningful and which should be ignored. Adding a new implementation requires careful parity with secret creation and mount readiness semantics.

### Test Signals
Compile-time assertions in concrete files (`var _ SidecarInterface = ...`) are the main coverage. Behavioral coverage is indirect through builder tests for pod specs and serverless cache behavior.
