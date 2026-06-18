## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless.go

### Purpose
`serverless.go` implements `ServerlessBuilder`, a sidecar builder for serverless Kubernetes environments where hostPath is unavailable. It creates a privileged JuiceFS sidecar that mounts through an application shared volume/emptyDir model and supports PVC, emptyDir, inline CSI, and ephemeral cache volumes.

### Important APIs, Types, And Functions
`ServerlessBuilder` embeds `PodBuilder` and stores the application pod and PVC. `NewServerlessBuilder()` returns `SidecarInterface`. `NewMountSidecar()` builds the sidecar pod template. `OverwriteVolumes()` rewrites application volumes to `emptyDir`; `OverwriteVolumeMounts()` sets host-to-container propagation. `genServerlessVolumes()` creates the shared mount volumeMount and check script Secret mount. `genCacheDirVolumes()` supports non-hostPath cache volumes.

### Control Flow
`NewMountSidecar` starts from common pod generation, clears labels/annotations, configures the check-mount lifecycle hook, adds `JFS_NO_UMOUNT` and `JFS_FOREGROUND`, appends serverless volumes, appends cache volumes, and sets the init-plus-mount shell command. `genServerlessVolumes` finds the application volume whose PVC claim name matches the target PVC and mounts that shared volume at the JuiceFS mount path with bidirectional propagation.

### State, Persistence, And Dependencies
The builder persists desired pod spec state only. It depends on app pod/PVC state to find the shared volume name. Cache state may be persisted through PVCs or ephemeral volume claim templates. It depends on `config`, `corev1`, `ptr`, and shell escaping.

### Integration Points
This builder is selected for serverless injection paths through `SidecarInterface`. It relies on `secret.go` for credentials/check script, and on the injection layer to call overwrite hooks for application volume mutation.

### Risks
If no matching PVC volume is found in the app pod, the shared volume name remains empty and the generated volumeMount is invalid. The privileged container requirement may not be allowed on all serverless providers. Serverless cache intentionally ignores hostPath cache dirs, which can surprise users migrating from normal mount pods. The lifecycle assumes mount propagation works in the platform.

### Test Signals
`serverless_test.go` covers generic ephemeral cache volume generation and confirms no hostPath volumes are emitted. Additional integration tests should validate shared volume name discovery, overwrite hooks, lifecycle command escaping, and behavior when app/PVC do not match.
