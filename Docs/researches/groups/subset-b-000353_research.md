# Research Report: subset-b-000353

This grouped report covers iSCSI node device handling, CSI release tooling, CSI sanity-test fixtures, and NFS driver build, CI, and Helm deployment files assigned to `subset-b-000353`. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsi.go -->
# sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsi.go

Purpose: implements the iSCSI connector lifecycle for the CSI iSCSI driver: session discovery, target login, device path detection, `lsblk` device-tree parsing, multipath selection, SCSI device removal, JSON connector persistence, and persisted connector reload.

Important APIs and types: `Connector` is the central state object, carrying volume name, target IQN, portals, LUN, CHAP secrets, iface, retry settings, discovery flags, `Devices`, and `MountTargetDevice`. Public helpers include `Connect`, `(*Connector).Connect`, `Disconnect`, `(*Connector).Disconnect`, `(*Connector).DisconnectVolume`, `GetSCSIDevices`, `GetISCSIDevices`, `RemoveSCSIDevices`, `PersistConnector`, `(*Connector).Persist`, `GetConnectorFromFile`, `(*Connector).IsMultipathEnabled`, `(*Connector).IsMultipathConsistent`, and `Device` methods `Exists`, `GetPath`, `WWID`, `HCTL`, `WriteDeviceFile`, `Shutdown`, `Delete`, and `Rescan`. Testability is provided through package variables that wrap command, stat, glob, open, timeout, and sleep functions.

Control flow: `Connect` defaults retry and interval values, resolves the iface, extracts transport from `iscsiadm -m iface`, then loops over target portals through `connectTarget`. Each target rescans existing sessions, builds a by-path device path for TCP or wildcard PCI transport, checks for an existing session, optionally performs discovery and CHAP DB setup, logs in, and waits for the path to appear. The connector then filters `lsblk` output to iSCSI devices, selects either the single device or a common multipath child, and validates multipath consistency when applicable. `DisconnectVolume` flushes the multipath map before removing physical SCSI devices, or removes the single target device directly. `GetConnectorFromFile` reloads JSON then refreshes device state from live `lsblk` output.

State and persistence: persistent state is the JSON connector file written by `Persist` and rehydrated by `GetConnectorFromFile`. Host state is modified through `iscsiadm`, `/dev/disk/by-path`, `/dev/mapper`, `/dev/<device>`, `lsblk`, `scsi_id`, `blockdev`, and sysfs files under `/sys/class/scsi_device/<h:c:t:l>/device/{state,delete,rescan}`. In-memory connector fields are mutated during connect and reload.

Dependencies and integration: integrates with Linux open-iscsi, SCSI sysfs, multipath topology, Kubernetes `klog`, and JSON serialization. The `iscsiadm.go` command wrappers and `multipath.go` timeout wrappers are direct collaborators.

Risks: `parseSessions` assumes IQNs contain a colon before the short name. `lsblk` parsing uses simple space splitting despite requesting columns that can be affected by unexpected spacing. `IsMultipathEnabled` dereferences `MountTargetDevice`, so callers must set it first. The legacy `Disconnect` strips the port before logout, while session matching elsewhere uses host:port. `ExecWithTimeout`-backed operations are short, so slow storage nodes may appear failed. Multipath consistency assumes all leaf devices report the same size, LUN, distinct HBA, and WWID relationship.

Test signals: no tests are in this file, but the command wrappers and filesystem functions are injectable for unit tests. Runtime test coverage is implied by CSI sanity and node integration flows that exercise connect, mount, and cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsiadm.go -->
# sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsiadm.go

Purpose: provides the narrow `iscsiadm` command facade and CHAP configuration helpers used by the connector lifecycle.

Important APIs and types: `Secrets` carries CHAP `SecretsType`, username/password, and optional bidirectional username/password fields. Public command helpers include `ListInterfaces`, `ShowInterface`, `CreateDBEntry`, `Discoverydb`, `GetSessions`, `Login`, `Logout`, `DeleteDBEntry`, and `DeleteIFace`. Internal helpers `iscsiCmd`, `iscsiadmDebug`, and `createCHAPEntries` centralize timeout execution, logging, and `iscsiadm -o update` argument construction.

Control flow: every public helper builds a specific `iscsiadm` mode/action invocation and delegates to `iscsiCmd`. `CreateDBEntry` creates a node entry for IQN/portal/interface and then applies discovery and session CHAP settings when the corresponding secret type is `chap`. `Discoverydb` creates a sendtargets discoverydb entry, optionally applies discovery CHAP, runs `--discover`, and deletes the discoverydb entry on discovery failure. `Login` logs in and deletes the node DB entry if login fails.

State and persistence: state is persisted by open-iscsi in its node, iface, and discovery databases rather than in this package. The helper logs command output with newlines escaped. Secret values are passed as command-line arguments, which can expose them to process inspection and verbose logs if callers are not careful.

Dependencies and integration: uses `ExecWithTimeout` through the package-level `execWithTimeout` hook, Linux `iscsiadm`, and `klog`. It is called by `iscsi.go` for discovery, login, session listing, interface inspection, logout, and cleanup.

Risks: command timeout is fixed at three seconds for all `iscsiadm` operations. CHAP is keyed by the exact string `chap`; other auth names are ignored. `Login` reports a sendtargets-style error message although it is logging in. Secrets are embedded in argv for `iscsiadm -v`.

Test signals: no direct tests are present, but the command execution hook makes the API suitable for unit tests that assert arguments and error handling.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsilib/iscsiadm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsilib/multipath.go -->
# sources/control-plane/csi-driver-iscsi/pkg/iscsilib/multipath.go

Purpose: supplies command execution with timeout plus multipath device flush and resize operations used during iSCSI volume cleanup and expansion.

Important APIs and types: `ExecWithTimeout(command, args, timeout)` runs a command under `context.WithTimeout`. `FlushMultipathDevice(*Device)` invokes `multipath -f <path>`. `ResizeMultipathDevice(*Device)` invokes `multipathd resize map <name>`.

Control flow: `ExecWithTimeout` builds an `exec.CommandContext`, returns deadline errors explicitly, and otherwise returns stdout plus command error. `FlushMultipathDevice` resolves a device path, runs `multipath -f`, tolerates the device already disappearing, rewrites `map in use` into a clearer error, and logs the outcome. `ResizeMultipathDevice` runs `multipathd` and wraps combined output in the error.

State and persistence: these functions mutate host device-mapper/multipath state. No repository state is persisted.

Dependencies and integration: depends on Linux `multipath`, `multipathd`, `os.Stat`, `exec`, `context`, and `klog`. `iscsi.go` calls flush during `DisconnectVolume`; resize is available for expansion paths elsewhere in the driver.

Risks: `ExecWithTimeout` uses `errors.Is(err, ee)` with a nil `*exec.ExitError`, so stderr replacement is unlikely to behave as intended; `errors.As` would be the normal pattern. Five-second multipath flush may be too short on busy systems. Flush trusts `Device.GetPath`, so wrong `Type`/`Name` fields can target the wrong path.

Test signals: no direct tests are present; host command hooks inherited from package variables allow stubbing in unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsilib/multipath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.github/dependabot.yaml -->
# sources/control-plane/csi-driver-iscsi/release-tools/.github/dependabot.yaml

Purpose: configures Dependabot for the release-tools repository copy to update GitHub Actions dependencies daily.

Important APIs and types: YAML uses Dependabot `version: 2`, `enable-beta-ecosystems: true`, a single `updates` item for `package-ecosystem: github-actions`, root directory `/`, daily schedule, labels, and an open PR limit of 10.

Control flow: GitHub Dependabot reads this declarative config and opens dependency update PRs for workflow actions. There is no runtime script logic.

State and persistence: state lives in GitHub Dependabot PRs and repository workflow files. This file only stores policy.

Dependencies and integration: integrates with GitHub Actions and project labels `area/dependency`, `release-note-none`, and `ok-to-test`.

Risks: broad daily updates with a PR limit of 10 can create maintenance churn. Only GitHub Actions are covered, not Go, Docker, or Python dependencies.

Test signals: effectiveness is visible through generated Dependabot PRs and CI on those PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/codespell.yml -->
# sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/codespell.yml

Purpose: runs codespell on pushes and pull requests for release-tools.

Important APIs and types: one `codespell` job runs on `ubuntu-latest`, checks out code with a pinned `actions/checkout` SHA, then runs pinned `codespell-project/actions-codespell` with filename checking and skip patterns.

Control flow: GitHub triggers the workflow on every push and PR. The action scans tracked text while skipping binary image extensions, sums, `.git`, its own workflow file, and `prow.sh`.

State and persistence: no durable state is written except workflow logs and check status.

Dependencies and integration: depends on GitHub Actions, checkout, and the codespell action. It complements `verify-spelling.sh`, which uses `misspell`.

Risks: skip patterns intentionally exclude `prow.sh`, so spelling errors there are not caught by this workflow. Pinned action SHAs improve reproducibility but require manual updates.

Test signals: workflow pass/fail is the direct signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/trivy.yaml -->
# sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/trivy.yaml

Purpose: scans the configured Go build image for vulnerabilities using Trivy.

Important APIs and types: workflow runs on pushes to `master` and daily schedule. It extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, emits it as a step output, then scans `golang:<version>` with a pinned Trivy action and all severities enabled.

Control flow: checkout, shell extraction of the Go version, Trivy image scan, and fail on vulnerability finding because `exit-code: 1`.

State and persistence: no repo state is written; scan results live in workflow logs/checks.

Dependencies and integration: depends on the exact text shape of `prow.sh`, GitHub Actions, Docker image availability, and Trivy vulnerability DB.

Risks: the `grep|awk|sed` parser is brittle if `prow.sh` formatting changes. `ignore-unfixed: true` reduces noise but can hide unresolved base image exposure until a fixed package exists.

Test signals: scheduled and push workflow status show current Go image vulnerability health.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.prow.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/.prow.sh

Purpose: acts as the Prow entrypoint for testing the `csi-release-tools` repository itself.

Important APIs and types: shell script invokes `verify-shellcheck.sh`, `verify-spelling.sh`, and `verify-boilerplate.sh` with the current directory.

Control flow: `bash -e` exits on the first failed verifier. No setup or cleanup beyond the called scripts.

State and persistence: no persistent state besides verifier side effects such as temporary installs or logs.

Dependencies and integration: integrates with Kubernetes Prow jobs and the release-tools verification scripts in the same directory.

Risks: it does not run `prow.sh main`, so it validates release-tools hygiene but not full build/e2e orchestration behavior. The checks depend on Docker, shellcheck, Go, Python, or misspell availability as handled by child scripts.

Test signals: Prow pass/fail for the three validation gates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/csi-driver-iscsi/release-tools/boilerplate/boilerplate.py

Purpose: validates that source files contain the expected Kubernetes copyright/license boilerplate for their extension or basename.

Important APIs and types: argparse options accept explicit filenames, `--rootdir`, `--boilerplate-dir`, and `--verbose`. Core functions are `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`.

Control flow: reference boilerplates are loaded from `boilerplate.*.txt`. Candidate files are either supplied explicitly or discovered by walking the root, pruning skipped directories. For Go files, leading build constraints are stripped; for shell and Python files, shebangs are stripped. The header is normalized by replacing a year with `YEAR` and compared to the reference. Failing paths are printed to stdout, with optional diffs to stderr.

State and persistence: read-only filesystem scan. It opens `/dev/null` when not verbose.

Dependencies and integration: used by `verify-boilerplate.sh`; depends on Python standard library modules `argparse`, `difflib`, `glob`, `os`, `re`, `sys`, and `datetime`.

Risks: `refs[extension]` and `refs[basename]` assume a matching boilerplate exists. The skipped directory list is substring based and may skip unexpected paths. It returns exit code 0 even when files fail; the wrapper enforces failure by inspecting stdout.

Test signals: wrapper execution in Prow and GitHub CI reveals missing or malformed headers.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.sh

Purpose: generic Cloud Build entrypoint for repositories importing CSI release-tools.

Important APIs and types: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: when Google Cloud Build invokes this script, `prow.sh` defines configuration and helper functions, then `gcr_cloud_build` authenticates Docker with gcloud, prepares the build environment, optionally registers QEMU, and runs `make push-multiarch`.

State and persistence: pushes container images to the configured registry through `REGISTRY_NAME` and `GIT_TAG` environment values.

Dependencies and integration: depends on Cloud Build, gcloud, Docker buildx, Go, repository Makefile targets, and `release-tools/prow.sh`.

Risks: assumes caller has a top-level `release-tools` import and Makefile support for `push-multiarch`. Missing environment variables are handled mostly by downstream make/prow logic.

Test signals: Cloud Build success and pushed multi-architecture images.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.yaml -->
# sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.yaml

Purpose: reusable Google Cloud Build configuration for Kubernetes CSI multi-architecture image publishing.

Important APIs and types: sets `timeout: 7200s`, allows loose substitutions, runs one step in `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud:v20260205-38cfa9523f`, uses `./.cloudbuild.sh` as entrypoint, and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME`.

Control flow: Cloud Build resolves substitutions, launches the builder image, executes `.cloudbuild.sh`, and delegates actual image build/push behavior to release-tools.

State and persistence: produces pushed images in the staging registry; the YAML itself is declarative.

Dependencies and integration: integrates with Kubernetes image-pushing jobs, repo symlink conventions, Dockerfiles that accept `binary`, and `release-tools/cloudbuild.sh`.

Risks: the builder image tag is pinned and must be maintained. Repositories without expected Makefile/Dockerfile contracts will fail at runtime. Default substitution values are placeholders and rely on Prow/Cloud Build overrides.

Test signals: Cloud Build logs, resulting image manifests, and promotion readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/csi-driver-iscsi/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper script for CSI documentation maintainers to list supported sidecar release versions and optionally associated Docker images.

Important APIs and types: functions include `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`. CLI accepts repeated `--repo/-R`, `--display/-d`, and `--doc/-D`.

Control flow: verifies GitHub CLI availability, fetches releases with `gh release list`, groups semantic `vX.Y.Z` releases by major/minor, selects supported versions based on CSI support policy, prints release dates and age, and optionally fetches each release page to extract a `docker pull` command.

State and persistence: no files are written; all output goes to stdout.

Dependencies and integration: depends on `gh`, Python `dateutil.relativedelta`, GitHub release metadata, and release note text conventions for Docker image extraction.

Risks: release parsing assumes tab-separated `gh release list` fields and published timestamp at index 3. The latest grouped version is always supported even if malformed policy inputs exist. `--display` defaults to true even when `--doc` is requested, so doc output includes display output too.

Test signals: manual output can be compared with CSI sidecar docs and GitHub release pages.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/filter-junit.go -->
# sources/control-plane/csi-driver-iscsi/release-tools/filter-junit.go

Purpose: command-line utility that merges and filters JUnit XML so Prow/Spyglass only receives relevant test cases.

Important APIs and types: flags are `-o` output path and `-t` test-name regex. XML structs are `TestResults`, `TestSuite`, `TestCase`, and custom `SkipReason` to preserve empty `<skipped></skipped>` elements.

Control flow: parses flags, compiles the regex, reads each input XML, first trying direct `<testsuite>` unmarshalling and falling back to `<testsuites><testsuite>`. It filters testcases by name, de-duplicates by name, replaces skipped-only entries with real runs, marshals the merged suite, and writes stdout or a file.

State and persistence: writes one output XML file or stdout. No other state.

Dependencies and integration: used by `prow.sh` through `run_filter_junit` for E2E and make-test JUnit processing. Depends on Go `encoding/xml`, `flag`, `os`, and `regexp`.

Risks: stdin reading uses `os.Stdin.Read(data)` into a nil slice, so `-` input is broken. Map iteration makes testcase output order nondeterministic. XML pass-through is incomplete by design and only preserves known fields.

Test signals: generated `junit_final.xml` and Spyglass rendering are runtime signals; no unit tests are present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/generate-patch-release-notes.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/generate-patch-release-notes.sh

Purpose: maintainer automation for generating patch release changelog PRs across CSI repositories.

Important APIs and types: configurable `releases` array contains `repo version` pairs. `gen_patch_relnotes` wraps Kubernetes `release-notes` with `CSI_RELEASE_TOKEN`, start revision, branch, org, repo, markdown links, and output file.

Control flow: for each release entry, the script parses minor and patch versions, computes the previous patch tag, checks out a changelog branch from `upstream/release-<minor>`, generates release notes, prepends a release header to `CHANGELOG-<minor>.md`, commits, force pushes, and creates a GitHub PR with `gh pr create`.

State and persistence: mutates local Git checkouts, branches, changelog files, remote branches, and GitHub PRs.

Dependencies and integration: depends on `gh`, `release-notes`, git remotes named `upstream` and `origin`, `CSI_RELEASE_TOKEN`, `GITHUB_USER`, and a local directory layout where repos are sibling directories.

Risks: `set -x` can expose command details. Branches are force-pushed and deleted locally. The release list is empty by default and must be edited. Existing PR regeneration is explicitly not handled.

Test signals: generated changelog diff, successful commit/push, and created PR.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/generate-patch-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/go-get-kubernetes.sh

Purpose: updates Kubernetes staging-module dependencies in a Go module to a target Kubernetes version while maintaining necessary replace directives.

Important APIs and types: CLI accepts optional `-p` prune and a required Kubernetes version `x.y.z`. Internal helpers are `help` and `die`.

Control flow: downloads the target `kubernetes/kubernetes` `go.mod`, extracts staging module replaces, optionally prunes unused replaces, resolves each staging module version via `go mod download <mod>@kubernetes-<version>`, writes `go mod edit -replace`, obtains imported packages through `go list`, maps packages to replaced modules, and runs `go get` on package-level dependencies at the target version.

State and persistence: mutates `go.mod` and later `go.sum` via Go tooling. It reads module graph and package dependency state from the current repository.

Dependencies and integration: depends on curl, sed, grep, Go modules, network access to GitHub and module proxies, and Kubernetes staging module versioning conventions.

Risks: package discovery fallback still may fail for broken repos. It intentionally expands shell word splitting for package lists. Network or proxy flakiness can leave partial `go.mod` edits. The help text says optional `-p`, but usage line is confusing.

Test signals: `SUCCESS`, clean `go mod tidy`, and downstream build/test/vendor checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/go-modules-targeted-update.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/go-modules-targeted-update.sh

Purpose: batch-updates a selected list of Go modules across selected CSI sidecar release branches and opens PRs.

Important APIs and types: variables `org`, `modules`, and `releases` define target organization, module versions, and `repo branch` pairs. The script requires `GITHUB_USER`.

Control flow: for each release row, fetches upstream, recreates `module-update-<branch>`, checks out from `upstream/<branch>`, runs `go get` for each configured module, tidies and vendors, commits all changes, force pushes, and opens a PR with the module list in the body.

State and persistence: mutates local repos, branches, `go.mod`, `go.sum`, `vendor`, remote branches, and GitHub PRs.

Dependencies and integration: depends on `gh`, git remotes, Go tooling, vendored repos, and sibling checkout layout.

Risks: release list is commented out by default. It does not resolve API incompatibilities after dependency bumps. `set -x` reveals commands. The `if [ "$repo" != "#" ]` check does not robustly skip commented lines unless parsed exactly.

Test signals: successful build/tests after PR creation, clean vendor diff, and CI on generated PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/go-modules-targeted-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/go-modules-update.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/go-modules-update.sh

Purpose: broad automation for updating Kubernetes dependencies and release-tools subtree across multiple Kubernetes CSI repositories.

Important APIs and types: options `-u` GitHub username and `-v` Kubernetes version. The embedded here-doc lists target repos and branches. `MAX_RETRY` controls retry attempts around `go-get-kubernetes.sh`.

Control flow: logs into GitHub CLI, iterates repos, recreates `module-update-<branch>`, updates `release-tools` via git subtree pull with conflict fallback to archive replacement, retries `release-tools/go-get-kubernetes.sh -p <version>` with tidy/vendor cleanup, commits, rewrites origin to the user's fork, runs `make test`, pushes, and creates a PR.

State and persistence: mutates many local checkouts, subtrees, dependencies, vendor directories, remotes, branches, and GitHub PRs.

Dependencies and integration: depends on git subtree, GitHub CLI, Go modules, repository Makefiles, release-tools scripts, and a sibling org directory layout.

Risks: the retry loop condition syntax combines command and numeric comparison in a fragile way. PR `--head` and `--base` are hard-coded to master in the create call even when iterating other branches. It force pushes and changes the origin remote. Interface incompatibilities are explicitly not handled.

Test signals: `make test`, generated dependency diffs, successful push, and PR CI.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/go-modules-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/prow.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/prow.sh

Purpose: shared Prow and Cloud Build orchestration library for Kubernetes CSI repositories, covering build, unit tests, kind cluster setup, CSI driver deployment, Kubernetes E2E, CSI sanity, JUnit generation, snapshot controller setup, and multi-arch image publishing.

Important APIs and types: `configvar` declares overridable defaults for Go versions, build platforms, kind/Kubernetes versions, hostpath driver deployment, sidecar E2E, sanity, feature gates, and test selection. Major functions include `ensure_paths`, `run_with_go`, `install_kind`, `install_ginkgo`, `git_checkout`, `git_clone`, `start_cluster`, `install_csi_driver`, `install_snapshot_crds`, `install_snapshot_controller`, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `install_e2e`, `install_sanity`, `run_e2e`, `run_sanity`, `make_test_to_junit`, `main`, and `gcr_cloud_build`.

Control flow: repos source this file after overriding variables. `main` creates work directories, builds binaries and containers, runs unit tests as JUnit, installs kind if needed, creates non-alpha and optional alpha clusters, applies snapshot CRDs/controllers, deploys the CSI driver, runs sanity and E2E subsets selected by focus/skip regexes, collects logs, tears down clusters, and merges JUnit output. `gcr_cloud_build` configures Docker auth/QEMU and runs `make push-multiarch`.

State and persistence: creates temporary work under GOPATH, writes artifacts/JUnit/log files, creates and deletes kind clusters, loads local Docker images, patches checked-out Kubernetes manifests in the work tree for canary tests, and pushes images in Cloud Build mode.

Dependencies and integration: integrates with Go toolchains via `GOTOOLCHAIN`, kind, Docker, kubectl, ginkgo, Kubernetes source builds, csi-test, external-snapshotter manifests, repo Makefiles, Prow artifact conventions, and Cloud Build/gcloud.

Risks: large shell surface with many environment contracts. Some defaults can become stale as Kubernetes, sidecars, and kind evolve. Many operations depend on network access and mutable external repos. It uses `git clean -fdx` inside its own checked-out work paths. Image and deployment override generation depends on Makefile `CMDS` parsing.

Test signals: Prow job success, unit JUnit, E2E JUnit, sanity JUnit, kind logs, cluster info artifacts, and successful multi-arch image pushes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/pull-test.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/pull-test.sh

Purpose: validates a `csi-release-tools` PR by importing the changed subtree into another repository and running that repository's Prow entrypoint.

Important APIs and types: uses `PULL_TEST_REPO_DIR` as the target repository directory and `CSI_RELEASE_TOOLS_DIR` as the current release-tools checkout.

Control flow: enables lazy blob fetching for Prow partial clones, records the release-tools directory, moves to the target repo, hard-resets it, pulls the current release-tools directory as a git subtree into `release-tools`, prints recent log entries, and `exec`s `./.prow.sh`.

State and persistence: destructively resets and mutates the target test repo workspace, then replaces the shell process with target Prow tests.

Dependencies and integration: depends on git subtree, Prow environment, and a target repo with `.prow.sh`.

Risks: `git reset --hard` is destructive by design in the target checkout. It assumes the subtree prefix is exactly `release-tools` and branch name `master`.

Test signals: downstream `.prow.sh` results in the importing repository.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/update-vendor.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/update-vendor.sh

Purpose: updates vendored dependencies for repos using either dep or Go modules.

Important APIs and types: no functions; top-level shell checks for `Gopkg.toml` or `go.mod`.

Control flow: if `Gopkg.toml` exists, runs `dep ensure`. If `go.mod` exists, runs `release-tools/verify-go-version.sh go`, then `go mod tidy` and `go mod vendor` with `GO111MODULE=on`.

State and persistence: mutates dependency metadata and `vendor` contents.

Dependencies and integration: depends on dep, Go modules, and release-tools Go-version policy.

Risks: no strict shell options are set, so failures can be less controlled than verifier scripts. It assumes `release-tools/verify-go-version.sh` is reachable from repo root.

Test signals: clean git diff after expected dependency changes and passing `verify-vendor.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/util.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/util.sh

Purpose: shared shell utility functions and color constants borrowed from Kubernetes-style hack scripts.

Important APIs and types: functions include `kube::util::sourced_variable`, `sortable_date`, `array_contains`, `trap_add`, `download_file`, `wait-for-jobs`, `join`, and `check-file-in-alphabetical-order`. It also declares ANSI color variables when not already set.

Control flow: utility functions are sourced by other scripts and execute only when called. `trap_add` composes new trap commands with existing ones. `download_file` retries curl downloads. `wait-for-jobs` aggregates background job failures.

State and persistence: modifies shell traps and color variables in the caller context. `download_file` writes the requested destination file.

Dependencies and integration: used by `verify-shellcheck.sh`; depends on bash, curl, date, diff, sort, awk, and shell job control.

Risks: `rm "${destination_file}" 2&> /dev/null` appears typo-like and may not redirect as intended. Trap composition evaluates command strings early by design. These utilities assume bash, not POSIX sh.

Test signals: scripts sourcing this file pass shellcheck and runtime validation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-boilerplate.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-boilerplate.sh

Purpose: enforcement wrapper around `boilerplate/boilerplate.py`.

Important APIs and types: accepts an optional root directory, defaults to the parent of release-tools, ensures `python` exists by linking python3 through `update-alternatives` if necessary, and collects failing files with `mapfile`.

Control flow: sets strict shell options, resolves `TOOLS` and `ROOT`, executes the boilerplate checker in verbose mode, prints each failing file, and exits nonzero when any file lacks the expected header.

State and persistence: may modify system alternatives to provide `/usr/bin/python`. Creates a temp file and removes it on exit, although the temp file is not used for test output.

Dependencies and integration: used by release-tools `.prow.sh` and importing repo Prow scripts. Depends on bash, Python, and boilerplate reference files.

Risks: `update-alternatives` may require privileges and is surprising in a verifier. The unused temp file/trap is harmless but noisy.

Test signals: Prow verifier pass/fail and printed failing file list.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-go-version.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-go-version.sh

Purpose: warns developers when their local Go major/minor differs from the build version configured in `release-tools/prow.sh`.

Important APIs and types: expects one argument: path to the Go binary. Internal `die` exits on missing binary/version failures.

Control flow: reads `go version`, extracts major.minor with sed, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a prominent warning if versions differ.

State and persistence: read-only except stderr output.

Dependencies and integration: called by `update-vendor.sh`; depends on Go, sed, and a repo-root relative `release-tools/prow.sh`.

Risks: it only warns, never fails on mismatch. Sourcing `prow.sh` runs all `configvar` declarations and may emit output that is redirected away, but still evaluates shell code.

Test signals: warning presence/absence during local vendor updates.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-go-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-logcheck.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-logcheck.sh

Purpose: verifies contextual logging usage with `sigs.k8s.io/logtools/logcheck`.

Important APIs and types: optional first argument is `LOGCHECK_VERSION`, default `0.10.0`. It computes `CSI_LIB_UTIL_ROOT` as the parent of release-tools and installs `logcheck` into a temp `GOBIN`.

Control flow: strict shell mode, create temp dir with cleanup trap, `go install` the requested logcheck version, then run `logcheck -check-contextual -check-with-helpers <root>/...`.

State and persistence: temporary binary directory only, deleted on exit. Does not change repo files.

Dependencies and integration: depends on Go module install, network access, and logcheck support for the target codebase.

Risks: variable names mention `CSI_LIB_UTIL` even though this is release-tools. Installing at runtime makes the verifier dependent on external module availability.

Test signals: nonzero exit from logcheck indicates logging violations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-logcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-shellcheck.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-shellcheck.sh

Purpose: runs ShellCheck over shell scripts in a repository, using an exact host ShellCheck version or a pinned Docker image.

Important APIs and types: configurable `ROOT` argument, `SHELLCHECK_VERSION=0.6.0`, pinned `SHELLCHECK_IMAGE`, disabled checks `SC1090` and `SC2230`, and helper functions `join_by`, `create_container`, and `remove_container`.

Control flow: sources `util.sh`, discovers `*.sh` files excluding hidden output, `.git`, vendor, and git-ignored files, detects host shellcheck version, otherwise starts a long-lived Docker container mounted at the repo root, runs shellcheck for every script, collects failures, and exits nonzero with all lint output if any fail.

State and persistence: may create and remove a Docker container named `k8s-shellcheck`. No repo files are modified.

Dependencies and integration: used by release-tools `.prow.sh`; depends on bash, git, find, Docker, ShellCheck, and `util.sh` trap handling.

Risks: pinned ShellCheck 0.6.0 is old. Docker is required when the exact host version is absent. Files without `.sh` extension are not linted even if executable shell.

Test signals: ShellCheck output and Prow verifier status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-spelling.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-spelling.sh

Purpose: checks spelling across tracked repository files using `misspell`.

Important APIs and types: `TOOL_VERSION=v0.3.4`, optional root argument, temp install directory, and cleanup trap.

Control flow: strict shell mode, install misspell into a temp directory with `go install` if absent, run `git ls-files -z | grep -z -v vendor | xargs -0 misspell --`, prefix errors, and exit nonzero when the error log is non-empty.

State and persistence: temp directory only; no repo writes.

Dependencies and integration: used by release-tools and NFS Prow scripts. Depends on Go, git, grep with null-data support, and misspell.

Risks: excludes paths containing `vendor` by grep substring, which may be broader than intended. Tool version is old and installed dynamically.

Test signals: printed `error:` lines and nonzero exit.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-subtree.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-subtree.sh

Purpose: verifies that a git subtree-managed directory has no local non-merge commits modifying it.

Important APIs and types: takes one required directory argument.

Control flow: finds the latest non-merge commit touching the directory with `git log --remove-empty --no-merges`. If one exists, prints the non-upstream log and exits nonzero; otherwise reports the directory as a clean upstream copy.

State and persistence: read-only Git history inspection.

Dependencies and integration: intended for repos importing `release-tools` via git subtree.

Risks: it trusts merge commits as upstream imports; local edits hidden inside a merge commit can bypass the check, as the comment notes. Requires full enough Git history for the directory.

Test signals: Prow verifier pass/fail and printed git log.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-vendor.sh -->
# sources/control-plane/csi-driver-iscsi/release-tools/verify-vendor.sh

Purpose: validates that Go module and vendor metadata are up to date.

Important APIs and types: top-level shell checks `go.mod`, Prow variables `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA`, and uses `go mod tidy` plus optional `go mod vendor`.

Control flow: if in a Prow presubmit whose diff does not touch dependency-relevant files or imports, skips the check. Otherwise runs tidy, fails if `go.mod` or `go.sum` changed, runs vendor when a vendor directory exists, and fails if vendor changed.

State and persistence: Go commands may modify module and vendor files; the script then reports those diffs as failures.

Dependencies and integration: used from Makefile test targets in importing repos. Depends on Git, Go modules, and Prow env for skip optimization.

Risks: references `${JOB_NAME}` without a default under non-strict shell, so local unset variables evaluate empty but would break under nounset. The skip heuristic can miss dependency effects outside import/go.mod/vendor/release-tools changes.

Test signals: clean git status after tidy/vendor and verifier exit code.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/test/sanity/params.yaml -->
# sources/control-plane/csi-driver-iscsi/test/sanity/params.yaml

Purpose: supplies CSI sanity test volume parameters for the iSCSI driver.

Important APIs and types: YAML defines `source: "//127.0.0.1/share"`.

Control flow: `test/sanity/run-test.sh` passes this file to `csi-sanity` with `--csi.testvolumeparameters`.

State and persistence: declarative test input only.

Dependencies and integration: integrates with csi-test/csi-sanity and the iSCSI plugin's expected volume parameters.

Risks: the value resembles an SMB/NFS-style source rather than an iSCSI target tuple, so it may only be meaningful for skipped or limited sanity cases depending on driver expectations.

Test signals: sanity test startup and parameter parsing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/test/sanity/params.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/test/sanity/run-test.sh -->
# sources/control-plane/csi-driver-iscsi/test/sanity/run-test.sh

Purpose: launches the iSCSI CSI plugin locally and runs the CSI sanity suite against its Unix socket.

Important APIs and types: functions `cleanup` and `install_csi_sanity_bin`; constants include endpoint `unix:///tmp/csi.sock`, default node ID `CSINode`, csi-test version `v4.3.0`, and skipped test regex `Controller Server|should work|should be idempotent|should remove target path`.

Control flow: installs `csi-sanity` into GOPATH when missing, starts `bin/iscsiplugin` with sudo on GitHub Actions or directly locally, then runs `csi-sanity` with secrets, params, endpoint, verbose Ginkgo output, and skip list. Cleanup kills `iscsiplugin` and removes the cloned `csi-test` directory.

State and persistence: creates/clones under GOPATH, starts/kills a local plugin process, uses `/tmp/csi.sock`, and may remove a local `csi-test` directory.

Dependencies and integration: depends on Go/GOPATH, git, make, csi-test, built `bin/iscsiplugin`, sudo in GitHub Actions, and the YAML fixtures in this folder.

Risks: `GO111MODULE=off` and old csi-test version may be stale. `pkill -f iscsiplugin` can terminate unrelated matching processes. The broad skip regex means only a subset of sanity coverage runs.

Test signals: csi-sanity output and process cleanup behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/test/sanity/run-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/test/sanity/secrets.yaml -->
# sources/control-plane/csi-driver-iscsi/test/sanity/secrets.yaml

Purpose: provides CSI sanity secrets for node-stage operations.

Important APIs and types: YAML key `NodeStageVolumeSecret` contains `username: sanity` and `password: sanitytestpassword`.

Control flow: passed to `csi-sanity` through `--csi.secrets` by `run-test.sh`.

State and persistence: static test credentials stored in the repo; not production secrets.

Dependencies and integration: consumed by csi-test and the iSCSI plugin's secret parsing.

Risks: because names are generic, failures may be hard to distinguish from missing real CHAP parameters. It should not be reused outside test context.

Test signals: sanity tests that require node-stage secret input can parse the YAML.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/test/sanity/secrets.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.cloudbuild.sh -->
# sources/control-plane/csi-driver-nfs/.cloudbuild.sh

Purpose: NFS driver Cloud Build entrypoint that delegates multi-arch image publishing to shared release-tools.

Important APIs and types: sources `release-tools/prow.sh` and calls `gcr_cloud_build`.

Control flow: Cloud Build executes this script, which loads the shared function definitions and runs image build/push orchestration.

State and persistence: publishes NFS plugin images according to Makefile and Cloud Build environment.

Dependencies and integration: depends on release-tools, Cloud Build, gcloud, Docker buildx, and the NFS Makefile `push-multiarch` support inherited from `release-tools/build.make`.

Risks: thin wrapper offers no repo-specific validation; failures surface in downstream `gcr_cloud_build` or Makefile logic.

Test signals: Cloud Build success and pushed image manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/dependabot.yaml -->
# sources/control-plane/csi-driver-nfs/.github/dependabot.yaml

Purpose: configures automated dependency PRs for the NFS driver.

Important APIs and types: three Dependabot ecosystems: `gomod` at `/`, `github-actions` at `/`, and `docker` at `./`. Go and GitHub Actions have daily schedules and PR limit 1; Docker runs daily at 01:00 Asia/Shanghai with cleanup label.

Control flow: Dependabot monitors dependencies and opens PRs with standard labels.

State and persistence: generated PRs and dependency diffs in GitHub.

Dependencies and integration: integrates with GitHub labels, Go modules, workflow actions, and Dockerfile base image updates.

Risks: low PR limits serialize updates and may delay security updates when queues are busy. Docker PRs do not specify an open PR limit.

Test signals: Dependabot PRs and CI outcomes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/codeql-analysis.yml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/codeql-analysis.yml

Purpose: runs CodeQL security analysis for Go code in the NFS driver.

Important APIs and types: workflow triggers on pushes and PRs to `master` and `release-**`, plus daily schedule. Job grants `security-events: write`, sets up Go `^1.18`, checks out code, initializes CodeQL for language `go`, runs `make all`, then analyzes.

Control flow: CodeQL database initialization precedes build so compiled Go code is captured, then CodeQL uploads analysis results.

State and persistence: security alerts/results in GitHub code scanning.

Dependencies and integration: depends on GitHub CodeQL action, setup-go, checkout, and the Makefile build target.

Risks: setup Go version is older than the Makefile and Trivy workflow versions, which can expose version skew. Autobuild is replaced with explicit `make all` but still assumes Linux build defaults are valid.

Test signals: CodeQL job status and code scanning alerts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/codespell.yml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/codespell.yml

Purpose: runs codespell on NFS driver pushes and PRs.

Important APIs and types: one Ubuntu job with pinned checkout and pinned `actions-codespell`, filename checking, broad skip list, and ignored word `ro`.

Control flow: GitHub Actions scans text files except `.git`, workflow file, images, sums, vendor, `go.sum`, and `release-tools/prow.sh`.

State and persistence: check status and logs only.

Dependencies and integration: complements release-tools `verify-spelling.sh` in Prow.

Risks: excludes `release-tools/prow.sh` and vendor/go.sum. Ignoring `ro` may hide real typo-like tokens but avoids false positives for read-only abbreviations.

Test signals: workflow status on push and PR.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/darwin.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/darwin.yaml

Purpose: runs NFS driver package unit tests on macOS.

Important APIs and types: triggers on all pushes and pull requests. The job uses `macos-latest`, setup-go `^1.16`, checkout, and `go test -v -race ./pkg/...`.

Control flow: setup Go, checkout source, print Go version, run race-enabled tests for package code.

State and persistence: no repo writes; GitHub test logs only.

Dependencies and integration: validates cross-platform package behavior outside Linux-specific container build paths.

Risks: Go `^1.16` is old relative to current build/scanning workflows. Tests that require Linux-only behavior should be guarded or skipped in package code.

Test signals: macOS race test pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/darwin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/linux.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/linux.yaml

Purpose: primary Linux CI for verification, tests, coverage, and container build.

Important APIs and types: triggers on pushes and PRs. Uses setup-go `^1.17`, checkout, `make verify`, `go test -race -covermode=atomic -coverprofile=profile.cov ./pkg/...`, `make container`, installs `goveralls`, and uploads coverage with `GITHUB_TOKEN`.

Control flow: a build step performs verification, race coverage tests, and Docker buildx container creation; a later step sends coverage.

State and persistence: creates coverage profile and local container images; writes coverage to Coveralls.

Dependencies and integration: depends on Makefile targets, Docker buildx, release-tools, hack verifiers, Go, and Coveralls.

Risks: building multi-arch containers in generic GitHub runners can be slow or flaky due to QEMU/binfmt. Go version differs from Trivy and Makefile release version.

Test signals: verify target, race coverage, container build, and Coveralls upload.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/linux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/pluto.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/pluto.yaml

Purpose: checks Kubernetes manifest API versions for deprecations with Fairwinds Pluto.

Important APIs and types: triggers on pushes and PRs. Downloads Pluto through a pinned action, then runs `pluto detect-files -d deploy` and `pluto detect-files -d deploy/example`.

Control flow: checkout, install Pluto, scan deployment directories.

State and persistence: no repo writes; workflow output only.

Dependencies and integration: validates Kubernetes YAML outside the Helm chart templates assigned here.

Risks: only scans `deploy` and `deploy/example`, not `charts`. Pluto version comes from pinned action but its API deprecation database may need updates.

Test signals: Pluto workflow pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/pluto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/shellcheck.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/shellcheck.yaml

Purpose: runs ShellCheck for NFS driver shell scripts on protected branches, release branches, version tags, and PRs.

Important APIs and types: uses pinned checkout and pinned `ludeeus/action-shellcheck`, sets `SHELLCHECK_OPTS: -e SC2034`, warning severity, checks scripts together, ignores `vendor`, `release-tools`, and `hack`, and formats output as gcc.

Control flow: GitHub triggers, action scans eligible shell scripts, and reports annotations.

State and persistence: workflow annotations/logs only.

Dependencies and integration: complements release-tools shellcheck but intentionally excludes imported release-tools and hack scripts.

Risks: warning severity may not fail issues depending on action behavior. Ignored paths can contain shell code not covered here.

Test signals: workflow status and annotations.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/shellcheck.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/static.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/static.yaml

Purpose: runs Go static analysis and Helm chart verification for the NFS driver.

Important APIs and types: `go_lint` job uses setup-go `^1.19`, pinned checkout, and pinned `golangci-lint-action` v2.10 with explicit enabled linters and 30-minute timeout. `verify-helm` installs `yq` via snap and runs `sudo hack/verify-helm-chart.sh`.

Control flow: the lint job analyzes Go code; the Helm job checks chart rendering/consistency through repository hack script.

State and persistence: no intended repo writes; verification may render temp artifacts.

Dependencies and integration: depends on `.golangci.yml`, golangci-lint, yq, Helm verification script, and sudo availability.

Risks: workflow args enable many linters beyond `.golangci.yml` default staticcheck, so local and CI lint surfaces may differ. Installing yq from snap can be slow or version-sensitive.

Test signals: lint annotations, Helm verification output, and job status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/static.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/trivy.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/trivy.yaml

Purpose: builds the NFS plugin image and scans it for OS and library vulnerabilities with Trivy.

Important APIs and types: runs on pushes to master and pull requests. Installs Go `1.25.11`, sets build env (`PUBLISH`, `REGISTRY`, `IMAGE_VERSION`, `ARCH`), runs `make nfs` and `make container-build`, then scans `test/nfsplugin:latest-linux-amd64` with pinned Trivy action and ECR-hosted DB.

Control flow: checkout, setup Go, build binary/image, scan image, fail on any severity because `exit-code: 1`.

State and persistence: creates local Docker image and vulnerability scan logs.

Dependencies and integration: depends on Docker buildx, Makefile targets, Dockerfile, Go, and Trivy DB.

Risks: Go version is very specific and may not exist in setup-go at all times. Scanning all severities including unknown can cause noisy failures. `ignore-unfixed` may still pass known unfixed vulnerabilities.

Test signals: successful image build and Trivy pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/windows.yaml -->
# sources/control-plane/csi-driver-nfs/.github/workflows/windows.yaml

Purpose: runs NFS driver package unit tests on Windows.

Important APIs and types: matrix contains Go `^1.16` on `windows-latest`, checkout, and `go test -v -race ./pkg/...`.

Control flow: install Go, checkout source, print Go version, run race-enabled tests.

State and persistence: workflow logs only.

Dependencies and integration: validates that package-level code compiles and tests outside Linux.

Risks: Windows cannot exercise Linux mount behavior, so coverage is limited to portable package code. Go `^1.16` is old compared with current build tooling.

Test signals: Windows race test status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.github/workflows/windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.golangci.yml -->
# sources/control-plane/csi-driver-nfs/.golangci.yml

Purpose: configures golangci-lint v2 behavior for the NFS driver.

Important APIs and types: sets config `version: "2"`, disables default linters, enables `staticcheck`, configures staticcheck `S*` checks, defines a depguard rule allowing standard library plus `k8s.io`, `sigs.k8s.io`, and `github.com`, adds exclusion presets and two revive text exclusions, and enables `gofmt` formatter.

Control flow: golangci-lint reads this file when invoked locally or by CI, although the static workflow also passes explicit linters via args.

State and persistence: no runtime state; policy only.

Dependencies and integration: consumed by `golangci-lint-action` and developer lint runs.

Risks: depguard is configured but not enabled in this file, so the rule may be inert unless enabled by CI args. CI args enable additional linters, creating possible mismatch with this config.

Test signals: lint pass/fail and formatter checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.prow.sh -->
# sources/control-plane/csi-driver-nfs/.prow.sh

Purpose: NFS driver Prow entrypoint that customizes shared CSI release-tools to run only relevant tests.

Important APIs and types: defaults `CSI_PROW_TESTS` to `unit`, sources `release-tools/prow.sh`, runs boilerplate and spelling verifiers, then calls `main`.

Control flow: repo-specific verification runs before shared build/test orchestration. Because tests default to unit, `prow.sh main` builds, runs Makefile tests, and container-related flow according to shared logic without k/k E2E by default.

State and persistence: creates Prow work/artifact state through shared `main`; verifier temp state only.

Dependencies and integration: depends on imported release-tools and NFS Makefile targets.

Risks: k/k E2E is disabled by default, so Prow does not validate full cluster storage behavior unless a job overrides variables. Boilerplate/spelling run outside `main`, so failures stop before build diagnostics.

Test signals: Prow unit/build/verifier status and artifacts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/Dockerfile -->
# sources/control-plane/csi-driver-nfs/Dockerfile

Purpose: packages the built NFS CSI plugin binary into a Debian-based runtime image.

Important APIs and types: base image is `registry.k8s.io/build-image/debian-base:bookworm-v1.0.8`. Build args are `ARCH` and `binary=./bin/${ARCH}/nfsplugin`. It copies the binary to `/nfsplugin`, installs/upgrades runtime packages, and sets `/nfsplugin` as entrypoint.

Control flow: Docker build receives architecture-specific binary path from Makefile, copies it, upgrades packages, unholds `libcap2`, installs `ca-certificates`, `mount`, `nfs-common`, and `netbase`, then runs the plugin as PID 1.

State and persistence: produces container image layers. Runtime state is managed by Kubernetes pods.

Dependencies and integration: used by Makefile `container-build`; requires prebuilt binary and Debian package repositories.

Risks: `apt upgrade -y` makes builds depend on current package repository state and can reduce reproducibility. Runtime image includes mount/NFS tools and requires privileged Kubernetes deployment to mount NFS.

Test signals: successful `make container-build`, Trivy scan, and pod startup.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/Makefile -->
# sources/control-plane/csi-driver-nfs/Makefile

Purpose: defines build, verification, container, publish, Helm, sanity, and E2E targets for the CSI NFS driver.

Important APIs and types: key variables include `CMDS=nfsplugin`, `PKG`, `IMAGE_VERSION`, `LDFLAGS`, `EXT_LDFLAGS`, registry/image names, `ALL_ARCH.linux`, `ALL_OS_ARCH`, and `E2E_HELM_OPTIONS`. Targets include `all`, `verify`, `unit-test`, `sanity-test`, `nfs`, `nfs-armv7`, `container-build`, `container-linux-armv7`, `container`, `push`, `push-latest`, `install-nfs-server`, `install-helm`, `e2e-bootstrap`, `e2e-teardown`, and `e2e-test`.

Control flow: `all` builds the Linux plugin. `verify` runs unit tests and `hack/verify-all.sh`. `container` configures buildx/binfmt, builds binaries and images for arm64, amd64, ppc64le, and arm/v7. Push targets create Docker manifests under CI. E2E bootstrap builds/pushes images, installs Helm, and deploys the chart with test overrides.

State and persistence: writes binaries under `bin/<arch>`, creates Docker images/manifests, pushes images, installs Kubernetes resources with kubectl/Helm, and writes coverage profiles.

Dependencies and integration: includes `release-tools/build.make`, uses Go modules with vendor mode, Docker buildx, Helm, kubectl, and repository tests.

Risks: `CMDS` is defined twice. Default `REGISTRY` points at a personal namespace. Cross-arch builds depend on binfmt/QEMU. `IMAGE_VERSION` changes under CI unless `PUBLISH` is set, which affects reproducibility of E2E images.

Test signals: unit coverage, verify target, sanity test, container build/push, Helm install, and E2E test status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/artifacthub-repo.yml -->
# sources/control-plane/csi-driver-nfs/charts/artifacthub-repo.yml

Purpose: declares Artifact Hub repository ownership metadata for the NFS CSI driver Helm chart repository.

Important APIs and types: contains `repositoryID` and one owner entry with name and email.

Control flow: Artifact Hub reads this metadata when indexing or verifying chart ownership.

State and persistence: declarative repository metadata only.

Dependencies and integration: integrates with Artifact Hub chart listing and ownership workflows.

Risks: stale owner contact can break chart maintenance or verification notices.

Test signals: Artifact Hub repository page ownership/status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/artifacthub-repo.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/index.yaml -->
# sources/control-plane/csi-driver-nfs/charts/index.yaml

Purpose: Helm chart repository index for published `csi-driver-nfs` chart versions.

Important APIs and types: `apiVersion: v1`, entries under `csi-driver-nfs`, each with chart API version, appVersion, created timestamp, description, digest, name, URL to packaged chart tarball, and chart version. Includes current `latest` packaged as `v0.0.0`.

Control flow: Helm clients read this file to resolve chart versions and download packages from raw GitHub URLs.

State and persistence: persistent chart release metadata generated at `2026-04-17T13:22:50.057996816Z`.

Dependencies and integration: consumed by Helm repositories and Artifact Hub.

Risks: appVersion formatting changes across versions (`4.13.x` without `v`, older versions with `v`). URLs point at the `master` branch raw content, so branch rewrite or file removal would break installs.

Test signals: `helm repo update`, `helm search repo`, and chart install from each URL.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/index.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/Chart.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/Chart.yaml

Purpose: Helm chart metadata for the latest NFS CSI driver chart.

Important APIs and types: chart `apiVersion: v1`, `appVersion: latest`, description, name `csi-driver-nfs`, and version `v0.0.0`.

Control flow: Helm reads this metadata during packaging, linting, dependency resolution, and install display.

State and persistence: static chart metadata.

Dependencies and integration: used by Makefile E2E Helm install and chart index packaging.

Risks: `v0.0.0` latest chart version is suitable for moving latest but not immutable release installs. App version `latest` can obscure the exact driver image version unless values override image tags.

Test signals: Helm lint/package/install behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/Chart.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/crd-csi-snapshot.yaml

Purpose: conditionally installs CSI snapshot CRDs required for external snapshotting support.

Important APIs and types: rendered only when both `.Values.externalSnapshotter.enabled` and `.Values.externalSnapshotter.customResourceDefinitions.enabled` are true. Defines `VolumeSnapshot`, `VolumeSnapshotClass`, and `VolumeSnapshotContent` CRDs in `snapshot.storage.k8s.io`, with v1 served/storage versions and deprecated v1beta1 schemas marked `served: false`. CRDs carry `helm.sh/resource-policy: keep`.

Control flow: Helm template emits three large CRD YAML documents. Kubernetes API server registers namespaced `VolumeSnapshot` and cluster-scoped class/content resources. Snapshot controller and CSI snapshotter sidecar then reconcile these APIs.

State and persistence: creates cluster-scoped CRDs that persist after Helm uninstall because of the keep policy. Snapshot custom resources and their status subresources become persistent Kubernetes API objects.

Dependencies and integration: integrates with `csi-snapshot-controller.yaml`, controller sidecar snapshotter in `csi-nfs-controller.yaml`, and external-snapshotter CRD schemas.

Risks: CRDs are large copied schemas and can drift from external-snapshotter releases. Helm does not manage CRD upgrades cleanly, and keep policy leaves resources behind. v1beta1 is present but not served, which can break old clients expecting beta APIs.

Test signals: Helm render/install, `kubectl get crd volumesnapshots.snapshot.storage.k8s.io`, snapshot controller readiness, and snapshot E2E tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/crd-csi-snapshot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-controller.yaml

Purpose: Helm template for the NFS CSI controller Deployment.

Important APIs and types: creates an `apps/v1` Deployment with configurable name, namespace, replicas, strategy, affinity, node selectors, tolerations, priority class, service account, and resources. Containers include `csi-provisioner`, `csi-resizer`, optional `csi-snapshotter`, `liveness-probe`, and privileged `nfs`.

Control flow: sidecars talk to `/csi/csi.sock` in an `emptyDir` shared with the NFS driver container. Provisioner and resizer use leader election in the release namespace and disable `VolumeAttributesClass`. The NFS container runs with host networking, mounts kubelet pods directory bidirectionally, exposes liveness, and receives controller settings for mount permissions, working mount dir, delete policy, tar-based snapshots, and compression.

State and persistence: creates Kubernetes Deployment/Pods; uses hostPath `kubeletDir/pods` for mount propagation and an in-pod socket `emptyDir`.

Dependencies and integration: depends on service account/RBAC templates outside this subset, image values, kubelet directory values, CSI sidecars, and the NFS plugin binary image.

Risks: controller hostNetwork and privileged `SYS_ADMIN` are high privilege but needed for NFS mount operations. Affinity logic uses templated string inspection for `nodeSelectorTerms`, which can be brittle. Long sidecar timeouts may delay failure surfacing.

Test signals: Helm install, Deployment rollout, sidecar leader election, PVC provisioning/resizing/snapshot tests, and liveness probe health.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

Purpose: registers the NFS CSI driver with Kubernetes through a `CSIDriver` object.

Important APIs and types: creates `storage.k8s.io/v1` `CSIDriver` named `.Values.driver.name`, sets `attachRequired: false`, always enables `Persistent` lifecycle mode, conditionally enables `Ephemeral`, and conditionally sets `fsGroupPolicy: File`.

Control flow: Kubernetes storage components read this object to understand attach behavior, inline volume support, and fsGroup handling.

State and persistence: creates a cluster-scoped CSIDriver object.

Dependencies and integration: must match the `--drivername` used by controller and node plugin pods and any StorageClass/SnapshotClass templates.

Risks: driver name mismatch breaks provisioning and node registration. Enabling inline volume or fsGroup policy depends on cluster version support and driver implementation behavior.

Test signals: `kubectl get csidriver`, successful pod inline volumes, PVC mount behavior, and fsGroup E2E.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-node.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-node.yaml

Purpose: Helm template for the NFS CSI node DaemonSet that registers the driver and performs node-side mounts.

Important APIs and types: creates an `apps/v1` DaemonSet with configurable update strategy, node placement, service account, priority, resources, and image values. Containers are `liveness-probe`, `node-driver-registrar`, and privileged `nfs`. Optional host mount option propagation mounts `/etc/nfsmount.conf` and `/etc/nfsmount.conf.d`.

Control flow: the NFS driver listens on a hostPath CSI socket under `.Values.kubeletDir/plugins/csi-nfsplugin`; the registrar publishes that socket via kubelet plugin registration path. The driver mounts kubelet pods directory with bidirectional propagation and reports liveness on the configured port. Host networking is enabled to preserve NFS connections.

State and persistence: creates host directories under kubelet plugin and plugin registry paths, mounts host pods directory, and optionally host NFS config files. The DaemonSet persists one pod per eligible Linux node.

Dependencies and integration: depends on kubelet plugin registration, RBAC/service account, image values, node OS selectors, and host NFS utilities in the container image.

Risks: privileged `SYS_ADMIN` and hostPath mounts create a broad node security boundary. Incorrect `kubeletDir` breaks registration or mount propagation. Host mount option propagation may create files/directories on the host.

Test signals: DaemonSet rollout, node-driver-registrar health, `CSINode` driver entries, pod volume mounts, and liveness probes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-nfs-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
# sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-snapshot-controller.yaml

Purpose: conditionally deploys the external snapshot-controller used for CSI snapshot lifecycle reconciliation.

Important APIs and types: rendered when `.Values.externalSnapshotter.enabled` is true. Creates an `apps/v1` Deployment with configurable name, replicas, labels, annotations, priority, resources, image, and service account. Uses leader election in the release namespace and `minReadySeconds: 15`.

Control flow: controller pod runs the snapshot-controller image, watches snapshot CRDs, and coordinates `VolumeSnapshot`/`VolumeSnapshotContent` lifecycle independently of the NFS controller sidecar snapshotter.

State and persistence: creates Deployment/Pods and leader-election state in Kubernetes. It manages snapshot API objects created by users.

Dependencies and integration: requires snapshot CRDs, RBAC/service account templates, image values, and optional controller affinity/tolerations inherited from chart values.

Risks: the template reuses `.Values.controller.affinity`, `runOnControlPlane`, `runOnMaster`, and tolerations rather than externalSnapshotter-specific placement values, which couples controller placement settings. If CRDs are disabled or already incompatible, pods may fail readiness.

Test signals: Deployment rollout, snapshot-controller logs, CRD availability, and snapshot create/delete E2E.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-nfs/charts/latest/csi-driver-nfs/templates/csi-snapshot-controller.yaml -->
