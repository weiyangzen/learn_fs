## sources/control-plane/juicefs-csi-driver/pkg/util/resource/pod.go

### Purpose
`resource/pod.go` provides pod status helpers, patch helpers, readiness wait loops, mount-pod reference utilities, upgrade eligibility checks, pod spec merge functions, namespace/PV lookup helpers, and corrupted mount-path handling for the JuiceFS CSI driver.

### Important APIs, Types, And Functions
Status helpers include `IsPodReady`, `IsPodError`, `IsPodComplete`, `IsPodResourceError`, `GetPodStatus`, `IsPodHasResource`, `DeleteResourceOfPod`, and `SetRequestToZeroOfPod`. Patch helpers include `RemoveFinalizer`, `AddPodLabel`, `AddPodAnnotation`, `DelPodAnnotation`, and `ReplacePodAnnotation`. Runtime helpers include `GetAllRefKeys`, `WaitUntilPodRunning`, `WaitUntilMountReady`, `ShouldDelay`, `GetPVWithVolumeHandleOrAppInfo`, `GetCommPath`, `GetUniqueId`, `MergeEnvs`, `MergeMountOptions`, `MergeVolumes`, `FilterVars`, `FilterPodsToUpgrade`, `CanUpgrade`, `CanUpgradeWithHash`, `GetUpgradeUUID`, and `HandleCorruptedMountPath`.

### Control Flow
Readiness functions inspect pod conditions and container states. Patch helpers marshal strategic merge or JSON patch payloads and call `K8sClient.PatchPod`. Wait loops poll pod phase or mount path inode until a 60s timeout. `ShouldDelay` reads delete-delay annotations, computes and writes a delete-at timestamp, and later compares it to current time. Merge helpers preserve CSI-managed env/options while replacing user-configured values from the new setting. Upgrade checks enforce hash label, image support, readiness, and absence of unmount prestop hooks. Corrupted mount handling finds running mount pods for a volume and annotates the one referencing the corrupted path for immediate reconciliation.

### State, Persistence, And Dependencies
State is mostly Kubernetes pod metadata and spec patches. Mount readiness reads local filesystem inode state. Dependencies include `common`, `config`, `util`, `k8sclient`, Kubernetes patch types, fields/selectors, resource quantities, and syscall stat data.

### Integration Points
`PodMount` relies on annotation helpers, readiness waits, delayed deletion, and ref counting. Upgrade controllers rely on merge and eligibility helpers. CSI publish/unpublish and reconciler paths use PV lookup and corrupted mount annotation behavior.

### Risks
`DelPodAnnotation` builds JSON patch paths from raw annotation keys; keys containing `/` or `~` require JSON Pointer escaping and may fail otherwise. `GetUniqueId` assumes older pod names contain `nodeName-` and can panic on malformed names. `WaitUntilPodRunning` and `WaitUntilMountReady` use fixed 60s loops. Merge helpers manipulate shell command strings by splitting fields, which is fragile for quoted options. `MergeVolumes` assumes `jfsSetting.Attr` may be non-nil but references `jfsSetting.Attr.VolumeDevices` in one loop before the later nil guard.

### Test Signals
No `pod_test.go` for this file is in the required subset, but mount tests exercise annotation helpers indirectly. Strong additional tests would cover JSON pointer escaping, delayed deletion annotation transitions, mount readiness inode checks, merge command rewriting, upgrade eligibility, and corrupted mount-path annotation selection.
