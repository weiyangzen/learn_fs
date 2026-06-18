# subset-b-000424 Research

Grouped research report for the requested Rook command and Helm chart files. Each file section preserves the original source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/osd.go -->
## sources/control-plane/rook/cmd/rook/ceph/osd.go

Purpose: defines hidden `rook ceph osd` Cobra subcommands for OSD config initialization, provisioning, starting a ceph-volume-provisioned OSD, and removing OSDs. It is the CLI bridge between Kubernetes/operator-provided flags and lower-level Ceph OSD daemon/orchestration packages.

Important APIs and functions: `addOSDFlags()` wires flags for device selection, store config, PVC-backed OSDs, replacement OSDs, and removal options. `verifyConfigFlags()` enforces cluster/node and Ceph monitor credential flags. `writeOSDConfig()`, `prepareOSD()`, `startOSD()`, and `removeOSDs()` are command handlers. `parseDevices()` converts JSON `osdcfg.ConfiguredDevice` input into daemon `DesiredDevice` values. `readCephSecret()` reads the mounted mon secret and falls back to `ROOK_CEPH_SECRET`.

Control flow: init registers flags, applies `ROOK_*` env overrides, and assigns handlers. Provisioning verifies required flags, loads the Ceph secret, selects devices from exact JSON, regex filter, or path filter, builds a Rook cluster context, initializes monitor endpoints, derives CRUSH location, writes Ceph config, optionally destroys a replacement OSD, creates an OSD agent, then calls `osddaemon.Provision()`. On provisioning failure, it records an `OrchestrationStatusFailed` entry in the Kubernetes ConfigMap KV store before terminating. Start and remove paths validate inputs, initialize shared config, then delegate to daemon start/remove helpers.

State and persistence: mutates global `cfg` and `clusterInfo`, reads secrets from mounted files/env, writes Ceph config and OSD orchestration status, and can destroy/remove OSDs or backing devices through downstream daemon calls. Dependencies include Kubernetes client-go, Rook operator controller helpers, Ceph client/config packages, and Cobra/pflag env flag helpers.

Risks: replacement/removal and `force-format` paths are destructive. Device selection flags are mutually exclusive only in provisioning logic, so validation regressions could select unintended disks. Boolean removal flags are strings due flag parsing issues, which creates parse-failure risk. Secret fallback via environment variable is retained for compatibility but is less secure. Test signals are in `osd_test.go` for device parsing and secret fallback only; cluster interactions and destructive workflows rely on integration/downstream tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/osd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/osd_test.go -->
## sources/control-plane/rook/cmd/rook/ceph/osd_test.go

Purpose: unit-tests the local helper behavior in `osd.go`, specifically configured device parsing and Ceph secret loading. It does not exercise the full Cobra command paths or Kubernetes/Ceph orchestration.

Important APIs and functions: `TestParseDesiredDevices()` builds `osdcfg.ConfiguredDevice` slices, marshals them to JSON, calls `parseDevices()`, and asserts the resulting `osddaemon.DesiredDevice` fields. `TestReadSecretFile()` calls `readCephSecret()` against missing, env-backed, empty, and populated secret sources.

Control flow: tests are table-like but implemented inline. The parsing test covers multiple devices, invalid negative and zero `OSDsPerDevice`, propagation of `DatabaseSizeMB`, `DeviceClass`, and `MetadataDevice`, and empty input returning an empty slice. The secret test first expects a missing file error, then sets `ROOK_CEPH_SECRET` to verify fallback, creates a temp file to verify empty-file rejection, and finally writes a keyring value to confirm file-based loading.

State and persistence: uses temp files and environment variables, and mutates package-level `clusterInfo.CephCred.Secret`. Because global state is shared with other package tests, future tests should reset env and `clusterInfo` carefully.

Dependencies and integration points: depends on `testify/assert`, Go `encoding/json`, and the OSD config/daemon types whose field names define the JSON contract expected by the operator. These tests provide useful regression signals for CLI/operator data handoff but do not validate downstream Ceph or Kubernetes side effects. Risks include missing coverage for flag validation, filter/path-filter exclusivity, OSD removal boolean parsing, orchestration status updates, and fatal termination behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/osd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/discover.go -->
## sources/control-plane/rook/cmd/rook/discover.go

Purpose: defines the hidden `rook discover` command used by the operator to run the device discovery daemon. It periodically discovers storage devices and optionally augments data via `ceph-volume inventory`.

Important APIs and functions: `discoverCmd` is the Cobra command. `init()` registers `--discover-interval` and `--use-ceph-volume`, applies `ROOK_*` environment overrides, and binds `RunE` to `startDiscover()`. `startDiscover()` sets logging, logs startup flags, creates the in-cluster Rook context, and calls `discover.Run()`.

Control flow: command execution is straightforward: parse flags/env, initialize logging, create Kubernetes/Rook clients via `rook.NewContext()`, then delegate the long-running loop to `pkg/daemon/discover`. Errors from discovery are treated as fatal with `rook.TerminateFatal()`.

State and persistence: this file has no direct persistence. State is in the daemon package and Kubernetes resources it updates. The command consumes process env, command flags, and in-cluster configuration.

Dependencies and integration points: integrates with `cmd/rook/rook` for logging/context, `pkg/daemon/discover` for actual scanning, Cobra for CLI, and the shared flag/env loader. Risks: hidden command assumes it runs in a Kubernetes pod with valid service account credentials; bad intervals or ceph-volume behavior are not validated here. Test signals are absent in this file; confidence depends on daemon package tests and operator deployment tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/discover.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/main.go -->
## sources/control-plane/rook/cmd/rook/main.go

Purpose: entry point for the `rook` binary. It assembles root-level command groups, hides backend/operator commands from normal users, adds user-facing commands, and executes `rook.RootCmd`.

Important APIs and functions: `main()` calls `addCommands()` and then `rook.RootCmd.Execute()`. `addCommands()` registers version, discovery, key management, Ceph backend, and utility commands, marks all currently registered root commands hidden, then adds `userfacing.Commands`.

Control flow: backend commands are added first and then hidden as a second line of defense. User-facing commands are added after this hiding loop so their own package can make them visible and attach signal/logging behavior. Execution errors are printed to stdout with a formatted `rook error` message rather than fatal termination.

State and persistence: no persistent state; this file mutates the global Cobra command tree at process startup. Dependencies include command packages whose init functions also register flags/subcommands.

Integration points: this is the boundary between operator-internal CLI surfaces and supported user commands. Ordering matters: if a future user-facing command is added before the hide loop, it may be hidden unintentionally; if a backend command is added after the loop, it may be exposed unless explicitly hidden. Test signals are not present here. Risks include global Cobra state interactions and silent continuation after `Execute()` returns an error because `main()` does not call `os.Exit(1)`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/rook/rook.go -->
## sources/control-plane/rook/cmd/rook/rook/rook.go

Purpose: shared command infrastructure for the Rook binary. It defines the root command, logging setup, Kubernetes/Rook client context creation, operator pod introspection helpers, fatal termination behavior, Ceph version detection, and flexible Kubernetes client creation for user-facing tools.

Important APIs and functions: `RootCmd`, `SetLogLevel()`, `LogStartupInfo()`, `NewContext()`, `GetOperatorImage()`, `GetOperatorServiceAccount()`, `CheckOperatorResources()`, `TerminateOnError()`, `TerminateFatal()`, `GetOperatorBaseImageCephVersion()`, and `GetInternalOrExternalClient()`.

Control flow: init registers persistent `--log-level`, initializes Cobra help/completion, applies `ROOK_*` env overrides, and sets a quiet controller-runtime zap logger. `NewContext()` creates an in-cluster REST config and Kubernetes, Rook, NetworkAttachmentDefinition, and apiextensions clients; failures terminate. `GetInternalOrExternalClient()` tries each `KUBECONFIG` path, then default CLI config, then in-cluster config.

State and persistence: global `logLevelRaw`, `RootCmd`, and package logger drive process behavior. `TerminateFatal()` appends errors to `/dev/termination-log` and exits through fatal logging. `CheckOperatorResources()` sets `OPERATOR_RESOURCES_SPECIFIED` when the running operator container has resources configured.

Dependencies and integration points: central dependency for almost all Rook CLI commands. It depends on client-go, Rook generated clients, NAD clients, controller-runtime logging, and Rook utility packages. Risks: in-cluster-only `NewContext()` makes hidden commands unsuitable outside pods; termination-log writes assume the file exists and is writable; global logging/env state can make tests order-sensitive. No direct tests are listed here.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/rook/rook.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/secret.go -->
## sources/control-plane/rook/cmd/rook/secret.go

Purpose: hidden key-management utility commands for retrieving KMS secrets and rotating OSD key encryption keys. It is intended for operator-controlled encrypted OSD workflows.

Important APIs and functions: `KeyManagementCmd` is the parent Cobra command. `startSecret()` builds signal-aware context, reads namespace and cluster name from env, fetches the `CephCluster`, validates KMS connection details when enabled, and returns a KMS config plus Rook context. `cliGetSecret()`/`getSecret()` fetch a KMS key and write it to a file. `cliRotateSecret()`/`rotateSecret()` invoke `osd.RotateKeyEncryptionKey()`.

Control flow: commands are added during init. Both operational handlers establish a shutdown-signal context. `getSecret()` requires exactly two args, gets a named secret, rejects empty values, and writes the output file with mode `0400`. `rotateSecret()` accepts a secret name plus data/metadata/wal device paths, then delegates key rotation.

State and persistence: reads `POD_NAMESPACE` and `ROOK_CLUSTER_NAME`; reads the CephCluster CR; may validate external KMS connectivity; writes secret material to a file; and mutates encrypted devices during rotation through downstream OSD logic.

Dependencies and integration points: KMS config, Ceph cluster client, operator shutdown signal list, Kubernetes/Rook clients, and encrypted OSD packages. Risks: secret file output path is user-provided; rotation is device-destructive if given wrong paths; fatal exits reduce composability. There are no direct tests here, so validation should include KMS-enabled e2e and rotation workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/secret.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/multus/multus.go -->
## sources/control-plane/rook/cmd/rook/userfacing/multus/multus.go

Purpose: defines the visible `rook multus` command grouping for tools that help users configure Multus or compatible multi-network providers for Rook.

Important APIs and functions: `Cmd` is the Cobra command with `Use: multus`; init attaches `validation.Cmd` as its subcommand. The long description points to the Kubernetes Network Plumbing Working Group multi-network spec.

Control flow: no runtime logic beyond command tree assembly. All execution is delegated to subcommands in the validation package and to shared user-facing command setup.

State and persistence: no local state. It depends on global Cobra command registration and the validation package.

Integration points: `cmd/rook/main.go` exposes this through `userfacing.Commands`, and `userfacing.go` wraps it with interrupt handling, logging setup, and help initialization. Risks are low, but adding more subcommands should account for the user-facing package's persistent pre/post run behavior. Test signals are absent; coverage depends on CLI/help tests or validation package tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/multus/multus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/multus/validation/config.go -->
## sources/control-plane/rook/cmd/rook/userfacing/multus/validation/config.go

Purpose: provides `rook multus validation config` subcommands that print example validation-test YAML for common deployment scenarios.

Important APIs and functions: `configCmd` is the parent. `converged`, `dedicated-storage-nodes`, and `stretch-cluster` each call a constructor in `pkg/daemon/multus`, convert the resulting config to YAML with `ToYAML()`, and print it to stdout.

Control flow: init attaches the three scenario commands. Each command has no args and returns conversion errors to Cobra. There is no filesystem or Kubernetes interaction.

State and persistence: stateless. Output is generated from defaults in the daemon multus package, so the content version tracks daemon config types rather than static YAML in this file.

Dependencies and integration points: depends on `pkg/daemon/multus` default config constructors and Cobra. It supports the `validation run --config` path by giving users valid config starting points. Risks: scenario defaults can drift from documentation or actual validation behavior; stdout-only output means shell redirection is expected. No direct tests are present in this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/multus/validation/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/multus/validation/validation.go -->
## sources/control-plane/rook/cmd/rook/userfacing/multus/validation/validation.go

Purpose: implements the visible Multus validation CLI for running, cleaning up, and configuring network validation tests before installing Rook with Multus.

Important APIs and functions: `Cmd`, `runCmd`, and `cleanupCmd` are Cobra commands. Global `validationConfig` holds a `multus.ValidationTest`. `runValidation()` handles config-file loading, CLI-derived defaults, validation, execution, report printing, success cleanup, and exit codes. `runCleanup()` deletes test resources. Custom pflag values `timeoutMinutes` and `timeoutSeconds` validate positive durations.

Control flow: init creates defaults, registers flags on run/cleanup, sets network/service-account/image/host-check and config-file options, and marks `--config` mutually exclusive with most run flags except `--host-check-only`. Run and cleanup obtain a Kubernetes client via `rook.GetInternalOrExternalClient()`. The run path reads YAML config if specified, otherwise builds a simple node config from `--daemons-per-node`; then validates and calls `validationConfig.Run(ctx)`. Success with no suggestions triggers cleanup and exit 0; failure or suggestions prints diagnostics and leaves resources for debugging.

State and persistence: creates and cleans Kubernetes test resources through `pkg/daemon/multus`. Reads optional config file and `KUBECONFIG`. Mutates process-global `validationConfig`, which can make tests or repeated command invocations order-sensitive.

Dependencies and integration points: integrates user-facing CLI, Kubernetes client selection, and multus validation daemon logic. Risks: explicit `os.Exit()` paths complicate unit tests; leaving resources after suggestions/failure is intentional but can surprise automation; config-file mutual exclusion must stay synced with new flags. Direct tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/multus/validation/validation.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/userfacing.go -->
## sources/control-plane/rook/cmd/rook/userfacing/userfacing.go

Purpose: centralizes baseline behavior for supported user-facing Rook CLI commands.

Important APIs and functions: `Commands` currently contains `multus.Cmd`. init iterates commands and ensures they are visible, have signal-aware context setup, configure logging, validate args, stop signal capture after execution, and initialize help command/flag.

Control flow: each command gets a `PersistentPreRunE` that creates a context canceled by Ctrl-C or SIGTERM, stores its cancel function in package-global `stopSignalCapture`, calls `rook.SetLogLevel()`, and returns `cmd.ValidateArgs(args)`. `PersistentPostRun` cancels signal capture if set.

State and persistence: no external persistence, but uses package-global cancel state. It mutates command definitions at init time.

Dependencies and integration points: bridges user-facing commands with shared root logging and graceful cancellation. It relies on Cobra pre/post-run semantics; child commands that define their own persistent pre/post runs could override this behavior. Risks: a single global `stopSignalCapture` assumes one command execution per process; `cmd.ValidateArgs()` in pre-run can be redundant with Cobra's normal args validation and may have subtle interactions. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/userfacing/userfacing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/util/cmdreporter.go -->
## sources/control-plane/rook/cmd/rook/util/cmdreporter.go

Purpose: hidden utility command that runs a command to completion and stores stdout, stderr, and return code in a Kubernetes ConfigMap. It is intended to be invoked via operator helpers rather than by end users.

Important APIs and functions: `CmdReporterCmd` defines flags `--command`, `--config-map-name`, and `--namespace`, all required. `runCmdReporter()` parses the JSON-list command string, creates a signal-aware context, builds the Rook Kubernetes context, constructs `pkg/daemon/util.CmdReporter`, and runs it.

Control flow: init declares flags and panics if required marking fails. Runtime parsing is delegated to `util.CmdReporterFlagArgumentToCommand()`. A nonzero child command return code is not itself a command error; errors are reserved for parse/run/storage failures per the command long description.

State and persistence: writes or overwrites command result data in a ConfigMap and applies ownership/application labeling in the daemon utility. Reads in-cluster Kubernetes credentials. Hidden command state is only flag globals.

Dependencies and integration points: used by operator/k8sutil wrappers for jobs or diagnostics. Risks: command input is powerful by design; RBAC and caller construction must constrain it. ConfigMap overwrite behavior is intentional but requires label conflict safeguards downstream. No direct tests in this file; parser/reporter package tests are the likely signal.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/util/cmdreporter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/util/doc.go -->
## sources/control-plane/rook/cmd/rook/util/doc.go

Purpose: package documentation for `cmd/rook/util`, stating that it contains top-level utility commands that are neither storage backends nor tied to a specific backend.

Important APIs and functions: no exported runtime symbols beyond the package declaration. The meaningful command in this subset is `CmdReporterCmd` in `cmdreporter.go`.

Control flow, state, and persistence: none. It affects Go documentation and package organization only.

Dependencies and integration points: no imports. It gives maintainers a place to add utility commands without conflating them with Ceph backend commands or user-facing command groups. Risks and tests are minimal; any behavior risk belongs to concrete files in the package.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/util/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/version/version.go -->
## sources/control-plane/rook/cmd/rook/version/version.go

Purpose: implements the `rook version` command that prints the Rook build version and Go runtime version.

Important APIs and functions: `VersionCmd` is a Cobra command with `Use: version`; its `RunE` prints `rook: <version.Version>` and `go: <runtime.Version()>`.

Control flow: no flags or arguments are declared. On execution it writes to stdout and returns nil. In `main.go`, the command is initially added with backend commands and hidden by the root command hiding loop unless separately exposed elsewhere.

State and persistence: no persistent state. It reads `github.com/rook/rook/pkg/version.Version` and Go runtime metadata.

Dependencies and integration points: useful for debugging image/build/runtime skew. Risks are low; the main subtlety is command visibility because `main.go` hides all commands added before user-facing commands. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/ceph-csi-drivers/values.yaml -->
## sources/control-plane/rook/deploy/charts/ceph-csi-drivers/values.yaml

Purpose: provides Rook-compatible defaults for installing the upstream `ceph-csi-drivers` chart alongside the Rook operator chart.

Important configuration: `operatorConfig.namespace` defaults to `rook-ceph`; `driverSpecDefaults.imageSet.name` points at `rook-csi-operator-image-set-configmap`; node and controller CSI plugins get critical priority classes. Driver blocks enable RBD and CephFS by default and disable NFS and NVMe-oF, with provisioner names matching Rook naming conventions such as `rook-ceph.rbd.csi.ceph.com`.

Control flow: values-only file consumed by Helm and the ceph-csi-operator dependency. No templating logic in this file, but comments explain that driver names must match Rook provisioner names in StorageClasses and VolumeSnapshotClasses.

State and persistence: influences Kubernetes CSI driver resources rendered by the ceph-csi-drivers chart, not directly by Rook templates. Misconfiguration persists as mismatched driver names and broken dynamic provisioning.

Dependencies and integration points: tightly coupled to `rook-ceph/templates/configmap.yaml`, which renders the image set ConfigMap, and to cluster chart StorageClasses that use RBD/CephFS provisioner names. Risks: changing the Rook operator namespace requires changing driver names; enabling disabled drivers requires matching Rook/operator support and RBAC. Test signal should come from Helm render tests and CSI provisioning e2e.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/ceph-csi-drivers/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/library/Chart.yaml -->
## sources/control-plane/rook/deploy/charts/library/Chart.yaml

Purpose: declares the Rook Helm library chart used to share template definitions across Rook charts.

Important metadata: apiVersion v2, name `library`, type `library`, version `0.0.1`, and description. Developer notes define conventions: all templates should start with `_`, helper names should use `library.*`, cluster-scoped definitions should use `library.cluster.*`, and feature templates are preferred over scattering related content.

Control flow: as a Helm library chart, it does not render standalone Kubernetes resources. It provides named templates included by dependent charts such as `rook-ceph` and `rook-ceph-cluster`.

State and persistence: no cluster state directly. It affects rendered manifests through included templates.

Dependencies and integration points: dependent chart `Chart.yaml` files reference this chart via `file://../library`. Notes describe symlink usage to avoid churn from `helm dependency update` archives. Risks: breaking helper names or assumptions can affect multiple charts at once; Helm dependency packaging behavior should be validated in chart tests. No direct runtime tests are represented in this file.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/library/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/Chart.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/Chart.yaml

Purpose: declares the Helm chart that manages a single Ceph cluster namespace for Rook.

Important metadata: apiVersion v2, name `rook-ceph-cluster`, version/appVersion `0.0.1`, icon and source URL, and a dependency on the local `library` chart.

Control flow: this chart renders CephCluster-scoped resources such as CephCluster, pools, filesystems, object stores, dashboard exposure, toolbox deployment, monitoring rules, RBAC, SCC, and snapshot classes according to `values.yaml`.

State and persistence: chart install/upgrade manages namespace-scoped and some cluster-scoped Kubernetes resources for a Ceph cluster. Persistent effects include Ceph CRs that cause operator reconciliation and storage resources.

Dependencies and integration points: expects the Rook operator chart to be installed, and uses library chart helpers. Risks: version/appVersion placeholders require release automation to stamp real values; dependency path assumes repository chart layout. Test signals should include Helm lint/template rendering and operator e2e installs for representative values.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/externalrules.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/externalrules.yaml

Purpose: Prometheus alert rules for external Ceph cluster mode, where Rook provisions Kubernetes consumers for a Ceph cluster not fully managed locally.

Important content: defines `persistent-volume-alert.rules` with `PersistentVolumeUsageNearFull` and `PersistentVolumeUsageCritical`. Both alerts calculate PVC used/capacity ratios by joining kubelet volume stats with PVC and StorageClass metadata, restricted to provisioners matching RBD or CephFS CSI drivers.

Control flow: selected by `templates/prometheusrules.yaml` when `.Values.cephClusterSpec.external.enable` is true. The PrometheusRule template can merge overrides or disable rules by alert name through `monitoring.prometheusRuleOverrides`.

State and persistence: renders into a `PrometheusRule` CR when monitoring rule creation is enabled. It does not mutate Ceph state but drives alerting state in Prometheus/Alertmanager.

Dependencies and integration points: requires kubelet volume metrics, kube-state-metrics PVC/storageclass metrics, and Prometheus Operator CRDs. Risks: label joins assume `cluster`, `namespace`, `persistentvolumeclaim`, and `storageclass` labels are available; external clusters get only PVC capacity alerts here, not full Ceph health coverage. Test signals should include YAML parse/render and PromQL validation where available.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/externalrules.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/localrules.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/localrules.yaml

Purpose: default Prometheus alert rules for locally managed Ceph clusters. The file is adapted from Ceph mixin alerts with Rook-specific changes, excluding cephadm alerts and adding/adjusting Prometheus scrape-job alerts.

Important rule groups: cluster health, monitors, OSDs, MDS/CephFS, mgr/prometheus module, placement groups, nodes, pools, health checks, hardware, Prometheus server scrape jobs, RADOS, generic daemon crashes, RBD mirror, NVMe-oF, and certificate manager. Alerts cover quorum risk, disk pressure, OSD down/full/flapping/read errors, PG unclean/damaged/unavailable, filesystem damage/offline/degraded/read-only, pool fullness/growth, slow ops, hardware failures, missing scrape jobs, RBD mirror sync problems, NVMe-oF scale/latency/security/interface concerns, and Ceph certificate warnings/errors.

Control flow: loaded by `templates/prometheusrules.yaml` when the CephCluster is not external. That template can override fields or disable individual rules by alert/record name.

State and persistence: rendered as PrometheusRule CR content; it affects alerting and operational response, not Ceph state. PromQL uses Ceph mgr/exporter metrics, node exporter metrics, kube metrics, and alert-template queries.

Dependencies and integration points: depends on monitoring being enabled, Prometheus Operator CRDs, Ceph mgr prometheus module/exporter metrics, node exporter, and consistent `cluster` labels. Risks: PromQL joins and label expectations are fragile across metric version changes; some alerts use Ceph health-detail names that may change with Ceph releases; broad rule volume can create noise unless overrides are tuned. Test signal should include render, YAML parse, and Prometheus rule validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/prometheus/localrules.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephblockpool.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephblockpool.yaml

Purpose: renders CephBlockPool CRs and optional RBD StorageClasses from `.Values.cephBlockPools`.

Important template behavior: iterates each block pool, emits `ceph.rook.io/v1` `CephBlockPool` in the release namespace with raw `.spec`, then emits a `storage.k8s.io/v1` StorageClass when `storageClass.enabled` is true. The StorageClass includes labels/annotations, default-class annotation, RBD CSI provisioner derived from `csiDriverNamePrefix` or `operatorNamespace`, pool and clusterID parameters, user-supplied parameters rendered through `tpl`, reclaim policy, expansion, binding mode, mount options, and allowed topologies.

Control flow: value-driven range with conditionals for optional StorageClass and nested fields.

State and persistence: creates Ceph pools through Rook operator reconciliation and creates cluster-scoped StorageClasses. StorageClass defaults can affect all future PVCs.

Dependencies and integration points: depends on Rook CephBlockPool CRD, CSI RBD driver naming, secrets configured in values parameters, and operator namespace convention. Risks: `tpl` allows values to reference Helm context, useful but capable of rendering invalid/surprising parameters; setting `isDefault` can change cluster-wide storage behavior; mismatched driver names break provisioning. Helm render tests should cover prefix/operator namespace variants.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephblockpool.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephcluster.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephcluster.yaml

Purpose: renders the primary `CephCluster` custom resource for the cluster chart.

Important template behavior: sets metadata name from `.Values.clusterName` or the release namespace, places it in the release namespace, and applies optional labels/annotations from `cephClusterMetadata`. The spec optionally renders monitoring settings, optional `cephImage` as `cephVersion`, then appends raw `.Values.cephClusterSpec`.

Control flow: simple single-resource template with `with` blocks. Monitoring values are rendered before the generic cluster spec, so users should avoid duplicating incompatible monitoring keys in `cephClusterSpec`.

State and persistence: creates/updates the CephCluster CR, which drives operator reconciliation of the entire Ceph deployment. Persistent effects include host data directories, daemons, secrets, ConfigMaps, services, and storage lifecycle managed by the operator.

Dependencies and integration points: depends on the CephCluster CRD and Rook operator. `cephImage` provides a chart-level override while `cephClusterSpec` mirrors CRD shape. Risks: raw `toYaml` of cluster spec gives power but little chart-side validation; dangerous fields such as cleanup policy, storage discovery, and unsupported Ceph versions are passed through. Test signals should include Helm rendering and e2e operator reconciliation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephcluster.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephecblockpool.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephecblockpool.yaml

Purpose: renders erasure-coded block pool support from `.Values.cephECBlockPools`, including data and metadata pools plus optional RBD StorageClass.

Important template behavior: for each entry it creates a data `CephBlockPool` named `<name>` and replicated metadata pool named `<name>-metadata`, rendering `spec.dataPool` and `spec.metadataPool`. When storageClass is enabled, it creates an RBD StorageClass with provisioner from `csiDriverNamePrefix` or `operatorNamespace`, clusterID, metadata pool, dataPool, image settings, fixed RBD CSI secret references, ext4 fstype, expansion, and reclaim policy.

Control flow: range over values; StorageClass conditional. Unlike the normal blockpool template, many CSI parameters are hard-coded instead of arbitrary `tpl` parameters.

State and persistence: creates Ceph pools and cluster-scoped StorageClass. Erasure-coded pools affect durability/performance tradeoffs and require correct metadata pool setup.

Dependencies and integration points: depends on Rook CephBlockPool CRD and RBD CSI driver. Risks: clusterID in values can drift from release namespace; incorrect EC parameters or metadata pool settings can create unusable or unsafe storage; hard-coded secret names assume standard Rook CSI secret generation. Default values keep this disabled/commented, so render coverage may be weaker unless explicitly tested.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephecblockpool.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephfilesystem.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephfilesystem.yaml

Purpose: renders CephFS resources and optional CephFS StorageClasses from `.Values.cephFileSystems`.

Important template behavior: for each filesystem it creates a `CephFilesystemSubVolumeGroup` named `<filesystem>-csi` with filesystemName and default distributed pinning, then creates the `CephFilesystem` CR from raw `spec`. If `storageClass.enabled`, it creates a CephFS CSI StorageClass with provisioner from `csiDriverNamePrefix` or `operatorNamespace`, fsName, pool name defaulting to `<fs>-data0`, clusterID, templated user parameters, reclaim policy, expansion, binding mode, and mount options.

Control flow: range with StorageClass conditional and optional fields. A YAML document separator is emitted before the conditional StorageClass, which should be checked in disabled cases for clean rendering.

State and persistence: creates CephFS metadata/data pools and MDS daemons through Rook, a subvolume group, and optional cluster-scoped StorageClass. StorageClass choices persist into PVC provisioning.

Dependencies and integration points: relies on CephFilesystem and CephFilesystemSubVolumeGroup CRDs plus CephFS CSI driver. Risks: pool name must correspond to a real filesystem data pool; default StorageClass toggles can affect cluster-wide PVC binding; `tpl` parameters may render invalid values. Tests should include enabled/disabled storage class renders and non-default pool values.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephfilesystem.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-httproute.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-httproute.yaml

Purpose: renders Gateway API HTTPRoute resources for Ceph RGW object stores with route exposure enabled.

Important template behavior: iterates `.Values.cephObjectStores` and checks `route.enabled` via `dig`. For enabled stores, it creates `gateway.networking.k8s.io/v1` `HTTPRoute` in the release namespace, with optional annotations, hostname, parentRefs, one backendRef to `rook-ceph-rgw-<store-name>`, port from route override or gateway secure/plain port, and path match defaults.

Control flow: pure values range with optional output per object store.

State and persistence: creates HTTPRoute resources that route external or internal Gateway API traffic to RGW services. It does not configure RGW itself.

Dependencies and integration points: requires Gateway API CRDs and a compatible Gateway/controller. It depends on Rook operator-created RGW service naming. Risks: if route port defaults to a nil gateway port, rendered manifests may be invalid; parentRefs and hostnames must match cluster Gateway policy; securePort selection may need TLS backend alignment. Test signals should include Helm render with route enabled and Gateway API validation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-httproute.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-ingress.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-ingress.yaml

Purpose: renders Kubernetes Ingress resources for Ceph RGW object stores with ingress exposure enabled.

Important template behavior: iterates `.Values.cephObjectStores` and checks `ingress.enabled` via `dig`. For enabled stores, it creates `networking.k8s.io/v1` `Ingress` in the release namespace, with optional annotations, host/path/pathType, backend service `rook-ceph-rgw-<store-name>`, port from ingress override or RGW secure/plain port, optional ingressClassName, and optional TLS.

Control flow: per-object-store conditional output.

State and persistence: creates Ingress resources for RGW service exposure. It relies on an external ingress controller for actual routing.

Dependencies and integration points: depends on Rook RGW service naming, user-supplied host/TLS/class, and Kubernetes networking API. Risks: TLS/backend protocol annotations must match whether RGW uses securePort; host/path defaults can expose services broadly; missing ingress controller support leaves resources inert. Tests should render ingress-enabled object stores with secure and plain ports.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore-ingress.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore.yaml

Purpose: renders CephObjectStore CRs and optional Object Bucket Claim StorageClasses from `.Values.cephObjectStores`.

Important template behavior: for each object store, creates `CephObjectStore` in the release namespace with raw `.spec`. If `storageClass.enabled`, creates a StorageClass with provisioner `<release-namespace>.ceph.rook.io/bucket`, objectStoreName/objectStoreNamespace parameters, optional labels/annotations, reclaim policy, binding mode, and user-supplied parameters.

Control flow: range over object stores with optional StorageClass document.

State and persistence: causes the Rook operator to create RGW/object-store resources and creates a cluster-scoped bucket provisioner StorageClass for ObjectBucketClaims.

Dependencies and integration points: depends on CephObjectStore CRD, lib-bucket-provisioner/Rook bucket provisioning, and RGW service naming used by ingress/route templates. Risks: StorageClass provisioner uses release namespace directly rather than operator namespace; incorrect region or store names break bucket provisioning; object store specs can preserve pools on delete, affecting cleanup expectations. Tests should include object store with storage class enabled and disabled.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/cephobjectstore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/configmap.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/configmap.yaml

Purpose: conditionally renders a `rook-config-override` ConfigMap that carries custom Ceph config overrides into cluster tooling and operator-managed daemons.

Important template behavior: if `.Values.configOverride` is non-empty, creates a v1 ConfigMap named `rook-config-override` in the release namespace with `data.config` containing the provided multi-line config.

Control flow: single conditional. Uses `nindent` to preserve block scalar formatting.

State and persistence: stores arbitrary Ceph config override text in Kubernetes. The toolbox deployment mounts this ConfigMap and merges it into generated `ceph.conf`; operator behavior may also consume this standard name depending on Rook reconciliation.

Dependencies and integration points: linked to values comments and toolbox script. Risks: arbitrary Ceph config can destabilize clusters; malformed config is not chart-validated; ConfigMap absence must be handled by consumers as optional. Test signal should include render with empty and non-empty overrides.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/deployment.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/deployment.yaml

Purpose: renders the optional `rook-ceph-tools` toolbox Deployment when `.Values.toolbox.enabled` is true.

Important template behavior: creates one replica with labels, optional revision history, host networking if the CephCluster network provider is host, configurable image/security/resources/tolerations/affinity/priority, and service account `rook-ceph-default`. The container runs an inline bash script that builds `/etc/ceph/ceph.conf` from mon endpoints, writes a keyring from `ROOK_CEPH_SECRET` or mounted secret file, merges optional config override, and watches mon endpoint ConfigMap changes every 10 seconds.

Control flow: template conditional for the whole Deployment, plus inline shell loops for runtime config regeneration.

State and persistence: mounts mon secret, mon endpoints ConfigMap, optional config override, and emptyDir ceph config. It writes generated config/keyring inside the pod only. Persistent cluster effects come from user actions run inside the toolbox.

Dependencies and integration points: depends on Rook-created `rook-ceph-mon` secret and `rook-ceph-mon-endpoints` ConfigMap. Risks: inline shell parsing of mon endpoints is brittle; env-secret fallback is less secure; toolbox grants admin access to users with pod exec; host networking follows cluster network choice. Tests should render enabled toolbox with host and non-host networking.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/httproute.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/httproute.yaml

Purpose: renders a Gateway API HTTPRoute for the Ceph dashboard when `.Values.route.dashboard.host` is configured.

Important template behavior: creates `HTTPRoute` named `<clusterName>-dashboard`, applies optional labels/annotations, sets hostnames, parentRefs, backend service `rook-ceph-mgr-dashboard`, port from explicit dashboard port or defaults to 8443 for SSL and 7000 for non-SSL, and path match from values.

Control flow: single conditional around dashboard route host presence.

State and persistence: exposes the mgr dashboard through Gateway API. It does not enable the dashboard; that comes from CephCluster spec.

Dependencies and integration points: requires Gateway API CRDs/controller and Rook-created dashboard service. Risks: backend TLS expectations are not encoded in HTTPRoute; wrong port defaults or parentRefs break routing; exposing dashboard should be paired with auth/TLS policy. Tests should render with SSL and non-SSL dashboard settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/httproute.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/ingress.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/ingress.yaml

Purpose: renders a Kubernetes Ingress for the Ceph dashboard when `.Values.ingress.dashboard.host` is configured.

Important template behavior: creates `Ingress` named `<clusterName>-dashboard`, applies optional labels/annotations, host/path/pathType, backend service `rook-ceph-mgr-dashboard`, backend port name `https-dashboard` when dashboard SSL is true or `http-dashboard` otherwise, optional ingressClassName, and optional TLS.

Control flow: single conditional on dashboard ingress host.

State and persistence: exposes the Ceph mgr dashboard through an ingress controller. It does not manage dashboard auth or the underlying service.

Dependencies and integration points: depends on Rook-created mgr dashboard service and ingress controller behavior. Risks: annotations must align with SSL backend behavior, especially for NGINX; only one ingress class mechanism should be used per values comments; exposing dashboard without proper TLS/auth policy is sensitive. Render tests should cover SSL true/false and TLS/class settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/ingress.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/prometheusrules.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/prometheusrules.yaml

Purpose: renders a Prometheus Operator `PrometheusRule` resource for Ceph alerts when monitoring rule creation is enabled.

Important template behavior: gated by `.Values.monitoring` and `.Values.monitoring.createPrometheusRules`. It labels the rule for rook-prometheus, applies optional labels/annotations, selects `prometheus/localrules.yaml` by default or `prometheus/externalrules.yaml` when `cephClusterSpec.external.enable` is true, parses the file with `fromYaml`, then iterates groups/rules. For each rule it determines a name from alert or record, applies `monitoring.prometheusRuleOverrides` via `mergeOverwrite`, drops disabled rules, and omits empty groups.

Control flow: dynamic render-time rule loading and override merging.

State and persistence: creates PrometheusRule CRs, usually in release namespace or `rulesNamespaceOverride`.

Dependencies and integration points: depends on packaged rule files, Prometheus Operator CRD, Helm functions, and values schema. Risks: override names must exactly match alert/record names; malformed overrides can produce invalid Prometheus rules; external-mode detection depends on values shape. Test signals should include Helm render and promtool validation for default and override cases.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/prometheusrules.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/rbac.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/rbac.yaml

Purpose: renders CephCluster-namespace RBAC resources when the cluster chart is installed into a namespace different from the operator namespace.

Important template behavior: checks `ne .Release.Namespace .Values.operatorNamespace`, then includes library templates for cluster service accounts, clusterrolebindings, roles, rolebindings, and monitoring roles/bindings when monitoring is enabled.

Control flow: all detailed RBAC objects are delegated to the library chart. This template exists to avoid duplicating cluster-scoped resource definitions when cluster and operator share the same namespace.

State and persistence: creates service accounts and RBAC bindings required for the operator to manage Ceph resources in a separate cluster namespace.

Dependencies and integration points: depends on `library.cluster.*` templates and `monitoring.enabled`. Risks: namespace comparison is the only gate; incorrect `operatorNamespace` can omit required RBAC or create redundant bindings. Because logic is delegated, tests must render with same-namespace and separate-namespace values and inspect included library outputs.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/securityContextConstraints.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/securityContextConstraints.yaml

Purpose: renders an OpenShift `SecurityContextConstraints` resource for Rook and Ceph daemons when the cluster supports `security.openshift.io/v1`.

Important template behavior: gated by `.Capabilities.APIVersions.Has "security.openshift.io/v1"`. It creates SCC `rook-cluster-<namespace>` with privileged containers and hostPath allowed, host network/ports allowed only when `cephClusterSpec.network.provider` is `host`, capabilities `MKNOD` and `SYS_ADMIN`, host IPC, runAsAny user, SELinux/fsGroup constraints, allowed volume types, and service account users for default, mgr, osd, rgw, and nvmeof.

Control flow: Kubernetes capability detection plus network-provider conditional.

State and persistence: creates cluster-level OpenShift security policy granting elevated permissions to Rook service accounts.

Dependencies and integration points: OpenShift SCC API and Rook service account naming. Risks: SCC is broad by necessity for host storage; host network toggling must match cluster spec; missing service accounts for new daemon types can block pods. Tests should render under OpenShift capabilities and verify non-OpenShift omission.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/securityContextConstraints.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/volumesnapshotclass.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/volumesnapshotclass.yaml

Purpose: renders optional CephFS and RBD `VolumeSnapshotClass` resources.

Important template behavior: reads `.Values.cephFileSystemVolumeSnapshotClass` and `.Values.cephBlockPoolsVolumeSnapshotClass`. For each enabled class it creates `snapshot.storage.k8s.io/v1` VolumeSnapshotClass with labels, default-class annotation, driver from `csiDriverNamePrefix` or `operatorNamespace`, clusterID, standard snapshotter secret references, user parameters, and deletionPolicy defaulting to Delete.

Control flow: independent conditionals for filesystem and block-pool snapshot classes.

State and persistence: creates cluster-scoped snapshot class resources used by CSI external snapshotter. Default-class annotations can affect snapshot behavior cluster-wide.

Dependencies and integration points: requires snapshot CRDs/controller, Ceph CSI drivers, and Rook CSI secret naming. Risks: enabling defaults can conflict with other snapshot classes; driver name mismatch breaks snapshotting; deletionPolicy has data retention implications. Tests should render both enabled classes and prefix/operator namespace variants.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/volumesnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values-external.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values-external.yaml

Purpose: alternative values file for deploying the cluster chart against an external Ceph cluster.

Important configuration: `cephClusterSpec.external.enable: true`, crash collector disabled, and monitor daemon health check interval configured. Resource lists for CephBlockPools, CephFileSystems, and CephObjectStores are empty maps, so the chart does not create default local storage resources.

Control flow: values-only file consumed by Helm. In particular, `templates/prometheusrules.yaml` uses `external.enable` to select external Prometheus rules.

State and persistence: creates a CephCluster CR configured as external when combined with the chart, but avoids local pools/filesystems/object stores by default. Persistent state is mostly Kubernetes-side integration resources and external-cluster connection artifacts managed elsewhere.

Dependencies and integration points: depends on external cluster setup, secrets/config expected by Rook external cluster workflows, and the normal cluster chart templates. Risks: empty maps must be compatible with templates that normally range lists; external mode has reduced alert coverage; missing external connection prerequisites will cause operator reconciliation failures. Test signals should include Helm render with this file and external cluster e2e.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values-external.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values.yaml

Purpose: default values for installing one locally managed Rook Ceph cluster and common storage resources.

Important configuration: operator namespace, cluster name, optional config override, toolbox settings, monitoring and PrometheusRule overrides, Ceph image (`quay.io/ceph/ceph:v20.2.1` by default), and a large `cephClusterSpec`. Defaults create a converged cluster with `/var/lib/rook`, 3 mons, 2 mgrs, dashboard enabled with SSL, network encryption/compression disabled, crash and log collectors, host cleanup disabled unless explicitly confirmed, default daemon resources, disruption management, health checks, and storage discovery using all nodes and all devices. Defaults also create RBD, CephFS, and RGW object store definitions and StorageClasses; snapshot classes are disabled; EC pools are commented out; dashboard/objectstore ingress and routes are disabled by default.

Control flow: values are consumed by many templates using raw `toYaml`, ranges, and conditionals. Comments document CRD equivalents and production warnings.

State and persistence: these defaults can create real Ceph storage, host data directories, StorageClasses, pools, filesystems, object stores, and optional external exposure/alerting resources. `cleanupPolicy.confirmation` is the destructive cleanup gate.

Dependencies and integration points: depends on Rook operator, CRDs, Ceph image support, CSI driver naming, Prometheus/Gateway/Ingress/Snapshot APIs when enabled. Risks: `useAllNodes` and `useAllDevices` are dangerous in real clusters without careful node/device constraints; default StorageClass settings affect cluster-wide PVCs; image tag policy warns against floating major tags in production; cleanup and preserve/delete settings affect data retention. Tests should render default, external, monitoring, snapshot, and exposure scenarios.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph-cluster/values.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/Chart.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/Chart.yaml

Purpose: declares the Helm chart for installing the Rook Ceph operator and related operator-level resources.

Important metadata: apiVersion v2, name `rook-ceph`, description, version/appVersion `0.0.1`, icon/source, dependency on local `library`, and dependency on `ceph-csi-operator` version `1.0.1` from the Ceph repository with alias `ceph-csi-operator`, conditioned by `csi.installCsiOperator`.

Control flow: chart dependencies determine whether Helm also renders/manages the CSI operator subchart. Operator templates in this chart configure RBAC, ConfigMaps, and the operator Deployment.

State and persistence: chart install creates cluster-wide/operator namespace resources and optionally the CSI operator resources.

Dependencies and integration points: local library chart, external ceph-csi-operator chart, and values under `csi.installCsiOperator`. Risks: release automation must stamp versions; external dependency availability affects dependency update/install; disabling CSI operator changes driver management assumptions. Tests should include dependency rendering with condition true and false.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/aggregate-roles.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/templates/aggregate-roles.yaml

Purpose: optionally renders Kubernetes aggregate ClusterRoles that add ObjectBucketClaim permissions to default `view` and `edit` roles.

Important template behavior: gated by `.Values.rbacAggregate.enableOBCs`. It creates `rook-ceph-obc-view` labeled `aggregate-to-view` with get/list/watch on `objectbucketclaims`, and `rook-ceph-obc-edit` labeled `aggregate-to-edit` with create/delete/deletecollection/patch/update on `objectbucketclaims`. Both use shared chart labels from the library helper.

Control flow: all output is conditional.

State and persistence: creates cluster-scoped RBAC aggregation roles that affect users bound to Kubernetes built-in aggregate roles.

Dependencies and integration points: requires Kubernetes RBAC aggregation controller and objectbucket.io CRDs. Risks: enabling this broadens default role capabilities cluster-wide; edit role lacks get/list/watch here, relying on aggregation with view or separate permissions. Test signals should render enabled and disabled paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/aggregate-roles.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/cluster-rbac.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/templates/cluster-rbac.yaml

Purpose: renders CephCluster-scoped service accounts, roles, and bindings in the operator namespace by including library templates.

Important template behavior: always includes `library.cluster.serviceaccounts`, `library.cluster.clusterrolebindings`, `library.cluster.roles`, and `library.cluster.rolebindings`. When `.Values.monitoring.enabled` is true it also includes monitoring role and rolebinding helpers.

Control flow: no local resource definitions beyond include ordering. It mirrors the cluster chart RBAC template for the common same-namespace operator/cluster installation case.

State and persistence: creates namespace/service-account/RBAC objects needed for Rook-managed Ceph daemons and monitoring integration.

Dependencies and integration points: tightly coupled to library chart helper names and monitoring value semantics. Risks: changes in library helpers affect both operator and cluster charts; monitoring RBAC must align with Prometheus ServiceMonitor/PrometheusRule behavior. Tests should render with monitoring enabled and disabled and compare library output.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/cluster-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrole.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrole.yaml

Purpose: defines cluster-scoped RBAC permissions for the Rook Ceph operator, cluster management, mgr, object bucket provisioning, OSD node access, and COSI object storage provisioning.

Important template behavior: gated by `.Values.rbacEnable`. It creates `rook-ceph-system`, `rook-ceph-cluster-mgmt`, `rook-ceph-global`, `rook-ceph-mgr-cluster`, `rook-ceph-mgr-system`, `rook-ceph-object-bucket`, `rook-ceph-osd`, and `objectstorage-provisioner-role`. Permissions include pod/log/exec access, CSI addon/operator resources, CRD get, core services/endpoints/PV/PVC/events, jobs/cronjobs, broad watch/update/status/finalizers across Rook Ceph CRDs, PDBs/deployments/replicasets, OpenShift machine disruption resources, CSIDrivers, NAD get, OBC/OB resources, and COSI resources.

Control flow: static RBAC manifests under one feature flag.

State and persistence: creates powerful cluster roles that enable operator reconciliation across namespaces and storage APIs.

Dependencies and integration points: Kubernetes RBAC, Rook CRDs, objectbucket.io, COSI, CSI addons, OpenShift APIs, and library labels. Risks: broad permissions are operationally necessary but security-sensitive; new CRDs/subresources must be added consistently; disabling RBAC requires pre-provisioned equivalent roles. Tests should compare rendered RBAC to controller permission needs and run e2e under restricted clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrole.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrolebinding.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrolebinding.yaml

Purpose: binds cluster-scoped roles from `clusterrole.yaml` to the operator and object storage provisioner service accounts.

Important template behavior: gated by `.Values.rbacEnable`. It creates ClusterRoleBindings for `rook-ceph-system`, `rook-ceph-global`, and `rook-ceph-object-bucket` to service account `rook-ceph-system` in the release namespace, plus `objectstorage-provisioner-role-binding` to service account `objectstorage-provisioner`.

Control flow: static manifests with release namespace substitution.

State and persistence: grants cluster-wide permissions to operator and COSI service accounts.

Dependencies and integration points: depends on service account creation from library templates and roles from `clusterrole.yaml`. Risks: namespace mismatch prevents bindings from granting permissions; disabling RBAC requires equivalent external bindings; objectstorage service account must exist when COSI driver is enabled. Render and e2e tests should validate service account names across values variants.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/clusterrolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/configmap.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/templates/configmap.yaml

Purpose: renders operator configuration ConfigMaps, including mutable operator settings and CSI image-set values.

Important template behavior: always creates `rook-ceph-operator-config` in the operator namespace with data such as `ROOK_LOG_LEVEL`, Ceph command timeout, OBC watch/provisioner settings, loop devices, mon root setting, unused CRUSH rule deletion, discovery daemon enablement, optional udev blacklist, revision history limit, host network enforcement, metrics bind address, and other optional settings. A second ConfigMap `rook-csi-operator-image-set-configmap` is rendered within `.Values.csi`, adding image references for provisioner, attacher, resizer, snapshotter, registrar, cephcsi plugin, and csi-addons when repository and tag are set.

Control flow: optional keys are rendered only when values are non-empty; CSI image map is under a `with .Values.csi`.

State and persistence: stores operator settings read at runtime and image choices consumed by the CSI operator/driver specs.

Dependencies and integration points: operator code watches `rook-ceph-operator-config`; ceph-csi driver defaults reference the image-set ConfigMap. Risks: some settings require operator restart despite comments separating mutable settings; string values must match operator env parsing; missing CSI image keys may defer to defaults elsewhere. Tests should render minimal and full CSI image settings.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/deployment.yaml -->
## sources/control-plane/rook/deploy/charts/rook-ceph/templates/deployment.yaml

Purpose: renders the Rook Ceph operator Deployment.

Important template behavior: creates `rook-ceph-operator` with replicas `0` when `scaleDownOperator` is true, otherwise `1`; optional revision history; Recreate strategy; labels/annotations; priority/tolerations; operator image from `.Values.image`; args `ceph operator`; optional container security context; emptyDir mounts for `/var/lib/rook` and `/etc/ceph`; many env vars controlling namespace scope, concurrency, discovery daemon scheduling/resources, OpenShift hostpath privilege detection, custom hostname label, device hotplug, discovery interval, unreachable node toleration, and pod/node identity. It sets hostNetwork/dnsPolicy when requested, nodeSelector, service account when RBAC is enabled, and resources if provided.

Control flow: many optional value-driven env blocks, plus capability detection for OpenShift SCC behavior.

State and persistence: creates the long-running operator Deployment that reconciles all Rook Ceph resources. Runtime state is mostly in Kubernetes resources; pod-local config dirs are emptyDir.

Dependencies and integration points: depends on RBAC/service accounts, operator ConfigMap, CRDs, CSI/image settings, and Kubernetes/OpenShift capabilities. Risks: scaling operator to zero halts reconciliation; currentNamespaceOnly and RBAC scope must align; host network and privileged hostpath settings affect scheduling/security; discovery env values must parse correctly downstream. Tests should render common defaults, namespace-only, OpenShift, and scaled-down cases.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/deploy/charts/rook-ceph/templates/deployment.yaml -->
