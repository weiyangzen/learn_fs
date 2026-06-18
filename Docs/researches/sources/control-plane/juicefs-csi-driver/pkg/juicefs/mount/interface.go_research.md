## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/interface.go

### Purpose
`interface.go` defines `MntInterface`, the mount backend abstraction used by CSI node/control paths. It unifies Kubernetes mount-pod mode and direct process mount mode behind one contract while embedding the standard Kubernetes mount interface.

### Important APIs, Types, And Functions
`MntInterface` embeds `k8sMount.Interface` and adds `JMount`, `JCreateVolume`, `JDeleteVolume`, `GetMountRef`, `UmountTarget`, `JUmount`, `AddRefOfMount`, and `CleanCache`. Methods accept `context.Context`, `config.AppInfo`, and `config.JfsSetting` depending on operation. Comments mark `podName` parameters as pod-mode-specific.

### Control Flow
No implementation flow exists here. Callers invoke the interface for volume lifecycle and mount lifecycle operations without knowing whether the backend uses Kubernetes pods or local processes.

### State, Persistence, And Dependencies
The interface itself has no state. Implementations persist state differently: `PodMount` uses Kubernetes pods/secrets/jobs/annotations; `ProcessMount` uses local mountpoints and filesystem state. Dependency on `k8sMount.Interface` means mocks and implementations must also provide mount listing, mount, unmount, and related methods.

### Integration Points
Implemented by `PodMount` and `ProcessMount`; generated mocks in `mocks/mock_mnt.go` support tests. CSI node service code can depend on this interface for mount lifecycle decisions.

### Risks
Some methods do not apply cleanly to both implementations. `ProcessMount.AddRefOfMount` panics, so callers must not call it in process mode. The embedded mount interface expands the mock surface and can create stale generated mocks when upstream interfaces change.

### Test Signals
Compile-time implementation assertions in concrete files and generated mock compilation are primary. Behavioral tests in `pod_mount_test.go` and `process_mount_test.go` verify selected interface methods.
