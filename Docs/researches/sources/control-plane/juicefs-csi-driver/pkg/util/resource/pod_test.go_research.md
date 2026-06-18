<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pod_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/pod_test.go

### Purpose
`pod_test.go` is the unit-test specification for JuiceFS CSI pod resource helpers. It exercises pod resource stripping, readiness/error predicates, reference annotation filtering, mount pod unique-id parsing, and sidecar mount-pod mutation helpers.

### Important APIs, Types, And Functions
The tests cover `DeleteResourceOfPod`, `IsPodHasResource`, `IsPodReady`, `IsPodError`, `IsPodResourceError`, `GetAllRefKeys`, `GetUniqueId`, `MergeEnvs`, `MergeVolumes`, `MergeMountOptions`, and generic `FilterVars`. Shared fixtures define CPU/memory `ResourceRequirements` and representative mount-sidecar commands.

### Control Flow
Most tests are table driven. They construct Kubernetes `corev1.Pod` objects with targeted status, resource, environment, volume, and command fields, invoke a helper, then compare the mutated pod or returned boolean/map against the expected state. The mount-option tests use realistic shell command strings containing config copy/auth/mount command sequences and verify that helper logic rewrites only the final `mount.juicefs ... -o` options.

### State, Persistence, And Dependencies
No persistent state is created. The file depends on Kubernetes core API structs, `resource.Quantity`, `metav1`, `testify/assert`, and JuiceFS CSI config constants. The tests model Kubernetes pod state in memory, including status phases, conditions, container waiting/terminated states, labels, annotations, volumes, mounts, devices, and init-container commands.

### Integration Points
These tests protect helpers consumed by mount pod lifecycle, webhook sidecar injection, controller cleanup, and dashboard/debug code. `MergeVolumes` and `MergeMountOptions` are especially tied to `config.JfsSetting`, cache directory/PVC settings, and the builder-generated JuiceFS mount command contract.

### Risks
Coverage focuses on positive helper behavior and a few malformed command paths, but it does not exercise nil containers across every mutating helper. `MergeMountOptions` depends on string parsing of shell commands, so changes in builder command format can break behavior while still compiling. `GetUniqueId` is tested for one pod-name shape only. The tests compare slices exactly, so helper ordering changes are observable.

### Test Signals
Strong signals include resource requests/limits removal, readiness requiring both container and pod readiness, error detection for failed/unknown pods and non-creating waiting states, resource-pressure admission failures, SHA-derived reference annotation filtering, preserving/overwriting selected `JFS_*` envs, cache-dir/cache-PVC volume generation, duplicate option overwrite, option removal, and generic slice filtering for envs, volumes, mounts, and devices.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pod_test.go -->
