# Research Report: subset-b-000408

Grouped research for Longhorn scalability dashboards/scripts and Mayastor CI/build configuration. Each source section is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scalability/dev/control_plane_grafana_dashboard.json -->
# sources/control-plane/longhorn/scalability/dev/control_plane_grafana_dashboard.json

## Purpose
Grafana dashboard JSON for "Longhorn Control Plane Scalability" (`uid` `OUbS8NYIl`). It observes Kubernetes workload startup behavior, Longhorn-system pod resource use, apiserver request rate, and etcd health under scalability tests. The dashboard uses Prometheus datasource `uid: prometheus`, dark style, schema version 37, five-minute refresh, and a single query variable `cluster` sourced from `label_values(etcd_server_has_leader, job)`.

## Important APIs, Types, and Queries
The file is declarative Grafana dashboard schema: top-level `templating`, built-in annotations, and `panels`. Key panel groups are row panels `Workload`, `Longhorn CPU and RAM`, and `ETCD`.

Workload panels query `kube_pod_info`, `kube_pod_status_ready_time`, `kube_pod_created`, `kube_pod_status_phase`, and `kube_pod_container_status_restarts_total` in namespace `default`. They expose pod counts, phase distribution, startup-time histogram, count of pods ready within or beyond four minutes, per-minute running transition rate, per-node pod density, top 100 slow-starting pods, and crashed pod count.

Longhorn resource panels query `node_namespace_pod_container:container_cpu_usage_seconds_total:sum_irate`, `container_memory_rss`, and `container_memory_working_set_bytes` for namespace `longhorn-system`, grouped by pod.

ETCD panels query the selected `$cluster` job for `etcd_server_has_leader`, watch/lease `grpc_server_started_total` minus `grpc_server_handled_total`, unary RPC rates/errors, `etcd_mvcc_db_total_size_in_bytes`, p99 WAL/backend commit histograms, process RSS, client and peer network byte rates, proposal failed/pending/committed/applied counters, daily leader-election changes, and p99 peer RTT.

## Control Flow
Grafana evaluates the dashboard variable first, then panel targets over the active time range. Row panels organize metrics but do not perform computation. Most panels are direct PromQL expressions; histogram and table panels depend on Grafana transformations/visualization defaults rather than custom code.

## State and Persistence
Dashboard state is entirely persisted in this JSON file: panel IDs, grid positions, datasource references, variable defaults, refresh interval, and annotation config. Runtime state lives in Grafana and Prometheus only. The dashboard assumes metrics history is retained by Prometheus and does not write application state.

## Dependencies and Integration Points
Requires Grafana schema v37 compatibility and a Prometheus datasource with `uid` `prometheus`. It integrates with kube-state-metrics, kubelet/cAdvisor recording rules, Kubernetes apiserver metrics, and etcd metrics. The `$cluster` variable assumes etcd jobs expose `etcd_server_has_leader`; default value is `kube-etcd`.

## Risks
The workload panels hard-code namespace `default`, so tests running elsewhere are invisible. The Longhorn resource panels hard-code namespace `longhorn-system`. The `cluster` variable is tied to etcd job labels and can silently miss metrics if the Prometheus job naming differs. Some queries use `OR vector(0)`, hiding absent series as zero. The startup-time expressions subtract timestamps and rely on kube-state-metrics readiness data being present and semantically compatible.

## Test Signals
Useful validation is `jq` parse success, Grafana import success, and Prometheus query preview for every panel. Operational test signals include non-empty pod startup panels during scalability workloads, Longhorn resource lines for active system pods, and etcd panels showing leader count and proposal/RPC activity for the selected cluster.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scalability/dev/control_plane_grafana_dashboard.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scalability/dev/data-plane-grafana_dashboard.json -->
# sources/control-plane/longhorn/scalability/dev/data-plane-grafana_dashboard.json

## Purpose
Grafana dashboard JSON for "Reference Setup, Scalability, Performance, and Sizing" (`uid` `2fqV-mhSz`). It visualizes Longhorn data-plane benchmark output from `kbench_metric_exporter_*` Prometheus metrics across access mode, test mode, rate-limit mode, IO pattern, and IO type. It refreshes every five seconds in UTC.

## Important APIs, Types, and Queries
The dashboard uses Grafana schema v37, built-in annotations, and custom template variables: `volume_access_mode` (`rwo`, `rwx`), `test_mode` (`read-only`, `write-only`, `read-write`), and `rate_limit_type` (`no-rate-limit`, `rate-limit`). The read panels are stored under a collapsed `Read Performance` row; write panels are expanded under `Write Performance`.

Metrics are organized around `kbench_metric_exporter_iops`, `kbench_metric_exporter_bandwidth`, and `kbench_metric_exporter_latency`. Each metric is filtered by the three variables plus `io_pattern` (`random` or `sequential`) and `io_type` (`read` or `write`). Panels show raw series, `sum by(volume_name)`, `sum by(pod)`, `avg(...)`, and `count(...)` variants for IOPS, bandwidth, and latency.

## Control Flow
Grafana resolves the three custom variables, evaluates hidden panels inside the collapsed read row and visible write panels, then renders time series and text separators. There is no imperative logic; dashboard behavior is driven by templated PromQL labels. The collapsed row preserves read panels while keeping the default view focused on write performance.

## State and Persistence
All dashboard state is in JSON: variable defaults (`rwx`, `write-only`, `rate-limit`), panel IDs/layout, row collapsed state, datasource references, and visualization options. Benchmark data is persisted in Prometheus; the dashboard writes no state.

## Dependencies and Integration Points
Requires Grafana, Prometheus datasource `uid: prometheus`, and a kbench metric exporter that emits the exact label set used by the queries: `volume_access_mode`, `test_mode`, `rate_limit_type`, `io_pattern`, `io_type`, `volume_name`, and `pod`. It integrates with Longhorn scalability/performance test workflows that label metrics consistently.

## Risks
Every panel depends on exact label names and values; missing or renamed labels produce empty graphs. Defaults bias the initial view to RWX, write-only, rate-limited tests. The dashboard does not template namespace, cluster, or datasource. Some count panels are labeled "Pods" while counting metric series/containers, so interpretation depends on exporter cardinality. Collapsed read panels can hide failures in read-test telemetry unless explicitly expanded.

## Test Signals
Validation signals are JSON parse/import success, all template variables selectable, and non-empty PromQL results for both read and write panels after a kbench run. Cross-check average, sum-by-PVC, sum-by-pod, and count panels against raw exporter series to catch label-cardinality drift.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scalability/dev/data-plane-grafana_dashboard.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/generate-backupstore-credentials.sh -->
# sources/control-plane/longhorn/scripts/generate-backupstore-credentials.sh

## Purpose
Bash generator for Longhorn backupstore credential Kustomize overlays under `deploy/backupstores/overlays/generated-credentials`. It supports `azurite`, `cifs`, `minio`, `nfs`, and `all`, producing secret patch YAMLs and per-backend `kustomization.yaml` files.

## Important APIs, Functions, and Data
Top-level environment inputs include Azure blob variables, CIFS credentials, AWS/S3-compatible credentials, optional TLS cert/key values, and `AWS_ENDPOINTS`. `SUPPORTED_BACKENDS` drives `all` generation.

Functions: `check_env_or_fail` validates required environment variables; `generate_all_overlay` writes an aggregate Kustomization referencing all backends; `generate_backend` dispatches to backend-specific generators; `generate_azurite_backend`, `generate_cifs_backend`, `generate_minio_backend`, and `generate_nfs_backend` write overlays; `generate_patch_with_ns` writes Kubernetes `Secret` patches; `b64`, `fail_if_base64_encoded`, and `is_base64` handle base64 behavior.

## Control Flow
The entry point parses `--no-encode` and one backend argument. It reports base64 mode, then either iterates all supported backends and writes the aggregate overlay or writes a single backend. Each credential backend removes and recreates its target directory before generating files. MinIO validates `AWS_ENDPOINTS` differently depending on base64 mode and requires cert/key when the decoded or raw endpoint is HTTPS.

## State and Persistence
The script destructively replaces backend output directories with generated Kubernetes YAML. Secrets are persisted in generated files, base64-encoded by default or written as supplied with `--no-encode`. No cluster state is changed directly.

## Dependencies and Integration Points
Depends on Bash, GNU/coreutils-like `base64`, and the Longhorn repo layout. Outputs are Kustomize overlays that reference `deploy/backupstores/base/<backend>` and secret names such as `azblob-secret`, `cifs-secret`, and `minio-secret` in `longhorn-system` and sometimes `default` namespaces.

## Risks
Generated files may contain live credentials. `is_base64` treats many short strings as valid base64, so double-encode protection can reject legitimate plaintext. `rm -rf "${TARGET_DIR:?}"` is guarded but still destructive within the generated credentials tree. In `--no-encode` mode the script expects already-base64 values but only decodes `AWS_ENDPOINTS` for HTTPS detection, not every secret value.

## Test Signals
Run with dummy credentials for each backend and assert expected files exist, YAML parses, and Kustomize can build each overlay. Test `--no-encode` with known base64 values and HTTPS/non-HTTPS endpoints. Confirm no generated credentials are accidentally committed.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/generate-backupstore-credentials.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/generate-longhorn-yaml.sh -->
# sources/control-plane/longhorn/scripts/generate-longhorn-yaml.sh

## Purpose
Generates static Longhorn install manifests from the Helm chart into `deploy/longhorn.yaml` and `deploy/longhorn-okd.yaml`.

## Important APIs and Variables
Variables derive `PRJ_DIR`, `CHART_DIR`, the two deploy output paths, temp output path, and `NAMESPACE` defaulting to `longhorn-system`. It requires `helm` version 3 or 4.

## Control Flow
With `errexit` and `xtrace`, the script checks Helm availability/version. For each deploy YAML, it writes an explicit Namespace object because `helm template` does not honor `--create-namespace`. For the OKD manifest it sets `OKD_ENABLED_FLAG="--set openshift.enabled=true"`, then runs `helm template longhorn "$CHART_DIR" --namespace "$NAMESPACE" ... --no-hooks`. It filters Helm ownership/chart metadata lines and atomically replaces the output from a temp file.

## State and Persistence
Persists generated manifests in the repo's `deploy` directory, overwriting existing files. It does not touch cluster state. `OKD_ENABLED_FLAG` is not reset inside the loop, but because the OKD file is last in the current array order this does not affect the normal two-output run.

## Dependencies and Integration Points
Depends on Helm v3/v4, chart templates under `chart`, and standard shell tools. Integrates with release/update scripts and static manifest consumers.

## Risks
The metadata filtering is grep-based and may remove unintended lines containing `helm.sh` or `app.kubernetes.io/managed-by: Helm`. If output order changes, `OKD_ENABLED_FLAG` could leak into later manifests. The error message references `$DEPLOY_YAML` before loop assignment under failure conditions.

## Test Signals
Run the script and compare generated manifest diffs, validate YAML parse, and perform a server-side or dry-run Kubernetes validation for both standard and OKD manifests. Confirm namespace override behavior with `NAMESPACE=...`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/generate-longhorn-yaml.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/helm-docs.sh -->
# sources/control-plane/longhorn/scripts/helm-docs.sh

## Purpose
Runs the `jnorwood/helm-docs:v1.9.1` Docker image against the Longhorn `chart` directory to regenerate Helm chart documentation.

## Important APIs and Variables
Derives `PRJ_DIR` and `CHART_DIR`, prints the chart path, then invokes `sudo docker run -v "$CHART_DIR:/helm-docs" -u $(id -u) jnorwood/helm-docs:v1.9.1`.

## Control Flow
`errexit` and `xtrace` stop on failures and echo commands. There is no argument parsing. Docker runs as the current UID inside the container to reduce root-owned output.

## State and Persistence
Mutates files under `chart`, typically README-style generated docs, through the bind mount. Docker image layers/cache live outside the repository.

## Dependencies and Integration Points
Requires sudo, Docker, network access or cached image, and the Helm chart tree. Integrates with chart release maintenance and documentation checks.

## Risks
Pinning to an old helm-docs image can diverge from chart features. `sudo docker` may fail in noninteractive CI or create files with unexpected group/permissions. The script does not verify Docker is installed before running.

## Test Signals
Run and inspect `git diff chart`. A clean regeneration should produce expected README changes only. CI can validate by rerunning and requiring no diff.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/helm-docs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/lhexec -->
# sources/control-plane/longhorn/scripts/lhexec

## Purpose
Convenience wrapper to execute Longhorn engine commands for a named volume by locating the running engine instance manager and invoking the engine binary through `kubectl exec`.

## Important APIs and Functions
Uses namespace `longhorn-system`. `print_usage` documents volume and command arguments. `check_volume_exist` verifies `lhv` custom resource existence. `check_engine_state` queries `lhe` resources for the volume's `.status.currentState`. `exec_command` queries `.status.instanceManagerName` and `.status.port`, discovers the Longhorn binary path from process command lines, then runs it with `--url localhost:<port>`.

## Control Flow
The script handles help/empty arguments, defaults missing command args to `help`, validates volume and engine state, and delegates to `exec_command`. JSONPath filters select Longhorn engine CRs by `spec.volumeName`.

## State and Persistence
The script itself persists nothing. Invoked engine subcommands may read or mutate volume engine state, snapshots, replicas, or metadata depending on arguments.

## Dependencies and Integration Points
Requires `kubectl` access to the Longhorn namespace and CRDs `lhv`/`lhe`. Depends on instance-manager pods supporting `bash`, `ps`, `grep`, `awk`, and the Longhorn engine process command shape.

## Risks
Command arguments are interpolated into a remote shell string, so quoting and injection risks exist if untrusted values are passed. `kubectl exec -it` can misbehave in non-TTY automation. If multiple engines match, JSONPath output may concatenate values. Binary discovery by process grep is fragile.

## Test Signals
Use `lhexec <volume> help` on a known running volume. Negative tests should cover missing volume, stopped engine, and command args with spaces. A safer future test would assert generated `kubectl` calls in a mocked environment.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/lhexec -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/load-images.sh -->
# sources/control-plane/longhorn/scripts/load-images.sh

## Purpose
Loads a Longhorn image archive if provided, tags listed images into an optional private registry namespace, and pushes them.

## Important APIs and Variables
`list` defaults to `longhorn-images.txt`; `CONTAINER_CLI` defaults to `docker` and can be set to `podman`. Flags are `--registry`, `--image-list`, `--images`, and `--help`.

## Control Flow
The script parses flags, appends a slash to non-empty registry, enables `errexit` and `xtrace`, loads an archive when `--images` is set, then iterates every line of the image list. It normalizes images of forms `a/b/c`, `a/b`, or bare name into `${registry}longhornio/<final-name>`, then tags and pushes.

## State and Persistence
Mutates local container image storage by loading/tagging images and remote registry state by pushing tags. It persists no repo files.

## Dependencies and Integration Points
Depends on Docker or Podman, registry credentials, and an image-list file. Integrates with air-gapped/private registry workflows for Longhorn deployments.

## Risks
Unquoted variables allow breakage with spaces or glob characters in paths. The usage text contains a typo for `--image-list`. The path normalization assumes Longhorn images should be pushed under `longhornio/` regardless of source registry. No retry or digest verification is performed after push.

## Test Signals
Use a temporary local registry and short image list to assert load/tag/push behavior. Validate both Docker and Podman paths when supported, with and without `--images`.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/load-images.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/longhorn_rancher_chart_migration.sh -->
# sources/control-plane/longhorn/scripts/longhorn_rancher_chart_migration.sh

## Purpose
Migrates a Longhorn installation managed by Rancher's legacy catalog app model to Helm/App Marketplace ownership. It has two modes: `migrate` patches downstream resources with Helm labels/annotations, and `cleanup` marks/deletes the old Rancher project app after manual chart install.

## Important APIs and Variables
Requires `kubectl get-all` from `ketall`. Inputs are upstream Rancher kubeconfig, downstream cluster kubeconfig, `--type migrate|cleanup`, and optional `--dry-run`. Constants are `RELEASE_NAMESPACE=longhorn-system` and `RELEASE_NAME=longhorn-system`.

The script reads the downstream cluster ID from kubeconfig server URL, searches upstream `apps.project.cattle.io`, extracts catalog/template/version from `.spec.externalId`, and obtains old values from `.spec.valuesYaml` or `.spec.answers`.

## Control Flow
After parsing and validation, it locates the Rancher Project App. In cleanup mode it verifies downstream `longhorn-manager` DaemonSet is Helm-managed, patches the upstream app with skip-uninstall/migration annotations, then deletes it. In migrate mode it verifies Longhorn setting `concurrent-automatic-engine-upgrade-per-node-limit` is `0`, lists all resources labeled `io.cattle.field/appId=<release>`, annotates CRDs as release `longhorn-crd` with keep policy, and annotates/labels all other resources as Helm release `longhorn`.

## State and Persistence
In migrate mode it mutates Kubernetes labels and annotations on many downstream resources. In cleanup mode it mutates and deletes the upstream Rancher app object. `--dry-run=client` can prevent server writes for most kubectl operations.

## Dependencies and Integration Points
Integrates with Rancher `apps.project.cattle.io`, Longhorn settings CRs, Kubernetes resources returned by `kubectl get-all`, Helm ownership metadata, and the manual Rancher UI chart installation step.

## Risks
Broad resource patching can affect every object with the legacy app label. Kubeconfig parsing via grep/awk is brittle. Several variable expansions are unquoted, so paths or unexpected values can break execution. Cleanup deletes the Rancher app and relies on prior manual install success. It does not verify Helm release readiness after migration.

## Test Signals
Use `--dry-run` on a staging Rancher install and inspect planned resources. Pre/post checks should include Longhorn setting value, resource labels/annotations, Helm release ownership, and successful old app cleanup only after new chart health is confirmed.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/longhorn_rancher_chart_migration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/migrate-for-pre-070-volumes.sh -->
# sources/control-plane/longhorn/scripts/migrate-for-pre-070-volumes.sh

## Purpose
Wrapper for the Longhorn manager's `migrate-for-pre-070-volumes` command, used to migrate old pre-0.7.0 Longhorn volumes by volume name or `--all`.

## Important APIs and Functions
Namespace constant `NS=longhorn-system`; `print_usage`; `exec_command` finds a `longhorn-manager` pod via `kubectl get po -l app=longhorn-manager`, then runs `longhorn-manager migrate-for-pre-070-volumes` inside it.

## Control Flow
Help or empty argument prints usage. Otherwise the script warns if more than one argument is passed, then forwards all args to the manager command.

## State and Persistence
The wrapper persists nothing locally, but the manager command mutates Longhorn volume metadata/state for old volumes.

## Dependencies and Integration Points
Requires `kubectl`, Longhorn manager pods, and manager binary support for the migration command. Integrates with Longhorn CR/state migration workflows.

## Risks
It selects the second line of tabular `kubectl get po` output instead of using JSONPath, so output changes can break selection. It does not exit after detecting too many arguments. `kubectl exec -it` may fail in noninteractive contexts.

## Test Signals
Test `--help`, a dry/non-mutating manager invocation if available, and `--all` in a controlled cluster. Confirm old volumes become compatible and no unrelated volumes are modified.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/migrate-for-pre-070-volumes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/restore-backup-to-file.sh -->
# sources/control-plane/longhorn/scripts/restore-backup-to-file.sh

## Purpose
Runs the Longhorn engine container to restore a backup URL into a raw or qcow2 file under `/tmp/restore`.

## Important APIs and Variables
Flags include AWS credentials, CIFS credentials, `--backup-url`, `--output-file`, `--output-format`, `--version`, and optional `--backing-file`. It invokes `docker run ... longhornio/longhorn-engine:<version> longhorn backup restore-to-file`.

## Control Flow
The script parses flags and validates required backup URL, output file, output format, and Longhorn version. S3 URLs require AWS access key and secret. It builds Docker args: S3 gets AWS env vars; non-S3 gets Linux capabilities and apparmor relaxation; CIFS adds CIFS env vars. It mounts `/tmp/restore:/tmp/restore` and runs `restore-to-file` with output/backing-file options.

## State and Persistence
Writes the restored image file into the host `/tmp/restore` directory. Pulls or uses a Longhorn engine image by version. Does not change Kubernetes state.

## Dependencies and Integration Points
Requires Docker, Longhorn engine image availability, backupstore access, and host `/tmp/restore`. Integrates with Longhorn backup formats and S3/NFS/CIFS URL schemes.

## Risks
Credentials are exposed on the Docker command line/environment. The script validates S3 credentials but not CIFS credentials for CIFS URLs. Quoting around `backup_url` is awkward and can break URLs containing shell-special characters. Output file is forced under `/tmp/restore/${output_file}` even if the user supplies an absolute path. Privileged capabilities for non-S3 restores increase host risk.

## Test Signals
Restore a small known backup to raw and qcow2 and compare size/checksum or filesystem mountability. Test S3 and CIFS/NFS paths separately. Validate failure paths for missing credentials and invalid image versions.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/restore-backup-to-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/save-images.sh -->
# sources/control-plane/longhorn/scripts/save-images.sh

## Purpose
Pulls images listed in a Longhorn image list and optionally saves them into a gzip-compressed archive for offline transfer.

## Important APIs and Variables
`list` defaults to `longhorn-images.txt`; `CONTAINER_CLI` defaults to Docker. Flags are `--images`, `--image-list`, `--platform`, and `--help`.

## Control Flow
After flag parsing and help handling, `errexit` and `xtrace` are enabled. The script pulls each listed image, adding `--platform` when requested. If an archive path is provided, it runs container `save` for all listed images and pipes to `gzip -c`.

## State and Persistence
Mutates local container image cache by pulling images. Optionally writes a tar.gz archive at the requested path.

## Dependencies and Integration Points
Depends on Docker or Podman, network/registry access, image-list file, and gzip. Pairs with `load-images.sh` for air-gapped Longhorn installations.

## Risks
Unquoted variables can break paths with spaces. Saving all images in one command can be memory/disk intensive. There is no digest pinning or verification. Blank/comment lines in the list are not ignored.

## Test Signals
Use a small image list and confirm pulls succeed, archive is readable by `docker load`/`podman load`, and platform-specific pulls produce expected architecture images.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/save-images.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-chart-questions.sh -->
# sources/control-plane/longhorn/scripts/update-chart-questions.sh

## Purpose
Updates image tag defaults inside `chart/questions.yaml` from `deploy/longhorn-images.txt`.

## Important APIs and Functions
`check_yq` requires the mikefarah `yq` implementation. For each image line, the script parses `repo`, `tag`, and `component`, maps recognized Longhorn/CSI component names to chart question variable keys, then runs `yq eval -i` to update matching `.questions[].subquestions[]` defaults.

## Control Flow
After yq validation, the script loops through the image list. Recognized components update a specific chart variable; unrecognized components print a message and continue.

## State and Persistence
Mutates `chart/questions.yaml` in place. No cluster or runtime state is touched.

## Dependencies and Integration Points
Depends on mikefarah/yq, the chart question schema, and `deploy/longhorn-images.txt` component naming. Integrates with release automation that keeps image tags synchronized across manifests and Rancher chart questions.

## Risks
Component mapping is duplicated across other update scripts and can drift. Missing variables in questions.yaml do not appear to fail the script. Image lines without tags or non-`longhornio/` prefixes can parse incorrectly.

## Test Signals
Run after modifying `deploy/longhorn-images.txt`, inspect `chart/questions.yaml` diff, and validate with chart packaging/tests. Add coverage for every recognized component and an unknown component.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-chart-questions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-chart-readme.sh -->
# sources/control-plane/longhorn/scripts/update-chart-readme.sh

## Purpose
Updates image tag default values in `chart/README.md` table rows based on `deploy/longhorn-images.txt`.

## Important APIs and Data
Parses image `repo`, `tag`, and component like the questions update script. Maps component names to chart value keys. Builds an escaped default string and key, then uses `sed` to replace the default column in README table rows where the key and string type match.

## Control Flow
The script loops through image lines, maps each component, skips unknown components, writes a temporary README, and replaces the original file for each component.

## State and Persistence
Mutates `chart/README.md` repeatedly in place via `chart/README.md.tmp`.

## Dependencies and Integration Points
Depends on POSIX shell utilities and the README table format generated by helm-docs. Integrates with chart documentation and image tag release workflow.

## Risks
The sed expression is tightly coupled to markdown table spacing and the `string` type column. The `escaped_new_default` construction uses backticks in a way that is hard to read and may be fragile. Component mapping duplicates other scripts and includes components not updated by `update-chart-values.sh`.

## Test Signals
Run and inspect the README diff for each component. Re-run `helm-docs.sh` if README generation is authoritative, and ensure script output remains idempotent.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-chart-readme.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-chart-values.sh -->
# sources/control-plane/longhorn/scripts/update-chart-values.sh

## Purpose
Updates selected CSI/support-bundle image tag values inside `chart/values.yaml` from `deploy/longhorn-images.txt`.

## Important APIs and Functions
Validates mikefarah/yq. Maps components `csi-attacher`, `csi-provisioner`, `csi-resizer`, `csi-snapshotter`, `csi-node-driver-registrar`, `livenessprobe`, and `support-bundle-kit` to `.image...tag` paths, then runs `yq -i`.

## Control Flow
The loop parses every image line and updates recognized components. Unknown components are reported and skipped, including core Longhorn images such as manager/engine/ui.

## State and Persistence
Mutates `chart/values.yaml` in place.

## Dependencies and Integration Points
Depends on mikefarah/yq and the chart values schema. It integrates with release image bump workflows but only for a subset of images, likely because other Longhorn core image tags are managed differently.

## Risks
Partial component coverage can surprise maintainers expecting all image tags to be updated. Missing YAML paths may be created or silently changed depending on yq behavior. Component mapping duplication can drift.

## Test Signals
Run against a controlled image list and verify only intended values change. Chart rendering should be tested after updates.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-chart-values.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-manifests-dev-version.sh -->
# sources/control-plane/longhorn/scripts/update-manifests-dev-version.sh

## Purpose
Bumps Longhorn manifests from a current version to a `-dev` chart/app version and replaces matching image tags with `master-head`, then regenerates deploy manifests.

## Important APIs and Variables
Inputs are `CURRENT_VERSION` and `NEW_VERSION` from environment or positional args. `NEW_VERSION` is formed as `$2-dev`. It finds all `*.yaml` and `longhorn-images.txt` files under the repo.

## Control Flow
With `errexit` and `nounset`, the script builds a manifest file list. For `Chart.yaml`, it replaces `version: <current>` and `appVersion: v<current>` with the dev version. For all other files, it replaces occurrences of `: v<CURRENT_VERSION>` with `master-head`. It prints each updated file, then sources `scripts/generate-longhorn-yaml.sh`.

## State and Persistence
Mutates many YAML files and image-list files in the repo, then overwrites generated deploy manifests.

## Dependencies and Integration Points
Depends on GNU sed behavior, find, and Helm through the sourced generation script. Integrates with Longhorn development manifest preparation.

## Risks
The echo says `$NEW_VERSION-dev` even though `NEW_VERSION` already includes `-dev`. Sourcing another script means its shell options/variables affect the current process. The broad find/sed operation can change unintended YAML files. It assumes tags are formatted exactly with a leading `v` after a colon.

## Test Signals
Run on a disposable branch and inspect diffs. Validate chart version/appVersion, image-list tags, generated deploy YAML, and `helm template` output. A no-op or wrong-current-version run should be detected by diff review.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-manifests-dev-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-uninstall-manifest.py -->
# sources/control-plane/longhorn/scripts/update-uninstall-manifest.py

## Purpose
Python utility that synchronizes the Longhorn API resources in `uninstall/uninstall.yaml` ClusterRole from CRDs present in `deploy/longhorn.yaml`.

## Important APIs, Classes, and Functions
Class `YAMLResourceProcessor` stores `longhorn_manifest`, `uninstall_file`, and temp output path. `load_yaml_documents` streams non-empty YAML docs with PyYAML and wraps parse/IO failures. `extract_crd_resources` scans for `CustomResourceDefinition` documents and appends the first DNS segment of each CRD name, removing the `.longhorn.io` suffix by split. `update_cluster_role` replaces the `resources` list for rules whose `apiGroups` equals `["longhorn.io"]`. `process_files` writes all updated docs to `uninstall.tmp.yaml`. `main` runs with fixed repo-relative paths and atomically replaces the uninstall file with `os.replace`.

## Control Flow
The script reads generated deploy manifest CRDs, builds the resource list, streams the existing uninstall manifest, updates matching ClusterRole rules, dumps each document followed by `---`, replaces the original file, and reports success. Exceptions print an error and exit non-zero.

## State and Persistence
Mutates `uninstall/uninstall.yaml` in place via a temp file. It reads only local YAML manifests and does not touch a cluster.

## Dependencies and Integration Points
Requires Python, PyYAML, and execution from the Longhorn repo root because paths are relative. Integrates with manifest generation so the uninstall job's RBAC tracks current Longhorn CRDs.

## Risks
The CRD resource derivation uses `name.split(".")[0]`, which works for standard `<plural>.longhorn.io` names but would truncate any plural containing dots. `yaml.dump` may reorder formatting, comments, and style. It updates every ClusterRole document with a longhorn.io rule, not just a named role. No explicit test verifies that generated resources match Kubernetes plural resource names.

## Test Signals
Run after `generate-longhorn-yaml.sh`, diff `uninstall/uninstall.yaml`, and parse with Kubernetes tooling. Compare extracted CRD plural names to the ClusterRole longhorn.io resource list.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/scripts/update-uninstall-manifest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn/uninstall/uninstall.yaml -->
# sources/control-plane/longhorn/uninstall/uninstall.yaml

## Purpose
Kubernetes manifest for a Longhorn uninstall job. It creates a service account, broad ClusterRole, ClusterRoleBinding, and batch Job that runs `longhorn-manager uninstall --force` in namespace `longhorn-system`.

## Important APIs and Resources
Resources include `ServiceAccount longhorn-uninstall-service-account`, `ClusterRole longhorn-uninstall-role`, `ClusterRoleBinding longhorn-uninstall-bind`, and `Job longhorn-uninstall`. The ClusterRole grants `*` verbs over CRDs, core pods/PVs/PVCs/nodes/configmaps/secrets/services/endpoints, apps workloads, batch jobs/cronjobs, pod disruption budgets, storage resources, leases, and many Longhorn CRD resources. Webhook configurations get `get` and `delete`. PriorityClasses get `watch` and `list`.

## Control Flow
When applied, Kubernetes creates RBAC and starts the job. The job runs container image `longhornio/longhorn-manager:master-head` with command `longhorn-manager uninstall --force`, `LONGHORN_NAMESPACE=longhorn-system`, `activeDeadlineSeconds: 900`, `backoffLimit: 1`, and `restartPolicy: Never`.

## State and Persistence
Applying this manifest creates cluster-wide RBAC and a namespaced job. The job is intentionally destructive: it deletes Longhorn resources and related cluster resources according to manager uninstall logic. The manifest itself is static but should be updated by `scripts/update-uninstall-manifest.py` as CRDs change.

## Dependencies and Integration Points
Depends on Kubernetes batch/RBAC APIs, Longhorn manager image availability, and the Longhorn CRD/resource model. Integrates with uninstall documentation and release manifests.

## Risks
RBAC is intentionally broad and cluster-scoped. The image tag `master-head` is unsuitable for stable releases unless rewritten. Forced uninstall can remove data-plane resources; operators must understand data-loss implications. Longhorn CRD list can drift if not regenerated from manifests.

## Test Signals
YAML parse and Kubernetes dry-run validation are basic signals. In a disposable cluster, apply the manifest and verify the job completes, Longhorn resources are removed, and no unrelated resources are deleted. Confirm RBAC resource list matches generated CRDs.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn/uninstall/uninstall.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.cargo/config.toml -->
# sources/control-plane/mayastor/.cargo/config.toml

## Purpose
Workspace Cargo configuration for Mayastor builds on `x86_64-unknown-linux-gnu`, plus release profile optimization settings.

## Important APIs and Settings
Target rustflags set `target-cpu=nehalem`, link against `lzma`, and request `lld` with `-fuse-ld=lld`. Release profile enables fat LTO and sets `codegen-units = 1`.

## Control Flow
Cargo reads this file automatically for builds in the workspace. The target-specific rustflags affect compiler and linker invocation; release profile settings affect optimization and code generation.

## State and Persistence
No runtime state. It changes build artifacts under Cargo target directories by altering compilation flags.

## Dependencies and Integration Points
Requires toolchains/linkers that support `lld` and an available `liblzma`. The nehalem CPU baseline influences binary compatibility for x86_64 deployments. Integrates with Nix/dev/CI build environments.

## Risks
Machines without `lld` or `liblzma` fail to link. `target-cpu=nehalem` may exclude older CPUs but keeps a relatively conservative baseline. Fat LTO and single codegen unit improve optimization but increase release build time and memory use.

## Test Signals
Run `cargo build` and `cargo build --release` in the intended Nix/CI environment. Verify produced binaries run on supported CPUs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.cargo/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/auto_assign.yml -->
# sources/control-plane/mayastor/.github/auto_assign.yml

## Purpose
Configuration for a GitHub auto-assign action to add reviewers to pull requests.

## Important Settings
`addReviewers: true`, `addAssignees: false`, four reviewer usernames, `skipKeywords: [wip]`, and `numberOfReviewers: 2`.

## Control Flow
The external auto-assign action reads this file on PR events and randomly or deterministically chooses two reviewers unless the PR includes a skip keyword.

## State and Persistence
No repo runtime state. It mutates PR metadata by requesting reviewers.

## Dependencies and Integration Points
Depends on whichever GitHub Action/app is configured to consume `auto_assign.yml`. Integrates with code review workflow and bors-required approvals.

## Risks
Reviewer list can become stale. Only `wip` is skipped, so draft or other blocked PR labels may still request reviewers depending on action behavior. It does not assign issue owners.

## Test Signals
Open a test PR and verify two reviewers are requested; include `wip` and confirm reviewer assignment is skipped.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/auto_assign.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/bors.toml -->
# sources/control-plane/mayastor/.github/bors.toml

## Purpose
Bors merge queue policy for Mayastor.

## Important Settings
Required status is `bors-ci`; PR statuses are `commitlint` and `DCO`; timeout is 10000 seconds; two approvals are required; merged branches are deleted; block labels are `DO NOT MERGE` and `wip`; bot committer identity is configured.

## Control Flow
Bors reads this policy when handling commands such as `bors merge`, checks statuses/approvals/labels, creates staging/trying branches, waits for `bors-ci`, and merges on success.

## State and Persistence
Mutates GitHub PR/branch state via bors. This config persists policy only.

## Dependencies and Integration Points
Integrates with `.github/workflows/pr-ci.yml` producing `bors-ci`, `pr-commitlint.yml`, `staging-dco.yml`, and GitHub review approvals.

## Risks
If workflow names or required statuses drift, bors blocks all merges. Required approvals overlap with GitHub branch protection and can confuse maintainers if inconsistent. Long timeout reflects heavy CI but can delay feedback.

## Test Signals
Submit a test PR through bors and verify staging triggers `bors-ci`, commitlint, and DCO as expected. Confirm block labels prevent queueing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/bors.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/bdd.yml -->
# sources/control-plane/mayastor/.github/workflows/bdd.yml

## Purpose
Reusable GitHub Actions workflow for Mayastor BDD tests.

## Important Jobs and Steps
`bdd-tests` runs on `cncf-ubuntu-16-64-x86` with read contents and OIDC token permissions. It checks out submodules, installs Nix, injects GitHub token/trusted users into Nix config, pre-populates `nix-shell`, uses Rust cache, builds binaries with `io-engine-testing`, prepares kernel modules and hugepages, configures Docker journald logging, sets up Python venv, runs `./scripts/pytest-tests.sh`, publishes pytest report, collects failure artifacts with `ci-report.sh`, checks coredumps, and cleans Python tests.

## Control Flow
Triggered only by `workflow_call`, typically from PR/bors CI. Cleanup and coredump checks run with `if: always()`, while reports/artifacts run on failure or cancellation.

## State and Persistence
Creates build outputs, Python reports, Docker state, kernel module state, hugepage settings, and uploaded artifacts. It does not persist repo changes.

## Dependencies and Integration Points
Depends on custom CNCF runner capabilities, Nix shell, SPDK submodule Nix sources, Docker, kernel modules `nvme_tcp`, `nbd`, `nvme_rdma`, gdb, and test scripts. Integrates into `pr-ci.yml`.

## Risks
Runner-specific kernel/module requirements make portability low. The workflow mutates `/etc/nix/nix.conf` and Docker daemon config. Empty GitHub token input to Nix install may be intentional but fragile. Heavy BDD cleanup must remain reliable to avoid contaminating shared runners.

## Test Signals
Primary signal is `pytest-tests.sh` xunit report plus coredump absence. Failure artifact `ci-report-bdd` is the diagnostic package.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/bdd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/develop-to-release.yml -->
# sources/control-plane/mayastor/.github/workflows/develop-to-release.yml

## Purpose
Automates preparation of release branches by updating submodule branch metadata and creating/approving/queueing a PR.

## Important Jobs and Steps
On push to `release/**`, job `prepareReleaseBranch` checks out, runs `./scripts/set-submodule-branches.sh --branch "$branch"`, creates a signed-off PR with `peter-evans/create-pull-request@v5`, labels it, approves it using two tokens, and comments `bors merge`.

## Control Flow
The create-pull-request step may or may not produce a PR; approval and bors steps are conditional on a PR number output.

## State and Persistence
Mutates git branches/PRs in GitHub. No cluster/runtime state.

## Dependencies and Integration Points
Requires secrets `ORG_CI_GITHUB` and `ORG_CI_GITHUB_2`, GitHub CLI availability, bors, and submodule scripts.

## Risks
Automated self-approval and merge commands must be tightly permissioned. If submodule script produces unintended diffs, automation can queue them quickly. Uses older create-pull-request major than `mod-update.yml`.

## Test Signals
Push a release branch in a controlled repo and verify PR contents, approvals, labels, signoff, and bors queueing.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/develop-to-release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/fossa.yml -->
# sources/control-plane/mayastor/.github/workflows/fossa.yml

## Purpose
Runs FOSSA license/security scanning on `develop` and `release/**` pushes.

## Important Jobs and Steps
Single `fossa-scan` job on `ubuntu-latest`, checkout with recursive submodules, then `fossas/fossa-action@v1.4.0` using `FOSSA_API_KEY`.

## Control Flow
Push trigger starts the scan. The action handles dependency discovery and reporting to FOSSA.

## State and Persistence
No repo writes. External FOSSA project state is updated.

## Dependencies and Integration Points
Requires FOSSA secret and action availability. Recursive submodules are included in scan context.

## Risks
Scan coverage depends on FOSSA action support for Nix/Rust/submodules. Secret absence fails the workflow. Only push branches are scanned, not every PR.

## Test Signals
Successful FOSSA action run and updated FOSSA report. Branch protection may consume this if configured externally.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/fossa.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/image-pr.yml -->
# sources/control-plane/mayastor/.github/workflows/image-pr.yml

## Purpose
Reusable CI workflow that verifies Mayastor release images can be built without publishing.

## Important Jobs and Steps
`image-build-test` checks out recursive submodules, installs Nix, and runs `./scripts/release.sh --skip-publish --build-bins`.

## Control Flow
Triggered by `workflow_call`, consumed by `pr-ci.yml`. Failure blocks the aggregate `bors-ci`.

## State and Persistence
Builds local artifacts/images on the runner but does not push because `--skip-publish` is used.

## Dependencies and Integration Points
Depends on Nix, release script, Docker/build tooling implied by the script, and submodules.

## Risks
Only validates build path, not registry auth or publish path. Running on `ubuntu-latest` may differ from release runners.

## Test Signals
Successful `release.sh --skip-publish --build-bins` is the gate.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/image-pr.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/image.yml -->
# sources/control-plane/mayastor/.github/workflows/image.yml

## Purpose
Builds and pushes Mayastor release/dev images on branch pushes and as a reusable workflow for staging releases.

## Important Jobs and Steps
Triggers on pushes to `develop` and `release/**`, plus `workflow_call` with required `tag`, `registry`, and `namespace`. Job checks out full history/submodules, refetches tags for tag builds, installs Nix, logs into Docker Hub and GHCR, then runs `./scripts/release.sh` with workflow inputs for dispatch-style events or no args for push events.

## Control Flow
Event name decides whether to pass explicit tag/registry or rely on release script defaults. The workflow sets `TAG` from inputs.

## State and Persistence
Builds images and pushes them to registries. No repo files are changed.

## Dependencies and Integration Points
Requires Docker Hub credentials, GHCR token, Nix, recursive submodules, and release script. Called by `staging.yml`.

## Risks
The branch for explicit args checks `workflow_dispatch`, but this workflow declares `workflow_call`, not `workflow_dispatch`; called workflows may therefore skip explicit args and run default push behavior unless GitHub event semantics are accounted for. Registry credentials are broad. Tag refetch workaround is specific to checkout behavior.

## Test Signals
For push builds, verify expected image tags appear in registries. For reusable calls, verify inputs are actually honored; this deserves explicit CI audit because of the event-name condition.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/lint.yml -->
# sources/control-plane/mayastor/.github/workflows/lint.yml

## Purpose
Reusable workflow for Rust, JS, Python, and Nix linting.

## Important Jobs and Steps
`code-linter` checks out submodules, installs Nix, sets `NIX_PATH` from `spdk-rs/nix/sources.json`, warms nix-shell, uses Rust cache, runs `rust-style.sh` with `FMT_OPTS=--check`, `rust-linter.sh`, `js-check.sh`, Black check for `test/python`, and `nixpkgs-fmt --check .`.

## Control Flow
Triggered by `workflow_call`; usually called by aggregate PR CI.

## State and Persistence
Creates build/cache artifacts on runner. Does not mutate repo because all formatters are in check/diff mode.

## Dependencies and Integration Points
Depends on Nix shell providing Rust, JS, Python, and Nix tooling. Integrates with pre-commit hooks and bors CI.

## Risks
Tool versions are controlled indirectly by Nix/submodules; submodule drift can change lint behavior. Black only checks `test/python`, not arbitrary Python files outside that tree.

## Test Signals
Success of each lint command. Re-running locally inside nix-shell should reproduce CI.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/lint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/mod-update.yml -->
# sources/control-plane/mayastor/.github/workflows/mod-update.yml

## Purpose
Manual workflow to update selected or all git submodules and create an automated PR.

## Important Jobs and Steps
`workflow_dispatch` input `submodules` accepts comma-separated module names. Job checks out full history with recursive submodules, runs `./utils/dependencies/scripts/git/submodule-branches.sh -u -m "<input>"`, creates a signed-off PR with `peter-evans/create-pull-request@v7`, then approves it with the default GitHub token if a PR exists.

## Control Flow
Manual trigger only. PR branch is `update-submodules/<ref_name>` and is deleted after merge.

## State and Persistence
Mutates submodule pointers and creates PR branches. No runtime state.

## Dependencies and Integration Points
Requires `ORG_CI_GITHUB` for PR creation and submodule helper scripts. Ties into bors/approval workflow externally.

## Risks
Automated approval by CI bot may not satisfy all branch protections. Submodule updates can bring large behavioral changes; this workflow does not run validation itself beyond PR creation. Input parsing is delegated to the script.

## Test Signals
Dispatch with a small submodule set and verify PR diff, labels/metadata if any, signoff, and subsequent CI.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/mod-update.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/nightly-ci.yml -->
# sources/control-plane/mayastor/.github/workflows/nightly-ci.yml

## Purpose
Manual wrapper that runs the standard PR CI as a nightly-style check.

## Important Jobs and Steps
Workflow has `ci` job using `./.github/workflows/pr-ci.yml`, then `nightly-ci` job that depends on it and exits zero if successful.

## Control Flow
Triggered by `workflow_dispatch`. The second job is gated by `if: success()` and `needs: ci`.

## State and Persistence
No repo state. It creates whatever artifacts the underlying PR CI workflows create.

## Dependencies and Integration Points
Depends entirely on `pr-ci.yml` reusable workflow and its child lint/unit/bdd/image workflows.

## Risks
Despite the name, there is no scheduled trigger. It only runs when manually dispatched. The final job provides a simple green status but no extra coverage beyond PR CI.

## Test Signals
Successful completion of underlying `pr-ci.yml` and final `nightly-ci` step.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/nightly-ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/pr-ci.yml -->
# sources/control-plane/mayastor/.github/workflows/pr-ci.yml

## Purpose
Aggregate reusable and push-triggered CI workflow for bors staging/trying branches.

## Important Jobs
Jobs call reusable workflows: `lint-ci` -> `lint.yml`, `int-ci` -> `unit-int.yml`, `bdd-ci` -> `bdd.yml`, `image-ci` -> `image-pr.yml`. Final `bors-ci` requires all four and exits zero on success.

## Control Flow
Triggered by `workflow_call` or pushes to `staging` and `trying`. GitHub's dependency graph ensures the final status only appears after all child CI completes successfully.

## State and Persistence
Child workflows create build/test artifacts; this file itself persists no state.

## Dependencies and Integration Points
Directly integrates with `bors.toml`, where `bors-ci` is required. Also underpins `nightly-ci.yml`.

## Risks
If any child workflow name/path changes, bors CI breaks. The final job provides no additional validation beyond dependency success. It is not directly configured for pull_request events; bors or other workflows must call/push it.

## Test Signals
Presence of a successful `bors-ci` status after lint, integration, BDD, and image build test pass.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/pr-ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/pr-commitlint.yml -->
# sources/control-plane/mayastor/.github/workflows/pr-commitlint.yml

## Purpose
Validates commit messages on pull requests and staging branch pushes.

## Important Jobs and Steps
`commitlint` checks out full history, installs `@commitlint/config-conventional` and `@commitlint/cli`, then for PRs calculates base/head SHAs, force-enables the custom code-review rule by editing `commitlint.config.js`, runs `npx commitlint --from ... --to ... -V`, and fails on duplicate commit subjects. For staging branch it succeeds without linting PR commits.

## Control Flow
Triggers on PR opened/edited/reopened/synchronize and push to `staging`. Branch comparison is skipped for `refs/heads/staging`.

## State and Persistence
Mutates the checked-out `commitlint.config.js` in the runner only. Writes a temporary `subjects` file. Does not push changes.

## Dependencies and Integration Points
Depends on npm, commitlint config, full git history, and GitHub PR event fields. Provides required status listed in `bors.toml`.

## Risks
The shell test `if [ ! ${{ github.ref }} = "refs/heads/staging" ]; then` is unquoted and can be brittle. Editing config with sed assumes exact text. Duplicate subject detection can reject legitimate fixup/split commits.

## Test Signals
Open PRs with valid/invalid commit subjects, code-review wording, and duplicate subjects. Staging branch should not fail due to missing PR fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/pr-commitlint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/pr-submodule-branch.yml -->
# sources/control-plane/mayastor/.github/workflows/pr-submodule-branch.yml

## Purpose
Checks that submodule branch metadata matches the target branch and that submodule HEADs point to expected branches.

## Important Jobs and Steps
On PRs and pushes to `develop`, `release/**`, and `staging`, the job conditionally checks out with either default token or `ORG_CI_GITHUB`, recursive submodules, determines `check_branch` from PR base ref or current ref, runs `./scripts/set-submodule-branches.sh --branch "$check_branch"`, prints `.gitmodules`, checks no diff in `.gitmodules`, then runs `./scripts/check-submodule-branches.sh`.

## Control Flow
The dual checkout steps use an environment probe for secret presence. The first validation step fails if `.gitmodules` would need changes for the target branch.

## State and Persistence
May mutate `.gitmodules` in the runner while testing, but requires diff to be empty. No repo changes are pushed.

## Dependencies and Integration Points
Depends on submodule scripts and recursive checkout permissions. Integrates with release/develop branch management.

## Risks
Secret-based conditional checkout is unusual and should be checked carefully; unavailable secrets on forked PRs can alter behavior. `.gitmodules` diff check catches branch metadata but not all submodule pointer issues, hence second script.

## Test Signals
PR targeting develop/release with correct and incorrect submodule branch metadata. Verify fork PRs work without privileged token.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/pr-submodule-branch.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/release.yml -->
# sources/control-plane/mayastor/.github/workflows/release.yml

## Purpose
Release-created workflow that validates a release tag and mirrors images from dev registry to Docker Hub.

## Important Jobs and Steps
`preflight-checks` checks out full history/submodules, installs Nix, warms staging shell, logs into Docker Hub, then runs `validate.sh --tag <ref_name> --type release`. `release-images` repeats checkout/Nix/logins for Docker Hub and GHCR, then runs `mirror-images.sh --source ghcr.io/<owner>/mayastor/dev --target docker.io/<owner> --tag <ref_name>`.

## Control Flow
Triggered when a GitHub release is created. Image mirroring requires preflight success.

## State and Persistence
Does not write repo files. Mutates external registries by mirroring images to Docker Hub.

## Dependencies and Integration Points
Requires staging scripts under `utils/dependencies`, Nix, Docker Hub/GHCR credentials, and release tags matching validation policy.

## Risks
Release creation immediately triggers registry operations. Credentials and image source/target paths must match repository owner conventions. Validation is delegated to external scripts not visible in this file.

## Test Signals
Dry-run or staging release validation where supported, successful `validate.sh`, and expected image tags present in Docker Hub after mirroring.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/staging-dco.yml -->
# sources/control-plane/mayastor/.github/workflows/staging-dco.yml

## Purpose
Provides a `DCO` status on pushes to the `staging` branch.

## Important Jobs and Steps
Single `DCO` job on `ubuntu-latest` that echoes `DCO`.

## Control Flow
Triggered only by `push` to `staging`.

## State and Persistence
No state changes.

## Dependencies and Integration Points
Integrates with bors `pr_status = ["commitlint", "DCO"]`, likely satisfying the DCO status for bors-created staging branches.

## Risks
This does not validate signoffs; it only creates a passing status. Real DCO enforcement must exist elsewhere or be accepted as a policy tradeoff.

## Test Signals
Push to staging and confirm a passing `DCO` check appears.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/staging-dco.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/staging.yml -->
# sources/control-plane/mayastor/.github/workflows/staging.yml

## Purpose
Manual staging release workflow that validates a tag and builds/pushes dev images.

## Important Jobs and Steps
`workflow_dispatch` requires `tag`. `preflight-checks` checks out submodules, installs Nix, warms staging shell, logs into a registry using `REGISTRY_USERNAME/PASSWORD`, and runs `validate.sh --tag <TAG> --type staging`. `build-images` calls reusable `image.yml` with `registry: ghcr.io`, `namespace: mayastor/dev`, and inherited secrets.

## Control Flow
Image build starts only after preflight succeeds. The tag is also exposed as `TAG` env.

## State and Persistence
No repo writes. Pushes images through the called image workflow.

## Dependencies and Integration Points
Depends on staging scripts, Nix, registry secrets, and `image.yml`. Integrates with the release pipeline that later mirrors dev images.

## Risks
The login step name is incomplete (`Login to`). More importantly, `image.yml`'s event-name condition may not honor `workflow_call` inputs, so staging image tagging should be verified. Registry credential target is implicit because no `registry` input is passed to docker/login-action.

## Test Signals
Manual dispatch with a staging tag, successful validation, and expected images in `ghcr.io/<owner>/mayastor/dev:<tag>`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/staging.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/unit-int.yml -->
# sources/control-plane/mayastor/.github/workflows/unit-int.yml

## Purpose
Reusable integration/unit workflow for Rust and JS gRPC tests.

## Important Jobs and Steps
`int-tests` runs on `cncf-ubuntu-16-64-x86`, checks out submodules, installs/configures Nix, warms nix-shell, uses Rust cache with save only on release/develop, builds binaries with `io-engine-testing`, configures hugepages/modules/NVMe, sets Docker journald logging, runs Rust tests via `cargo-test.sh`, checks coredumps and cleans, then runs JS gRPC tests via `grpc-test.sh`, wraps xunit XML in `<testsuites>`, publishes report, collects artifacts on failure, checks coredumps again, and cleans again.

## Control Flow
Rust tests and cleanup/coredump checks run before JS tests. Several diagnostic steps use `if: always()`, while artifact upload occurs on failure/cancellation.

## State and Persistence
Creates build outputs, test processes, Docker state, kernel module/hugepage settings, xunit reports, and optional artifacts. Does not commit changes.

## Dependencies and Integration Points
Depends on custom runner with kernel support, Nix shell, SPDK/submodules, Docker, gdb, and scripts `nvme-conf.sh`, `cargo-test.sh`, `grpc-test.sh`, `ci-report.sh`, `check-coredumps.sh`, and `clean-cargo-tests.sh`. Called by `pr-ci.yml`.

## Risks
The workflow has two `Check Coredumps` and `Cleanup` step names, which can make logs less clear. Kernel/hardware assumptions make it runner-specific. If Rust tests fail, JS tests may be skipped because there is no `if: always()` on `Run JS Grpc Tests`.

## Test Signals
Successful Rust cargo tests, JS gRPC xunit report, no coredumps since `TEST_START_DATE`, and absence of failure artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.github/workflows/unit-int.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/.pre-commit-config.yaml -->
# sources/control-plane/mayastor/.pre-commit-config.yaml

## Purpose
Pre-commit hook configuration for formatting, linting, and commit-message checks.

## Important Hooks
External hooks include `nixpkgs-fmt` v1.2.0 and `trailing-whitespace` from pre-commit-hooks v4.0.1. Local system hooks run `./scripts/rust-style.sh`, `./scripts/rust-linter.sh`, `./scripts/js-check.sh`, commitlint through a shell pipeline stripping comments after the scissors line, and Black for Python files.

## Control Flow
Pre-commit selects hooks by file type/stage. Rust hooks ignore filenames and run workspace-level scripts. Commit lint runs at `commit-msg` stage using `$1` as the message file.

## State and Persistence
Hooks may modify files only where tools do so; rust linter/style scripts may be check-only or formatting depending on their internals. Commitlint blocks commits. No runtime state.

## Dependencies and Integration Points
Requires pre-commit, Nix formatter, local scripts, semistandard/JS tooling, commitlint, and Black available on PATH. Mirrors CI lint and commitlint policies.

## Risks
System-language hooks rely on developer machine setup; missing tools cause local failures. Rust hooks run globally and can be slower than file-scoped checks. Commitlint shell quoting with `$1` depends on pre-commit argument behavior.

## Test Signals
Run `pre-commit run --all-files` and make a test commit with invalid message to verify `commit-msg` enforcement.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/Cargo.toml -->
# sources/control-plane/mayastor/Cargo.toml

## Purpose
Root Cargo workspace manifest for the Mayastor/io-engine repository.

## Important APIs and Data
Defines `[profile.dev] panic = "abort"`, workspace resolver `1`, and members including `jsonrpc`, `libnvme-rs`, `io-engine`, `io-engine-bench`, tests, `sysfs`, `spdk-rs`, and utility dependency crates. `[workspace.dependencies]` centralizes versions for async/runtime, tracing, serde, errors, URL/UUID/time, gRPC/protobuf, device/system crates, Docker/k8s, and NATS.

## Control Flow
Cargo uses this manifest to resolve workspace membership and shared dependency versions. Member crates inherit workspace dependency versions where configured.

## State and Persistence
No runtime state. It controls dependency resolution and build graph persisted in Cargo lock/build outputs elsewhere.

## Dependencies and Integration Points
Integrates many Rust crates: `tokio`, `futures`, `tracing`, `serde`, `snafu`, `tonic/prost`, `udev`, `bindgen`, `nix`, `bollard`, `kube`, `k8s-openapi`, and internal path dependency `prost-extend`.

## Risks
Resolver version `1` can have feature-unification behavior different from newer resolver 2. Centralized dependency versions simplify consistency but make upgrades broad. `panic = "abort"` in dev changes debugging and unwind behavior.

## Test Signals
Run `cargo metadata`, `cargo check --workspace`, and CI integration tests. Dependency updates should be validated across all workspace members.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/Dockerfile -->
# sources/control-plane/mayastor/Dockerfile

## Purpose
Builds a Nix-based Mayastor development/CI environment image with dependencies pre-downloaded and prebuilt for nightly and stable channels.

## Important Instructions
Starts from `nixos/nix`, sets `NIX_EXPR_DIR=/tmp/nix-expr`, adds `nixpkgs-unstable`, installs `bash git nano sudo procps`, copies `shell.nix` and `nix`, then runs `nix-shell --argstr channel nightly` and `nix-shell --argstr channel stable`.

## Control Flow
Docker builds layers in order: Nix channel setup, base tools, copy Nix expressions, pre-populate debug and release dependency shells.

## State and Persistence
Persists Nix store contents and installed tools inside the image. Does not include full source tree, only Nix expressions.

## Dependencies and Integration Points
Depends on Nix channel availability and repo Nix expressions. Used by CI/CD pipeline and development to avoid repeatedly resolving/building dependencies.

## Risks
`nixpkgs-unstable` is mutable unless pinned elsewhere by shell.nix inputs, so rebuilds can drift. Prebuilding both channels can be expensive. The image includes sudo and editor utilities, increasing size.

## Test Signals
Build the Dockerfile and run `nix-shell --argstr channel nightly --run "cargo --version"` or equivalent dependency checks inside the image.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/commitlint.config.js -->
# sources/control-plane/mayastor/commitlint.config.js

## Purpose
Commitlint configuration enforcing conventional commit types, formatting, and a custom rule preventing review-fixup commits from being merged.

## Important APIs and Rules
Exports default JS object with `rules`, `defaultIgnores: false`, `ignores`, and `plugins`. Type enum allows build/chore/ci/docs/feat/fix/perf/refactor/revert/style/test/example/security. Subject/body/footer/header length and casing rules are configured. Custom plugin rule `code-review-rule` rejects subjects containing `code-review`, `review comment`, `address comment`, or `addressed comment`.

## Control Flow
Commitlint loads this module and invokes configured rules per commit message. Ignore functions bypass bors and merge-pull-request messages.

## State and Persistence
No runtime state. CI may modify the checked-out copy with sed to enforce the code-review rule in PR validation.

## Dependencies and Integration Points
Used by pre-commit and `.github/workflows/pr-commitlint.yml`. Depends on commitlint supporting ESM default export and plugin object format.

## Risks
`defaultIgnores: false` means many generated commit types are linted unless custom ignores catch them. Subject substring matching can reject legitimate descriptions. CI sed mutation assumes exact text layout.

## Test Signals
Run `npx commitlint` over sample valid/invalid messages, including bors merge messages and review-fixup subjects.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/commitlint.config.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/doc/etc/nexus.conf -->
# sources/control-plane/mayastor/doc/etc/nexus.conf

## Purpose
Example SPDK/Mayastor nexus configuration that composes a nexus device from two iSCSI children.

## Important Sections
`[Nexus]` defines `Dev e5dc0d39-ffa2-4917-b404-e3a0ed8c2409 512 64 iscsi0 iscsi1`, indicating a nexus UUID/device with block size/size parameters and two child bdev aliases. `[iSCSI_Initiator]` maps two iSCSI URLs to `iscsi0` and `iscsi1`.

## Control Flow
When consumed by the relevant SPDK/Mayastor config loader, iSCSI initiator bdevs are established first and the nexus device is assembled from them.

## State and Persistence
Static config only. Runtime use would create initiator sessions and a nexus device in process memory.

## Dependencies and Integration Points
Depends on reachable iSCSI targets at the hard-coded IPs/ports and Mayastor/SPDK support for these config sections.

## Risks
Hard-coded private IPs and IQNs make it example-specific. No authentication is configured. If used accidentally in production, it points to fixed test endpoints.

## Test Signals
Use only in a lab where the target config is active, then verify both iSCSI children connect and the nexus appears.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/doc/etc/nexus.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/doc/etc/target.conf -->
# sources/control-plane/mayastor/doc/etc/target.conf

## Purpose
Example SPDK iSCSI target configuration exposing two malloc-backed disks.

## Important Sections
`[Malloc]` creates two 64 MiB LUNs with 4096-byte block size. `[iSCSI]` sets node base `iqn.2019-05.io.openebs`. `PortalGroup1` listens on `0.0.0.0:3261`; `InitiatorGroup1` allows any initiator/netmask. `TargetNode0` and `TargetNode1` expose `disk0` and `disk1` with queue depth 128; the first explicitly sets `AuthMethod None`.

## Control Flow
SPDK target initialization creates malloc bdevs, configures portal/initiator groups, and exposes target nodes mapping LUN0 to each malloc disk.

## State and Persistence
Static config. Runtime state includes in-memory malloc disks and iSCSI sessions; data is not persistent across process restart.

## Dependencies and Integration Points
Designed to pair with `doc/etc/nexus.conf` iSCSI initiator URLs. Requires SPDK iSCSI target support and port 3261 availability.

## Risks
Allows any initiator and no authentication, so it is only safe for isolated test environments. Malloc disks are volatile. Binding `0.0.0.0` exposes the target on all interfaces.

## Test Signals
Start the target in an isolated environment and use an iSCSI initiator or Mayastor nexus config to connect to `disk0` and `disk1`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/doc/etc/target.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/.cargo/config.toml -->
# sources/control-plane/mayastor/io-engine-bench/.cargo/config.toml

## Purpose
Cargo target configuration for `io-engine-bench` tests/benchmarks requiring elevated privileges.

## Important Settings
For both `x86_64-unknown-linux-gnu` and `aarch64-unknown-linux-gnu`, Cargo uses `runner = ".cargo/runner.sh"`. Comments state the runner asks for sudo password as needed.

## Control Flow
When Cargo runs binaries/tests for those targets inside `io-engine-bench`, it invokes `.cargo/runner.sh` instead of executing the binary directly.

## State and Persistence
No persistent state in this file. The runner may elevate and mutate system state depending on benchmark behavior.

## Dependencies and Integration Points
Depends on `.cargo/runner.sh`, sudo/elevated privileges, and Linux targets. Integrates with Mayastor benchmarks that need privileged device operations.

## Risks
Cargo test/run behavior changes only in this subcrate, which can surprise developers. Privileged runners are unsuitable for untrusted code. Missing runner script breaks cargo execution.

## Test Signals
Run `cargo test` or benchmark commands in `io-engine-bench` on both supported architectures where possible and verify the runner prompts/elevates correctly.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-bench/.cargo/config.toml -->
