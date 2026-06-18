## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod.go

### Purpose
`pod.go` builds managed JuiceFS mount pods. It turns `config.JfsSetting` into a privileged Kubernetes pod with mount commands, secret-projected credentials, host mount propagation, FUSE passfd support, cache volumes, hostPath mounts, user custom volumes, and optional init containers.

### Important APIs, Types, And Functions
`PodBuilder` embeds `BaseBuilder`; `NewPodBuilder()` constructs it. `NewMountPod(podName)` is the primary API. Helper functions include `genCommonContainer()`, `expandMountPodTemplate()`, `genCacheDirVolumes()`, `genHostPathVolumes()`, `genPodVolumes()`, and `genCleanCachePod()`. Cache support covers hostPath cache dirs, cache PVCs, emptyDir cache, inline CSI cache volumes, and generic ephemeral volumes.

### Control Flow
`NewMountPod` starts from `genCommonJuicePod`, sets restart policy, pod name, command, and `JFS_FOREGROUND=1`. If the pod has a name and the image supports fuse-pass, it obtains a passfd socket address and injects `common.JfsCommEnv`. It appends mount-pod-only volumes, cache volumes, hostPath volumes, caller-provided volumes/mounts/devices, and init containers. `genPodVolumes` mounts the host mountpoint base bidirectionally and mounts the FUSE fd socket directory; `updatedb.conf` is mounted when the driver is mutable.

### State, Persistence, And Dependencies
The function persists desired state only as a `corev1.Pod` object. Once created by `PodMount`, annotations track references and UUIDs. Cache volume state may create host directories, PVC mounts, emptyDir state, inline CSI volumes, or ephemeral PVCs. It depends on `config`, `common`, `passfd`, Kubernetes core APIs, and mount-template expansion from `config.ReplaceMountPodTemplate`.

### Integration Points
`PodMount.createOrAddRef` calls `NewMountPod` before creating managed mount pods. `JobBuilder` reuses pod generation for one-shot jobs. Sidecar builders embed and adapt it. The generated pod spec interacts with FUSE passfd servers, host mount propagation, node selector scheduling, cleanup jobs, and secrets from `secret.go`.

### Risks
Mount pods are privileged root containers with bidirectional host mount propagation. Cache and hostPath template expansion must be correct because it directly controls host filesystem access. Ephemeral cache PVCs add selected-node annotations only for normal mount pods because they bypass the scheduler; serverless differs. `NewMountPod` returns passfd errors, so callers must handle image/upgrade compatibility carefully.

### Test Signals
`pod_test.go` validates cache volume counts and ephemeral selected-node annotations, generated pod YAML for labels/annotations/service accounts/env/config volumes/cache dirs/metrics/fuse pass, template expansion for cache-dir and hostPath, mount command generation, metrics port extraction, and hostPath volume generation.
