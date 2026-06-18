## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/container.go

### Purpose
`container.go` implements `ContainerBuilder`, the normal Kubernetes sidecar builder for JuiceFS mounts. It embeds `PodBuilder` and satisfies `SidecarInterface`, reusing the mount-pod spec but adapting it for an injected sidecar container inside an application pod. The sidecar preserves the JuiceFS mount command and common container configuration while stripping mount-pod-only labels, annotations, and FUSE passfd volume wiring.

### Important APIs, Types, And Functions
`NewContainerBuilder(setting, capacity)` returns a `SidecarInterface` backed by `ContainerBuilder`. `NewMountSidecar()` creates the sidecar pod template by calling `NewMountPod("")`, adds check-mount secret volumes, removes `config.JfsFuseFdPathName`, injects a `PostStart` lifecycle hook, and sets the shell command to optional init command plus mount command. `OverwriteVolumes()` rewrites application PVC volumes to hostPath volumes rooted under `config.MountPointPath`; `OverwriteVolumeMounts()` intentionally leaves mounts unchanged. `genSidecarVolumes()` mounts the `check_mount.sh` secret directory read-only at `/jfs-scripts`.

### Control Flow
Construction starts with normal `PodBuilder` output, then removes metadata that belongs only to managed mount pods. It appends an extra secret-backed volume and mount, removes FUSE passfd hostPath entries, builds lifecycle variables for subpath/quota checks, and escapes shell strings before embedding them into the `bash -c` post-start command. Command generation follows the same `genInitCommand()` then `genMountCommand()` sequence as mount pods.

### State, Persistence, And Dependencies
This builder does not persist state directly. It materializes Kubernetes pod, volume, volumeMount, lifecycle, and hostPath state from `config.JfsSetting`, `capacity`, and common constants. It depends on `PodBuilder`, `config`, `corev1`, `ptr`, filepath joining, and `security.EscapeBashStr` to avoid shell injection in lifecycle arguments.

### Integration Points
It is consumed by sidecar injection paths through `SidecarInterface`. The generated sidecar depends on `BaseBuilder.NewSecret()` because the check script and mount credentials are stored in the same Kubernetes Secret. `OverwriteVolumes` is used by higher-level code that mutates application volumes to point at the JuiceFS host mount.

### Risks
The hostPath rewrite assumes the JuiceFS mount has appeared under `config.MountPointPath/mountPath`; if propagation or mount readiness fails, the app sees an empty or stale host path. `NewMountSidecar()` ignores the error from `NewMountPod("")`; future passfd or template errors could be silently dropped. The lifecycle shell command is complex and must remain escaped consistently.

### Test Signals
There is no direct `container.go` test in this subset. Indirect signals come from `pod_test.go` for command, metrics, cache volume, and fuse-pass behavior, plus any sidecar integration tests that assert labels/annotations are cleared, FUSE passfd volumes are removed, and `jfs-check-mount` mounts the full secret directory instead of a subPath file.
