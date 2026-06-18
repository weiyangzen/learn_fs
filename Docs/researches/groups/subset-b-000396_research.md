# subset-b-000396 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/container.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/interface.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/job.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/job.go

### Purpose
`job.go` builds Kubernetes Jobs used for one-shot JuiceFS operations: create/delete subpath volumes, clean cache, abort hung FUSE connections, canary image/binary checks, and snapshot create/restore/delete workflows. It centralizes job naming, pod template reuse, command construction, TTL/backoff policies, and owner/integration defaults.

### Important APIs, Types, And Functions
`JobBuilder` embeds `PodBuilder`; `NewJobBuilder()` creates it. `NewJobForCreateVolume()`, `NewJobForDeleteVolume()`, and `NewJobForCleanCache()` produce volume lifecycle jobs. `GenJobNameByVolumeId()` hashes a volume ID to a stable `juicefs-...` prefix. `newJob()` builds the shared JuiceFS job template and `newCleanJob()` builds node-pinned cache-clean jobs. `NewFuseAbortJob()` builds a privileged sysfs job that may write `/sys/fs/fuse/connections/<minor>/abort`. `NewCanaryJob()` builds a node-pinned canary job from an existing mount pod. Snapshot APIs are `NewJobForSnapshot()`, `NewJobForRestore()`, and `NewJobForDeleteSnapshot()`.

### Control Flow
Create/delete jobs start from `newJob()`, combine optional init commands with a JuiceFS mount command, then perform mkdir or `juicefs rmr` under `/mnt/jfs`. `newJob()` sets a default secret name if absent, reuses common pod generation, adds a PreStop lazy unmount, lets the scheduler choose a node, copies CSI pod scheduling constraints, and sets a short TTL. FUSE abort jobs check fuse-pass health via inode probing first, inspect `waiting`, and only write `abort` when the kernel reports pending requests. Canary jobs delete any existing job with the same deterministic name before returning a fresh spec. Snapshot jobs mount, create/prepare paths, call `juicefs clone` or `juicefs rmr`, and unmount best-effort.

### State, Persistence, And Dependencies
The persisted state is Kubernetes `batchv1.Job` objects and their pod templates. Jobs also depend on Secrets produced by `NewSecret()` and later owned by the Job. Naming persists through a truncated sha256 hash of volume IDs. The code depends on `config`, `common`, `k8sclient`, `util`, Kubernetes batch/core APIs, and shell command strings.

### Integration Points
`PodMount.JCreateVolume`, `JDeleteVolume`, and `CleanCache` create these jobs, then wait for completion. `NewCanaryJob` integrates with upgrade/restart flows by deriving settings from a mount pod. `NewFuseAbortJob` integrates with corrupted/hung FUSE recovery and depends on dev minor tracking from `util/dev_minor.go`.

### Risks
Command strings are shell-heavy and must be escaped; create/delete commands escape subpaths, but snapshot/restore path inputs are interpolated more directly and need trusted caller validation. `newJob()` mutates `r.jfsSetting.SecretName`, which is convenient but surprising. TTL assumptions may fail on clusters without TTL-after-finished support, so cleanup code must handle stale jobs. FUSE abort is intentionally privileged and hostPath-backed, so it has a high security blast radius. Snapshot restore refuses non-empty targets, but path handling still matters.

### Test Signals
No direct job-builder tests are listed, but `resource/job_test.go` covers completion/failure/recycle helpers consumed by waiting code. Useful integration checks include generated job names, TTL/backoff values, owner secret creation, mount command content, FUSE abort skip/abort branches, and snapshot command path handling.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod_test.go

### Purpose
`pod_test.go` is the main specification test suite for mount pod generation. It asserts exact Kubernetes pod specs and important helper behavior for cache volumes, generated commands, metrics ports, fuse-pass support, template expansion, and hostPath volume creation.

### Important APIs, Types, And Functions
The tests define `podDefaultTest` as the canonical expected mount pod. `deepcopyPodFromDefault` builds independent expected objects. Test cases cover `PodBuilder.genCacheDirVolumes`, `PodBuilder.NewMountPod`, cache-dir expansion from `MountPodPatch`, hostPath template expansion, `BaseBuilder.genMountCommand`, `BaseBuilder.genMetricsPort`, and `PodBuilder.genHostPathVolumes`.

### Control Flow
Tests build `config.JfsSetting` values through `config.ParseSetting` or literals, then call builder helpers and compare generated Kubernetes objects. The exact-pod tests marshal to YAML before comparison, making field ordering less brittle than raw struct formatting. Fuse-pass tests initialize test passfd state and switch images to one that supports smooth upgrade behavior.

### State, Persistence, And Dependencies
The test mutates global `config.NodeName`, `config.Namespace`, and `config.GlobalConfig.MountPodPatch` in places, with some defers for cleanup. It uses local filesystem cleanup for `tmp` passfd artifacts. Dependencies include Kubernetes core types, `sigs.k8s.io/yaml`, `stretchr/testify/assert`, `passfd`, and configuration parsing.

### Integration Points
The tests encode the expected contract consumed by `PodMount`, `JobBuilder`, and sidecar builders. They indirectly protect secret key references, mount path constants, metrics ports, cache volume naming, FUSE communication environment variables, and host mount propagation fields.

### Risks
Snapshot-style YAML comparisons are useful but can be brittle when Kubernetes defaults or struct fields change. Some tests append to reused slices while checking lengths, so they primarily validate aggregate count behavior rather than isolated helper output. Global config mutation can leak if future tests miss cleanup.

### Test Signals
Strong signals are failure of exact pod YAML comparisons, missing selected-node annotations for generic ephemeral cache volumes, wrong cache/hostPath template expansion, wrong metrics port defaults/fallbacks, and missing `JFS_SUPER_COMM` for fuse-pass-capable images.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/pod_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret.go

### Purpose
`secret.go` builds the Kubernetes Secret used by JuiceFS mount pods, jobs, and sidecars. The Secret carries serialized settings, credentials, env values, optional session tokens, init config, and the `check_mount.sh` script used by sidecar lifecycle hooks.

### Important APIs, Types, And Functions
Constants define `checkMountScriptName`, `checkMountScriptDir`, and `checkMountScriptPath`. `checkMountScriptContent` polls for a JuiceFS mount and optionally sets quota for subpaths. `BaseBuilder.NewSecret()` creates a labeled `corev1.Secret`. `BaseBuilder.GetEnvKey()` returns secret keys that should be exposed as env vars. Owner helpers are `SetPodAsOwner`, `SetPVCAsOwner`, `SetPVAsOwner`, and `SetJobAsOwner`.

### Control Flow
`NewSecret` collects non-empty sensitive settings into `StringData`, always includes `jfsSettings`, adds `check_mount.sh` after replacing placeholder characters with backticks, parses format options to extract `session-token`, then copies arbitrary `jfsSetting.Envs`. It sets namespace/name from the setting and labels the secret as a JuiceFS secret. Owner helpers overwrite owner references with a single owner reference suited to garbage collection.

### State, Persistence, And Dependencies
The output Secret persists credentials and scripts in Kubernetes. It depends on `config.JfsSetting`, Kubernetes core/batch/meta APIs, and `common.JuicefsSecretLabelKey`. Data includes cleartext StringData before Kubernetes stores it, so logging must avoid dumping secrets.

### Integration Points
`PodBuilder` and `JobBuilder` expect secret keys to exist for generated env `SecretKeyRef`s. Sidecar builders mount `check_mount.sh` from this Secret. `PodMount` creates/updates the Secret and sets PV or Job owners; sidecar injection likely sets pod/PVC ownership depending on lifecycle.

### Risks
Arbitrary environment keys can override expected keys if names collide. `GetEnvKey` detects `session-token` with a substring check, while `NewSecret` parses options; mismatches are possible on malformed options. Owner helper calls replace existing references rather than appending. The embedded shell script must remain executable and safe because it runs in container lifecycle hooks.

### Test Signals
`secret_test.go` verifies `GetEnvKey` includes meta URL, secret keys, token, passphrase, and custom env keys. Additional useful tests would check `session-token`, check script presence, label/namespace/name, and owner reference shapes.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret_test.go

### Purpose
`secret_test.go` tests the env-key projection contract for Secrets. It verifies that `BaseBuilder.GetEnvKey()` returns expected secret keys for configured credentials and custom env values.

### Important APIs, Types, And Functions
The sole test is `TestBaseBuilder_GetEnvKey`. It builds a `BaseBuilder` with a `JfsSetting` containing `MetaUrl`, `SecretKey`, `SecretKey2`, `Token`, `Passphrase`, and `Envs`, then compares the returned slice with the expected key list.

### Control Flow
The table test directly calls `GetEnvKey()` and uses `reflect.DeepEqual`. There is no Kubernetes fake client and no Secret object creation.

### State, Persistence, And Dependencies
The test has no persistent state. It depends on `config.JfsSetting` and Go reflection.

### Integration Points
This is a small guard for the env variables later emitted by common pod/job generation. If `GetEnvKey` omits a key, generated containers may not receive the corresponding credential SecretKeyRef.

### Risks
The test does not cover `session-token`, `SecretKey2` ordering with maps beyond one custom env, `EncryptRsaKey`, `InitConfig`, actual Secret contents, labels, or owner references. Because Go map iteration order is random, multiple `Envs` entries could make strict slice ordering brittle.

### Test Signals
Failure indicates a credential/env key contract change. Broader coverage would assert `NewSecret().StringData` and env key behavior from parsed format options.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/secret_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless_test.go

### Purpose
`serverless_test.go` validates serverless cache-volume behavior, especially generic ephemeral cache support without hostPath output.

### Important APIs, Types, And Functions
`Test_serverless_getCacheDirVolumes_ephemeral` constructs a `ServerlessBuilder` with a `JfsSetting` containing one `CacheEphemeral` entry. It calls `genCacheDirVolumes()` and inspects returned volumes and mounts.

### Control Flow
The test scans returned `cacheVolumes` for `cachedir-ephemeral-0`, checks the `Ephemeral.VolumeClaimTemplate`, storage class, storage quantity, access modes, and mount path, then verifies no returned volume has a hostPath source.

### State, Persistence, And Dependencies
No state persists beyond local structs. The test depends on Kubernetes core APIs and resource quantity parsing.

### Integration Points
It protects the serverless builder contract that cache dirs must not require host filesystem access. This matters for app pod mutation and provider compatibility.

### Risks
The test covers cache generation only; it does not exercise `NewMountSidecar`, shared PVC volume discovery, lifecycle hooks, `JFS_NO_UMOUNT`, or overwrite hooks. It also does not test PVC, emptyDir, or inline CSI cache variants.

### Test Signals
Failures point to serverless cache regression, especially accidental hostPath emission or broken generic ephemeral PVC template fields.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/serverless_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/vci-serverless.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/builder/vci-serverless.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/interface.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/mocks/mock_mnt.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/mocks/mock_mnt.go

### Purpose
`mock_mnt.go` is generated GoMock code for `mount.MntInterface`. It lets tests set expectations for mount lifecycle operations without invoking real Kubernetes API calls or host mount commands.

### Important APIs, Types, And Functions
`MockMntInterface` stores a `gomock.Controller` and recorder. `NewMockMntInterface` constructs it. The mock implements `AddRefOfMount`, `CleanCache`, `GetMountRef`, `GetMountRefs`, `IsLikelyNotMountPoint`, `JCreateVolume`, `JDeleteVolume`, `JMount`, `JUmount`, `List`, `Mount`, `MountSensitive`, `UmountTarget`, and `Unmount`, with matching recorder methods under `EXPECT()`.

### Control Flow
Each method marks itself as a test helper, calls `ctrl.Call`, type-asserts return values, and returns them. Recorder methods call `RecordCallWithMethodType` with the reflected method signature.

### State, Persistence, And Dependencies
State is limited to gomock expectation bookkeeping. The file depends on `github.com/golang/mock/gomock`, `context`, `reflect`, `config.JfsSetting`, and `k8s.io/utils/mount`.

### Integration Points
Tests for CSI driver code that consumes `MntInterface` import this package to isolate mount operations. Because the source interface embeds `k8sMount.Interface`, the mock must also include the embedded mount methods.

### Risks
This is generated code and should not be manually edited. It can become stale if `MntInterface` or the embedded `k8sMount.Interface` changes; stale mocks typically fail compilation or miss expected methods.

### Test Signals
Compilation is the main signal. GoMock tests using `EXPECT()` provide behavioral signals for call order, arguments, and injected errors.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/mocks/mock_mnt.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount.go

### Purpose
`pod_mount.go` implements the Kubernetes mount-pod backend. It creates or reuses managed JuiceFS mount pods, tracks bind-mount references as pod annotations, creates Secrets and Jobs for lifecycle operations, waits for mount readiness, cleans up pods/secrets, and optionally uses the kubelet API for faster local mount pod discovery.

### Important APIs, Types, And Functions
`PodMount` embeds `SafeFormatAndMount` and holds a `K8sClient` plus optional `KubeletClient`. Public interface methods are `JMount`, `GetMountRef`, `UmountTarget`, `JUmount`, `JCreateVolume`, `JDeleteVolume`, `AddRefOfMount`, and `CleanCache`. Important helpers include `waitUntilKubeletCanSeePod`, `listMountPodsOfUniqueId`, `genMountPodName`, `createOrAddRef`, `waitUntilMountReady`, `waitUntilJobCompleted`, `setUUIDAnnotation`, `setMountLabel`, `GetJfsVolUUID`, `getErrContainerLog`, `getNotCompleteCnLog`, `GetRef`, and `GenPodNameByUniqueId`.

### Control Flow
`JMount` hashes settings, assigns an upgrade UUID, locks by hash, finds/reuses a mount pod, labels the app pod, creates or adds a reference, optionally waits for kubelet visibility, waits for mount readiness, and stores the JuiceFS UUID annotation if needed. `createOrAddRef` mutates mount path and secret name, creates directories, creates/updates the Secret, starts fuse-pass serving when supported, creates the pod, or adds a reference to an existing pod. `JUmount` removes the target annotation, checks remaining refs, honors delayed deletion annotations, stops fuse-pass, attempts source unmount, deletes the pod, and deletes the related Secret best-effort.

### State, Persistence, And Dependencies
Persistent state lives in Kubernetes pods, annotations, labels, jobs, and secrets. Reference keys are derived from target paths and counted by matching key/value pairs. Local state includes FUSE fd servers and cached dev minor values. Dependencies include `builder`, `k8sclient`, `resource`, `passfd`, `config`, `common`, Kubernetes retry/errors/fields APIs, host `umount`, and local filesystem helpers.

### Integration Points
This is the main backend for CSI node mount operations in pod mode. It integrates with `PodBuilder` and `JobBuilder`, `resource` wait/patch helpers, kubelet pod listing, app pod labels, FUSE passfd upgrade flows, and clean-cache jobs.

### Risks
Concurrency is controlled by a per-hash lock, but Kubernetes object races still require retry-on-conflict patching. Annotation JSON patch paths depend on safe reference key formats. Kubelet list fallback must remain correct or mount pod reuse can miss pods. `createOrAddRef` mutates `jfsSetting.MountPath` and `SecretName`, which callers must treat as side effects. `waitUntilJobCompleted` treats NotFound as success, which is correct after TTL recycle but can mask premature deletion. Deleting a pod with no refs is sensitive because delayed delete and fuse-pass cleanup must happen in the right order.

### Test Signals
`pod_mount_test.go` covers adding refs, unmount reference deletion, pod deletion/no deletion cases, lazy unmount output handling, create-or-add-ref reuse/new-pod behavior, `JMount` error path, constructor output, and `GetRef`. Additional integration tests should cover kubelet fallback, delayed delete, job completion errors, fuse-pass server cleanup, and app pod scheduling inheritance.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount_test.go

### Purpose
`pod_mount_test.go` validates key `PodMount` behaviors using fake Kubernetes clients, monkey patches, and mocked mount operations. It focuses on reference annotations, mount pod deletion rules, lazy unmount handling, create-or-add-reference behavior, and constructor/ref helpers.

### Important APIs, Types, And Functions
The file defines reusable pods `testA` through `testH` with different annotations/statuses. Tests cover `AddRefOfMount`, `JUmount`, `UmountTarget`, `genMountPodName` plus `createOrAddRef`, `JMount`, `NewPodMount`, and `GetRef`. Mock tests use gomonkey patches for Kubernetes errors, `os.MkdirAll`, `os.Stat`, `exec.Cmd.CombinedOutput`, and cleanup functions.

### Control Flow
Fake-client tests create pods, invoke `PodMount` methods, then inspect pod annotations or deletion. Mocked tests force error branches such as GetPod failure, conflict retries, delete errors, cleanup errors, and create-pod failures. The wait/create tests patch filesystem calls to avoid real host mount setup.

### State, Persistence, And Dependencies
State persists in the fake Kubernetes client across some table cases, so tests depend on object setup order. Global `jfsConfig.NodeName` is initialized in `init`. The suite depends on `fake.Clientset`, gomonkey, GoConvey, passfd test initialization, driver mocks, and Kubernetes mount exec implementations.

### Integration Points
These tests protect behavior used by CSI unpublish and publish flows: annotations are the reference counter, pod deletion happens only when refs are gone, and existing pods can be reused by unique ID/hash. They also validate the `UmountTarget` contract used by node cleanup paths.

### Risks
Monkey-patching core functions can hide integration issues and may be fragile across Go/runtime versions. Some fake-client table tests reuse one clientset, so leaked objects can affect later cases if names collide. Coverage of kubelet API, delayed deletion, job waiting, and real readiness polling is limited.

### Test Signals
Failures in annotation equality indicate reference tracking regressions. Pod deletion expectation failures indicate unmount lifecycle changes. `UmountTarget` tests signal command-output parsing and cleanup behavior changes. `GetRef` tests protect the key/value matching rule.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/pod_mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount.go

### Purpose
`process_mount.go` implements the direct process-based mount backend. Instead of creating mount pods, it invokes JuiceFS mount commands on the host, creates/deletes subpath directories, checks local mount readiness, unmounts targets and shared refs, and cleans cache directories directly.

### Important APIs, Types, And Functions
`ProcessMount` embeds `SafeFormatAndMount`. `NewProcessMount()` constructs it. Public methods include `JCreateVolume`, `JDeleteVolume`, `JMount`, `GetMountRef`, `UmountTarget`, `JUmount`, `AddRefOfMount`, `CleanCache`, and `RmrDir`. Internal `jmount()` handles CE versus EE mount flow. `defaultCheckTimeout` is shared with pod mode.

### Control Flow
`JCreateVolume` strips readonly options, mounts JuiceFS, creates the subpath with `0777` permissions if absent, fixes permissions after umask, then unmounts. `JDeleteVolume` mounts, checks the subpath, runs `juicefs rmr`, then unmounts. `JMount` pre-creates subpath for readonly mounts, then calls `jmount`. `jmount` uses kernel mount for EE sources without `://`; CE sources create the mount directory, unmount any existing mount, spawn `mount.juicefs` with `JFS_FOREGROUND=1`, and poll `os.Stat` until inode `1` indicates readiness. `JUmount` checks existence/mountpoint/corruption, gets device refs, unmounts the target, and unmounts the shared ref only when it was the last reference.

### State, Persistence, And Dependencies
State is local filesystem and kernel mount state. Cache cleanup deletes `cacheDir/id/raw/chunks`. The backend depends on host JuiceFS binaries (`CeMountPath`, `CeCliPath`, `CliPath`), Kubernetes mount utilities, `os/exec`, syscall env/stat, and util helpers for timeouts, refs, and mountpoint inspection.

### Integration Points
This backend satisfies `MntInterface` for deployments that do not use mount pods. CSI node operations can use it to mount directly into target paths. It shares config settings and logging helpers with pod mode but not Kubernetes object state.

### Risks
`AddRefOfMount` panics, so callers must avoid it in process mode. `jmount` runs the mount command in a goroutine and does not retain or inspect process errors after startup; readiness polling is the only success signal. Cleanup depends on inode `1`, mount table parsing, and timeout behavior, which can vary by filesystem/kernel. Recursive delete uses external JuiceFS CLI and must not receive untrusted paths.

### Test Signals
`process_mount_test.go` covers constructor output, EE mount success/error, CE mount success and error branches, unmount behavior, and corrupted/path existence cases. Additional tests should cover create/delete volume, cache cleanup, and `RmrDir` command selection.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount_test.go

### Purpose
`process_mount_test.go` validates direct process mount behavior without performing real JuiceFS mounts. It uses GoMock mount interfaces and monkey patches filesystem/process functions to exercise success and failure branches.

### Important APIs, Types, And Functions
Tests cover `NewProcessMount`, `ProcessMount.JUmount`, and `ProcessMount.JMount`. Mocked dependencies include `k8sMount.PathExists`, `k8sMount.IsNotMountPoint`, `util.GetMountDeviceRefs`, `os.MkdirAll`, `os.Stat`, `syscall.Environ`, and `exec.Cmd.Run`.

### Control Flow
`TestProcessMount_JUmount` verifies successful unmount, PathExists errors, and unmount errors. `TestProcessMount_JMount` splits EE behavior (delegates to `Mount`) from CE behavior (directory checks, existing mount unmount, command run, inode readiness), then covers stat errors, inode-not-ready timeout path, PathExists errors, mkdir errors, mountpoint check errors, and pre-unmount errors.

### State, Persistence, And Dependencies
The tests do not persist real mount state. They depend heavily on monkey-patched global functions and GoMock expectations. Fake file info types from driver mocks provide inode `1` or `2` to simulate ready/unready mountpoints.

### Integration Points
These tests guard the local backend used by CSI mount operations when not using pod mode. They also protect interactions with `k8s.io/utils/mount.SafeFormatAndMount`.

### Risks
There is no direct coverage of `JCreateVolume`, `JDeleteVolume`, `GetMountRef`, `CleanCache`, or `RmrDir`. The CE mount command runs in a goroutine in production; monkey-patched `Run` returning nil does not verify process lifecycle or stderr handling. Timeout branches can be slow or flaky if contexts change.

### Test Signals
Failures usually indicate changed mountpoint readiness logic, changed EE/CE source classification, or changed unmount reference behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/juicefs/mount/process_mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client.go -->
## sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client.go

### Purpose
`client.go` wraps Kubernetes client-go for the CSI driver. It centralizes in-cluster configuration, QPS/Burst tuning, pod/secret/job/PV/PVC/storage/app object CRUD, pod logs, pod exec, events, configmaps, and a small node cache.

### Important APIs, Types, And Functions
Patch payload helper structs model JSON patch values. `K8sClient` stores the Kubernetes interface, rest config, API server list-cache flag, and one-minute node cache. Constructors are `NewClient`, `NewClientWithConfig`, and `newClient`. Resource methods include pod create/get/list/patch/update/delete/log, node list/get/cache, secret CRUD/patch, job CRUD/delete, PV/PVC/storage/app getters, `ExecuteInContainer`, configmap get/create/update, event create/list, and `ListPersistentVolumesByVolumeHandle`.

### Control Flow
`NewClient` reads in-cluster config, applies a 10s timeout, reads `KUBE_QPS` and `KUBE_BURST`, then constructs the wrapper. Listing methods translate label and field selectors into Kubernetes list options; pod listing can set `ResourceVersion=0` when `ENABLE_APISERVER_LIST_CACHE=true`. `CreatePod` sanitizes NUL characters out of toleration keys before submitting. `ExecuteInContainer` builds a pod exec request and streams over SPDY.

### State, Persistence, And Dependencies
Persistent external state is Kubernetes API objects. Internal state includes the rest config and node cache protected by a mutex. Dependencies include client-go Kubernetes, REST, SPDY remotecommand, Kubernetes API types, gRPC status codes, environment variables, and util helpers.

### Integration Points
`PodMount`, `resource` helpers, builder canary jobs, namespace inference, and other CSI components depend on this wrapper. It is also the unit-test seam for fake clients.

### Risks
`ExecuteInContainer` calls `rest.InClusterConfig()` again rather than reusing `K8sClient.RestConfig`, which can diverge in tests or custom configs. `ListPersistentVolumesByVolumeHandle` lists all PVs and filters client-side. Event creation uses the legacy core Event API. `CreatePod` silently mutates toleration keys. Cache and list-cache flags can trade freshness for speed.

### Test Signals
`client_test.go` covers constructor error cases and basic fake-client pod create/get/patch/update/delete. Additional coverage should include selector translation, node cache expiry, secret/job operations, exec config reuse, and toleration key cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client_test.go

### Purpose
`client_test.go` tests a narrow subset of the Kubernetes client wrapper, mainly constructor failure paths and pod CRUD/patch behavior against a fake clientset.

### Important APIs, Types, And Functions
Tests include `TestNewClient`, `TestK8sClient_CreatePod`, `TestK8sClient_GetPod`, `TestK8sClient_PatchPod`, `TestK8sClient_UpdatePod`, and `TestK8sClient_DeletePod`. They use gomonkey to patch `rest.InClusterConfig` and `kubernetes.NewForConfig`, and Kubernetes fake clients for pod operations.

### Control Flow
Constructor tests force nil config, config errors, and new-client errors. CRUD tests create fake `K8sClient` wrappers, optionally seed pods, invoke methods, and compare resulting pod objects or error expectations. Patch tests marshal JSON patch payloads and use `types.JSONPatchType`.

### State, Persistence, And Dependencies
All state is in fake Kubernetes clientsets. Dependencies include GoConvey, gomonkey, client-go fake, Kubernetes API types, and reflection.

### Integration Points
The tests protect the wrapper behavior used by `PodMount` and resource helpers for basic pod lifecycle operations.

### Risks
Coverage is shallow compared with `client.go`: no node cache, list selectors, secrets, jobs, events, logs, exec, configmaps, PV/PVC, or environment QPS/Burst parsing are tested. Fake client behavior differs from real API server validation.

### Test Signals
Failures indicate basic wrapper regressions or changed fake-client object semantics. New wrapper methods should add fake-client or integration tests where possible.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/k8sclient/kubelet_client.go -->
## sources/control-plane/juicefs-csi-driver/pkg/k8sclient/kubelet_client.go

### Purpose
`kubelet_client.go` implements a minimal HTTPS client for the kubelet `/pods/` endpoint. `PodMount` uses it to list local running pods faster than the API server and avoid mount-pod reuse/listing races.

### Important APIs, Types, And Functions
Constants define the default timeout and service account token file. `KubeletClient` stores host, port, and `http.Client`. `KubeletClientConfig` mirrors kubelet transport config fields. `makeTransport()` builds TLS/bearer-token transports. `NewKubeletClient(host, port)` reads cert/key/timeout env vars and creates the client. `Access()` validates `/pods/`. `GetNodeRunningPods()` fetches and decodes a `corev1.PodList`. `checkKubeletAccessErr()` tracks repeated access failures and exits after five.

### Control Flow
Construction chooses service-account bearer token unless client cert/key env vars are set, configures insecure TLS with server name `kubelet`, applies `KUBELET_TIMEOUT`, builds transport, and returns an HTTPS client. `Access` and `GetNodeRunningPods` perform GET requests, drain/close bodies, require 2xx status, decode JSON for pod lists, and reset/increment the global error counter.

### State, Persistence, And Dependencies
No Kubernetes objects are mutated. Internal process state includes global `kubeletAccessErrCount`. Dependencies include `net/http`, client-go transport/TLS helpers, service-account token file, kubelet HTTPS endpoint, environment variables, and Kubernetes core types.

### Integration Points
`NewPodMount` creates this client when `config.KubeletPort` and `config.HostIp` are set and `Access()` succeeds. `PodMount.listMountPodsOfUniqueId` uses `GetNodeRunningPods()` before falling back to API server listing.

### Risks
`checkKubeletAccessErr` calls `os.Exit(1)` after repeated failures, which can terminate the CSI node process from a helper path. TLS defaults are insecure unless CA material is provided. The package-global error counter applies across all client instances. `/pods/` requires kubelet authn/authz permissions that vary by cluster.

### Test Signals
No tests are listed. Useful tests would use `httptest.Server` for success/status/decode errors, env parsing for timeout/certs, and access error counter behavior without actually exiting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/k8sclient/kubelet_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/dev_minor.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/dev_minor.go

### Purpose
`dev_minor.go` tracks FUSE device minor numbers for mounted JuiceFS paths. It supports later FUSE abort jobs by remembering the kernel connection minor associated with a mount pod before the mount disappears or becomes corrupted.

### Important APIs, Types, And Functions
`procSelfMountInfoPath` points at `/proc/self/mountinfo` and can be overridden in tests. `devMinorCache` is a `sync.Map`. `SaveFuseDevMinor(podName, mntPath)` parses mountinfo and stores the minor. `GetSavedFuseDevMinor(podName)` retrieves it. `DeleteFuseDevMinor(podName)` removes it. `GetFuseDevMinor(mntPath)` scans mountinfo for the mount point with `fuse` or `fuse.*` fs type and returns the minor.

### Control Flow
Saving is best-effort: if parsing fails or no matching FUSE mount exists, nothing is stored. Retrieval type-asserts the cached value to `uint32`. Deletion simply removes the key.

### State, Persistence, And Dependencies
State is in-memory only and process-local. It is not persisted to Kubernetes despite the TODO suggesting mount pod annotations. Dependencies include `k8s.io/utils/mount.ParseMountInfo`, strings, and sync.

### Integration Points
`PodMount.JUmount` calls `SaveFuseDevMinor` before deleting a no-ref mount pod. `builder.NewFuseAbortJob` can use the saved minor to target `/sys/fs/fuse/connections/<minor>`.

### Risks
The cache is lost on process restart, so recovery after restart may lack dev minor data. `GetSavedFuseDevMinor` assumes all stored values have the expected type. Mountinfo parsing is namespace-dependent; the CSI process must see the relevant mount namespace.

### Test Signals
No tests in this subset. Useful coverage would override `procSelfMountInfoPath` with fixture mountinfo, verify fuse/fuse.* matching, no-match behavior, and cache delete semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/dev_minor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/dispatch/pool.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/dispatch/pool.go

### Purpose
`pool.go` provides a tiny bounded concurrency helper. It limits worker goroutines using a buffered channel and offers both synchronous wait-for-result and fire-and-forget modes.

### Important APIs, Types, And Functions
`Pool` has `Num` and `PoolCh`. `NewPool(num)` clamps num to at least one. `RunAndWait(ctx, worker)` acquires a slot, runs the worker in a goroutine, and waits for either context cancellation or the worker error. `Run(ctx, worker)` starts a goroutine that acquires a slot and invokes the worker without returning a result.

### Control Flow
`RunAndWait` sends to `PoolCh` before starting the goroutine, defers slot release inside the goroutine, and selects between `ctx.Done()` and `errCh`. `Run` starts a goroutine first, then acquires a slot inside it, so callers do not block on pool capacity.

### State, Persistence, And Dependencies
State is in-memory channel occupancy. There is no persistence. Dependencies are only `context` and `fmt`.

### Integration Points
Any driver code needing bounded dispatch can use it. The helper is generic and not JuiceFS-specific.

### Risks
`RunAndWait` closes `errCh` with a defer in the caller after receiving; if context returns first, the worker goroutine may later send to a closed channel, causing a panic. `Run` has no error propagation and can accumulate blocked goroutines waiting for slots. Returned context errors are collapsed to `fmt.Errorf("context timeout")`, losing cancellation details.

### Test Signals
No tests are listed. Useful tests should cover cancellation before worker completion, slot release, num clamping, and the potential send-on-closed-channel race.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/dispatch/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/log.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/log.go

### Purpose
`log.go` provides context-aware logger propagation and secret redaction for map-based configuration data. It lets call chains use a logger stored in context and provides a utility to strip sensitive values before logging.

### Important APIs, Types, And Functions
`LogKey` and `LoggerType` define the context key. `WithLog(parentCtx, log)` stores a `klog.Logger`. `GenLog(ctx, log, name)` returns the context logger if present, otherwise a named child logger when `name` is non-empty. `stripKeys` lists sensitive keys. `StripSecret(secret)` copies a string map, replaces sensitive keys with `"***"`, and recursively redacts JSON `initconfig`.

### Control Flow
Logger generation is first context lookup, then optional `WithName`. Secret stripping copies the input map to avoid mutation, checks known key names exactly, parses `initconfig` as JSON object if present, recursively strips it, and marshals it back.

### State, Persistence, And Dependencies
There is no persistent state. Dependencies are `context`, `encoding/json`, and `klog/v2`.

### Integration Points
Mount and resource code call `util.GenLog` to preserve operation-scoped loggers. Configuration and secret logging paths can call `StripSecret` before emitting user-provided settings.

### Risks
The context value is type-asserted without checking, so a wrong value under the same key panics. Redaction is exact-key and lowercase oriented; variants outside `stripKeys` are not masked. Invalid `initconfig` JSON becomes `"null"` or an empty marshaled structure after ignored errors, which can alter observability output.

### Test Signals
No tests are listed. Useful tests would assert non-mutation, nested `initconfig` redaction, missing/uppercase key behavior, and logger context override semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/job.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/job.go

### Purpose
`resource/job.go` provides Kubernetes Job status helpers and a wait loop for job completion. It is used by mount and lifecycle code to interpret batch job conditions and recycle stale jobs.

### Important APIs, Types, And Functions
`IsJobCompleted(job)` checks for a true `JobComplete` condition. `IsJobFailed(job)` checks for a true `JobFailed` condition. `GetJobStatus(job)` renders a compact status string from active/succeeded/failed/terminating counts and conditions. `IsJobShouldBeRecycled(job)` decides whether a completed/failed job should be manually deleted. `WaitForJobComplete(ctx, client, name, timeout)` polls until success, failure, NotFound, or timeout.

### Control Flow
Status helpers iterate conditions. Recycle logic returns false unless the job is terminal, true if TTL is absent, false for failed jobs without completion time, and true if completion time plus TTL is before now. The wait loop ticks every two seconds, treats NotFound as success, fails on `JobFailed`, returns nil on `JobComplete`, and on timeout tries to fetch the job for a final status.

### State, Persistence, And Dependencies
No state is persisted here; it reads Kubernetes Job status through `K8sClient`. Dependencies include Kubernetes batch/core APIs, `config.Namespace`, `k8sclient`, and time.

### Integration Points
`PodMount.waitUntilJobCompleted` has its own shorter wait loop but uses `IsJobCompleted` and `IsJobShouldBeRecycled`. Other lifecycle controllers can call `WaitForJobComplete`.

### Risks
NotFound-as-success is appropriate for TTL cleanup but can hide unexpected deletion. Timeout handling calls `client.GetJob` with the already-expired `waitCtx`, which may return context errors instead of useful status. `GetJobStatus` overwrites status by count order before appending conditions, so mixed states need careful interpretation.

### Test Signals
`job_test.go` covers complete/failed condition recognition and recycle decisions for TTL/no-TTL/expired/nonterminal/nil-completion cases. Wait-loop behavior is not covered.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/job_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/job_test.go

### Purpose
`job_test.go` verifies the pure Job status helpers in `resource/job.go`. It documents how completion, failure, and recycle decisions are expected to behave for representative Kubernetes Job statuses.

### Important APIs, Types, And Functions
Tests are `TestIsJobCompleted`, `TestIsJobFailed`, and `TestIsJobShouldBeRecycled`. They construct `batchv1.Job` objects with controlled conditions, TTLs, and completion times.

### Control Flow
The first two tests use table cases with complete and failed conditions. The recycle test uses current time, a one-second TTL, and cases for fresh completed jobs, no TTL, completion time older than TTL, non-complete jobs, and failed jobs without completion time.

### State, Persistence, And Dependencies
There is no external state. Dependencies are Kubernetes batch/core/meta APIs and `time`.

### Integration Points
These tests protect helper behavior consumed by mount job wait/recycle paths.

### Risks
`WaitForJobComplete` is not tested. Edge cases such as multiple conditions, terminating count rendering, and failed jobs with old completion times are not covered.

### Test Signals
Failures indicate changed terminal-condition interpretation or cleanup policy. Any change to TTL behavior should update this suite.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/namespace.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/namespace.go

### Purpose
`namespace.go` infers an application namespace when incoming pod data does not include one. It handles direct namespace/request namespace, default fallback, and a JuiceFS PV/PVC-based lookup for controller-owned pods affected by missing namespace data.

### Important APIs, Types, And Functions
`GetNamespace(ctx, client, pod, reqNs)` is the main API. `checkOwner(ctx, client, ownerRefs, namespace)` verifies whether pod owners exist in a candidate namespace for ReplicaSet, StatefulSet, DaemonSet, or Job.

### Control Flow
`GetNamespace` returns `pod.Namespace` if set, then `reqNs` if provided, then `"default"` when the pod has no owners. Otherwise it lists all PVs, filters JuiceFS CSI PVs with claim refs, walks pod PVC volumes, matches PVC names to PV claim names, validates the pod owner in the PV claim namespace, and returns that namespace. NotFound owner checks cause the candidate to be skipped; other errors abort.

### State, Persistence, And Dependencies
The function reads Kubernetes PV and owner resources but does not mutate them. Dependencies include `K8sClient`, Kubernetes core/meta errors, `config.DriverName`, and owner resource getters.

### Integration Points
Used by CSI code that receives incomplete pod namespace context and needs to find the correct PVC namespace for JuiceFS volumes.

### Risks
It lists all PVs and filters client-side, which can be expensive. Matching only by PVC name before owner validation can be ambiguous across namespaces. `checkOwner` returns on the first owner reference, so pods with multiple owners may not be fully considered. Unsupported owner kinds lead to `no owner found`.

### Test Signals
No tests in this subset. Useful tests should cover direct namespace, request namespace, default fallback, owner kind resolution, NotFound skip behavior, and ambiguous PVC names.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/namespace.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pod.go -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pod.go -->
