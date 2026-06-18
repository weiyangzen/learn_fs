# Research: subset-b-000393

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/package.json -->
## sources/control-plane/juicefs-csi-driver/package.json

Purpose: this Node package manifest exists to support documentation quality gates for the JuiceFS CSI driver repository, not the Go runtime. It names the package `juicefs-csi-driver`, pins version metadata, and provides npm scripts for Markdown linting, broken-link checking, and autocorrect checks over `./docs/`.

Important APIs and commands: the operational surface is the `scripts` block. `markdown-lint` and `markdown-lint-fix` run `markdownlint-cli2` against `./docs/**/*.md`; `check-broken-link` runs `remark --quiet --frail ./docs/`; `autocorrect-lint` and `autocorrect-lint-fix` run `autocorrect` over docs; `lint` chains markdownlint, remark link validation, and autocorrect linting. The `remarkConfig` loads `remark-validate-links-heading-id` and `remark-validate-links`.

Control flow and state: there is no application runtime state. State is npm dependency resolution through lockfiles outside this item and the docs tree being linted. Script failures are intended to fail CI or local quality runs.

Dependencies and integration points: dependencies are documentation tooling only: `markdownlint-cli2`, two custom markdownlint rules, `remark-cli`, `remark-validate-links`, and heading-id validation. The manifest integrates with CI/developer workflows that execute `npm run lint` before publishing or merging documentation.

Risks: the scripts target `./docs/` lowercase, while this repository also has `Docs/`; this is likely inherited from the upstream project and may not validate generated research artifacts. The manifest does not pin an `autocorrect` dependency, implying that binary must be installed outside npm. Dependency major-version ranges may change lint behavior.

Test signals: this file is itself not tested by Go tests. Its quality signal is successful `npm run lint` in environments with dependencies installed and `autocorrect` available.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/package.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/common/common.go -->
## sources/control-plane/juicefs-csi-driver/pkg/common/common.go

Purpose: this file centralizes string constants shared across the CSI driver control plane, node-side controllers, config parsing, Kubernetes metadata, and mount-pod construction. It is a dependency boundary that prevents ad hoc label, annotation, secret, and path key duplication.

Important constants: pod identity and selectors include `CSINodeLabelKey/Value`, `PodTypeKey`, `PodTypeValue`, `PodUniqueIdLabelKey`, `PodJuiceHashLabelKey`, and `PodUpgradeUUIDLabelKey`. Lifecycle constants include `Finalizer`, `DeleteDelayTimeKey`, `DeleteDelayAtKey`, `ImmediateReconcilerKey`, and `CleanCache`. CSI secret keys cover provisioner, node publish, and controller expand secret references. PV/PVC config keys cover mount pod resources, labels, annotations, service account, image, cache PVC/emptyDir/inline volumes, host path, clean-cache, and mount share mode. Smooth-upgrade constants define FUSE fd handoff labels, host/pod paths, env names, and job metadata.

Control flow and state: the file has no functions and no mutable state; behavior emerges wherever these constants are consumed. For example, config parsing reads `MountPodCpuLimitKey`, controllers filter pods by `PodTypeKey`, and pod driver cleanup checks `CleanCache`.

Dependencies and integration points: it is imported heavily by `pkg/config`, `pkg/controller`, mount pod builders, resource utilities, and admission sidecar logic. The constants form an implicit Kubernetes API contract with StorageClass parameters, PV volume attributes, PVC annotations, pod labels, ConfigMaps, Secrets, and Jobs.

Risks: because these values are external API keys, renaming or changing them is a breaking change. Some names are intentionally broad, such as `app`, `volume-id`, and `juicefs-hash`, so label collisions are possible if used outside the expected namespace. The unexported webhook injection suffix constants are assembled into exported labels; maintainers must preserve those exact composed strings.

Test signals: no direct tests target this constants file, but almost every config/controller test depends on these values. Failures would appear as selector mismatches, missing annotations, and invalid generated pod metadata in higher-level tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/common/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/batch_config.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/batch_config.go

Purpose: this file models and persists batch upgrade plans for mount pods. It also provides a small diff helper that computes old and renewed `JfsSetting` values for upgrade comparison.

Important APIs/types: `BatchConfig` stores upgrade parallelism, error behavior, recreation policy, optional node/unique ID filters, batches of `MountPodUpgrade`, and an overall `UpgradeStatus`. `MountPodUpgrade` stores mount pod name, node, CSI node pod name, and per-pod status. Status constants are `pending`, `running`, `success`, `fail`, `stop`, and `pause`. `NewBatchConfig` creates deterministic batches. `LoadUpgradeConfig`, `LoadBatchConfig`, `CreateUpgradeConfig`, and `UpdateUpgradeConfig` read/write the `upgrade` JSON entry in a Kubernetes ConfigMap. `GetDiff` and `GetDiffWithNode` compare current and renewed settings using `RevertSettingWithNode` and `ReNew`.

Control flow: `NewBatchConfig` indexes CSI node pods by node name, sorts input mount pods with `podList`, and fills fixed-size batches of length `parallel`. Sorting is by node name, then the `common.UniqueId` annotation. ConfigMap creation first checks whether the named ConfigMap already exists; only not-found allows creation. Update requires the ConfigMap to exist and replaces `Data` with a single `upgrade` payload.

State and persistence: upgrade state is persisted in a namespaced ConfigMap under `config.Namespace`, labeled as `common.ConfigTypeValue`. The serialized JSON includes every batch and status. The diff path returns sanitized settings via `Safe`, so sensitive values are masked before display/logging.

Dependencies and integration points: depends on Kubernetes CoreV1 ConfigMaps, API error classification, `pkg/k8sclient`, and common metadata constants. Diffing integrates tightly with `setting.go`, especially node-aware mount-pod patch application.

Risks: `NewBatchConfig` divides by `parallel` and allocates `(len(pods)+parallel-1)/parallel`; `parallel <= 0` will panic or misbehave and is not guarded here. Missing CSI node entries produce empty `CSINodePod` names. `LoadBatchConfig` assumes `cm.Data["upgrade"]` exists and contains valid JSON. `CreateUpgradeConfig` refuses overwrite, which is safe but means callers must decide between create and update.

Test signals: `batch_config_test.go` covers deterministic sorting/batching and node-aware diff behavior. It does not cover ConfigMap CRUD error handling, invalid JSON, missing `upgrade`, or zero/negative parallelism.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/batch_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/batch_config_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/batch_config_test.go

Purpose: this test file validates batch upgrade ordering and the node-selector-aware diff path.

Important test cases: `TestNewBatchConfig` verifies that `NewBatchConfig` preserves requested `Parallel`, groups pods into batches of that size, and sorts pods first by `Spec.NodeName` and then by `common.UniqueId` annotation. Scenarios cover normal two-pod input, multiple nodes, and multiple unique IDs on the same node. `TestGetDiffWithNodeRespectsNodeSelector` mutates `GlobalConfig.MountPodPatch` to include a `NodeSelector`, then verifies `GetDiffWithNode` applies labels only when the provided Kubernetes Node matches.

Control flow and fixtures: tests construct `corev1.Pod` objects directly with names, annotations, labels, node names, and a minimal mount container command. The node-selector test saves and restores `GlobalConfig` to isolate global mutation.

State and persistence behavior: no external Kubernetes API is used. The only persistent-like state is process-global `GlobalConfig`, restored after the test. The expected `BatchConfig` values intentionally omit zero-value fields such as `IgnoreError`, `NoRecreate`, and `CSINodePod`.

Dependencies and integration points: uses `testify/assert`, Kubernetes core API types, and constants from `pkg/common`. It exercises `setting.go` indirectly through `GetDiffWithNode`, `RevertSettingWithNode`, `ReNew`, and mount pod patch application.

Risks and gaps: there is no assertion for `ignoreError`, `recreate=false`/`NoRecreate`, node and unique ID filters, CSI node pod mapping, empty pod lists, or invalid `parallel`. ConfigMap load/create/update helpers are untested. The diff test checks only labels, not full setting hash or option changes.

Test signal strength: good for deterministic ordering and recent node selector semantics; limited for persistence and error paths.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/batch_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/command.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/command.go

Purpose: this file generates JuiceFS CLI command arguments for auth/format operations and queries CE volume UUIDs. It deliberately separates real arguments used inside CSI from mount-pod command arguments that substitute sensitive values through environment variables.

Important APIs: `KeysCompatible` rewrites legacy secret keys such as `accesskey` and `secretkey` to canonical dashed keys. `GenAuthCmd` returns two arg slices for `juicefs auth`: actual args and redacted/env-backed command args. `GenFormatCmd` does the same for `juicefs format`, using CE CLI path and `metaurl`. `GetJfsVolUUID` runs `juicefs config <source>` for CE settings and parses `"UUID": "...";` EE settings return `s.Name` directly.

Control flow: both command generators validate nil secrets and required names. `GenAuthCmd` escapes plain keys, strips secret values into env references for token/secret/passphrase, honors `JFS_NO_UPDATE_CONFIG=enabled`, optionally writes `initconfig` into `setting.ClientConfPath` when `ByProcess` is true and a config file does not already exist, appends parsed format options, strips `session-token` from mount pod args, and appends `--conf-dir`. `GenFormatCmd` validates `metaurl`, optionally adds `--no-update`, appends format/storage keys, strips `secret-key`, then appends env-substituted `${metaurl}` and volume name for pod args.

State and persistence: `KeysCompatible` mutates the input map. `GenAuthCmd` may write a config file with mode `0644` under `setting.ClientConfPath`. `GetJfsVolUUID` executes a subprocess with inherited environment plus `s.Envs`; no Kubernetes state is touched.

Dependencies and integration points: depends on package globals `CliPath`, `CeCliPath`, `ByProcess`, and default timeout from `setting.go`; uses `security.EscapeBashStr`; returns gRPC status errors for CSI-invalid inputs. It feeds `JfsSetting.FormatCmd` via `genFormatCmd` in `setting.go`.

Risks: regex parsing of JSON output is brittle compared with JSON decoding and may overmatch if output changes. `KeysCompatible` can overwrite canonical keys if both old and new keys exist. `JFS_NO_UPDATE_CONFIG` makes `bucket` mandatory and causes filesystem writes, which can surprise tests and operators. `GetJfsVolUUID` timeout is fixed to `8*defaultCheckTimeout` and subprocess errors include command output.

Test signals: `command_test.go` covers UUID parsing, subprocess error propagation, and EE shortcut behavior. It does not test command generation, escaping, env stripping, legacy-key collision behavior, or config-file creation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/command.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/command_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/command_test.go

Purpose: this test file verifies `GetJfsVolUUID`, the command-executing path in `command.go`.

Important test cases: the `normal` case monkey-patches `exec.Cmd.CombinedOutput` to return representative `juicefs config` output containing JSON and asserts the UUID string is extracted. The `status error` case makes `CombinedOutput` fail and asserts an error is returned. The `ee` case sets `IsCe=false` and verifies no subprocess parsing is needed; the UUID is the setting name.

Control flow and fixtures: tests use GoConvey nested `Convey` blocks and `gomonkey` to patch `CombinedOutput` on `*exec.Cmd`. Settings include `Source`, `Name`, `Envs`, and `IsCe`.

State and persistence behavior: no real subprocess is executed because `CombinedOutput` is patched. No environment mutation or filesystem writes occur.

Dependencies and integration points: depends on monkey patching internals of `os/exec`, so it is sensitive to Go/runtime compatibility and test execution restrictions. It exercises the public behavior expected by `ParseSettingWithNode` when no UUID is provided for CE volumes.

Risks and gaps: does not cover timeout behavior, `"database is not formatted"` special handling, malformed output without UUID, environment propagation, or command path selection. It also does not test `GenAuthCmd` or `GenFormatCmd`, leaving sensitive argument stripping and shell escaping without direct coverage in this file.

Test signal strength: narrow but useful for the UUID extraction branch and EE/CE split.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/command_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/config.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/config.go

Purpose: this file defines global CSI driver configuration, mount pod patch configuration, and config-loading/reloading behavior. It is the central process-wide config authority for the JuiceFS CSI driver.

Important globals: runtime feature flags include `ByProcess`, `Provisioner`, `CacheClientConf`, `MountManager`, `Webhook`, `Immutable`, share-mount flags, kubelet access, and grace-upgrade behavior. Path/image defaults include mount bases, CLI paths, mount images, config paths, and built-in versions. `CSISetEnvMap`, `CSISetOptsMap`, and `interVolumesPrefix` define values managed internally by the CSI driver. `PodLocks` provides 1024 mutexes keyed by hash/name.

Important types/APIs: `PVCSelector` extends Kubernetes label selectors with storage class and name. `MountPodPatch` describes configurable mount pod changes: image overrides, cache dirs, labels, annotations, host networking/PID, DNS, probes, lifecycle, resources, volumes, volume devices/mounts, env, init containers, and mount options. `Config` contains feature toggles and `MountPodPatch`. `GenMountPodPatch` filters and merges patches. `LoadConfig`, `LoadFromConfigMap`, and `StartConfigReloader` load YAML config from files or ConfigMaps. `GetGlobalConfigName`, `GetPodLockKey`, and `GetPodLock` support operational coordination.

Control flow: mount pod patch matching requires every configured selector to match: PVC selector if present and node selector if present. Merge behavior is ordered; later matching patches can replace scalar fields, labels, annotations, resources, env, cache dirs, init containers, and mount options. Volumes are additive but internal names and duplicates are ignored; volume mounts/devices are accepted only when their volume was added in the same merge step. `GenMountPodPatch` also selects CE/EE image and optionally replaces `${MOUNT_POINT}`, `${VOLUME_ID}`, `${VOLUME_NAME}`, and `${SUB_PATH}` templates through JSON serialization.

State and persistence: `GlobalConfig` is a mutable package global. `LoadConfig` and `LoadFromConfigMap` replace it wholesale. `StartConfigReloader` starts goroutines: one fsnotify watcher and one five-minute fallback reload ticker. `WebPort` is initialized from `JUICEFS_CSI_WEB_PORT` at package init.

Dependencies and integration points: imports Kubernetes API types, labels/selectors, fsnotify, klog, YAML parsing, `pkg/common`, `pkg/k8sclient`, and `pkg/util`. `setting.go` calls `applyConfigPatch`, which delegates to `GlobalConfig.GenMountPodPatch`. Controllers and pod builders consume feature flags and path/image defaults.

Risks: global mutable config has concurrency and test isolation risk; reload swaps the pointer without explicit synchronization. Patch merging replaces entire maps/slices rather than deep-merging many fields. `deepCopy` ignores marshal/unmarshal errors. A duplicated `ReadinessProbe` merge block suggests minor maintenance drift. VolumeMount/VolumeDevice validation only permits volumes added in that same patch, not previously existing volumes, which is intentional for safety but can surprise users.

Test signals: `config_test.go` covers YAML loading, patch selector semantics, template replacement idempotence, volume filtering, DNS config, `SupportFusePass`, and node selector behavior. Reloader goroutines and ConfigMap loading are not directly tested.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/config_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/config_test.go

Purpose: this test file validates global config loading and mount pod patch generation/matching.

Important test cases: `TestLoadConfig` writes a YAML config to `/tmp/test-config.yaml`, calls `LoadConfig`, and asserts parsed patch entries for images, labels, annotations, PVC selector, resources, probes, termination grace period, env, volumes, volume devices, and cache dirs. `TestGenMountPodPatch` covers empty config, matching/unmatching PVC selectors, ordered merge/overwrite, template replacement, duplicate/internal volume filtering, mount options, node selector matching, and DNS policy/config. `TestSupportFusePass` verifies `DisableGraceUpgrade` gates utility support detection. `TestGenMountPodPatchParseTwice` ensures template replacement does not mutate original config due to deep copy. `TestMountPodPatch_isMatch` and `_isMatchWithNode` cover selector combinations.

Control flow and fixtures: tests build minimal Kubernetes API objects directly and use table-driven assertions. `toPtr` helps express pointer fields. Tests frequently compare full `MountPodPatch` structs with `assert.Equal`.

State and persistence behavior: `TestLoadConfig` writes and removes a temporary file and resets `GlobalConfig` afterward. Several tests instantiate local `Config` values, minimizing global interaction.

Dependencies and integration points: uses `testify/assert`, Kubernetes core/meta/resource APIs, and config globals. It indirectly protects behavior used by `setting.go` and pod builder generation.

Risks and gaps: no test covers `LoadFromConfigMap`, `StartConfigReloader`, fsnotify symlink handling, invalid YAML in full config loading, environment compatibility via `ENABLE_NODE_SELECTOR`, or concurrent reload/read behavior. Some selector tests call `isMatch` with nil node for node selector cases and then separately cover node-aware matching.

Test signal strength: strong for patch parsing and merge semantics; weak for live reload and Kubernetes ConfigMap integration.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/setting.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/setting.go

Purpose: this file builds, sanitizes, renews, hashes, and reverts `JfsSetting`, the runtime description of a JuiceFS mount. It combines CSI secrets, PV/PVC volume context, mount options, global config, node context, existing mount pod metadata, and cache definitions.

Important types: `JfsSetting` contains volume identity, CE/EE mode, source/meta URL, storage and format options, secret material, env/config maps, cache volume declarations, mount paths, subpath, secret name, PV/PVC/node pointers, `PodAttr`, and mount share mode. `PodAttr` stores mount pod namespace, paths, image, resources, labels, annotations, probes, lifecycle, volumes, env, cache dirs, DNS, host settings, tolerations, service account, and image pull secrets. Cache structs model PVC, EmptyDir, CSI inline, and generic ephemeral caches.

Important APIs: `ParseSettingWithNode` is the main constructor. `GenCacheDirs` normalizes cache storage into mount pod volumes and `cache-dir` options. `GenPodAttrWithCfg` initializes pod attributes from defaults, CSI pod spec, volume context, and global patches. `GenSettingAttrWithMountPod` reconstructs and renews settings for existing mount pods. `RevertSettingWithNode` prefers serialized `jfsSettings`, then PV/PVC/custom secret parsing, then mount pod introspection. `ReNew` overlays custom secret changes and reapplies patch/cache/hash logic. `ParseAppInfo`, format option parsing/representation/stripping, `ParsePodResources`, `applyConfigPatch`, `IsCEMountPod`, `getPVNameFromTarget`, and `GenHashOfSetting` are supporting APIs.

Control flow: parsing begins with secret YAML/JSON into a setting, validates `name`, sets defaults, detects CE mode by `metaurl`, parses nested `configs` and `envs`, reads volume context for subPath, clean-cache, delete delay, and host paths, generates pod attrs, validates mount options, generates cache dirs, resolves UUID when needed, and generates format/auth commands. Renewal merges customer secret values into an existing setting, reapplies PV mount options, rebuilds cache dirs, computes a deterministic hash, and captures upgrade UUID. Hash generation deliberately clears target-specific fields, forces mount path to `/jfs/<uniqueId>`, sorts slices, and SHA-256 hashes JSON.

State and persistence: `Safe` masks sensitive fields but mutates through `sCopy := s`, so it modifies the receiver rather than a deep copy. `ParseSettingWithNode` stores pointers to PV/PVC/Node and secrets. `GenSettingAttrWithMountPod` reads Kubernetes PV/PVC/Secret/Node through `k8sclient`. `ReNew` may generate new `FormatCmd` and set `CustomerSecret`. Cache cleanup intent is persisted as setting fields and annotations consumed later by controllers.

Dependencies and integration points: depends on package globals from `config.go`, CLI command generation from `command.go`, common metadata keys, Kubernetes API types, `pkg/k8sclient`, `pkg/util`, and `pkg/util/security`. Pod builders and controllers rely on `JfsSetting` and `PodAttr` to generate or patch mount pods.

Risks: `Safe` side effects can surprise callers and may erase sensitive values from the original setting. `GenCacheDirs` dereferences `cacheDir.SizeLimit` for EmptyDir patches without nil checks. `ReNew` assumes `s.Attr` is non-nil. `ParseSettingWithNode` returns a mostly empty setting with nil secrets, which callers must handle. Global config and package globals influence parsing heavily, making tests and concurrent reloads sensitive. YAML-or-JSON parsing accepts broad YAML syntax that may coerce values unexpectedly.

Test signals: `setting_test.go` is broad, covering secret parsing, resources, cache modes including ephemeral volumes, mount option validation, YAML/JSON parsing, resource parsing, format option stripping, target path parsing, config patch application, node-aware reconstruction, and hash determinism.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/setting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/setting_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/config/setting_test.go

Purpose: this large test file validates the `JfsSetting` construction and transformation pipeline.

Important test cases: `TestParseSecret` covers nil secrets, missing names, env/config parsing, storage and resource volume context, labels/annotations, service account, secret fields, auth format command generation, cache PVCs, mount image override, host path, and mount option override by patch. `TestGenSettingAttrWithMountPodRespectsNodeSelector` uses a fake Kubernetes client to verify node-aware global patch application. `Test_genCacheDirs` covers default cache dir, PVC cache from volume context and patch, EmptyDir, hostPath, conflicts, ephemeral cache with default/explicit access modes, and combined cache types. `Test_genAndValidOptions`, `Test_parseYamlOrJson`, `Test_parsePodResources`, `Test_ParseFormatOptions`, `Test_getPVNameFromTarget`, `Test_applyConfigPatch`, and `TestGenHashOfSetting` exercise focused helpers.

Control flow and fixtures: tests construct expected full `JfsSetting` values and compare marshaled JSON or deep equality. Some tests mutate `GlobalConfig.MountPodPatch` and defer reset. The node-selector reconstruction case uses `fake.NewSimpleClientset` with Secret, PV, and Node objects.

State and persistence behavior: no real Kubernetes cluster is used. A fake client simulates API reads. Process-global `GlobalConfig` is reset after mutation, but package-level resource variables are reused across tests.

Dependencies and integration points: uses Kubernetes core API/resource/meta types, `k8sclient`, `fake` clientset, `testify/assert`, klog, and common constants. It tests behavior that pod builders, pod controllers, and upgrade diffing depend on.

Risks and gaps: the very large `TestParseSecret` table is useful but brittle because full JSON comparisons can fail on harmless field additions. It does not deeply cover `RevertSettingWithNode` branches with serialized `jfsSettings`, custom secret precedence errors, nil `Attr` in `ReNew`, or real UUID subprocess behavior. Cache EmptyDir patch nil `SizeLimit` risk is not covered.

Test signal strength: strong for normal setting parsing and helper semantics; medium for Kubernetes reconstruction; limited for failure branches involving live API and mount pod introspection.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/config/setting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller.go

Purpose: this controller watches application pods injected with JuiceFS sidecar containers and cleans up FUSE sidecars after app containers have terminated. It prevents completed non-restarting app pods from staying alive solely because the mount sidecar is still running.

Important APIs: `AppController` wraps `K8sClient`. `Reconcile` fetches the pod, filters with `ShouldInQueue`, kills mount processes if app containers have been terminated for over five minutes, otherwise executes sidecar PreStop unmount hooks and requeues. `umountFuseSidecars`, `umountFuseSidecar`, `killFuseProcesss`, and `killFuseProcess` execute cleanup commands inside matching containers. `SetupWithManager` registers pod watches. `ShouldInQueue` encapsulates eligibility.

Control flow: a pod is eligible only if sidecar injection is marked done, injection is not disabled, restart policy is not Always, no JuiceFS sidecar exists as an init container, at least one regular container name contains `jfs-mount`, status is Running with at least two container statuses, all non-mount containers are terminated, and mount containers are still running. Reconcile finds the latest non-mount terminated finish time; after five minutes it runs `pkill -fe juicefs`, otherwise it runs configured PreStop commands.

State and persistence: no persistent resource is written directly. The controller performs Kubernetes exec calls into containers and returns requeue intervals. Errors from known unmounted states and exit code 137/143 are intentionally ignored in cleanup paths.

Dependencies and integration points: depends on controller-runtime, Kubernetes pod events, `pkg/k8sclient.ExecuteInContainer`, common sidecar labels/names, and util label checks. It is relevant to webhook/sidecar mode rather than standalone mount pods.

Risks: container name matching uses substring containment for `jfs-mount`, which can match unexpected names. The typo `killFuseProcesss` is harmless but visible. `ShouldInQueue` does not check non-mount container exit codes, only termination. Exec-based cleanup depends on container runtime availability and PreStop correctness. Requeue every five minutes can continue until the pod leaves the eligible state.

Test signals: `app_controller_test.go` covers queue eligibility and unmount success/error behavior using monkey-patched `ExecuteInContainer`. It does not cover the full `Reconcile` five-minute kill branch or controller-runtime watch predicates.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller_test.go

Purpose: this test file validates app-sidecar queue filtering and sidecar unmount helper behavior.

Important test cases: `Test_shouldRequeue` covers missing injection label, restart policy Always, no fuse container, app container still running, fuse container already exited, one or more app containers terminated while fuse is running, app container still running in multi-container pods, and Pending pods. `TestAppController_umountFuseSidecars_normal` monkey-patches `ExecuteInContainer` to succeed and checks no-fuse, one sidecar, and multiple sidecars. `TestAppController_umountFuseSidecars_error` patches exec to fail and verifies errors propagate when sidecars have PreStop commands.

Control flow and fixtures: pods are built inline with labels, restart policies, containers, phases, and container states. Monkey patching is done with `gomonkey` on `K8sClient.ExecuteInContainer`.

State and persistence behavior: no cluster calls occur. The tests simulate exec behavior and do not mutate persistent state.

Dependencies and integration points: uses Kubernetes pod/status types, `pkg/common`, `pkg/k8sclient`, `go-logr`, `record`, and `gomonkey`. It protects the behavior expected by controller-runtime watch predicates because those predicates call `ShouldInQueue`.

Risks and gaps: tests do not cover ignored stderr strings such as `not mounted`, ignored exit code 137/143, missing PreStop behavior, `killFuseProcess`, or complete `Reconcile` behavior with old app termination times. Some unused field structs remain from older controller patterns.

Test signal strength: good for filter conditions and basic exec error propagation; limited for time-based and Kubernetes-client branches.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/app_controller_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/controller_suite_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/controller_suite_test.go

Purpose: this is the Ginkgo/Gomega suite bootstrap for controller package specs.

Important APIs: `TestService` registers Gomega’s fail handler and runs specs under the suite name `Controller Suite`.

Control flow and state: there is no controller logic here. It enables BDD specs such as `mountinfo_test.go` to run through Go’s `testing` entrypoint.

Dependencies and integration points: imports `github.com/onsi/ginkgo/v2` and `github.com/onsi/gomega`. Any Ginkgo `Describe` blocks in the controller package are attached to this test entry.

Risks: suite-level bootstraps can hide ordering/state leakage if specs mutate globals without cleanup. This file itself has no cleanup hooks.

Test signals: success indicates Ginkgo specs were registered and run; detailed assertions live in the spec files.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/controller_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/job_controller.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/job_controller.go

Purpose: this controller recycles JuiceFS-related Kubernetes Jobs, especially node-bound jobs whose CSI node pod no longer exists and completed jobs that were not automatically removed.

Important APIs: `JobController` wraps `K8sClient`. `Reconcile` fetches a Job, ignores missing/deleting jobs, checks node binding, verifies CSI node presence, and deletes jobs that should be recycled. `SetupWithManager` registers controller-runtime watches on `batchv1.Job`.

Control flow: if a Job has no `spec.template.spec.nodeName`, only `resource.IsJobShouldBeRecycled` is checked. If it is node-bound, the controller lists CSI node pods in `config.Namespace` with label `app=juicefs-csi-node` and field selector `spec.nodeName=<node>`. Absence of a CSI pod marks the job for recycling. Recycling deletes the job and requeues only on delete error in the node-bound path.

State and persistence: persistent state changes are Kubernetes Job deletions. No status updates or finalizers are managed here.

Dependencies and integration points: depends on Kubernetes batch API, controller-runtime, common CSI node labels, config namespace, `pkg/k8sclient`, and `pkg/util/resource` job predicates. `pod_driver.go` creates fuse abort jobs that this controller can later recycle.

Risks: watch predicates return true for delete events whose deletion timestamp is nil, which can enqueue already-deleted objects and then resolve as missing. Job recycling depends on labels and namespace for CSI node pods; misconfiguration can delete useful jobs. There are no tests for this file in the listed subset.

Test signals: no direct tests. Indirect confidence comes from resource utility tests elsewhere if present; this subset provides no direct coverage of job reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/job_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/mount_controller.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/mount_controller.go

Purpose: this controller manages mount pod deletion/finalizer behavior from the control-plane perspective. It prevents mount pod finalizers from being removed while the CSI node pod still exists, and it cleans pending unscheduled mount pods whose application references have disappeared.

Important APIs: `MountController.Reconcile` handles deleted mount pods and pending unscheduled mount pods. `handlePendingMountPod` scans reference annotations and deletes orphaned pending pods. `GetPodByUidAndNode` searches app pods by UID, optionally constrained to a node. `shouldInQueue` filters mount pods by `app.kubernetes.io/name=juicefs-mount` and finalizer. `SetupWithManager` installs pod watches for deletion and pending-unscheduled scenarios.

Control flow: Reconcile fetches the pod and returns on not found. If the pod is Pending, has no deletion timestamp, and has no node name, it calls `handlePendingMountPod`. Otherwise, only deleting pods with the JuiceFS finalizer proceed. For deleting pods, it lists CSI node pods on the same node. If any exist, it requeues after five seconds; if none exist, it removes the finalizer. Pending cleanup extracts target pod UIDs from annotations whose key equals `util.GetReferenceKey(target)`, searches for matching app pods, and deletes the mount pod when zero referenced app pods remain.

State and persistence: state changes are pod deletion for orphan pending mount pods and finalizer removal for deleting mount pods after CSI node disappearance. Reference state is encoded in mount pod annotations.

Dependencies and integration points: depends on controller-runtime, Kubernetes pod list selectors, `pkg/k8sclient`, common labels/finalizer, config namespace, `pkg/util`, and `pkg/util/resource`. It coordinates with pod driver annotation reference format and node scheduling behavior.

Risks: pending cleanup relies on target path parsing and UID extraction; malformed references are skipped and can lead to deletion if no valid refs remain. `GetPodByUidAndNode` lists all namespaces with a label-exists selector, then scans UIDs; correctness depends on app pods carrying `common.UniqueId`. Finalizer removal waits on CSI node presence but not necessarily active mount cleanup state.

Test signals: no direct tests for this file in the listed subset. Its helpers share target parsing with tested mountinfo/setting helpers, but reconciliation behavior is untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/mount_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo.go

Purpose: this file parses and interprets Linux mount table data for CSI target paths. It lets the pod driver detect normal mounts, missing targets, corrupt FUSE mounts, inconsistent mount records, and subPath bind mounts that may require recovery or cleanup.

Important types/APIs: `mountInfoTable` stores parsed `k8sMount.MountInfo` rows and a pod UID deletion map. `parse` reads `/proc/self/mountinfo`. `setPodStatus` records whether a pod is deleting. `resolveTarget` validates CSI target paths, extracts pod UID and PV name, resolves the base CSI mount and matching subPath mounts. `resolveTargetItem` aggregates mountinfo records into `targetItem` values. `targetItem.check` uses `os.Stat` and Kubernetes mount corruption detection to set status. `getPodUid` and `getPVName` parse kubelet CSI paths.

Control flow: `resolveTarget` splits target paths around `volumes/kubernetes.io~csi`, computes the pod directory and subPath prefix, resolves exact base target records, and resolves all subPath records below `volume-subpaths/<pv>`. When no exact base record exists, it still creates a target item and checks the filesystem path as not mounted/not existing/unexpected. `resolveTargetItem` groups by mount point, counts duplicate records, tracks inconsistent roots, trims deleted root suffixes, and checks filesystem status.

State and persistence: `mountInfoTable` is an in-memory snapshot. The only external state read is `/proc/self/mountinfo` and filesystem metadata via `os.Stat`. The deleted-pod map is populated by `PodDriver` from Kubernetes pod state.

Dependencies and integration points: depends on Kubernetes mount utils, `os.Stat`, `pkg/util.DoWithTimeout`, and controller path conventions. `pod_driver.go` consumes `mountItem` and `targetItem` statuses in recovery and cleanup logic.

Risks: path parsing uses string splits and assumes kubelet path layout. `resolveTargetItem` map iteration makes subPath result order nondeterministic. `targetItem.check` compares timeout errors by exact string `"function timeout"`, which is brittle. It is Linux/kubelet specific and tightly coupled to mount propagation behavior.

Test signals: `mountinfo_test.go` covers normal base/subPath resolution, invalid targets, stat errors, unmounted targets, corrupt mounts, not-exist status, and inconsistent mount records using monkey-patched `os.Stat`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo_test.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo_test.go

Purpose: this Ginkgo spec validates `mountinfo.go` target resolution and status classification.

Important fixtures: `mockMountInfoTable` builds synthetic `k8sMount.MountInfo` rows for base CSI mounts and subPath mounts. The default fixture includes a base mount for `uid-1/pvn`, two subPath targets, duplicate mount records for one subPath, and other UIDs.

Important test cases: normal resolution asserts base target, subpath extraction, count aggregation, and mounted status. Invalid target path returns nil. Stat error returns `targetStatusUnexpect` with stored errors. A target absent from mountinfo but existing on disk is `targetStatusNotMount`. ENOTCONN classifies as `targetStatusCorrupt`. not-exist errors classify as `targetStatusNotExist`. Adding another base record with a different root marks the target inconsistent.

Control flow and state: tests monkey-patch `os.Stat` with ordered outputs via `gomonkey.ApplyFuncSeq`. They run under the Ginkgo suite initialized by `controller_suite_test.go`.

Dependencies and integration points: depends on Ginkgo/Gomega, gomonkey, Kubernetes mount info structs, `os`, and syscall errors. It directly protects logic consumed by pod driver recovery.

Risks and gaps: result order for subPath targets is map-driven, but the test handles either expected subpath. The tests do not exercise real `/proc/self/mountinfo`, timeout behavior from `DoWithTimeout`, deleted-pod status propagation, or `getPodUid/getPVName` as standalone table tests.

Test signal strength: strong for synthetic classification; limited for real node environment behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/mountinfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pod_controller.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/pod_controller.go

Purpose: this node-local controller reconciles JuiceFS mount pods assigned to the current CSI node. It builds a current pod/mountinfo snapshot and delegates detailed lifecycle handling to `PodDriver`.

Important APIs: `PodController` wraps `K8sClient` plus a controller-runtime cached reader. `Reconcile` filters by current `config.NodeName`, handles immediate reconciler annotations, parses mountinfo, lists app and mount pods on the node, constructs `PodDriver`, and returns requeue behavior. `SetupWithManager` watches mount pod create/update/delete events for the current node.

Control flow: reconciliation runs under `config.ReconcileTimeout`. It fetches the mount pod from cache, skips pods not on this node or not node-selected to it, removes `common.ImmediateReconcilerKey` annotations and immediately requeues, parses `/proc/self/mountinfo`, lists app pods with `common.UniqueId` label and mount pods with mount label on the current node, and passes their combined list to `NewPodDriver`. After `podDriver.Run`, it honors `DeleteDelayAtKey` by computing a requeue duration until the delayed delete time. Otherwise it requeues immediately or after ten minutes depending on `PodDriver` result.

State and persistence: state changes are delegated except for removal of immediate reconciler annotations. The controller reads mountinfo, cached pods, and delay annotations; it always returns `Requeue: true` after a successful driver run.

Dependencies and integration points: depends on controller-runtime cache/watch APIs, Kubernetes field/label selectors, `pkg/config`, `pkg/common`, `pkg/k8sclient`, `pkg/util`, `pkg/util/resource`, `mount.SafeFormatAndMount`, and `pod_driver.go`.

Risks: `SetupWithManager` names the controller `"mount"`, same as `MountController`, which can be confusing or conflicting depending on manager registration. Update predicate does not re-check node assignment, so updates to off-node mount pods with labels may enqueue but are skipped in Reconcile. Reliance on cached reader means stale cache is possible, although `PodDriver.Run` refetches the current pod from API.

Test signals: no direct tests for this file in the subset. Its delegated mountinfo and pod driver helper logic has partial tests, but orchestration, predicates, delayed requeue, and annotation removal are untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pod_controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver.go -->
## sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver.go

Purpose: this file implements the mount-pod lifecycle state machine for a node. It reconciles ready, pending, failed, completed, and deleting mount pods; cleans annotation references; recreates replacement mount pods; recovers corrupt bind mounts; removes finalizers; aborts stuck FUSE connections; and cleans cache directories.

Important types/APIs: `PodDriver` owns a `K8sClient`, `SafeFormatAndMount`, per-status handler map, unique-ID pod index, lock, and mountinfo snapshot. `Result` tells the caller whether to requeue immediately or after a duration. Statuses are `podReady`, `podError`, `podDeleted`, `podPending`, and `podComplete`. Key methods include `Run`, `checkAnnotations`, `podCompleteHandler`, `podErrorHandler`, `podDeletedHandler`, `cleanBeforeDeleted`, `podPendingHandler`, `podReadyHandler`, `recover`, `recoverTarget`, `CleanUpCache`, `applyConfigPatch`, `checkMountPodStuck`, `DoAbortFuse`, and `newMountPod`.

Control flow: `Run` refetches the pod from the API, updates the unique-ID index when status changed, removes stale target annotations first, then dispatches to a status handler. Annotation checking removes refs for app pods no longer present in the node pod snapshot, respects shared volume locks, clears delete-delay annotations when refs remain, and deletes unreferenced mount pods after optional delay and FUSE fd shutdown. Ready handling waits for the mount path, aborts/recreates stuck mount pods when supported, and recovers corrupt/missing bind targets. Deleted handling may clean mount paths and caches or create a replacement pod if references still exist. Pending/error handling can remove resource requests and recreate pods when scheduling failed due to resources. Complete handling creates a replacement when needed and deletes the completed pod.

State and persistence: persistent changes include pod creation/deletion, finalizer removal, secret create/update/delete, pod spec/object metadata mutation before create/update, annotation deletion, mount/unmount operations on the host, FUSE fd server state, saved FUSE dev minor files, abort Jobs, and cache cleanup jobs/commands. The unique-ID index and mountinfo table are per-reconcile in-memory snapshots with a lock for concurrent goroutine use.

Dependencies and integration points: heavily integrates with `config.GenSettingAttrWithMountPod`, `builder.NewPodBuilder`, `podmount.GenPodNameByUniqueId`, passfd FUSE handoff, resource utilities, Kubernetes API errors, controllerutil finalizers, util mount/path helpers, and mountinfo status classification. It is called only through `PodController`.

Risks: this is high-risk host/node code. It performs real unmounts, bind mounts, pod deletion/recreation, and background goroutines. Several loops sleep for 500 microseconds while waiting for pod deletion, which may be aggressive. `checkAnnotations` considers refs absent from the local snapshot as deleted, so stale cache/listing can remove annotations prematurely unless shared locks protect the path. `applyConfigPatch` mutates the input pod’s `Spec` and `ObjectMeta`, so callers must understand ownership. `newMountPod` has complex smooth-upgrade behavior around FUSE fd handoff and support detection. Error handling often logs and continues for cleanup paths, which favors availability but can hide partial cleanup failure.

Test signals: no direct tests for `pod_driver.go` are included in this subset. It is indirectly supported by tests for config setting, mountinfo resolution, and common resource utilities elsewhere, but the lifecycle state machine itself lacks direct coverage in the listed files.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/controller/pod_driver.go -->
