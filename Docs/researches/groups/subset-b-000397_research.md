# subset-b-000397 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc.go

### Purpose
`pvc.go` provides metadata substitution and reclaim-safety helpers for JuiceFS CSI PVC/PV resources. It resolves PVC/node placeholders in strings, resolves secret template variables, decides whether a subPath or provisioner secret is still shared by other PVs, and patches secret finalizers.

### Important APIs, Types, And Functions
`objectMetadata` stores simple data, labels, and annotations. `ObjectMeta` joins PVC and node metadata. `NewObjectMeta` builds that structure from a PVC and optional node. `StringParser` and `objectMetadata.stringParser` replace `${.PVC.name}`, `${.pvc.namespace}`, `${.node.labels.key}`, and similar placeholders. `ResolveSecret` expands `${pvc.name}`, `${pvc.namespace}`, `${pv.name}`, and `${pvc.annotations['key']}`. `CheckForSubPath` protects shared subPath deletion. `CheckForSecretFinalizer`, `AddSecretFinalizer`, `RemoveSecretFinalizer`, and `patchSecretFinalizer` manage finalizers on Kubernetes Secrets.

### Control Flow
`StringParser` applies a package regex to find placeholders, dispatches on `PVC`/`pvc`/`node`, and replaces each placeholder with the matching metadata map entry or an empty string for missing map keys. `CheckForSubPath` returns immediately for empty path patterns, rejects root subPaths, lists all PVs in the same StorageClass, and blocks deletion if another live PV has the same CSI `subPath`. `CheckForSecretFinalizer` similarly lists PVs in the same StorageClass and blocks finalizer removal if any other live PV references the same provisioner secret namespace/name. Finalizer updates mutate the local object, JSON-patch `/metadata/finalizers`, and call the k8s client.

### State, Persistence, And Dependencies
Persistent state is in Kubernetes PVs and Secrets. The file depends on corev1 resources, JSON Patch, controller-runtime finalizer helpers, the local k8s client wrapper, and JuiceFS `common.ProvisionerSecret*` volume-attribute keys. Local state is only transient metadata maps and patch payloads.

### Integration Points
Provisioning and cleanup paths can use these helpers to expand user-provided path/secret templates and avoid deleting shared JuiceFS subdirectories or secrets while another PV still references them. The finalizer helpers integrate with controller cleanup ownership around generated or user-supplied secrets.

### Risks
The placeholder regex and direct map lookups silently replace unknown keys with empty strings, which can hide misconfigured templates. `CheckForSubPath` and `CheckForSecretFinalizer` assume `volume.Spec.PersistentVolumeSource.CSI` and its attributes exist; callers must only pass JuiceFS CSI PVs. Both list all PVs and filter in memory, so very large clusters make deletion checks more expensive and race-prone. JSON Patch uses `replace` on `/metadata/finalizers`; a Secret without that path or with stale resource version behavior may require client retry at a higher layer.

### Test Signals
Useful signals are placeholder replacement for PVC/node data, labels, annotations, lowercase `pvc`, missing keys, subPath root rejection, shared subPath prevention, empty path-pattern allowance, shared secret blocking, no StorageClass/secret bypass, and finalizer patch behavior under already-present/already-absent finalizers.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc_test.go

### Purpose
`pvc_test.go` validates the metadata parsing and PVC/PV cleanup-safety contracts from `pvc.go`. It acts as the behavior reference for template substitution, subPath deletion gating, secret template expansion, and secret finalizer sharing decisions.

### Important APIs, Types, And Functions
The file tests `ObjectMeta.StringParser`, `CheckForSubPath`, `ObjectMeta.ResolveSecret`, and `CheckForSecretFinalizer`. It uses fake Kubernetes clientsets and `k8s.K8sClient` wrappers to simulate existing PVs.

### Control Flow
`TestObjectMetadata_StringParser` builds `ObjectMeta` by hand and verifies replacements for PVC names/namespaces, labels, annotations, node names, node pod CIDR, and node annotations with dotted/slashed keys. `TestCheckForSubPath` creates fake PVs, calls the helper with a target PV and path pattern, and checks the boolean/error result. `TestResolveSecret` validates `os.Expand`-style variable substitution. The finalizer test constructs target and peer PVs with storage classes and secret attributes to determine whether finalizer removal should be allowed.

### State, Persistence, And Dependencies
State is confined to fake Kubernetes API objects. Dependencies include Kubernetes fake clientsets, corev1 PV/PVC structs, metav1 metadata, and the project k8s client wrapper. No real cluster or filesystem is touched.

### Integration Points
The tests protect controller cleanup behavior where deleting a PV could delete a backing JuiceFS subPath or generated secret. They also protect StorageClass parameter and secret templating logic that users rely on for PVC- and node-derived configuration.

### Risks
The tests do not cover nil CSI sources, nil volume attributes, or client list errors, even though the production helpers dereference CSI fields. The placeholder tests accept empty-string replacement for missing keys, so they lock in permissive behavior. Fake clientsets do not model resource-version conflicts for JSON Patch finalizer updates.

### Test Signals
Strong signals include correct handling of uppercase/lowercase PVC placeholder names, annotations with dotted domains, root subPath refusal, shared-subPath refusal, no-peer deletion approval, `${pv.name}` substitution, and secret finalizer retention when another live PV references the same provisioner secret.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/pvc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/secret.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/secret.go

### Purpose
`secret.go` centralizes create-or-update behavior for JuiceFS CSI Kubernetes Secrets and provides the generated secret-name convention for unique mount IDs.

### Important APIs, Types, And Functions
`CreateOrUpdateSecret(ctx, client, secret)` creates the Secret when missing or JSON-patches `/data` and `/metadata/ownerReferences` when data or owner refs differ. `GetSecretNameByUniqueId(uniqueId)` returns `juicefs-<uniqueId>-secret`.

### Control Flow
The create/update function runs under `retry.RetryOnConflict`. It gets the old secret from `jfsConfig.Namespace` rather than `secret.Namespace`; a not-found result creates the provided secret. For existing secrets, it compares desired `StringData` against existing `Data`, checks data count differences, merges a single new owner reference by UID when provided, builds replacement JSON Patch operations, and applies them through `PatchSecret`.

### State, Persistence, And Dependencies
The function persists Kubernetes Secret data and owner references. It depends on client-go retry behavior, Kubernetes API error classification, JSON Patch, the project k8s client wrapper, global CSI namespace config, and contextual logging through `util.GenLog`.

### Integration Points
The helper is used by resource/controller code that needs idempotent mount or provisioning secrets. Owner-reference merging lets multiple PVCs or generated objects keep ownership ties without dropping existing references.

### Risks
The get path always uses `jfsConfig.Namespace`, while patch/create logs and the secret object may carry another namespace; callers must understand this namespace convention. Only the first desired owner reference is merged. The patch replaces the entire data map and ownerReferences array, which can remove fields not represented in `StringData` or previously merged owner refs if the comparison path changes. Secret labels, annotations, type, and binary-only `Data` keys are not preserved from the desired object.

### Test Signals
Important tests would cover create on not-found, no-op unchanged secret, StringData value changes, data key count changes, owner-reference merge by UID, conflict retry, namespace mismatch behavior, and preservation/removal semantics for fields outside `/data` and `/metadata/ownerReferences`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/secret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/terminal.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/terminal.go

### Purpose
`terminal.go` bridges browser/websocket terminal traffic to Kubernetes pod exec streams and provides file/log download helpers for pods. It supports interactive shell sessions, terminal resize messages, heartbeat timeout, direct command output streaming, and safe-ish log export.

### Important APIs, Types, And Functions
`terminalSession` implements `io.Reader`, `io.Writer`, and `remotecommand.TerminalSizeQueue`. `NewTerminalSession` starts heartbeat monitoring. `Write`, `Read`, and `Next` adapt websocket messages to SPDY exec streams. `ExecInPod` opens a TTY exec stream. `DownloadPodFile` streams stdout/stderr from a pod exec command to an `io.Writer`. `DownloadPodLog` streams Kubernetes pod logs into a local file under `/tmp`.

### Control Flow
`Read` receives a websocket message, decodes JSON containing `type`, `data`, `rows`, and `cols`, and returns stdin bytes, queues resize events, responds to pings, or emits the configured end-of-transmission string on protocol errors/default cases. `checkHeartbeat` closes the websocket when no ping has been observed for more than one minute. Exec/download functions build `PodExecOptions`, create a SPDY executor from the REST config and request URL, and call `StreamWithContext`. Log download validates the path prefix, opens the pod log stream, creates/truncates the destination file, copies the stream, and flushes the buffered writer.

### State, Persistence, And Dependencies
`terminalSession` keeps websocket connection state, a size channel, end-of-transmission sentinel, and last heartbeat time. Persistent side effects are local files written by `DownloadPodLog`. Dependencies include `golang.org/x/net/websocket`, Kubernetes client-go REST/SPDY remotecommand, corev1 pod exec/log APIs, and local resource logging.

### Integration Points
Dashboard or troubleshooting components can use this file to exec into mount pods or application pods, download files via `cat`/similar commands, and save pod logs. It sits between HTTP/websocket handlers and Kubernetes API server exec/log subresources.

### Risks
`Next` blocks forever if no resize event arrives; that is normal for the Kubernetes interface but can pin goroutines if streams leak. `Read` returns `0, nil` after resize/ping, which can cause tight read loops depending on caller behavior. The `/tmp` path check is a simple prefix test, so `/tmpfoo` passes and symlinks under `/tmp` are not controlled. `DownloadPodFile` merges stderr into the same writer as stdout. Heartbeat timestamps are updated without synchronization, creating a potential data race under the Go race detector.

### Test Signals
Useful coverage includes websocket stdin/resize/ping/default messages, malformed JSON behavior, heartbeat close after timeout, SPDY executor construction errors, command stream errors, log path rejection outside `/tmp`, copy/flush failures, and cancellation propagation through `StreamWithContext`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/terminal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume.go

### Purpose
`volume.go` detects which PVC-backed volumes in a pod are JuiceFS CSI volumes and provides an in-process lock table for serializing work by volume ID.

### Important APIs, Types, And Functions
`PVPair` groups a `PersistentVolume` and its claiming `PersistentVolumeClaim`. `GetVolumes(ctx, client, pod, reqNs)` returns whether the pod uses JuiceFS and all matching PV/PVC pairs. `getVol` implements the scan. `VolumeLocks`, `SharedVolumeLocks`, `NewVolumeLocks`, `TryAcquire`, and `Release` implement coarse volume-ID locks.

### Control Flow
`GetVolumes` resolves the effective namespace via `GetNamespace`, sets `pod.Namespace`, then delegates to `getVol`. `getVol` iterates pod volumes, fetches each referenced PVC, optionally fetches its StorageClass to detect dynamic JuiceFS provisioning, checks binding state, fetches the PV, and appends the pair if the PV CSI driver matches `config.DriverName`. If a PVC uses a JuiceFS StorageClass but is unbound, it returns an error instead of silently skipping. `TryAcquire` uses a mutex around a `sync.Map` check/store pair to provide atomic lock acquisition.

### State, Persistence, And Dependencies
The helper reads Kubernetes PVC, PV, StorageClass, and pod state through the project k8s client. The only local state is `SharedVolumeLocks`, a process-local lock map with no persistence across controller restarts. Dependencies include Kubernetes core/storage APIs, API error classification, and JuiceFS driver-name config.

### Integration Points
Admission sidecar mutation uses `GetVolumes` to decide whether a pod needs injection and which PV/PVC pairs to mutate. Controllers can use `VolumeLocks` to avoid concurrent operations on the same JuiceFS volume ID.

### Risks
The helper mutates the input pod namespace. StorageClass `NotFound` is tolerated so static PVs can still be detected by PV CSI driver, but other StorageClass errors abort the whole scan. A pod with multiple PVCs returns on the first fetch error. Process-local locks do not protect multi-replica controllers. `GetVolumes` requires helpers such as `GetNamespace` from adjacent files, so namespace resolution behavior is part of its contract.

### Test Signals
Tests should cover dynamic StorageClass detection, static CSI PV detection without an existing StorageClass, non-JuiceFS PV skip, unbound JuiceFS PVC error, multiple matching PVCs, missing PVC/PV errors, namespace override behavior, and lock acquisition/release contention.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume_test.go

### Purpose
`volume_test.go` validates JuiceFS PV/PVC discovery from pod volumes against fake Kubernetes resources.

### Important APIs, Types, And Functions
The file tests `GetVolumes` and the `PVPair` result contract. It constructs PVCs, PVs, a fake StorageClass name, fake clientset-backed `K8sClient`, and table-driven pod fixtures.

### Control Flow
The test pre-creates four PVCs and four PVs in a fake API server. Each table case builds a pod with one or more PVC volumes, calls `GetVolumes`, checks the `used` flag and result length, then matches each returned pair by PV/PVC name and compares full objects.

### State, Persistence, And Dependencies
State is fake Kubernetes API memory only. Dependencies include fake clientsets, corev1 resource structs, reflection comparison, and the local k8s client wrapper.

### Integration Points
The tests protect admission webhook behavior that relies on `GetVolumes` to decide whether to mutate an app pod. They also confirm that a missing/non-JuiceFS StorageClass does not prevent static PV CSI detection.

### Risks
The test does not create an actual StorageClass for the fake `StorageClassName`, so it mainly exercises fallback-to-PV detection rather than StorageClass provisioner detection. It does not cover unbound PVCs, missing resources, namespace override, or API errors. Full-object `DeepEqual` can be sensitive to fake client defaulting if client-go behavior changes.

### Test Signals
Covered signals include a single JuiceFS CSI PV, a non-CSI HostPath PV skip, two JuiceFS volumes in one pod, and a PVC with an unknown StorageClass still being recognized by bound PV CSI driver.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/volume_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/security/escape.go

### Purpose
`escape.go` provides a small shell-escaping helper for values inserted into bash command lines, focused on characters that can trigger command substitution, command chaining, redirection, or pipelines.

### Important APIs, Types, And Functions
`EscapeBashStr(s)` returns the original string when no risky characters are present, otherwise escapes backslashes and single quotes and wraps the value in ANSI-C `$'...'` quoting. `containsOne` checks whether a string contains any rune from a provided set.

### Control Flow
`EscapeBashStr` checks for `$`, backtick, `&`, `;`, `>`, `|`, `(`, or `)`. When found, it doubles backslashes, escapes single quotes as `\'`, and formats the result as `$'<escaped>'`. Strings without those characters are left unquoted.

### State, Persistence, And Dependencies
There is no persistent state. Dependencies are only `fmt` and `strings`. The helper is intended for command construction in JuiceFS mount/auth flows where user-controlled secrets or URLs may appear in shell text.

### Integration Points
Builder code that creates shell commands can use this helper to reduce injection risk for meta URLs, access keys, and other configuration values that are passed through `/bin/sh` or `bash`.

### Risks
The risky-character list is intentionally narrow and does not quote whitespace, glob characters, newlines, braces, or other shell metacharacters. `$'...'` is bash-specific; shells without ANSI-C quoting will not behave the same. Escaping only happens when a listed character appears, so a value containing spaces can still be split if inserted into an unquoted command position.

### Test Signals
Tests should validate round-trip shell interpretation, command-substitution suppression, quote/backslash escaping, and behavior for whitespace-only risky values if callers rely on preserving a single argument.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/security/escape_test.go

### Purpose
`escape_test.go` verifies `EscapeBashStr` by comparing expected strings and executing them through bash to confirm round-trip output.

### Important APIs, Types, And Functions
The test covers `EscapeBashStr` and indirectly `containsOne`. It uses `exec.Command("bash", "-c", fmt.Sprintf("echo %s", escaped))` and trims output with `strings.TrimSpace`.

### Control Flow
For each case, the test checks the exact escaped representation, then runs `echo <escaped>` in bash. If the command succeeds, it compares the trimmed output with the original input.

### State, Persistence, And Dependencies
No repository state is changed. The test depends on a local `bash` binary and the host shell behavior for ANSI-C quoting. It does not use Kubernetes.

### Integration Points
This test is a safety net for mount/auth command generation that must preserve literal values containing shell injection syntax.

### Risks
The test itself uses `echo`, which can have portability quirks for backslash-like content, though bash built-in behavior is stable enough for these cases. `TrimSpace` hides leading/trailing whitespace changes. The test does not cover whitespace-only splitting because the helper intentionally leaves strings without listed metacharacters unquoted.

### Test Signals
Covered signals include unchanged safe strings, command substitution and backtick strings being quoted, embedded single quotes, pre-existing backslashes, nested `$'...'` text, and bash round-trip output matching the original value.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/security/escape_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/util.go

### Purpose
`util.go` is a broad utility module for JuiceFS CSI. It handles endpoint parsing, mountinfo parsing, string/slice helpers, time parsing, shell quoting, mount/unmount helpers, mount-command introspection, image/version capability checks, disk usage, Prometheus registry creation, quantity parsing, directory creation, config parsing, internal filename decisions, generic helpers, illegal-character cleanup, and snapshot handle formatting.

### Important APIs, Types, And Functions
Key types are `mountInfo`, `ClientVersion`, and `JuiceConf`. Important functions include `ParseEndpoint`, `GetMountDeviceRefs`, `ContainsString`, `ContainsPrefix`, `ContainSubString`, `GetReferenceKey`, `GetTimeAfterDelay`, `GetTime`, `QuoteForShell`, `StripReadonlyOption`, `StripPasswd`, `RandStringRunes`, `DoWithTimeout`, `CheckDynamicPV`, `UmountPath`, `GetMountPathOfSidecar`, `GetMountPathOfPod`, `parseMntPath`, `CheckExpectValue`, `ImageResol`, `GetDiskUsage`, `NewPrometheus`, `ParseToBytes`, `Exists`, `MkdirIfNotExist`, version support functions, `ParseConfig`, `ContainsEnv`/volume helpers, `GetMountOptionsOfPod`, `GetJfsInternalFileName`, generic copy/merge/sort helpers, `ParseSubdirFromMountOptions`, `IsConfigEncrypted`, `CopySlice`, `RemoveIllegalChars`, `EnsureSnapshotHandle`, and `ParseSnapshotHandle`.

### Control Flow
Endpoint parsing accepts `tcp` or `unix`, removes stale unix sockets, and returns scheme/address. Mountinfo parsing reads `/proc/self/mountinfo`, parses fields around the `-` separator, finds the backing mount for a path, and returns other mountpoints sharing the same major/minor and filesystem type. Time helpers now emit RFC3339 UTC delayed timestamps and parse either RFC3339 or legacy local-time layout. Mount command parsing reads the third command element, takes the final newline-separated command, strips leading `exec`, and extracts `/jfs/<id>` or `/mnt/jfs` mount paths. Version helpers parse image tags and `juicefs version` strings, then compare CE/EE minimums for fuse pass, binary upgrade, quota path creation, and config encryption. `DoWithTimeout` runs a function in a child context and races parent cancellation, child deadline, and function completion.

### State, Persistence, And Dependencies
The file reads `/proc/self/mountinfo`, invokes `umount`, uses `syscall.Statfs`, creates directories, removes unix socket files, parses JSON, and creates Prometheus registries. Dependencies include Kubernetes `corev1`, Prometheus, klog, `k8s.io/utils/io.ConsistentRead`, standard filesystem/process packages, and project common constants.

### Integration Points
These helpers are shared across CSI endpoint startup, node mount cleanup, mount-pod and sidecar introspection, webhook decisions, controller cleanup, metrics exposure, snapshot identity, and version-gated feature rollout.

### Risks
`parseMntPath` and `GetMountOptionsOfPod` depend on specific shell command layout and can panic if `strings.Fields` returns an empty slice. `DoWithTimeout` can return `"function timeout"` when the child deadline fires even if the goroutine is about to return, and it does not wait for non-cooperative functions to stop. `Exists` returns true for permission and other stat errors. `StripPasswd` is heuristic and may mishandle uncommon URI shapes. Version parsing treats many unrecognized tags as dev and therefore unsupported. `GetMountDeviceRefs` is Linux/procfs-specific. `RemoveIllegalChars` removes all non-ASCII printable characters, which can discard valid Unicode names.

### Test Signals
High-value signals include endpoint parse/remove errors, mountinfo malformed lines, symlink/corrupt mountpoint paths, time-zone round trips, unmount tolerated messages, mount command variants, image/version threshold boundaries, byte parsing with unit suffixes, config encryption JSON variants, internal filename prefix behavior, snapshot handle parse errors, and illegal-character filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/util_test.go

### Purpose
`util_test.go` is the main unit-test specification for the broad helpers in `util.go`. It covers parsing, version gates, mount-command introspection, string helpers, time-zone behavior, map/slice utilities, and input cleanup.

### Important APIs, Types, And Functions
The file tests `ContainsString`, `ParseEndpoint`, `GetReferenceKey`, `GetTimeAfterDelay`, `GetTime`, `QuoteForShell`, `StripPasswd`, `CheckDynamicPV`, `ContainsPrefix`, `StripReadonlyOption`, `CheckExpectValue`, `ImageResol`, `ParseToBytes`, `parseClientVersionFromImage`, `SupportFusePass`, `GetMountPathOfPod`, `parseMntPath`, `SupportUpgradeRecreate`, `SupportUpgradeBinary`, `GetMountOptionsOfPod`, `SortBy`, `MergeMap`, `DeDuplicate`, `GetMountPathOfSidecar`, `SupportQuotaPathCreate`, `IsConfigEncrypted`, and `RemoveIllegalChars`.

### Control Flow
Most tests are table driven. Some use gomonkey/goconvey to force `url.Parse`, `os.Remove`, and `os.IsNotExist` error paths. Time tests explicitly alter `time.Local` to prove RFC3339 output round-trips correctly across UTC, UTC+8, and UTC-5 while legacy zone-less strings are parsed in local time. Mount path tests feed CE/EE command strings with init config, ACL symlink setup, `exec`, subpath creation, and malformed mount destinations.

### State, Persistence, And Dependencies
The tests are mostly pure and in-memory. `ParseEndpoint` can remove a unix socket path, but error tests monkey patch filesystem calls. Dependencies include gomonkey, goconvey, Kubernetes corev1 structs, metav1, common constants, and local time-zone manipulation.

### Integration Points
This suite protects behavior used by CSI server startup, mount pod lifecycle, controller cleanup, webhook sidecar handling, feature-gate decisions, and dashboard diagnostics. The time-zone tests specifically preserve compatibility between new RFC3339 scheduled times and legacy local-time timestamps.

### Risks
The tests do not cover proc mountinfo parsing, actual unmount execution, disk usage errors, Prometheus registry labels, snapshot handle helpers, or generic pointer/copy helpers. Some tests depend on exact current time to the second and allow small drift only in the explicit round-trip test. The tested command parsing still assumes the mount command is the final shell line.

### Test Signals
Strong signals include unsupported endpoint rejection, unix socket remove error handling, SHA reference-key stability, local-vs-UTC time parsing, password redaction, dynamic PV regex, CE/EE image classification, byte units, fuse-pass and upgrade thresholds, mount path extraction from several command layouts, map merge precedence, duplicate removal preserving order, sidecar label/container validation, quota support thresholds, config encryption booleans, and ASCII/nonprintable cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/handler.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/handler.go

### Purpose
`handler.go` implements admission webhook handlers for JuiceFS CSI pod sidecar injection, secret validation, static PV uniqueness validation, and mount-pod eviction protection.

### Important APIs, Types, And Functions
`SidecarHandler`, `NewSidecarHandler`, and `Handle` process pod mutation requests. `SecretHandler` validates Secrets through `validator.SecretValidator`. `PVHandler` rejects duplicate static JuiceFS PV volume handles. `EvictPodHandler` denies eviction of referenced mount pods in the CSI namespace. Handler constructors create controller-runtime admission decoders.

### Control Flow
`SidecarHandler.Handle` decodes the pod, skips if injection is already done or disabled by labels, calls `resource.GetVolumes`, allows non-JuiceFS pods, constructs a JuiceFS provider and `SidecarMutate`, mutates the pod, marshals it, and returns a JSON patch response. `SecretHandler` decodes a Secret and calls validator logic. `PVHandler` ignores non-JuiceFS or dynamically provisioned PVs, lists existing PVs by volume handle, and denies if any exist. `EvictPodHandler` only acts on `CREATE` of `pods/eviction` in `config.Namespace`; it fetches the pod, verifies mount-pod labels, then denies eviction when any annotation key equals `util.GetReferenceKey(annotationValue)`.

### State, Persistence, And Dependencies
The handlers read and write no state directly except returning admission patches/decisions. They depend on controller-runtime admission APIs, Kubernetes corev1, project k8s client, JuiceFS provider creation, resource helpers, mutator and validator packages, global config, and common labels.

### Integration Points
Registered webhook paths from `register.go` and installation manifests route Kubernetes admission requests here. Sidecar mutation ties pod admission to PV/PVC lookup, per-PVC secret creation, and mount sidecar generation. PV validation protects static PV uniqueness. Eviction validation integrates with Kubernetes drain/eviction flows.

### Risks
Sidecar injection returns bad request on volume lookup or mutation failures, so webhook `failurePolicy` determines cluster impact. `PVHandler` can deny the new PV because `ListPersistentVolumesByVolumeHandle` includes the current object if API timing changes. `EvictPodHandler` trusts annotation key/value hash convention and only applies in the configured namespace. Secret validation creates a provider with nil clients, so validator behavior depends on provider methods not requiring Kubernetes.

### Test Signals
Important tests include decode failures, skip labels, non-JuiceFS pod allowance, multi-PVC mutation patch shape, mutation errors, secret validation errors, static PV duplicate volume-handle denial, dynamic PV allowance, eviction subresource filtering, not-found pod allowance, non-mount pod allowance, and referenced mount-pod eviction denial.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/mutate.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/mutate.go

### Purpose
`mutate.go` defines the minimal interface contract for admission pod mutators in the JuiceFS webhook package.

### Important APIs, Types, And Functions
`Mutate` is an interface with `Mutate(ctx context.Context, pod *corev1.Pod) (*corev1.Pod, error)`.

### Control Flow
There is no implementation flow in this file. Concrete mutators, especially `SidecarMutate`, satisfy this interface and can be used through interface-typed constructors.

### State, Persistence, And Dependencies
No state is stored. Dependencies are `context` and Kubernetes `corev1.Pod`.

### Integration Points
`handler.go` creates a mutator through `mutate.NewSidecarMutate` and invokes it through this interface, keeping the admission handler decoupled from concrete mutation internals.

### Risks
The interface is intentionally broad and does not specify whether implementations mutate the input pod or return a deep copy. Callers should treat the returned pod as authoritative.

### Test Signals
Useful signals are compile-time interface assertions in concrete mutators and handler tests that exercise behavior through the interface rather than concrete-only methods.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/mutate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar.go

### Purpose
`sidecar.go` implements JuiceFS sidecar injection for pods admitted by the webhook. It converts PVC-backed volumes into hostPath mounts served by a generated JuiceFS mount sidecar or native sidecar init container, creates per-PVC secrets, and supports serverless-specific builders.

### Important APIs, Types, And Functions
`checkSupportNativeSidecar` gates native sidecars by Kubernetes version and global override. `SidecarMutate` holds the k8s client, JuiceFS provider, serverless flag, native sidecar support, PV/PVC pairs, and current `JfsSetting`. `NewSidecarMutate` discovers server version. `Mutate` loops over all PV pairs. `mutate` builds settings and injects resources. `Deduplicate`, `GetSettings`, `injectContainer`, `injectVolume`, `injectLabel`, `injectAnnotation`, and `createOrUpdateSecret` are the main subroutines.

### Control Flow
The constructor queries discovery `ServerVersion`, parses it, and enables native sidecar support for Kubernetes `>=1.29.0` unless the global override is set. For each PV/PVC pair, `mutate` reads node-publish secrets and volume attributes, overlays PVC annotations prefixed `juicefs`, resolves optional node metadata from `Spec.NodeName` or `NodeSelector`, parses a `JfsSetting`, selects a random mount path or a deterministic serverless PVC/UID path, enforces at least 1GiB quota capacity when quota is enabled, selects a builder, creates/updates a secret with the PVC as owner, builds a mount sidecar pod, deduplicates names, rewrites matching pod volumes/mounts, injects sidecar volumes, labels, annotations, and the container/init-container.

### State, Persistence, And Dependencies
Persistent state is the Kubernetes Secret created or updated for each PVC. The returned pod mutation is sent back as an admission patch. Dependencies include Kubernetes discovery/version APIs, corev1 resources, client-go retry, project config/global config, JuiceFS provider interface, mount builders, k8s client, resource PV pairs, and utility helpers.

### Integration Points
This is the core of webhook sidecar mode. It integrates pod admission with CSI PV attributes, PVC annotations, node labels/annotations for templating, builder-specific mount pod templates, serverless VCI/CCI modes, and Kubernetes native sidecar semantics.

### Risks
`GetSettings` assumes `pv.Spec.CSI.NodePublishSecretRef` is non-nil. Capacity below 1GiB fails admission when quota is enabled. `Deduplicate` only checks existing container/volume names and can still collide across multiple generated mount pods in edge cases. Secret update compares owner references by index, so reordered references can trigger updates. Native sidecar support is checked twice in the constructor. Pod volume rewrite affects app containers and, for native sidecars, init containers, but not ephemeral containers. Serverless mount paths based on PVC UID improve stability but can leak assumptions into hostPath layout.

### Test Signals
High-value tests include Kubernetes version/override gating, missing secret errors, PVC annotation overrides, node selector fallback, quota disabled/enabled capacity handling, serverless builder selection, secret create/update conflict paths, duplicate names across multiple PVCs, native sidecar init-container restart policy, volume/mount rewrite for app and init containers, and admission patch shape.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/mutate/sidecar.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/register.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/register.go

### Purpose
`register.go` wires JuiceFS admission handlers into a controller-runtime webhook server and defines their URL paths.

### Important APIs, Types, And Functions
Constants define `SidecarPath`, `ServerlessPath`, `SecretPath`, `PVPath`, and `EvictPodPath`. `Register(mgr, client)` registers mutating and optional validating webhook handlers.

### Control Flow
`Register` sets the controller-runtime logger, obtains the manager webhook server and scheme, always registers normal and serverless sidecar mutating handlers, and conditionally registers secret, PV, and eviction validators when `config.ValidatingWebhook` is true.

### State, Persistence, And Dependencies
The function mutates in-process manager/server registration state. Dependencies include controller-runtime manager/webhook packages, project config, k8s client, and handler constructors.

### Integration Points
The paths must match `juicefs-csi-webhook-install.sh` and deployment manifests. Admission requests for pod creation, secret validation, PV creation, and pod eviction reach `handler.go` through these registrations.

### Risks
Path drift between this file and generated installation manifests breaks webhooks. Validating handlers are gated by a process-global boolean, so deployment flags must align with installed `ValidatingWebhookConfiguration`. There is no idempotency guard if `Register` is called multiple times on the same server.

### Test Signals
Useful tests would assert registered paths and handler types under validating enabled/disabled modes and compare path constants against rendered webhook manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/register.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret.go

### Purpose
`secret.go` validates JuiceFS Secret content before admission, including config path shape, env serialization, and basic connectivity/authentication against CE or EE JuiceFS backends.

### Important APIs, Types, And Functions
`SecretValidator` wraps a `juicefs.Interface`. `NewSecretValidator` constructs it. `Validate(ctx, secret)` validates special `configs` and `envs` keys, builds a string secret map, obtains a `JfsSetting`, creates a temporary client config directory, and calls either `Status` for CE or `AuthFs` for EE. `ValidateConfigs` parses YAML/JSON into path mappings and requires non-empty absolute paths. `ValidateEnvs` parses YAML/JSON env maps.

### Control Flow
`Validate` first validates structured optional fields. It then copies all `secret.Data` bytes into strings, calls provider `Settings`, creates a temp dir under `os.TempDir`, assigns it to `ClientConfPath`, and defers cleanup. CE mode requires non-empty `metaurl` and calls `Status`; EE mode calls `AuthFs` in force mode.

### State, Persistence, And Dependencies
Temporary filesystem state is created and removed. External state may be contacted through the JuiceFS provider status/auth calls. Dependencies include Kubernetes Secrets, project config parsing helpers, the JuiceFS interface, and standard filesystem utilities.

### Integration Points
`SecretHandler` calls this validator for Kubernetes validating admission. Installed webhook configuration selects Secrets labeled for validation, so users can preflight mount secrets before workloads consume them.

### Risks
Validation can be slow or flaky because it can contact external metadata/auth services during admission. `failurePolicy` in manifests is Ignore, so validation failures may not block depending on installation. `ValidateConfigs` requires absolute paths but does not validate path existence. All secret bytes are converted to strings, which is fine for current config fields but unsuitable for arbitrary binary data.

### Test Signals
Needed tests include invalid configs YAML/JSON, empty config values, relative config paths, valid env maps, invalid env serialization, missing CE metaurl, provider `Settings` error, CE `Status` error, EE `AuthFs` error, temp-dir creation failure, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret_test.go

### Purpose
`secret_test.go` is a placeholder for future Secret validator tests.

### Important APIs, Types, And Functions
The only test function is `TestSecretValidate_Validate`, which currently contains `// TODO`.

### Control Flow
No validation logic is executed.

### State, Persistence, And Dependencies
No state is created. The file imports only `testing`.

### Integration Points
It marks the intended test location for `SecretValidator.Validate`, which is used by the validating admission handler.

### Risks
The absence of tests leaves admission-time secret validation under-covered, including external provider errors and config/env parser behavior.

### Test Signals
Future test signals should cover malformed configs/envs, CE and EE provider paths, temp directory errors, missing `metaurl`, and failure-policy expectations.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/secret_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/validator.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/validator.go

### Purpose
`validator.go` defines the generic validator interface used by webhook validation components.

### Important APIs, Types, And Functions
`Validator[T any]` declares `Validate(ctx context.Context, obj T) error`.

### Control Flow
There is no executable control flow beyond the interface declaration.

### State, Persistence, And Dependencies
No state is stored. The only dependency is `context`.

### Integration Points
`SecretValidator` asserts it implements `Validator[corev1.Secret]`. Additional validators can share the same typed interface.

### Risks
The interface does not distinguish transient from permanent errors or expose admission warning messages, so callers map all errors to a single admission failure path.

### Test Signals
Compile-time interface assertions in concrete validators are the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/validator/validator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/csi-doctor.sh -->
## sources/control-plane/juicefs-csi-driver/scripts/csi-doctor.sh

### Purpose
`csi-doctor.sh` is an operator diagnostic script for JuiceFS CSI. It discovers mount pods related to an application pod, prints debug information, locates app pods using a mount pod, collects CSI/mount/app/PV/PVC logs and YAMLs, runs `juicefs doctor` inside mount pods, and executes arbitrary commands in all mount pods.

### Important APIs, Types, And Functions
Commands include `debug`, `get-mount`, `get-oplog`, `get-app`, `collect`, `exec`, `doctor`, and `help`. Functions include `debug_app_pod`, `debug_pvc`, `get_mount_pod`, `get_oplog`, `get_app_pod`, `mount_exec`, `collect_pv`, `collect_juicefs_csi_msg`, `pd_collect`, `collect`, `doctor`, and `main`. Environment variables include `JFS_NS`, `APP_NS`, and `KBCTL`.

### Control Flow
`main` parses an action and optional app namespace. Debug flows read app pod events, PVCs, node name, PV CSI driver/volume handle, mount pod names on the same node, mount pod annotations that contain the app pod UID, mount pod logs, controller logs when PVCs are unbound, and CSI node logs. Collection flows create a temporary diagnosis directory, save app/PVC/PV/mount/CSI YAMLs, descriptions, logs, and resource usage, copy the script into a mount pod to run `doctor`, copy results back, tar the directory, and remove the temp directory. Lookup commands map app pods to mount pods or mount pods back to app pods using PV handles and reference annotations.

### State, Persistence, And Dependencies
The script reads Kubernetes state and writes local archives under the current directory after staging under `/tmp/<app>.diagnose`. It depends on `kubectl` or `KBCTL`, `timeout`, `grep -P`, `awk`, `tar`, `df`, `juicefs doctor` inside mount pods, and expected JuiceFS labels/annotations.

### Integration Points
It is a support tool for clusters running JuiceFS CSI. It depends on mount pods labeled `app.kubernetes.io/name=juicefs-mount`, CSI controller/node pod labels, PV CSI driver `csi.juicefs.com`, mount pod annotation conventions, and access log/internal file naming including `prefix-internal`.

### Risks
Many variables are unquoted, so names with unusual characters can break commands. `SHOULD_CHECK_CSI_CONRTROLLER` is misspelled but internally consistent. Some variables (`PVC_NAME`, `PV_NAME`, `diagnose_result`) are unused or referenced before assignment. Several paths call literal `kubectl` instead of `${kbctl}`. `grep -P` is not portable to all environments. The collection path assumes at least one mount pod exists before copying/running doctor. Logs and YAMLs may include secrets.

### Test Signals
Useful validation is best done with mocked kubectl output for app-to-PV-to-mount-pod discovery, unbound PVC controller-log triggering, app lookup from mount annotations, prefix-internal access-log path selection, no-mount-pod collection behavior, `KBCTL` override, and archive contents.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/csi-doctor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/juicefs-csi-webhook-install.sh -->
## sources/control-plane/juicefs-csi-driver/scripts/juicefs-csi-webhook-install.sh

### Purpose
`juicefs-csi-webhook-install.sh` prints or installs JuiceFS CSI manifests for webhook mode. It can generate self-signed TLS assets inline or use cert-manager resources for webhook serving certificates.

### Important APIs, Types, And Functions
Main commands are `install`, `print`, and `help`, with `-c/--with-certmanager`. `gen_webhook_manifests` creates OpenSSL CA/server keys and embeds base64 TLS data and CA bundles into generated YAML. `gen_webhook_manifests_with_cert_manager` emits cert-manager `Certificate`/`Issuer` resources and webhook annotations. `need_cmd`, `check_cmd`, `ensure`, and `main` support command validation and dispatch.

### Control Flow
The non-cert-manager path checks for `mktemp`, `openssl`, and `curl`, creates a temporary directory, generates CA and server cert/key for `juicefs-admission-webhook.kube-system.svc`, base64-encodes them, writes a large manifest, and substitutes TLS placeholders. The cert-manager path emits a similar manifest but relies on cert-manager CA injection and sets a placeholder CA bundle. `main` either pipes generated YAML to `kubectl apply -f -` or prints it.

### State, Persistence, And Dependencies
The script creates temporary local certificate files and, on install, persists Kubernetes RBAC, ServiceAccounts, controller/dashboard resources, Services, Secrets or cert-manager resources, CSIDriver, MutatingWebhookConfigurations, and ValidatingWebhookConfiguration. Dependencies include bash, OpenSSL, curl, kubectl, and optionally cert-manager in the target cluster.

### Integration Points
Generated webhook paths must match `register.go`: `/juicefs/inject-v1-pod`, `/juicefs/serverless/inject-v1-pod`, `/juicefs/validate-secret`, `/juicefs/validate-pv`, and `/juicefs/validate-evict-pod`. Namespace selectors opt pods into normal or serverless injection, and object selectors opt Secrets into validation.

### Risks
The manifest is embedded static YAML, so it can drift from kustomize/Helm sources and Go path constants. The self-signed cert lifetime and generated private key are managed outside cert rotation. `curl` is required even though the shown generation path primarily uses OpenSSL. `err` is referenced by `need_cmd`/`ensure` but not defined in the visible helper block, so missing command handling may fail unexpectedly. Generated resources are hard-coded to `kube-system` and `juicefs-admission-webhook`.

### Test Signals
Useful checks include shell syntax validation, `print` output applying through `kubectl --dry-run=server`, path constant parity with `register.go`, certificate SAN correctness, cert-manager output containing injection annotations, validating webhook failure policies, namespace/object selectors, and install behavior when required commands are missing.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/scripts/juicefs-csi-webhook-install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/app-pod-failure.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/app-pod-failure.yaml

### Purpose
This manifest defines a Chaos Mesh `PodChaos` experiment that periodically injects pod failure into one labeled application pod using JuiceFS CSI.

### Important APIs, Types, And Functions
The resource is `pingcap.com/v1alpha1`, kind `PodChaos`, named `app-pod-failure`. Key fields are `action: pod-failure`, `mode: one`, `duration: "60s"`, selector namespace `chaos-victim`, label selector `chaos: victim`, and scheduler cron `@every 5m`.

### Control Flow
Chaos Mesh schedules the experiment every five minutes, selects one matching pod in `chaos-victim`, and applies a pod-failure action for sixty seconds.

### State, Persistence, And Dependencies
Persistent state is the Chaos Mesh custom resource. It depends on Chaos Mesh CRDs/controllers and pods labeled by the overlay. The experiment affects live workload availability.

### Integration Points
The companion kustomization overlays the static-provisioning RWX example with namespace and common labels so this experiment targets the sample app.

### Risks
The selector is broad for all pods in `chaos-victim` with `chaos=victim`; common labels may also apply to non-app resources depending on kustomize output. `pod-failure` can mask storage-specific failures if app recovery behavior is not measured separately.

### Test Signals
Signals include Chaos Mesh admission accepting the CR, one victim pod being failed per schedule, JuiceFS mount recovery after app pod restart/failure, and no unintended namespace targeting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/app-pod-failure.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/kustomization.yaml

### Purpose
This kustomization assembles the app-pod-failure chaos scenario by combining a static RWX JuiceFS example with the PodChaos resource.

### Important APIs, Types, And Functions
It uses kustomize v1beta1, includes `../../../examples/static-provisioning-rwx` and `app-pod-failure.yaml`, sets namespace `chaos-victim`, and applies common label `chaos: victim`.

### Control Flow
Kustomize renders the base example and chaos resource into the `chaos-victim` namespace and labels resources so the PodChaos selector can find victim pods.

### State, Persistence, And Dependencies
Rendered manifests create application/storage resources and a Chaos Mesh experiment. It depends on the referenced example path and Chaos Mesh being installed.

### Integration Points
This overlay is included by the parent `tests/chaos/kustomization.yaml`. It links the target app and selector labels for the chaos experiment.

### Risks
Applying common labels to all resources can cause the chaos selector to match pods beyond the intended app if the base creates multiple pods. The relative base path must remain valid.

### Test Signals
Use `kustomize build` to verify namespace/label propagation, referenced base availability, and resulting PodChaos selector matching intended workload pods.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/chaos-mesh/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/chaos-mesh/kustomization.yaml

### Purpose
This kustomization installs or references Chaos Mesh resources required by the JuiceFS chaos tests.

### Important APIs, Types, And Functions
It uses kustomize v1beta1, includes remote resource `github.com/kustless/chaos-mesh`, and sets namespace `chaos-mesh`.

### Control Flow
Kustomize fetches the remote base and renders it into the `chaos-mesh` namespace.

### State, Persistence, And Dependencies
Persistent cluster state is the Chaos Mesh installation. It depends on network access to the remote GitHub base and that base remaining compatible.

### Integration Points
The parent chaos kustomization includes this alongside the app-pod-failure experiment so test clusters can install both Chaos Mesh and the scenario.

### Risks
The remote base is unpinned, so output can change over time or break builds. Network dependency can make validation flaky. Namespace assumptions must match the remote base.

### Test Signals
`kustomize build` and server-side dry-run should verify remote availability, CRD/controller installation, and namespace placement.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/chaos-mesh/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/kustomization.yaml

### Purpose
This top-level kustomization groups the JuiceFS CSI chaos test environment.

### Important APIs, Types, And Functions
It includes the `app-pod-failure` scenario and the `chaos-mesh` installation overlay.

### Control Flow
Kustomize renders both child resource trees in one build.

### State, Persistence, And Dependencies
Applying the output creates Chaos Mesh infrastructure and a victim workload/experiment. Dependencies are the two child kustomizations and their remote/local bases.

### Integration Points
This is the entry point for running the chaos fixture in validation pipelines or local clusters.

### Risks
Combining infrastructure and experiment in one kustomization may start chaos as soon as the controller is installed and ready. Remote Chaos Mesh drift can affect the whole top-level build.

### Test Signals
Signals include successful `kustomize build`, CRDs installed before experiment reconciliation, and victim pods correctly labeled/namespaced.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/fake_juicefs_provider.go -->
## sources/control-plane/juicefs-csi-driver/tests/sanity/fake_juicefs_provider.go

### Purpose
`fake_juicefs_provider.go` implements a minimal fake `juicefs.Interface` and fake filesystem object for CSI sanity tests without a real JuiceFS backend.

### Important APIs, Types, And Functions
`fakeJfsProvider` embeds `mount.FakeMounter`, stores fake filesystems and snapshot mappings, and implements provider methods such as `CreateSnapshot`, `DeleteSnapshot`, `RestoreSnapshot`, `CreateTarget`, `Settings`, `JfsCreateVol`, `JfsDeleteVol`, `JfsMount`, `JfsCleanupMountPoint`, `AuthFs`, `JfsUnmount`, `SetQuota`, `GetSubPath`, and `Status`. `fakeJfs` implements `CreateVol`, `GetBasePath`, `GetSetting`, and `BindTarget`.

### Control Flow
Snapshot creation records `snapshotID -> sourceVolumeID` and rejects the same snapshot ID for a different source. Restore checks snapshot existence. `CreateTarget` creates a directory if missing. `JfsMount` returns an existing fake filesystem named `fake` or creates one with base path `/jfs/fake`. `JfsUnmount` removes the target path if it exists. Several mount.Interface methods intentionally panic because the sanity path should not call them.

### State, Persistence, And Dependencies
Persistent test state is in-memory maps plus temporary directories created/removed under requested paths. Dependencies include `k8s.io/utils/mount`, project config, and JuiceFS interfaces. It does not contact Kubernetes or external storage.

### Integration Points
`sanity_test.go` passes this fake provider into `driver.NewFakeDriver`, allowing Kubernetes CSI sanity tests to exercise controller/node logic without a real JuiceFS mount.

### Risks
Panic stubs make unsupported call paths fail loudly, but they can obscure intended fake behavior if the driver starts using embedded `FakeMounter` methods. The fake returns empty/default settings and no-op quota/delete behavior, so it cannot catch many real backend errors. Snapshot state is not synchronized for parallel tests.

### Test Signals
Signals include idempotent create-volume behavior, snapshot create/delete/restore semantics, target directory creation/removal, status/auth no-ops, and no unexpected calls to panic-stubbed mount methods.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/fake_juicefs_provider.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/sanity_test.go -->
## sources/control-plane/juicefs-csi-driver/tests/sanity/sanity_test.go

### Purpose
`sanity_test.go` runs the Kubernetes CSI sanity test suite against a fake JuiceFS CSI driver served on a Unix socket.

### Important APIs, Types, And Functions
Constants define mount path, staging path, socket path, and CSI endpoint. `TestSanity` runs the Ginkgo suite. `BeforeSuite` creates `driver.NewFakeDriver(endpoint, newFakeJfsProvider())` and starts it. `AfterSuite` stops the driver and removes the socket. The `Describe` block builds `sanity.NewTestConfig` and calls `sanity.GinkgoTest`.

### Control Flow
Before the suite, the fake driver starts asynchronously and is expected not to error. The csi-test sanity suite connects to `unix:///tmp/csi.sock` and executes standard CSI conformance scenarios. After the suite, the driver stops and the socket file is removed.

### State, Persistence, And Dependencies
State includes a local Unix socket under `/tmp/csi.sock` and any temporary mount/stage directories used by the driver/sanity tests. Dependencies include Ginkgo, Gomega, `kubernetes-csi/csi-test`, and the fake provider.

### Integration Points
This is a standardized CSI API compatibility gate for the JuiceFS driver. It exercises driver methods through gRPC rather than direct package calls.

### Risks
The driver starts in a goroutine without explicit readiness wait beyond sanity connection behavior. Fixed `/tmp` paths can collide with concurrent runs. Fake provider behavior limits coverage of real mount/backend failures.

### Test Signals
Passing csi-test sanity cases signals basic CSI RPC contract compliance for identity, controller, and node paths supported by the fake driver. Failures indicate API-level regressions independent of real storage.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/sanity/sanity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomization.yaml

### Purpose
This kustomization defines the reconciliation validation fixture for a dynamic JuiceFS PVC shared by writer and reader deployments.

### Important APIs, Types, And Functions
It sets namespace `default`, common label `juicefs-csi-driver/validation: reconcile`, configuration `kustomizeconfig.yaml`, resource file `resources.yaml`, a `secretGenerator` named `juicefs` from `Secret-juicefs.env`, and vars `SECRET_NAME` and `SECRET_NAMESPACE` for StorageClass parameters.

### Control Flow
Kustomize generates a Secret, resolves vars into StorageClass parameter fields listed by `kustomizeconfig.yaml`, labels resources, and renders the validation workload.

### State, Persistence, And Dependencies
Applying output creates a secret, StorageClass, PVC, and two Deployments. It depends on a local `Secret-juicefs.env` file and kustomize var behavior.

### Integration Points
The generated StorageClass feeds secret names/namespaces into JuiceFS CSI provisioner and node publish flows. The deployments in `resources.yaml` validate read/write visibility through the shared PVC.

### Risks
Kustomize `vars` are deprecated in newer kustomize releases, so future tooling may require replacements. Missing `Secret-juicefs.env` breaks build. The fixture uses namespace `default`, which can collide in shared clusters.

### Test Signals
Signals include successful kustomize build, StorageClass parameters resolved to generated Secret name and namespace, PVC binding, writer appending data, and reader tailing the same file.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomizeconfig.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomizeconfig.yaml

### Purpose
`kustomizeconfig.yaml` tells kustomize that vars should be substituted inside StorageClass `parameters`.

### Important APIs, Types, And Functions
It defines one `varReference` with `kind: StorageClass` and `path: parameters`.

### Control Flow
During kustomize build, `$(SECRET_NAME)` and `$(SECRET_NAMESPACE)` occurrences under StorageClass parameters are eligible for substitution.

### State, Persistence, And Dependencies
No standalone state is created. It depends on kustomize config semantics and is consumed by the sibling kustomization.

### Integration Points
This file is necessary for `resources.yaml` StorageClass secret parameters to reference the generated Secret.

### Risks
If kustomize var support changes, the StorageClass can be rendered with unresolved `$(...)` strings. The reference is broad to all StorageClass parameters in this kustomization.

### Test Signals
Build output should show concrete secret name/namespace values in all four CSI secret parameter keys.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomizeconfig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/resources.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/resources.yaml

### Purpose
`resources.yaml` defines the dynamic-provisioning validation workload for JuiceFS CSI reconcile testing: a StorageClass, a large RWX PVC, and writer/reader deployments sharing it.

### Important APIs, Types, And Functions
The StorageClass `juicefs-sc` uses provisioner `csi.juicefs.com` and four CSI secret parameter keys. PVC `juicefs-pvc` requests `ReadWriteMany` and `10Pi`. Deployment `juicefs-writer` appends UTC timestamps to `/jfs/out.txt`; deployment `juicefs-reader` tails that file.

### Control Flow
When applied, the StorageClass references the generated Secret, the PVC triggers dynamic provisioning, the writer mounts the PVC and writes once per second, and the reader mounts the same PVC and follows the output file.

### State, Persistence, And Dependencies
State includes Kubernetes StorageClass/PVC/Deployments and data written to the JuiceFS volume. It depends on JuiceFS CSI driver, secret values, dynamic provisioning, RWX support, and BusyBox images.

### Integration Points
This fixture validates that controller provisioning, node publishing, and workload reconciliation produce a shared filesystem visible across deployments.

### Risks
`10Pi` is intentionally huge and relies on thin/quota behavior; clusters or quota settings that enforce real capacity may reject it. `tail -f /jfs/out.txt` can fail until the writer creates the file because the shell uses `errexit`. No resource requests or readiness probes are present.

### Test Signals
Signals include PVC bound to a JuiceFS PV, both deployments available, writer file growth, reader logs showing appended timestamps, and successful cleanup/reconcile after pod restarts.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/resources.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/tencentcloud-cos/k8s.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/tencentcloud-cos/k8s.yaml

### Purpose
This manifest defines a Tencent Cloud COS validation workload for JuiceFS CSI dynamic provisioning.

### Important APIs, Types, And Functions
It creates StorageClass `juicefs-sc` with provisioner `csi.juicefs.com` and fixed secret name/namespace `juicefs-secret/default`, PVC `juicefs-pvc` requesting RWX `10Pi`, and pod `juicefs-app` running CentOS to append UTC timestamps to `/data/out.txt`.

### Control Flow
Applying the StorageClass and PVC triggers provisioning using the pre-existing secret. The pod mounts the PVC at `/data` and writes a timestamp every five seconds.

### State, Persistence, And Dependencies
Persistent state includes StorageClass, PVC/PV, pod, and JuiceFS data backed by Tencent COS configuration in the secret. Dependencies include the CSI driver, correct `juicefs-secret`, COS credentials/config, and the CentOS image.

### Integration Points
This is a provider-specific validation fixture for Tencent COS storage, checking the same CSI dynamic provisioning/node publish path with COS-backed JuiceFS settings.

### Risks
Credentials are external and not represented here. `10Pi` capacity has the same quota/thin-provisioning concerns as other validation fixtures. The pod has no restart policy override, probes, or resource requests. CentOS image availability can affect validation unrelated to CSI.

### Test Signals
Signals include PVC binding, pod running, timestamp writes under `/data`, successful readback/log inspection, and cleanup of COS-backed JuiceFS resources.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/tencentcloud-cos/k8s.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/mergify.yml -->
## sources/control-plane/longhorn-engine/.github/mergify.yml

### Purpose
`mergify.yml` automates Longhorn Engine PR merge, Renovate approval, and conflict notification policies.

### Important APIs, Types, And Functions
Rules include automatic merge for PRs with successful AMD64/ARM64 binary builds, at least two approvals, and maintainer approval; automatic merge for Renovate PRs after the same build checks; automatic approval for Renovate PRs after builds; and conflict comments to the author.

### Control Flow
Mergify evaluates pull request conditions and performs rebase merges, approval reviews, or conflict comments.

### State, Persistence, And Dependencies
State is GitHub PR metadata and Mergify-managed reviews/comments/merges. Dependencies are Mergify, GitHub branch protection/check names, and Longhorn team membership.

### Integration Points
The required check names must match `.github/workflows/build.yml` job names. Renovate automation depends on author identity `renovate[bot]`.

### Risks
If build job names change, auto-merge stops. Renovate PRs can be approved and merged without human approval once builds pass. Rebase merge policy can rewrite PR merge topology. The conflict comment includes a Unicode emoji, which is harmless but non-ASCII.

### Test Signals
Signals include Mergify dry-run/status checks, rule matching for normal and Renovate PRs, branch protection alignment, and conflict comment behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/mergify.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/backport-pr.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/backport-pr.yml

### Purpose
This GitHub Actions workflow delegates backport PR issue-linking logic to a reusable workflow in the central Longhorn repository.

### Important APIs, Types, And Functions
Workflow `Link-Backport-PR-Issue` runs on opened pull requests targeting `master` or `v*` branches. The single job uses `longhorn/longhorn/.github/workflows/backport-pr.yml` pinned to commit `666fcb2f...`.

### Control Flow
When a matching PR opens, GitHub Actions invokes the reusable workflow with inherited default context.

### State, Persistence, And Dependencies
State changes are controlled by the reusable workflow, likely GitHub PR/issue links or comments. Dependencies include GitHub Actions reusable workflow support and the pinned Longhorn commit.

### Integration Points
This keeps Longhorn Engine backport behavior aligned with central Longhorn automation.

### Risks
The pinned commit can become stale relative to current central workflow fixes. No explicit permissions are declared locally, so behavior depends on defaults and called workflow requirements.

### Test Signals
Signals include workflow dispatch on opened PRs, called workflow success, and expected issue/PR linkage on master and release branches.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/backport-pr.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/build.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/build.yml

### Purpose
`build.yml` is the main Longhorn Engine CI and image publication workflow. It builds and tests AMD64/ARM64 binaries, uploads artifacts, builds architecture-specific images, pushes them, and creates a multi-arch manifest.

### Important APIs, Types, And Functions
Jobs are `build_info`, `build-amd64-binaries`, `build-arm64-binaries`, `build-push-amd64-images`, `build-push-arm64-images`, and `manifest-image`. It uses pinned checkout, codecov, upload/download artifact, QEMU, Buildx, and Docker login actions. `build_info` computes version and image tag from branch/tag refs.

### Control Flow
Pushes to `master`, `v*`, tags `v*`, pull requests, and manual dispatch trigger the workflow. Binary jobs run `make ci`, `make sync-grpc-py`, and `make integration-test`, then upload `./bin/*`; AMD64 also uploads coverage. Push/tag/branch events then download artifacts, copy them into `package/bin`, log into Docker Hub, and run `make workflow-image-build-push` with arch-specific tags. The final job pulls both arch tags and creates a combined manifest tag.

### State, Persistence, And Dependencies
Persistent outputs include GitHub artifacts, Codecov uploads, Docker Hub images, and manifest lists. Dependencies include Docker Buildx, Docker Hub secrets, Codecov token, arm64 hosted runners, and Makefile/script targets.

### Integration Points
Mergify depends on the build job names. Docker image publishing depends on `Makefile` workflow targets and `scripts/package`. The Dockerfile supplies build/test/ci targets for `make ci` and integration test container images.

### Risks
The `build_info` tag parsing uses shell regex inside a GitHub expression context and should be monitored for tag variants. Docker login steps are enabled for branch and tag refs, so secret availability controls publish success. Artifact action versions are pinned but comments may drift. Integration tests run privileged containers and can be sensitive to runner kernel/device setup. PRs do not publish images, which is correct, but image jobs are skipped and Mergify only checks binary jobs.

### Test Signals
Signals include successful AMD64 and ARM64 `make ci`, generated Python gRPC stubs in sync, integration tests passing, coverage upload, artifact download/executable bits, architecture image push, and manifest creation from both arch images.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/build.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/codespell.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/codespell.yml

### Purpose
This workflow runs codespell on pull requests to Longhorn Engine.

### Important APIs, Types, And Functions
It triggers on PRs to `master`, `main`, or `v*.*.*`, checks out with pinned `actions/checkout`, and runs pinned `codespell-project/actions-codespell` with filename checking and a broad skip list.

### Control Flow
On matching PRs, the job checks out one commit and executes codespell against the repository while excluding generated/vendor/script/integration and manifest-like paths.

### State, Persistence, And Dependencies
No repository state is changed. Dependencies are GitHub Actions, codespell action, and the skip pattern.

### Integration Points
This is a PR quality gate complementary to build and commit-lint workflows.

### Risks
The skip list excludes many YAML, script, integration, and vendor paths, so spelling issues there are not caught. `fetch-depth: 1` is enough for codespell but not history-aware checks.

### Test Signals
Signals include action success on clean PRs, failure on intentional spelling mistakes in checked paths, and no false positives in skipped generated/vendor areas.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/conventional_commits.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/conventional_commits.yml

### Purpose
This workflow enforces conventional commit messages and semantic pull request titles.

### Important APIs, Types, And Functions
It triggers on PR opened, edited, synchronize, and reopened events. It grants read permissions, checks out PR commits at the head SHA with full history, runs `wagoid/commitlint-github-action`, and runs `amannn/action-semantic-pull-request` with allowed types.

### Control Flow
Each relevant PR event checks out the PR head, validates commit messages, then validates the PR title/type using `GITHUB_TOKEN`.

### State, Persistence, And Dependencies
No repo state is changed. Dependencies include the two pinned third-party actions and GitHub pull-request metadata.

### Integration Points
This workflow supports release-note/changelog hygiene for Longhorn Engine and complements automated backport/merge workflows.

### Risks
Full-history checkout can be slower. Allowed type `BREAKING` is unusual as a semantic type and may reflect local convention; if not, it can permit odd PR titles. Fork PR token permissions must satisfy the semantic PR action.

### Test Signals
Signals include failing invalid commit messages, failing invalid PR titles, accepting allowed types, and handling synchronize/reopened events.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/conventional_commits.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/fossa.yml -->
## sources/control-plane/longhorn-engine/.github/workflows/fossa.yml

### Purpose
This workflow runs FOSSA license/security scanning for the canonical Longhorn Engine repository.

### Important APIs, Types, And Functions
It triggers on pushes to `master`/`v*`, tags `v*`, and manual dispatch. The job is gated by `github.repository == 'longhorn/longhorn-engine'`, grants `contents: read`, checks out code, and runs pinned `fossas/fossa-action` with `FOSSA_API_KEY` and project `longhorn-engine`.

### Control Flow
On eligible events in the canonical repository, the job checks out the code and uploads scan data to FOSSA.

### State, Persistence, And Dependencies
State is external FOSSA project scan results. Dependencies include the FOSSA GitHub Action and the `FOSSA_API_KEY` secret.

### Integration Points
This supports compliance/release processes outside the build pipeline.

### Risks
Forks do not run scans. Secret absence or FOSSA outage fails the job. The action comment says locking is preferred even though the action is pinned.

### Test Signals
Signals include workflow skip on forks, successful scan upload in canonical repo, and FOSSA project updates for branch/tag pushes.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/fossa.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/stale.yaml -->
## sources/control-plane/longhorn-engine/.github/workflows/stale.yaml

### Purpose
This workflow delegates stale issue/PR handling to the central Longhorn reusable workflow.

### Important APIs, Types, And Functions
It runs manually or on cron `30 1 * * *`. The job calls `longhorn/longhorn/.github/workflows/stale.yaml` pinned to commit `efbad602...`.

### Control Flow
At the scheduled time or manual dispatch, GitHub Actions invokes the reusable stale workflow.

### State, Persistence, And Dependencies
State changes are produced by the called workflow, likely comments, labels, or closures on stale issues/PRs. Dependencies are the pinned central workflow and default permissions/secrets.

### Integration Points
This keeps stale policy shared with other Longhorn repositories.

### Risks
Pinned central workflow can become stale. Local permissions are not declared, so the called workflow must request or operate within inherited defaults.

### Test Signals
Signals include successful scheduled/manual invocation and expected stale labeling/commenting behavior in repository issues/PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/.github/workflows/stale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/Dockerfile -->
## sources/control-plane/longhorn-engine/Dockerfile

### Purpose
The Longhorn Engine Dockerfile defines reproducible build, validation, test, and artifact stages for CI and packaging. It builds a SUSE BCI Golang environment with native storage dependencies, liblonghorn, TGT, integration-test tooling, and Longhorn instance manager.

### Important APIs, Types, And Functions
Stages include `golangci-lint`, `base`, `build`, `validate`, `test`, `build-artifacts`, and `ci-artifacts`. Important args/envs are `TARGETARCH`, `SRC_BRANCH`, `SRC_TAG`, proxy args, `ARCH`, `GOFLAGS=-mod=vendor`, `PROTOBUF_VER_PY`, and `LONGHORN_INSTANCE_MANAGER_BRANCH`.

### Control Flow
The base stage installs repositories and packages, conditionally installs AMD64-only packages, copies `golangci-lint`, downloads architecture-specific MinIO and gRPC health probe binaries, builds libqcow, configures Python/pip and tox dependencies, clones dep-versions and checks out a matching tag when present, builds liblonghorn and TGT from dep-versions scripts, pre-warms integration tox, builds longhorn-instance-manager, installs Docker buildx, copies the repo, and sets entrypoint/CMD. Later stages run `scripts/build`, `scripts/validate`, or `scripts/test`, then scratch stages export binaries and coverage/validation markers.

### State, Persistence, And Dependencies
The image build downloads packages and source archives from SUSE/openSUSE, MinIO, AWS S3, GitHub, and dep-versions repositories. Build outputs are binaries under `bin/`, `coverage.out`, and `/validate.done` copied into scratch artifact stages.

### Integration Points
`Makefile` targets build this Dockerfile's named stages. GitHub Actions use the Dockerfile through `make ci`, `make integration-test`, and package/image workflows. Native dependencies support Longhorn engine features including TGT/iSCSI, qcow, RDMA libraries, qemu tools, filesystem utilities, and integration tests.

### Risks
Many external downloads are not checksum-pinned beyond the base image and syntax image digests. `SRC_BRANCH` default is master and dep-versions branch/tag resolution affects native dependency versions. The `ln -sf ... &` line backgrounds the first symlink command, which is unusual and can race with the subsequent pip command. Building instance-manager from its master branch can introduce drift. Privileged/runtime assumptions are deferred to integration tests.

### Test Signals
Signals include successful multi-arch base build, libqcow/liblonghorn/TGT build success, tox environment creation, instance-manager build, `scripts/build`, `scripts/validate`, `scripts/test`, artifact export contents, and image package compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/Makefile -->
## sources/control-plane/longhorn-engine/Makefile

### Purpose
The Makefile is the Longhorn Engine developer/CI command surface for Dockerized build, validation, test, packaging, integration tests, gRPC Python sync, and workflow image publishing.

### Important APIs, Types, And Functions
Variables include `PROJECT`, `MACHINE`, `DEFAULT_PLATFORMS`, `SRC_BRANCH`, and `SRC_TAG`. Targets include `build`, `validate`, `test`, `ci`, `package`, `integration-test`, `sync-grpc-py`, `buildx-machine`, `workflow-image-build-push`, `workflow-image-build-push-secure`, and `workflow-manifest-image`.

### Control Flow
Build/test/ci targets call `docker buildx build` with Dockerfile targets, exporting artifacts for `build` and `ci`. Integration tests build the base image, then run it privileged with host `/dev`, `/proc`, `/tmp` bind propagation, and tmpfs tox/venv paths. gRPC sync runs a container command. Workflow image targets ensure a buildx machine, call `scripts/package` with push/image envs, and create multi-arch manifests from arch-specific tags.

### State, Persistence, And Dependencies
Targets create Docker build cache, local `bin/` and `coverage.out` artifacts, Docker images, and pushed registry images. Dependencies include Docker Buildx, curl to central dep-versions for `SRC_BRANCH`, git tags, and scripts under `scripts/`.

### Integration Points
GitHub Actions call `make ci`, `make sync-grpc-py`, `make integration-test`, `make workflow-image-build-push`, and `make workflow-manifest-image`. The Dockerfile supplies named build targets used here.

### Risks
`SRC_BRANCH` is computed by sourcing a remote script at make parse time, creating a network dependency even for local commands. Integration tests require privileged Docker and host device/proc access. Manifest creation assumes both arch images already exist. Buildx machine creation is best-effort and may reuse stale configuration.

### Test Signals
Signals include local and CI success for each target, artifact presence after `ci`, integration test container able to access required host mounts, generated Python stubs staying clean, and manifest target finding both arch images.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/add_replica.go -->
## sources/control-plane/longhorn-engine/app/cmd/add_replica.go

### Purpose
`add_replica.go` defines Longhorn Engine CLI commands for adding replicas, starting an engine with replicas, reporting rebuild status, and verifying rebuilt replicas.

### Important APIs, Types, And Functions
`AddReplicaCmd` exposes `add-replica`/`add` with flags `restore`, `size`, `current-size`, `fast-sync`, `sync-local`, `file-sync-http-client-timeout`, `grpc-timeout-seconds`, and `replica-instance-name`. `addReplica` validates input and calls `sync.Task` methods. `StartWithReplicasCmd` and `startWithReplicas` start with a replica list. `RebuildStatusCmd`/`rebuildStatus` print JSON rebuild status. `VerifyRebuildReplicaCmd`/`verifyRebuildReplica` validate a rebuilt replica address/instance name.

### Control Flow
Each command action calls a helper and logs fatal on error. Helpers read global `url`, `volume-name`, and `engine-instance-name`, create a cancellable context, instantiate `sync.NewTask`, parse size flags with `units.RAMInBytes`, validate required args, and dispatch to the appropriate sync task method. `addReplica` uses `AddRestoreReplica` for restore/DR volumes and `AddReplica` otherwise, passing file sync timeout, fast-sync flag, nil progress callback, and gRPC timeout. Rebuild status marshals the returned map with indentation and prints to stdout.

### State, Persistence, And Dependencies
The command itself persists no local state, but `sync.Task` operations mutate Longhorn engine/controller replica state and may initiate rebuild/sync operations over network/gRPC/HTTP. Dependencies include urfave/cli, docker/go-units, logrus, JSON, context, and `pkg/sync`.

### Integration Points
These commands are part of the Longhorn Engine CLI used by managers/operators to add replicas during normal rebuild, restore/DR workflows, engine startup, and rebuild verification. They rely on global CLI flags defined elsewhere for controller URL and instance identity.

### Risks
The `sync-local` flag is declared but not used in `addReplica`, which may be dead or pending behavior. Contexts are cancelable but have no timeout here; long operations depend on sync task internals and the optional gRPC timeout flag. Size parsing accepts human-readable units from docker/go-units, so unit semantics should match Longhorn expectations. Fatal logging exits the process on command errors.

### Test Signals
Tests should cover missing replica/size/current-size errors, invalid size strings, restore versus normal dispatch, propagation of fast-sync/file-sync/gRPC timeout/replica-instance-name flags, JSON status output, verify command missing argument, and the unused `sync-local` flag decision.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/app/cmd/add_replica.go -->
