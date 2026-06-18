# subset-b-000337 research

Grouped research report for subset-b-000337. Each section preserves the source path and is delimited for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-shellcheck.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-shellcheck.sh

Purpose: repository lint gate for shell scripts. It discovers tracked `*.sh` files under the selected root, filters ignored paths with `git check-ignore`, excludes `_`, `.git`, and vendor trees, and runs shellcheck 0.6.0 either from the host or from the pinned `koalaman/shellcheck-alpine` image.
Important APIs/functions: sources `release-tools/util.sh` for `kube::util::trap_add`, defines `join_by`, `create_container`, and `remove_container`, and passes a comma-separated disabled lint list for SC1090 and SC2230.
Control flow/state: changes to the root directory, builds `all_shell_scripts`, checks host shellcheck version, starts a long-lived Docker container when needed, execs shellcheck for each file, accumulates non-empty diagnostics, and fails at the end if any diagnostics were collected. Persistent state is limited to the temporary Docker container named `k8s-shellcheck`, removed on EXIT.
Dependencies/integration: depends on git, shellcheck or Docker, the pinned image digest, and the repo's ignore rules. It is meant for release/Prow style verification.
Risks/test signals: fixed container name can collide with a concurrent run; the required shellcheck version is old; docker-only fallback fails in rootless/containerless CI. Success signal is the congratulatory message; failure prints all shellcheck diagnostics.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-spelling.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-spelling.sh

Purpose: spelling verification for tracked source files, excluding vendor content.
Important APIs/functions: installs `github.com/client9/misspell/cmd/misspell@v0.3.4` into a temporary `GOBIN` when no host `misspell` binary exists, then runs `git ls-files | grep -v vendor | xargs misspell`.
Control flow/state: creates a temp directory, registers an EXIT cleanup handler, writes misspell output to `errors.log`, prefixes emitted diagnostics with `error:`, and exits with status 1 when the log is non-empty. It does not persist repo state unless a host/tool install unexpectedly writes outside the temp directory.
Dependencies/integration: requires git, Go toolchain for on-demand install, network/module cache access when `misspell` is missing, and POSIX tools.
Risks/test signals: `grep -v vendor` is broad and may skip paths containing that token outside dependency trees; `xargs` may be sensitive to odd filenames; the tool version is old. Empty `errors.log` is the pass signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-subtree.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-subtree.sh

Purpose: guard that a directory managed by `git subtree` remains an upstream-only copy.
Important APIs/functions: accepts exactly one directory argument and uses `git log -n1 --remove-empty --format=%H --no-merges -- <dir>` to find non-merge commits touching that path.
Control flow/state: validates input, queries git history, prints the non-merge log and exits 1 if any local non-merge change exists, otherwise reports the directory as clean. It has no persistent state.
Dependencies/integration: depends on git history shape where subtree updates are merge commits and local edits are non-merge commits.
Risks/test signals: can be bypassed by editing subtree files inside a merge commit; shallow clones may hide history; path renames can affect detection. Success is no non-merge revision for the directory.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-vendor.sh -->
# sources/control-plane/beegfs-csi-driver/release-tools/verify-vendor.sh

Purpose: dependency/vendor consistency gate supporting older dep-based repos and Go modules.
Important APIs/functions: detects `Gopkg.toml` for `dep check`; detects `go.mod` for `go mod tidy` and, when `vendor/` exists, `go mod vendor`; compares `git status --porcelain` for `go.mod`, `go.sum`, and `vendor`.
Control flow/state: in Prow presubmits, uses `JOB_NAME`, `JOB_TYPE`, `PULL_BASE_SHA`, and git diffs to skip vendor checks when dependency-related files/imports are unchanged. Otherwise it runs module normalization and fails if files are modified.
Dependencies/integration: depends on dep or Go modules, git, and Prow env vars for skip behavior.
Risks/test signals: unquoted env tests can trip under strict shell in unusual envs; generated vendor changes are destructive to working tree until reverted by caller; skip heuristic only looks at imports and selected paths. Pass signal is up-to-date module/vendor status.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/driver/driver.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/driver/driver.go

Purpose: BeeGFS implementation of Kubernetes storage e2e `TestDriver`, `DynamicPVTestDriver`, and pre-provisioned driver interfaces.
Important APIs/types/functions: `baseBeegfsDriver`, `BeegfsDriver`, `BeegfsDynamicDriver`, `GetDriverInfo`, `PrepareTest`, `GetDynamicProvisionStorageClass`, `CreateVolume`, `GetPersistentVolumeSource`, `SetStorageClassParams`, `SetFSIndex`, `SetFSIndexForRDMA`, and `SetPerFSConfigs`.
Control flow/state: driver instances hold mutable `perFSConfigs`, `fsIndex`, and optional extra StorageClass parameters. Dynamic provisioning emits StorageClasses with `sysMgmtdHost` and `volDirBasePath`; pre-provisioned volumes create CSI PV sources whose handle is a BeeGFS URL built from selected FS config and static path.
Dependencies/integration: integrates with BeeGFS operator API config, `pkg/beegfs.NewBeegfsURL`, Kubernetes e2e storage framework, and CSI driver name `beegfs.csi.netapp.com`.
Risks/test signals: `fsIndex` is intentionally unchecked and panics/fails if tests set it out of range; mutable extra parameters must be unset after tests; capability flags control which upstream Kubernetes suites actually run. Compile-time interface assertions are the first signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/e2e_test.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/e2e_test.go

Purpose: top-level Ginkgo/Kubernetes e2e harness for BeeGFS CSI driver-specific and upstream storage suites.
Important APIs/functions: flag registration for dynamic/static BeeGFS paths, global `beegfsDriver` and `beegfsDynamicDriver`, `SynchronizedBeforeSuite`, `SynchronizedAfterSuite`, `Describe`, and `Test`.
Control flow/state: before-suite loads a clientset, checks for orphaned mounts, reads the active driver ConfigMap, unmarshals `PluginConfig`, and injects per-filesystem configs into both driver objects. after-suite archives service logs before checking orphaned mounts again. `Test` creates the report directory and runs Ginkgo.
Dependencies/integration: depends on Kubernetes e2e framework, Ginkgo/Gomega, testing manifests FS, BeeGFS e2e utilities, and `csi-beegfs-config.yaml` ConfigMap data.
Risks/test signals: global mutable driver state relies on Ginkgo synchronized ordering; failure before log archival can reduce diagnostics; orphan-mount checks require SSH/provider setup and at least two nodes. Suite success includes no orphaned mounts before or after.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/e2e_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/testsuites/beegfs.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/testsuites/beegfs.go

Purpose: BeeGFS-specific storage e2e suite layered on Kubernetes storage framework patterns.
Important APIs/functions: `beegfsTestSuite`, `InitBeegfsTestSuite`, `DefineTests`, setup/cleanup closures, and Ginkgo specs for multi-filesystem access, stripe pattern parsing, invalid pool handling, RDMA, host filesystem read-only protection, permissions, delete scoping, fallback timing, and 200-volume bulk performance.
Control flow/state: each spec initializes a `BeegfsDriver`, prepares a framework config, creates `VolumeResource` objects, and records them for cleanup. Some specs mutate driver StorageClass params; the slow serial fallback spec mutates live plugin config and restores it at the end.
Dependencies/integration: uses Kubernetes e2e pod/PV helpers, BeeGFS `beegfs-ctl`, FSExec host commands, driver ConfigMap/CR update helpers, and labels selecting controller/node pods.
Risks/test signals: concurrent bulk create can leak non-namespaced resources if goroutines fail before resource tracking; serial config mutation can disturb parallel tests if labels are ignored; timing assertions are environment-sensitive. Strong signals include explicit output checks for `beegfs-ctl`, permission mode/owner checks, tar diff validation, and creation/deletion timing bounds.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/testsuites/beegfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/driver_config.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/utils/driver_config.go

Purpose: helpers for locating and mutating the BeeGFS driver configuration used by e2e tests.
Important APIs/functions: `GetBeegfsDriverInUse`, `GetConfigMapInUse`, `GetPluginConfigInUse`, and `UpdatePluginConfigInUse`; package-level GVR for `beegfsdrivers.beegfs.csi.netapp.com/v1`.
Control flow/state: detects operator-enabled clusters through the dynamic client; otherwise finds the controller pod and the mounted `csi-beegfs-config*` ConfigMap. Updates either the BeegfsDriver CR or the ConfigMap, then deletes controller/node pods for ConfigMap-based deployments so they reload config.
Dependencies/integration: uses client-go dynamic and typed clients, operator API types, YAML strict marshal/unmarshal, and pod utility functions in this package.
Risks/test signals: expects exactly one BeegfsDriver in operator clusters; ConfigMap lookup depends on volume naming convention; updates are live cluster state and need log archival before restart. Success is pod restart/re-read without client errors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/driver_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/fs_exec.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/utils/fs_exec.go

Purpose: encapsulates creating a dynamic BeeGFS volume and pod so tests can execute commands on the host node where that volume is mounted.
Important APIs/types/functions: `FSExec`, `FSMountData`, `FindmntData`, `NewFSExec`, `GetVolumeSHA256Checksum`, `GetVolumeHostMountInfo`, `IssueCtlCommandWithBeegfsPathArgs`, `IssueCommandWithBeegfsPaths`, `IssueCommandWithResult`, and `Cleanup`.
Control flow/state: creates a volume resource, launches a pod consuming it, determines host mount paths by parsing `findmnt -J -t beegfs`, supports both SHA256 CSI staging paths and older PV-name paths, then routes commands through Kubernetes `HostExec`. Cleanup deletes pod, volume resource, and host exec artifacts.
Dependencies/integration: depends on Kubernetes storage e2e helpers, BeeGFS command-line utilities on the node PATH or plugin client path, JSON parsing of findmnt output, and kubelet CSI mount layout.
Risks/test signals: command format strings interpolate paths and should not receive untrusted input; failure during `CreateVolumeResource` can leak non-namespaced objects; mount detection assumes `source == beegfs_nodev` filters bind mounts. Tests using it signal via command stdout/stderr and cleanup aggregate errors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/fs_exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/utils.go -->
# sources/control-plane/beegfs-csi-driver/test/e2e/utils/utils.go

Purpose: shared e2e helpers for pod log archival, mount leak checks, pod discovery, permission validation, pool-id selection, and PVC creation without framework assertions.
Important APIs/functions: `VerifyDirectoryModeUidGidInPod`, `VerifyNoOrphanedMounts`, `ArchiveServiceLogs`, `AppendBytesToFile`, `GetRunningControllerPod`, `GetRunningNodePods`, `GetUnusedPoolId`, `ContainsString`, and `CreatePVCFromStorageClass`.
Control flow/state: many helpers fail tests directly through e2e framework assertions. Log archival appends pod logs to report files; orphan checks SSH to ready schedulable nodes and fails if BeeGFS mounts under kubelet remain; PVC creation returns errors so negative tests can inspect provisioning failure.
Dependencies/integration: Kubernetes e2e node/pod/PV/volume/SSH packages, client-go, labels `app=csi-beegfs-controller` and `app=csi-beegfs-node`, and report directory state.
Risks/test signals: `VerifyDirectoryModeUidGidInPod` assumes `ls -ld` field order; orphan checks require SSH provider and more than one ready node; appending logs can accumulate repeated entries. Test signals are explicit framework failures and report log files.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/e2e/utils/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-1.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-1.yaml

Purpose: Kubernetes test environment manifest for a BeeGFS 7-style single-node filesystem named `beegfs-fs-1`.
Important surface: StatefulSet with `beegfs-mgmtd`, `beegfs-meta`, and `beegfs-storage` containers using `${BEEGFS_VERSION}` images; initialization is driven by `beegfs_setup_*` env vars; connection auth is injected through `CONN_AUTH_FILE_DATA=${BEEGFS_SECRET}`.
Control flow/state: the containers initialize management, metadata, and two storage targets under `/mnt/*` paths, run with `hostNetwork: true`, and expose management/meta/storage TCP and UDP ports through a NodePort Service.
Dependencies/integration: consumed by test environment templating that substitutes BeeGFS version and secret; integrates with CSI config that points at the management host.
Risks/test signals: no persistent volume claims are declared, so data lifetime follows pod/container storage; hostNetwork can collide with ports on shared nodes; typo-prone setup target names affect filesystem initialization. Service readiness and CSI mount success are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-2.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-2.yaml

Purpose: second BeeGFS 7-style test filesystem, exercising connection auth delivered through a Kubernetes Secret volume instead of env-only data.
Important surface: `conn-auth-secret` Opaque Secret stores `connAuthFile`; StatefulSet `beegfs-fs-2` mounts it at `/etc/beegfs` and passes `connAuthFile=/etc/beegfs/connAuthFile` to mgmtd, meta, and storage containers.
Control flow/state: initializes one management target, one metadata target, and two storage targets, then exposes standard BeeGFS ports with a NodePort Service. Runtime state is container-local unless external storage is attached.
Dependencies/integration: templated `${BEEGFS_VERSION}` and `${BEEGFS_SECRET}` values; CSI config must match this auth file layout.
Risks/test signals: Secret key name differs from BeeGFS 8 manifests (`connAuthFile` versus `conn.auth`), so version-specific wiring matters; hostNetwork and NodePort increase environment coupling. Successful driver mounting across multiple FS configs validates it.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs-fs-2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-1.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-1.yaml

Purpose: BeeGFS 8 test filesystem with TLS enabled for the management daemon and connection auth.
Important surface: Secret `beegfs-env` provides `CONN_AUTH_FILE_DATA`, `TLS_CERT_FILE_DATA`, and `TLS_KEY_FILE_DATA`; mgmtd runs `beegfs-mgmtd --init` and starts with `--tls-disable=false`, while meta/storage keep classic setup commands and auth env injection.
Control flow/state: StatefulSet starts mgmtd/meta/storage in one host-networked pod and exposes standard BeeGFS service ports. TLS material is rendered into env vars from templated indented certificate/key data.
Dependencies/integration: depends on BeeGFS 8 container entrypoint behavior and template substitution for `${TLS_CERT_FILE_DATA_INDENTED}` and `${TLS_KEY_FILE_DATA_INDENTED}`.
Risks/test signals: only mgmtd is TLS-enabled here, so test config must match expected BeeGFS 8 TLS behavior; malformed indentation breaks Secret data. Successful CSI connection using TLS cert config is the key signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-2.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-2.yaml

Purpose: BeeGFS 8 test filesystem with TLS disabled and connection auth mounted from a Secret.
Important surface: Secret `conn-auth-secret` stores `conn.auth`; mgmtd starts with `--tls-disable=true`; meta and storage containers mount `/etc/beegfs` and use `connAuthFile=/etc/beegfs/conn.auth`.
Control flow/state: initializes a local mgmtd sqlite database plus metadata and two storage targets, using host networking and a NodePort Service for BeeGFS ports.
Dependencies/integration: templated `${BEEGFS_VERSION}` and `${BEEGFS_SECRET}`; paired with CSI test config to exercise BeeGFS 8 non-TLS auth layout.
Risks/test signals: Secret filename is version-specific; hostNetwork port collisions can prevent pod readiness; lack of durable storage means restart behavior may not mimic real clusters. Passing e2e mounts against this FS validates compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-connauth.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-connauth.yaml

Purpose: raw file-system-specific connection auth snippet used by Kustomize/test deployment for non-operator configuration.
Important surface: list entry with `sysMgmtdHost: localhost`, `connAuth: ${BEEGFS_SECRET}`, and intentionally omitted encoding field to verify backwards compatibility.
Control flow/state: no Kubernetes resource kind; it is transformed into a Secret/config artifact elsewhere.
Dependencies/integration: deployment documentation and Kustomize overlays expect this shape.
Risks/test signals: leaving encoding unspecified is deliberate; changing it would reduce backwards-compatibility coverage. Successful driver config parsing is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-connauth.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-cr.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-cr.yaml

Purpose: operator-mode test resources for deploying the BeeGFS CSI driver custom resource with connection auth.
Important surface: Secret `csi-beegfs-connauth` stores `csi-beegfs-connauth.yaml`; BeegfsDriver CR `csi-beegfs-cr` sets image override variables, controller node affinity, and plugin config stubs.
Control flow/state: the operator reconciles the CR into CSI controller/node services and reads the Secret for connection auth.
Dependencies/integration: requires the BeeGFS CSI operator CRD, `${CSI_IMAGE_NAME}`, `${CSI_IMAGE_TAG}`, `${BEEGFS_MGMTD}`, and `${BEEGFS_SECRET}` substitutions.
Risks/test signals: CR name is fixed by comment; malformed Secret YAML breaks operator reconciliation; test depends on master node label existing for preferred affinity. Operator-created driver pods are the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-cr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-tlscerts.yaml

Purpose: TLS certificate snippet for BeeGFS CSI test configuration.
Important surface: list item with `sysMgmtdHost: localhost` and `tlsCert` rendered from `${TLS_CERT_FILE_DATA_INDENTED}`.
Control flow/state: no Kubernetes resource by itself; consumed by deployment tooling that embeds TLS material into driver config.
Dependencies/integration: used with BeeGFS 8 TLS test manifests and config parsing.
Risks/test signals: certificate indentation is critical because YAML block scalar is used; successful TLS connection to mgmtd is the runtime signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-tlscerts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/nomad/test-nomad.sh -->
# sources/control-plane/beegfs-csi-driver/test/nomad/test-nomad.sh

Purpose: automated Nomad smoke test for deploying and removing BeeGFS CSI controller, node service, volume, and a consuming job.
Important APIs/functions: parses `<directory> [start|stop]`, uses `CONTAINER_DRIVER` defaulting to docker, optional `CSI_CONTAINER_IMAGE` substitution via sed, `nomad job run`, `nomad plugin status`, `nomad volume create/delete`, and `nomad job stop -purge`.
Control flow/state: start deploys controller and node jobs, polls controller and node health counts for up to 30 seconds each, creates a volume, and launches the test job with podman substitution when requested. stop tears down job, volume, controller, and node service. With no second arg it performs both.
Dependencies/integration: requires `NOMAD_ADDR`, `NOMAD_CACERT`, nomad CLI, docker/podman job files, `volume.hcl`, and local `job.nomad`.
Risks/test signals: many variable expansions are unquoted; health polling assumes numeric plugin status output; existing Nomad artifacts can make the script fail. Healthy plugin counts and successful volume/job operations are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/nomad/test-nomad.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.commitlintrc.yml -->
# sources/control-plane/ceph-csi/.commitlintrc.yml

Purpose: commit message policy consumed by commitlint.
Important surface: enforces max header length 72, no trailing period, non-empty subject, non-empty body, body line length 80, mandatory `Signed-off-by:` trailer, and a fixed type enum including build, cephfs, ci, csi, deploy, helm, rbd, nfs, nvmeof, and related categories.
Control flow/state: declarative only; commitlint reads it during local pre-commit and CI workflows.
Dependencies/integration: used by `.pre-commit-config.yaml`, `commitlint.yaml`, and `make commitlint`.
Risks/test signals: dependabot is exempt in workflow/Mergify because generated commits may not satisfy sign-off; type list must stay aligned with development guide. Passing commitlint is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.commitlintrc.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/dependabot.yml -->
# sources/control-plane/ceph-csi/.github/dependabot.yml

Purpose: Dependabot schedule and grouping policy for Go modules and GitHub Actions.
Important surface: weekly updates for root, `/actions/retest`, `/api`, `/e2e`, and GitHub Actions; dependency groups for Golang, Kubernetes, and GitHub dependencies; Kubernetes component modules are ignored in root due to `k8s.io/kubernetes` constraints.
Control flow/state: declarative GitHub service config. It labels generated PRs with `rebase` and skip labels for e2e/multi-arch where appropriate and prefixes commit messages with `rebase`.
Dependencies/integration: feeds CI/Mergify rules that understand `rebase`, `ci/skip/e2e`, and `ci/skip/multi-arch-build`.
Risks/test signals: ignored Kubernetes modules require manual coordinated updates; grouped updates can obscure a single failing dependency. Dependabot PR creation and CI outcomes are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/auto-assign.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/auto-assign.yaml

Purpose: issue self-assignment workflow. It triggers on created or edited issue comments and runs pinned `bdougie/take-action` with trigger `/assign`, a thank-you message, and `GITHUB_TOKEN`. It writes assignment state through GitHub APIs only. Risk is action trust/supply-chain despite pinning to a SHA; signal is issue assignee/comment updates.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/auto-assign.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/build-multi-stage.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/build-multi-stage.yaml

Purpose: PR image build validation. It waits one minute for labels, uses `actions/github-script` to detect `ci/skip/multi-arch-build`, then either runs `CONTAINER_CMD=docker ./scripts/build-multi-arch-image.sh` or `make containerized-build`. Concurrency cancels stale runs. Risk is label race and Docker-specific multi-arch behavior; success checks are multi-arch-build or single-arch-build.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/build-multi-stage.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/codespell.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/codespell.yaml

Purpose: PR spelling gate. It checks out the repository and runs `make containerized-test TARGET=codespell`. It depends on the Makefile test container and scripts/codespell config. Risk is container image freshness; success status is `codespell`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/codespell.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/commitlint.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/commitlint.yaml

Purpose: PR commit message gate for non-Dependabot PRs. It checks out the head SHA with full history and runs `make containerized-test TARGET=commitlint GIT_SINCE=origin/${GITHUB_BASE_REF}`. Risk is fetch/base-ref history issues; success status is `commitlint`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/commitlint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/dependency-review.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/dependency-review.yaml

Purpose: GitHub dependency-review gate on PRs. It checks out code and runs pinned `actions/dependency-review-action` with one allowed GHSA. It needs contents read permission. Risk is stale allowlist or advisory noise; signal is dependency review status.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/dependency-review.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/go-test.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/go-test.yaml

Purpose: Go validation workflow. Jobs check generated deploy code and clean git status, build `e2e.test` in container, run root Go tests, and run API module tests. It integrates with `make generate-deploy`, `check-all-committed`, `containerized-build`, and `containerized-test`. Risk is generated-code drift and container build cost; statuses gate Mergify.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/go-test.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/golangci-lint.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/golangci-lint.yaml

Purpose: Go lint gate. It checks out code and runs `make containerized-test TARGET=go-lint`, which generates lint config build tags then executes lint script. Risk is mismatch between build tags and CI image; signal is `golangci-lint`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/golangci-lint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/link-check.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/link-check.yaml

Purpose: markdown/link validation. It runs `make containerized-test TARGET=link-check`, which invokes lychee with repo config. Risk is network flake for external links; signal is `link-check`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/link-check.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/lint-extras.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/lint-extras.yaml

Purpose: non-Go lint aggregate. It runs `make containerized-test TARGET=lint-extras`, covering shell, markdown, YAML, Helm, and Python through scripts. Risk is Helm templates excluded from generic YAML parsing and checked separately; signal is `lint-extras`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/lint-extras.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mergify-copy-labels.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/mergify-copy-labels.yaml

Purpose: copies labels into Mergify merge-queue PRs on `pull_request_target` opened events. It uses a pinned Mergify action, adds `ok-to-test`, and uses `CEPH_CSI_BOT_TOKEN`. Risk is privileged target workflow token exposure if action behavior changes; signal is queue PR labels.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mergify-copy-labels.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mod-check.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/mod-check.yaml

Purpose: module/vendor consistency gate. It runs `make containerized-test TARGET=mod-check`, which tidies, vendors, verifies all modules, and fails on dirty git status. Risk is generated vendor churn; signal is `mod-check`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/mod-check.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/publish-artifacts.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/publish-artifacts.yaml

Purpose: publishes release/default-branch artifacts for official `ceph/ceph-csi`. On pushes to `devel` or `release-v*`, it logs into Quay, exports bot identity/token env vars, and runs `deploy.sh` with Docker. Risk is secret exposure and Docker-specific build assumptions; signal is successful artifact publishing.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/publish-artifacts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/pull-request-commentor.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/pull-request-commentor.yaml

Purpose: starts external Jenkins/e2e jobs when `ok-to-test` is applied. It comments `/test ...` commands for branch-specific Kubernetes versions, upgrade tests, then labels `ci/in-progress/e2e` and removes `ok-to-test`. It uses `pull_request_target` and bot token. Risk is matrix drift against supported branches; signal is comments and label transition.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/pull-request-commentor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/retest.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/retest.yaml

Purpose: scheduled retry automation for approved PRs. Every 30 minutes in official repo, it runs the local `actions/retest` action with required label `ci/retry/e2e`, max retry 5, and approval count 2. Risk is API rate limits and broad PR scan; signal is generated `/retest` comments.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/retest.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk-container-image.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/snyk-container-image.yaml

Purpose: scheduled/tag/release branch container vulnerability scan. It builds `make image-cephcsi` and runs Snyk Docker action against `quay.io/cephcsi/cephcsi:${{ github.base_ref }}` with Dockerfile path. Risk is base_ref being empty for tag/schedule contexts and secret typo `SYNK_TOKEN`; signal is uploaded scan result.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk-container-image.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/snyk.yaml

Purpose: scheduled/tag/release branch Go code vulnerability scan using Snyk. It checks out full history and runs pinned `snyk/actions/golang` with `SYNK_TOKEN`. Risk is token naming typo and Snyk action drift; signal is security scan status.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/snyk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/stale.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/stale.yaml

Purpose: daily stale issue/PR management in official repo. It marks issues after 30 days and closes after 7 more; PRs close after 14 stale days; labels such as keepalive/security/reliability/release requirement are exempt. Risk is accidentally closing long-running valid work without labels; signal is stale/wontfix labels and close comments.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/stale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/test-retest-action.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/test-retest-action.yaml

Purpose: PR validation for changes under `actions/retest`. It builds the Docker image from that directory to ensure the local action compiles with its vendored dependencies. Risk is build-only coverage without behavioral tests; signal is Docker build success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/test-retest-action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/tickgit.yaml -->
# sources/control-plane/ceph-csi/.github/workflows/tickgit.yaml

Purpose: TODO inventory on pushes to devel. It checks out and runs `make containerized-test TARGET=tickgit`, which scans the repo for tracked TODO markers. Risk is informational failures if tickgit config changes; signal is tickgit job output.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/workflows/tickgit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.mergify.yml -->
# sources/control-plane/ceph-csi/.mergify.yml

Purpose: central merge queue, CI gating, backport, review dismissal, and auto-label automation for Ceph CSI PRs.
Important surface: default queue uses rebase merge/update, requires two approved reviews including contributor and maintainer teams, DCO, standard GitHub Actions statuses, commitlint except Dependabot, and branch-specific external `ci/centos` e2e statuses unless `ci/skip/e2e` applies.
Control flow/state: Mergify evaluates queue conditions, adds `ok-to-test` for queued PRs needing external tests, dismisses stale approvals on updates, labels PRs based on title/body patterns, backports labeled devel PRs to release branches, and blocks `[skip ci]` descriptions by drafting/commenting.
Dependencies/integration: tied to workflow status names, external Jenkins context names, GitHub teams, bot accounts, and labels used by other workflows.
Risks/test signals: status-name drift or branch matrix changes can block merges; auto-label regexes can over/under-match; privileged bot actions affect reviews and labels. The merge queue status and labels are the operational signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.mergify.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.pre-commit-config.yaml -->
# sources/control-plane/ceph-csi/.pre-commit-config.yaml

Purpose: local pre-commit hook configuration mirroring part of CI hygiene.
Important surface: check sign-off, go-fmt, JSON/YAML syntax checks, newline fixer, trailing whitespace trim, and commitlint at commit-msg stage. Helm template YAML under CephFS/RBD chart templates is excluded from generic YAML parsing.
Control flow/state: declarative; pre-commit installs and runs pinned hook revisions. It mutates files for formatting/newline/whitespace hooks.
Dependencies/integration: complements Makefile lint targets and commitlint workflow.
Risks/test signals: old hook revisions may not match current tool behavior; generated template exclusions must stay scoped. Passing local pre-commit reduces CI failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.pre-commit-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/Makefile -->
# sources/control-plane/ceph-csi/Makefile

Purpose: main build, test, lint, module, container, image, deploy-generation, and e2e entrypoint for Ceph CSI.
Important targets: `test`, `go-test`, `go-test-api`, `mod-check`, `go-lint`, `lint-extras`, `commitlint`, `cephcsi`, `e2e.test`, `generate-deploy`, `run-e2e`, `containerized-build`, `containerized-test`, `image-cephcsi`, manifest push targets, and `clean`.
Control flow/state: discovers podman/docker, sets CPUSET support, loads `build.env` for versions/timeouts, builds with vendor mode and LDFLAGS carrying git commit/driver version, creates cached `.devel-container-id` and `.test-container-id`, and fails if module/deploy generation dirties git state.
Dependencies/integration: root of the GitHub Actions workflows, deploy generator, scripts directory, containerfiles, Go modules in root/e2e/api/actions/retest, and Quay image naming.
Risks/test signals: container cache IDs are local mutable state; `mod-check` rewrites vendor before checking status; UID/cgroup cpuset detection can differ by environment; Docker is forced for some multi-arch paths. CI statuses are direct Makefile target outcomes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/Dockerfile -->
# sources/control-plane/ceph-csi/actions/retest/Dockerfile

Purpose: Docker image for the local retest GitHub Action.
Important surface: multi-stage build from `golang:1.25` by default, copies action source into `/home/src`, builds `retest` from `main.go` with `-mod=vendor`, then installs it into `/usr/local/bin/retest` in the runtime image.
Control flow/state: no runtime state other than executing the binary as ENTRYPOINT.
Dependencies/integration: used by `actions/retest/action.yaml` and tested by `test-retest-action.yaml`; depends on vendored Go modules.
Risks/test signals: runtime image includes full Go base instead of a minimal image; base image tag is mutable unless overridden. Docker build success is the main signal.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/action.yaml -->
# sources/control-plane/ceph-csi/actions/retest/action.yaml

Purpose: GitHub Action metadata for the retest automation.
Important surface: inputs `max-retry`, `required-approve-count`, `exempt-label`, `required-label`, and `GITHUB_TOKEN`; runs as a Docker action using the local Dockerfile and exports `GITHUB_TOKEN` to the container.
Control flow/state: GitHub translates inputs into `INPUT_*` env vars read by `main.go`; persistent state is only PR comments/labels/statuses changed via GitHub API.
Dependencies/integration: invoked by `.github/workflows/retest.yaml`.
Risks/test signals: input names with hyphens require exact env lookup; token scope controls all behavior. Successful action run produces retest comments when conditions match.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/main.go -->
# sources/control-plane/ceph-csi/actions/retest/main.go

Purpose: scheduled GitHub API client that finds open PRs with a retry label, enough approvals, and failed statuses, then comments `/retest <context>` while respecting retry limits.
Important APIs/types/functions: `retestConfig`, `getConfig`, `validate`, `createClient`, `checkPRRequiredApproval`, `checkRetestLimitReached`, and `filterStatusList`. Uses `google/go-github` and OAuth2 token client.
Control flow/state: reads action env, lists open PRs, scans labels, skips exempt/missing labels, counts APPROVED reviews, lists statuses for the head SHA, keeps latest status per context, rebases PRs behind devel via Mergify comment, posts retest and diagnostic comments for failed contexts, requeues Mergify once, and stops after handling one PR with failures.
Dependencies/integration: GitHub repository env, bot token, Mergify commands, external CI status contexts, and PR comments as retry counter persistence.
Risks/test signals: label exemption only continues inner label loop rather than excluding the whole PR when exempt label is present; review counting does not de-duplicate reviewers or handle dismissals; PR listing lacks pagination. Logs and created comments are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/actions/retest/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/doc.go

Purpose: package documentation for deployment artifact helpers. It defines `deploy` as the namespace for functions returning standard/recommended manifests for container platforms. No functions or state live here; it integrates through subpackages such as Kubernetes and OCP. Test signal is documentation/build inclusion.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map.go

Purpose: renders the CephFS CSI `ceph-csi-config` ConfigMap from an embedded YAML template.
Important APIs/functions: `CSIConfigMapValues`, `CSIConfigMapDefaults`, `NewCSIConfigMap`, and `NewCSIConfigMapYAML`; uses Go `text/template`, `//go:embed`, and `ghodss/yaml` to unmarshal into `corev1.ConfigMap`.
Control flow/state: `NewCSIConfigMapYAML` parses the embedded template and executes it with provided name/cluster info; `NewCSIConfigMap` converts the YAML string to a typed object. It holds no persistent state.
Dependencies/integration: depends on shared `kubernetes.ClusterInfo` and the adjacent `csi-config-map.yaml` fixture.
Risks/test signals: `.ClusterInfo` is inserted using default Go formatting, so callers must verify produced JSON semantics; tests only assert non-empty YAML/name, not full config content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map.yaml

Purpose: embedded YAML template for the CephFS CSI ConfigMap.
Important surface: creates `apiVersion: v1`, `kind: ConfigMap`, metadata name from `.Name`, and `data.config.json` from `.ClusterInfo`.
Control flow/state: rendered by the package's `NewCSIConfigMapYAML` with no state of its own.
Dependencies/integration: must remain parseable by `ghodss/yaml` after template substitution and compatible with driver config loading.
Risks/test signals: incorrect indentation or non-JSON rendering of `.ClusterInfo` can produce a ConfigMap that exists but is semantically invalid. Unit tests cover render/non-empty only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map_test.go

Purpose: unit tests for CephFS ConfigMap render helpers.
Important APIs/functions: `TestNewCSIConfigMap` and `TestNewCSIConfigMapYAML` call defaults and assert no error, non-nil object, expected name, and non-empty YAML.
Control flow/state: no external state; test creates objects in memory.
Dependencies/integration: uses `stretchr/testify/require` and the embedded template.
Risks/test signals: coverage is shallow and does not parse or validate `config.json` semantics; failure signals template parsing/unmarshal/name regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csi-config-map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.go

Purpose: renders the Kubernetes `CSIDriver` object for the CephFS CSI driver.
Important APIs/functions: `CSIDriverValues`, `CSIDriverDefaults`, `NewCSIDriver`, and `NewCSIDriverYAML`; embeds `csidriver.yaml`, templates `.Name`, and unmarshals into `storagev1.CSIDriver`.
Control flow/state: parse/execute template on each call; no persistent state.
Dependencies/integration: used by automation that wants typed Kubernetes objects or YAML for installing the driver.
Risks/test signals: default driver name is part of the external CSI identity contract; changing attach/podInfo/fsGroup/seLinux settings in YAML changes cluster behavior. Unit tests catch basic rendering/unmarshal failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.yaml

Purpose: embedded CSIDriver manifest for CephFS. It sets name from `.Name`, `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy: File`, and `seLinuxMount: true`. Rendered by `NewCSIDriverYAML`; risk is changing driver identity or mount policy in a way Kubernetes storage behavior depends on. Unit tests verify parse/non-empty but not all spec values.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver_test.go

Purpose: unit tests for CephFS CSIDriver render helpers.
Important APIs/functions: `TestNewCSIDriver` and `TestNewCSIDriverYAML` verify defaults render without errors, object is non-nil, name matches, and YAML is non-empty.
Control flow/state: in-memory only.
Dependencies/integration: uses testify and embedded YAML.
Risks/test signals: tests do not assert CSIDriver spec fields, so behavioral spec regressions can pass unless unmarshal fails.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/csidriver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/doc.go

Purpose: package documentation for CephFS Kubernetes deployment artifact helpers. It exposes the package as a Go-consumable way to get recommended CephFS CSI manifests. No runtime logic or state is present; integration is through generated ConfigMap, CSIDriver, and for NFS RBAC helpers.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/cephfs/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/csi-config-map.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/csi-config-map.go

Purpose: shared data model for generated CSI config-map JSON.
Important APIs/types: `ClusterInfo`, `CephFS`, `RBD`, `NFS`, and `ReadAffinity` structs with JSON tags; embeds Kubernetes `corev1.SecretReference` for controller/node secret references.
Control flow/state: pure type definitions, no functions or persistence.
Dependencies/integration: consumed by cephfs/rbd/nfs `NewCSIConfigMap*` helpers and external automation building `config.json`.
Risks/test signals: zero values serialize into config JSON when callers pass uninitialized fields; struct tags form a compatibility contract with driver config parsing. Tests in subpackages verify only basic rendering, not semantic config validity.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/csi-config-map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/doc.go

Purpose: package documentation for Kubernetes deployment artifact helpers. It frames this package as a Go API for automation that deploys Ceph CSI. No runtime logic or state is present; integration is through exported types like `ClusterInfo` and provisioner RBAC interfaces.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map.go

Purpose: renders the NFS CSI `ceph-csi-config` ConfigMap from an embedded YAML template.
Important APIs/functions: `CSIConfigMapValues`, `CSIConfigMapDefaults`, `NewCSIConfigMap`, and `NewCSIConfigMapYAML`; uses Go `text/template`, `//go:embed`, and `ghodss/yaml` to unmarshal into `corev1.ConfigMap`.
Control flow/state: `NewCSIConfigMapYAML` parses the embedded template and executes it with provided name/cluster info; `NewCSIConfigMap` converts the YAML string to a typed object. It holds no persistent state.
Dependencies/integration: depends on shared `kubernetes.ClusterInfo` and the adjacent `csi-config-map.yaml` fixture.
Risks/test signals: `.ClusterInfo` is inserted using default Go formatting, so callers must verify produced JSON semantics; tests only assert non-empty YAML/name, not full config content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map.yaml

Purpose: embedded YAML template for the NFS CSI ConfigMap.
Important surface: creates `apiVersion: v1`, `kind: ConfigMap`, metadata name from `.Name`, and `data.config.json` from `.ClusterInfo`.
Control flow/state: rendered by the package's `NewCSIConfigMapYAML` with no state of its own.
Dependencies/integration: must remain parseable by `ghodss/yaml` after template substitution and compatible with driver config loading.
Risks/test signals: incorrect indentation or non-JSON rendering of `.ClusterInfo` can produce a ConfigMap that exists but is semantically invalid. Unit tests cover render/non-empty only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map_test.go

Purpose: unit tests for NFS ConfigMap render helpers.
Important APIs/functions: `TestNewCSIConfigMap` and `TestNewCSIConfigMapYAML` call defaults and assert no error, non-nil object, expected name, and non-empty YAML.
Control flow/state: no external state; test creates objects in memory.
Dependencies/integration: uses `stretchr/testify/require` and the embedded template.
Risks/test signals: coverage is shallow and does not parse or validate `config.json` semantics; failure signals template parsing/unmarshal/name regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-config-map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-cr.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-cr.yaml

Purpose: embedded NFS provisioner ClusterRole. It grants node, secret, event, PV/PVC, StorageClass, VolumeAttachment, CSI node, snapshot, and VolumeAttributesClass permissions needed by the external provisioner/snapshotter/attacher surfaces. Rendered into a typed `ClusterRole`. Risk is broad secret list/get access and drift with sidecar requirements; tests only assert unmarshal succeeds.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-cr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-crb.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-crb.yaml

Purpose: embedded NFS provisioner ClusterRoleBinding. It binds `.ServiceAccount` in `.Namespace` to cluster role `nfs-external-provisioner-runner`. Risk is name coupling to the ClusterRole template; tests assert typed object creation only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-crb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-r.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-r.yaml

Purpose: embedded namespaced Role for NFS provisioner config and leader-election resources. It grants ConfigMap get/list/create/delete and Lease get/watch/list/delete/update/create in `.Namespace`. Risk is legacy ConfigMap permissions may outlive need; tests verify parsing only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-r.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-rb.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-rb.yaml

Purpose: embedded RoleBinding for the NFS provisioner namespaced Role. It binds `.ServiceAccount` in `.Namespace` to `nfs-external-provisioner-cfg`. Risk is template/name coupling; tests verify parsing only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-rb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-sa.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-sa.yaml

Purpose: embedded ServiceAccount manifest for the NFS provisioner. It templates metadata name and namespace. It is used by YAML output while `NewCSIProvisionerRBAC` constructs an equivalent object directly. Risk is direct-construction/template drift; tests do not call `newServiceAccount`.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac-sa.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac.go

Purpose: renders and exposes typed NFS external provisioner RBAC artifacts.
Important APIs/functions: `CSIProvisionerRBACDefaults`, `NewCSIProvisionerRBAC`, `NewCSIProvisionerRBACYAML`, internal `newYAML`, `newServiceAccount`, `newClusterRole`, `newClusterRoleBinding`, `newRole`, `newRoleBinding`, and the `csiProvisionerRBAC` getter methods implementing `kubernetes.CSIProvisionerRBAC`.
Control flow/state: embeds five YAML templates, renders them with namespace/serviceAccount values, unmarshals into typed Kubernetes RBAC objects, and joins YAML docs for textual output. No persistent state.
Dependencies/integration: shared Kubernetes RBAC interface, `ghodss/yaml`, corev1/rbacv1 API types, and adjacent YAML templates.
Risks/test signals: `NewCSIProvisionerRBAC` manually constructs ServiceAccount instead of rendering `newServiceAccount`, so divergence from the SA YAML template could go unnoticed; tests cover object creation but not every RBAC rule.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac_test.go

Purpose: unit tests for NFS provisioner RBAC rendering. It validates `NewCSIProvisionerRBAC`, combined YAML output, and internal typed renderers for ClusterRole, ClusterRoleBinding, Role, and RoleBinding. State is in-memory only. The tests signal template parse/unmarshal regressions but do not inspect individual rules, subjects, or ServiceAccount YAML rendering.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csi-provisioner-rbac_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.go

Purpose: renders the Kubernetes `CSIDriver` object for the NFS CSI driver.
Important APIs/functions: `CSIDriverValues`, `CSIDriverDefaults`, `NewCSIDriver`, and `NewCSIDriverYAML`; embeds `csidriver.yaml`, templates `.Name`, and unmarshals into `storagev1.CSIDriver`.
Control flow/state: parse/execute template on each call; no persistent state.
Dependencies/integration: used by automation that wants typed Kubernetes objects or YAML for installing the driver.
Risks/test signals: default driver name is part of the external CSI identity contract; changing attach/podInfo/fsGroup/seLinux settings in YAML changes cluster behavior. Unit tests catch basic rendering/unmarshal failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.yaml

Purpose: embedded CSIDriver manifest for NFS. It sets name from `.Name`, `attachRequired: true`, `podInfoOnMount: true`, `fsGroupPolicy: File`, `seLinuxMount: true`, and `volumeLifecycleModes: Persistent`. Rendered by `NewCSIDriverYAML`; risk is lifecycle/attach policy drift. Unit tests verify basic render only.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver_test.go

Purpose: unit tests for NFS CSIDriver render helpers.
Important APIs/functions: `TestNewCSIDriver` and `TestNewCSIDriverYAML` verify defaults render without errors, object is non-nil, name matches, and YAML is non-empty.
Control flow/state: in-memory only.
Dependencies/integration: uses testify and embedded YAML.
Risks/test signals: tests do not assert CSIDriver spec fields, so behavioral spec regressions can pass unless unmarshal fails.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/csidriver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/doc.go

Purpose: package documentation for NFS Kubernetes deployment artifact helpers. It exposes the package as a Go-consumable way to get recommended NFS CSI manifests. No runtime logic or state is present; integration is through generated ConfigMap, CSIDriver, and for NFS RBAC helpers.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/nfs/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/provisioner.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/provisioner.go

Purpose: shared abstraction for provisioner RBAC artifact generators.
Important APIs/types: `CSIProvisionerRBAC` interface exposes getters for ServiceAccount, ClusterRole, ClusterRoleBinding, Role, and RoleBinding; `CSIProvisionerRBACValues` carries namespace and service account name.
Control flow/state: pure interface/value definitions.
Dependencies/integration: implemented by NFS provisioner RBAC generator and available for other backends.
Risks/test signals: interface assumes exactly one of each RBAC object, which may constrain future drivers needing multiple roles. Tests live in implementation packages.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/provisioner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.go

Purpose: renders the RBD CSI `ceph-csi-config` ConfigMap from an embedded YAML template.
Important APIs/functions: `CSIConfigMapValues`, `CSIConfigMapDefaults`, `NewCSIConfigMap`, and `NewCSIConfigMapYAML`; uses Go `text/template`, `//go:embed`, and `ghodss/yaml` to unmarshal into `corev1.ConfigMap`.
Control flow/state: `NewCSIConfigMapYAML` parses the embedded template and executes it with provided name/cluster info; `NewCSIConfigMap` converts the YAML string to a typed object. It holds no persistent state.
Dependencies/integration: depends on shared `kubernetes.ClusterInfo` and the adjacent `csi-config-map.yaml` fixture.
Risks/test signals: `.ClusterInfo` is inserted using default Go formatting, so callers must verify produced JSON semantics; tests only assert non-empty YAML/name, not full config content.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.yaml

Purpose: embedded YAML template for the RBD CSI ConfigMap.
Important surface: creates `apiVersion: v1`, `kind: ConfigMap`, metadata name from `.Name`, and `data.config.json` from `.ClusterInfo`.
Control flow/state: rendered by the package's `NewCSIConfigMapYAML` with no state of its own.
Dependencies/integration: must remain parseable by `ghodss/yaml` after template substitution and compatible with driver config loading.
Risks/test signals: incorrect indentation or non-JSON rendering of `.ClusterInfo` can produce a ConfigMap that exists but is semantically invalid. Unit tests cover render/non-empty only.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map_test.go

Purpose: unit tests for RBD ConfigMap render helpers.
Important APIs/functions: `TestNewCSIConfigMap` and `TestNewCSIConfigMapYAML` call defaults and assert no error, non-nil object, expected name, and non-empty YAML.
Control flow/state: no external state; test creates objects in memory.
Dependencies/integration: uses `stretchr/testify/require` and the embedded template.
Risks/test signals: coverage is shallow and does not parse or validate `config.json` semantics; failure signals template parsing/unmarshal/name regressions.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csi-config-map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.go

Purpose: renders the Kubernetes `CSIDriver` object for the RBD CSI driver.
Important APIs/functions: `CSIDriverValues`, `CSIDriverDefaults`, `NewCSIDriver`, and `NewCSIDriverYAML`; embeds `csidriver.yaml`, templates `.Name`, and unmarshals into `storagev1.CSIDriver`.
Control flow/state: parse/execute template on each call; no persistent state.
Dependencies/integration: used by automation that wants typed Kubernetes objects or YAML for installing the driver.
Risks/test signals: default driver name is part of the external CSI identity contract; changing attach/podInfo/fsGroup/seLinux settings in YAML changes cluster behavior. Unit tests catch basic rendering/unmarshal failures.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.yaml -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.yaml

Purpose: embedded CSIDriver manifest for RBD. It sets name from `.Name`, `attachRequired: true`, `podInfoOnMount: true`, `seLinuxMount: true`, and `fsGroupPolicy: File`. Rendered by `NewCSIDriverYAML`; risk is spec drift affecting attach and SELinux behavior. Unit tests only verify basic rendering.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver_test.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver_test.go

Purpose: unit tests for RBD CSIDriver render helpers.
Important APIs/functions: `TestNewCSIDriver` and `TestNewCSIDriverYAML` verify defaults render without errors, object is non-nil, name matches, and YAML is non-empty.
Control flow/state: in-memory only.
Dependencies/integration: uses testify and embedded YAML.
Risks/test signals: tests do not assert CSIDriver spec fields, so behavioral spec regressions can pass unless unmarshal fails.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/csidriver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/doc.go

Purpose: package documentation for RBD Kubernetes deployment artifact helpers. It exposes the package as a Go-consumable way to get recommended RBD CSI manifests. No runtime logic or state is present; integration is through generated ConfigMap, CSIDriver, and for NFS RBAC helpers.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/kubernetes/rbd/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/doc.go -->
# sources/control-plane/ceph-csi/api/deploy/ocp/doc.go

Purpose: package documentation for OpenShift deployment artifact helpers. It identifies `ocp` as the place to obtain recommended OpenShift artifacts for Ceph CSI. No runtime state or functions live here besides package declaration.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.go -->
# sources/control-plane/ceph-csi/api/deploy/ocp/scc.go

Purpose: renders OpenShift SecurityContextConstraints for Ceph CSI service accounts.
Important APIs/functions: `SecurityContextConstraintsValues`, `SecurityContextConstraintsDefaults`, `NewSecurityContextConstraints`, `NewSecurityContextConstraintsYAML`, and internal value wrapper adding `Prefix` from optional `Deployer`.
Control flow/state: embeds `scc.yaml`, computes prefix when deployer is non-empty, templates YAML, and unmarshals into OpenShift `security/v1.SecurityContextConstraints`. No persistent state.
Dependencies/integration: requires OpenShift API dependency and is used by deployers such as Rook that need prefixed service accounts.
Risks/test signals: SCC is highly privileged and user list must stay aligned with chart/deployment service account names; tests verify default and rook prefixes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.yaml -->
# sources/control-plane/ceph-csi/api/deploy/ocp/scc.yaml

Purpose: embedded OpenShift SCC manifest for Ceph CSI.
Important surface: allows privileged containers, hostNetwork, hostDir volumes, hostPorts, hostPID, hostIPC, SYS_ADMIN, RunAsAny/seLinux/fsGroup/supplementalGroups, selected volume types, and service account users for RBD, CephFS, NFS, and NVMe-oF plugin/provisioners.
Control flow/state: rendered with `.Namespace` and optional `.Prefix` by `NewSecurityContextConstraintsYAML`.
Dependencies/integration: OpenShift SCC admission and service account names from deployment artifacts.
Risks/test signals: broad privileges are required for CSI but high impact; missing a service account blocks pods under SCC admission. Unit tests assert prefix/name/user-prefix behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc_test.go -->
# sources/control-plane/ceph-csi/api/deploy/ocp/scc_test.go

Purpose: unit tests for OpenShift SCC rendering.
Important APIs/functions: `TestNewSecurityContextConstraints` subtests defaults and Rook deployer prefix; `TestNewSecurityContextConstraintsYAML` checks non-empty YAML.
Control flow/state: in-memory render/unmarshal only.
Dependencies/integration: OpenShift SCC API and testify.
Risks/test signals: tests check user prefixes but not all SCC privilege fields, so privilege drift can pass unless rendering breaks.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/deploy/ocp/scc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/api/doc.go -->
# sources/control-plane/ceph-csi/api/doc.go

Purpose: root package documentation for the public Ceph CSI API module. It declares package `api` as the consumable surface for deployment artifacts across container platforms. There is no runtime control flow or persistent state. Integration is through Go documentation/import boundaries; risk is only stale package description if exported APIs expand.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/api/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/artifacthub-repo.yml -->
# sources/control-plane/ceph-csi/charts/artifacthub-repo.yml

Purpose: Artifact Hub repository ownership claim. It declares a repository UUID and owner contacts for chart verification. No runtime control flow or cluster state. Dependency is Artifact Hub metadata processing. Risk is stale owner emails or repository ID mismatch; signal is Artifact Hub ownership validation.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/artifacthub-repo.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/Chart.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/Chart.yaml

Purpose: Helm chart metadata for `ceph-csi-cephfs`. It declares chart API v1, canary app/chart versions, description, keywords, home/source URLs, and icon. It integrates with Helm packaging and Artifact Hub. Risk is version metadata drift from image defaults; signal is `helm lint/package` metadata handling.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/ceph-conf.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/ceph-conf.yaml

Purpose: ConfigMap template for Ceph client config. It names the ConfigMap from `.Values.cephConfConfigMapName`, applies chart/common labels, renders `.Values.cephconf` through `tpl`, and provides an empty keyring. State is Kubernetes ConfigMap data consumed by plugin/provisioner pods. Risk is templated config injection or invalid ceph.conf; Helm lint/render and pod mounts are signals.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/ceph-conf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csidriver-crd.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csidriver-crd.yaml

Purpose: CSIDriver resource template for the CephFS chart. It sets driver name, labels, `attachRequired` from attacher enablement, `podInfoOnMount`, and values-driven `fsGroupPolicy` and `seLinuxMount`. It integrates with Kubernetes storage registration. Risk is mismatch between driverName and sidecar arguments; signal is successful CSIDriver creation and CSI registration.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csidriver-crd.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csiplugin-configmap.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csiplugin-configmap.yaml

Purpose: CSI plugin config ConfigMap template. It is skipped when `.Values.externallyManagedConfigmap` is true and otherwise writes `config.json` from `toJson .Values.csiConfig`. State is cluster config consumed by controller/node pods. Risk is invalid cluster JSON or missing externally managed ConfigMap; signal is pod config mount and driver startup.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/csiplugin-configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/encryptionkms-configmap.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/encryptionkms-configmap.yaml

Purpose: KMS configuration ConfigMap. It writes `config.json` from `.Values.encryptionKMSConfig` and labels as nodeplugin component. It integrates with encryption features in Ceph CSI. Risk is leaking or misplacing KMS metadata and invalid JSON; signal is encrypted volume workflow success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/encryptionkms-configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/extra-deploy.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/extra-deploy.yaml

Purpose: pass-through template for arbitrary additional manifests under `.Values.extraDeploy`. It ranges over user-provided objects and renders them with `tpl`. State and dependencies are fully user-defined. Risk is high because arbitrary templated YAML can create any resource; signal is Helm render/apply success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/extra-deploy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/groupsnapshotclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/groupsnapshotclass.yaml

Purpose: optional VolumeGroupSnapshotClass template. When enabled, it sets driver, clusterID, fsName, optional volumeGroupNamePrefix, group snapshotter secret name/namespace, annotations/labels, and deletionPolicy. It integrates with group snapshot CRDs and sidecar feature gates. Risk is CRD absence or secret namespace mismatch; signal is group snapshot creation.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/groupsnapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrole.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrole.yaml

Purpose: node plugin ClusterRole template. It grants node get, configmap get, and optionally broad secret get/list/watch for metadata KMS unless least-privileges mode is enabled. It integrates with nodeplugin service account. Risk is broad cluster secret read when not least-privileged; signal is node plugin access to config/KMS.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrole.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrolebinding.yaml

Purpose: binds the nodeplugin service account in the release namespace to the nodeplugin ClusterRole. It is conditional on `rbac.create`. Risk is name coupling to helper templates and missing RBAC when disabled; signal is node pods authorized for required API reads.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-clusterrolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-daemonset.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-daemonset.yaml

Purpose: DaemonSet for CephFS node service. It runs privileged `csi-cephfsplugin`, privileged node-driver-registrar, optional liveness/metrics container, hostNetwork/hostPID, kubelet hostPath mounts, `/dev`, `/sys`, `/run/mount`, `/lib/modules`, optional SELinux mount, config maps, memory key dir, and mountinfo hostPath. Args wire driver name, node ID, socket, mount options, read affinity, fencing, profiling, and slow-op logging. Risks are required host privileges, kubeletDir correctness, SELinux/socket access, and config map key mismatches. Signals are DaemonSet readiness, registrar socket registration, and mount workflows.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-daemonset.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-http-service.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-http-service.yaml

Purpose: optional Service exposing nodeplugin liveness Prometheus metrics. It supports annotations, clusterIP, externalIPs, loadBalancerIP/source ranges, servicePort, target containerPort, selector labels, and service type. Risk is exposing metrics more broadly than intended or selector mismatch. Signal is metrics endpoint reachability.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-http-service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-role.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-role.yaml

Purpose: least-privilege namespaced Role for metadata KMS secret access. It renders only when RBAC and leastPrivileges are enabled and metadata KMS secret namespace/name are set, granting get on a single secret resourceName. Risk is absent role when KMS values are incomplete; signal is encrypted volume key retrieval.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-rolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-rolebinding.yaml

Purpose: least-privilege RoleBinding for nodeplugin KMS secret access in the secret namespace. It binds the release namespace service account to the Role. Risk is cross-namespace binding mistakes; signal is nodeplugin authorization for the KMS secret.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-rolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-serviceaccount.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-serviceaccount.yaml

Purpose: optional ServiceAccount for nodeplugin pods. It uses helper-generated name, release namespace, chart labels, and common labels. Risk is mismatch when users disable creation but do not provide an existing account; signal is DaemonSet admission.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/nodeplugin-serviceaccount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrole.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrole.yaml

Purpose: provisioner ClusterRole template. It grants secrets/configmaps, PV/PVC, storageclasses, events, nodes, snapshot resources, optional group snapshot resources or replication resources, optional attacher permissions, and optional resizer PVC status permissions. It integrates with external-provisioner, snapshotter, attacher, and resizer sidecars. Risk is broad secret access and value-dependent RBAC drift from enabled sidecars. Signals are successful provisioning/snapshot/attach/resize workflows.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrole.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrolebinding.yaml

Purpose: binds the provisioner service account to the provisioner ClusterRole when RBAC is enabled. Risk is helper-name coupling and missing permissions when `rbac.create=false`. Signal is sidecar authorization.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-clusterrolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-deployment.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-deployment.yaml

Purpose: Deployment for CephFS controller/provisioner service. It runs the controller plugin plus external-provisioner, snapshotter, optional attacher, optional resizer, optional CSI controller helper, and optional liveness metrics. Values drive replica count, anti-affinity, hostNetwork, images, sidecar args, HTTP metrics ports, feature gates, config mounts, memory key dir, and scheduling. Risks include sidecar/RBAC mismatch, multi-replica leader election, socket sharing, configMapKey mismatch, and privileged host mounts. Signals are Deployment readiness and successful provisioning/snapshot/resize/attach paths.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-http-service.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-http-service.yaml

Purpose: optional Service exposing provisioner liveness Prometheus metrics. It mirrors service customization for clusterIP/externalIPs/loadBalancer settings and selects provisioner pods. Risk is metrics exposure or selector mismatch. Signal is metrics endpoint reachability.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-http-service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-role.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-role.yaml

Purpose: namespaced Role for provisioner ConfigMap and Lease resources used for config compatibility and leader election. Conditional on RBAC creation. Risk is insufficient lease permissions causing leader election failures. Signal is sidecar leader election and ConfigMap access.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-role.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-rolebinding.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-rolebinding.yaml

Purpose: binds the provisioner service account to the namespaced provisioner Role. Risk is service account naming mismatch. Signal is successful leader election/API access.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-rolebinding.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-serviceaccount.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-serviceaccount.yaml

Purpose: optional ServiceAccount for provisioner pods. It uses helper-generated name and release/chart labels. Risk is deployment failure when creation is disabled without an existing account. Signal is Deployment admission.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/provisioner-serviceaccount.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/secret.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/secret.yaml

Purpose: optional Secret for Ceph user credentials. It requires `.Values.secret.userID` and `.Values.secret.userKey` and writes them under `stringData`. It integrates with StorageClass snapshot/provisioner/node secret references. Risk is storing credentials in Helm release history and render failure when required values are absent. Signal is secret creation and volume operations.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/secret.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/snapshotclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/snapshotclass.yaml

Purpose: optional VolumeSnapshotClass template. It sets driver, clusterID, optional snapshotNamePrefix, snapshotter secret name/namespace, labels/annotations, and deletionPolicy. It integrates with snapshot CRDs and snapshotter sidecar. Risk is CRD absence or secret namespace mismatch. Signal is snapshot create/delete success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/snapshotclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/storageclass.yaml -->
# sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/storageclass.yaml

Purpose: optional CephFS StorageClass template. It sets provisioner driver, clusterID, fsName, optional pool/encryption/KMS/mount/mounter/volume prefix parameters, CSI secret references for provisioner, expand, controller-publish, and node-stage operations, reclaimPolicy, expansion flag, and mountOptions. Risk is incorrect secret namespaces, missing fsName/clusterID, or enabling encryption without KMS config. Signal is PVC provisioning and mount success.
Control flow/state: declarative or documentation-only unless noted; persistent behavior is through the generated GitHub/Kubernetes/Helm/GitHub Action state.
Dependencies/integration: tied to adjacent workflow, chart, or API consumers as described.
Risks/test signals: see purpose-specific risk and success signal above.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/charts/ceph-csi-cephfs/templates/storageclass.yaml -->
