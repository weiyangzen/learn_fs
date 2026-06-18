## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/vci-serverless.go

### Purpose
`vci-serverless.go` implements `VCIBuilder`, a Volcengine VCI-specific serverless sidecar builder. It adapts the serverless flow to provider annotations and non-privileged container requirements while preserving JuiceFS mount, check script, and cache behavior.

### Important APIs, Types, And Functions
Constants define VCI annotation keys and values. `VCIBuilder` embeds `ServerlessBuilder`. `VCIPropagationStruct` models the JSON annotation entries. `NewVCIBuilder()` constructs the implementation. `NewMountSidecar()` builds the provider-specific sidecar. `OverwriteVolumes()` uses `emptyDir`, `OverwriteVolumeMounts()` sets host-to-container propagation, `genVCIServerlessVolumes()` creates shared/check volumes, `genNonPrivilegedContainer()` omits privileged mode, and `genMountContainerName()` appends the PVC name to the mount container name.

### Control Flow
`NewMountSidecar` generates a common pod with the non-privileged container, initializes annotations, sets VCI bidirectional propagation config, appends a propagation entry for the mount container/path, merges any existing app VCI propagation JSON if valid, and logs invalid JSON. It then configures lifecycle check/quota behavior, renames the container, adds foreground/no-umount envs, appends VCI volumes and cache volumes, and sets the shell command.

### State, Persistence, And Dependencies
The state is Kubernetes pod spec and annotations. The provider-specific propagation state is serialized JSON in annotations. It depends on Kubernetes JSON utilities, `common`, `config`, `security.EscapeBashStr`, and inherited serverless cache generation.

### Integration Points
This builder plugs into the same `SidecarInterface` path as normal/serverless builders. Provider annotations integrate with VCI runtime mount propagation. Existing application annotations are preserved by parsing and appending them into the new propagation list.

### Risks
Invalid existing VCI propagation JSON is logged and ignored, which may drop app-requested propagation entries. The generated container name includes PVC name and must remain a valid Kubernetes container name. `genVCIServerlessVolumes` can emit an empty volume name if the PVC is not found in the app pod. Provider annotation contracts are external and may change.

### Test Signals
No direct VCI tests are present. Useful coverage would assert annotation JSON merge behavior, non-privileged security context, emptyDir overwrite, host-to-container mount propagation, shared volume matching, and malformed annotation handling.
