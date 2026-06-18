# Research: subset-b-000386

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/prow.sh -->
# sources/control-plane/external-snapshotter/release-tools/prow.sh

## Purpose
`prow.sh` is the shared Kubernetes CSI release-tools Prow entrypoint for build, unit, e2e, sanity, kind-cluster, snapshot-controller, and cloud-build workflows. It is intended to be imported or symlinked by CSI repositories, with extensive `CSI_PROW_*` configuration variables allowing each repo or job to tune Kubernetes, Go, kind, driver, deployment, test-selection, canary image, and artifact behavior.

## Important APIs, Types, and Functions
The script is a Bash API surface built around `configvar`, `get_versioned_variable`, `version_to_git`, `tests_enabled`, `tests_need_kind`, `regex_join`, `ensure_paths`, `run`, `run_with_go`, `install_kind`, `install_ginkgo`, `install_dep`, `git_checkout`, `git_clone`, `go_version_for_kubernetes`, `start_cluster`, `delete_cluster_inside_prow_job`, `find_deployment`, `install_csi_driver`, `install_snapshot_crds`, `install_snapshot_controller`, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `install_e2e`, `install_sanity`, `run_e2e`, `run_sanity`, `make_test_to_junit`, `version_gt`, `main`, and `gcr_cloud_build`. Its public variables include `CSI_PROW_BUILD_PLATFORMS`, `CSI_PROW_GO_VERSION_BUILD`, `CSI_PROW_KUBERNETES_VERSION`, `CSI_PROW_KIND_VERSION`, `CSI_PROW_KIND_IMAGES`, `CSI_PROW_DRIVER_*`, `CSI_PROW_E2E_*`, `CSI_PROW_SANITY_*`, `CSI_SNAPSHOTTER_VERSION`, and `CSI_PROW_TESTS`.

## Control Flow, State, and Persistence
At load time the script computes `RELEASE_TOOLS_ROOT`, `REPO_DIR`, Kubernetes version suffixes, and defaulted config variables. `main` creates a work tree under `$GOPATH/pkg/csiprow.*`, prepares `ARTIFACTS` and a private `bin`, builds repository binaries and images when enabled, optionally runs unit tests through `make_test_to_junit`, installs kind, tags local component images as `csiprow`, starts non-alpha and alpha kind clusters as needed, installs snapshot CRDs/controller, deploys the CSI driver, runs sanity, parallel, serial, feature-focused, alpha, and sidecar e2e suites, exports cluster logs in Prow, merges JUnit files with `filter-junit.go`, and returns accumulated failure state. State persists mostly in temporary work directories, `$ARTIFACTS`, Docker/kind images, KUBECONFIG, generated helper scripts for csi-sanity, and JUnit XML. `gcr_cloud_build` is a separate callable path for multiarch image publishing.

## Dependencies and Integration Points
The script integrates with Prow job variables (`JOB_NAME`, `JOB_TYPE`, `PULL_BASE_SHA`, `ARTIFACTS`), Go toolchains via `GOTOOLCHAIN`, Kubernetes source builds, `kind`, Docker, `kubectl`, `ginkgo`, `dep`, `curl`, `git`, repository `Makefile` targets (`all`, `test`, `container`, `push-multiarch`), CSI hostpath deployment conventions, external-snapshotter CRDs/controller manifests, Kubernetes e2e.test, csi-test/csi-sanity, and GCR cloud build credentials. It also expects top-level repos to expose deployment directories and `CMDS` variables in the Kubernetes CSI release-tools style.

## Risks and Test Signals
Risks include fragile Bash word splitting for image/deployment env, mutable global variables, dependency on network downloads and upstream release URLs, kind-image/Kubernetes-version drift, assumptions about `Makefile` `CMDS`, job-specific behavior when `$JOB_NAME` is absent, stale or missing `test-driver.yaml`, sed-based YAML image rewriting, and long-running cluster cleanup failures. Test signals are successful `make all`, `make -k test` conversion to JUnit, `make container`, kind creation, snapshot CRD/controller readiness loops, csi-sanity JUnit, ginkgo JUnit after filtering, exported cluster logs, and final `junit_final.xml`.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/pull-test.sh -->
# sources/control-plane/external-snapshotter/release-tools/pull-test.sh

## Purpose
`pull-test.sh` validates changes to `csi-release-tools` by importing the current checkout into another repository through `git subtree pull` and then running that repository's `.prow.sh`. It is designed for presubmit Prow jobs against release-tools itself.

## Important APIs, Types, and Functions
The script has no functions; execution is linear under `set -ex`. Key inputs are `PULL_TEST_REPO_DIR` and the current working directory as `CSI_RELEASE_TOOLS_DIR`. It sets and exports `GIT_NO_LAZY_FETCH=0` to work around blobless Prow clones.

## Control Flow, State, and Persistence
It records the release-tools checkout path, changes to `$PULL_TEST_REPO_DIR`, hard-resets that worktree, performs `git subtree pull --squash --prefix=release-tools "$CSI_RELEASE_TOOLS_DIR" master`, prints the last two commits, and `exec`s `./.prow.sh`. Persistent state is the modified test repo working tree and new subtree commit produced during the job.

## Dependencies and Integration Points
It depends on Git subtree support, Prow checkout conventions, a configured test repository in `$PULL_TEST_REPO_DIR`, and a runnable `.prow.sh` in that repository. It is tightly coupled to the release-tools subtree prefix being `release-tools`.

## Risks and Test Signals
The hard reset is destructive to the target test repo worktree, appropriate only in disposable CI. The script assumes the current release-tools checkout can be fetched as a git remote and that `master` is the expected subtree branch. Signals are a successful subtree pull, `git log -n2`, and whatever the downstream `.prow.sh` reports.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/update-vendor.sh -->
# sources/control-plane/external-snapshotter/release-tools/update-vendor.sh

## Purpose
`update-vendor.sh` regenerates dependency lock/vendor state for repos that either still use `dep` or use Go modules. It is a developer/CI helper for keeping vendored dependencies synchronized.

## Important APIs, Types, and Functions
The script has a simple top-level branch on repository files: if `Gopkg.toml` exists, it runs `dep ensure`; if `go.mod` exists, it runs `release-tools/verify-go-version.sh go`, then `GO111MODULE=on go mod tidy` and `GO111MODULE=on go mod vendor`.

## Control Flow, State, and Persistence
There is no cleanup or temporary state. It mutates dependency files and the `vendor/` tree in place through the selected dependency manager.

## Dependencies and Integration Points
It depends on `dep` for legacy projects, Go modules for modern projects, the repository-local `release-tools/verify-go-version.sh`, and a working `go` binary. It is meant to be invoked from a repository root where `release-tools` is available as a subtree.

## Risks and Test Signals
Risks are broad workspace churn from `go mod tidy/vendor`, environment-sensitive module resolution, and missing Go version compatibility. Test signals are a clean command exit plus subsequent `git diff` review or `verify-vendor.sh` showing no dependency drift.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/util.sh -->
# sources/control-plane/external-snapshotter/release-tools/util.sh

## Purpose
`util.sh` provides small Bash utility functions shared by release-tools verification scripts, mostly copied from Kubernetes helper conventions. It also centralizes ANSI color constants while marking them as intentionally sourced variables for shellcheck.

## Important APIs, Types, and Functions
Functions are `kube::util::sourced_variable`, `kube::util::sortable_date`, `kube::util::array_contains`, `kube::util::trap_add`, `kube::util::download_file`, `kube::util::wait-for-jobs`, `kube::util::join`, and `kube::util::check-file-in-alphabetical-order`. Constants are `color_start`, `color_red`, `color_yellow`, `color_green`, `color_blue`, `color_cyan`, and `color_norm`.

## Control Flow, State, and Persistence
The file is intended to be sourced. It mutates shell process state by defining functions, declaring readonly color variables once, and allowing callers to append trap handlers via `kube::util::trap_add`. `download_file` removes and rewrites a destination path, retrying curl up to five times. `wait-for-jobs` waits on all current background jobs and returns a failure count.

## Dependencies and Integration Points
Dependencies include Bash, `date`, `trap`, `awk`, `curl`, `seq`, `sleep`, `jobs`, `wait`, `diff`, and `sort`. `verify-shellcheck.sh` sources this file for trap composition and utilities.

## Risks and Test Signals
Risks include trap-command quoting complexity, Bash-only constructs, `download_file` deleting the destination before a successful replacement, and `wait-for-jobs` waiting for all shell jobs rather than a scoped list. Test signals are shellcheck coverage and successful use by scripts that source it, especially cleanup traps and alphabetized-file checks.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-boilerplate.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-boilerplate.sh

## Purpose
`verify-boilerplate.sh` enforces Kubernetes license/header boilerplate across a repository by delegating the actual scan to `boilerplate/boilerplate.py`.

## Important APIs, Types, and Functions
The script sets `errexit`, `nounset`, and `pipefail`, resolves `TOOLS`, `ROOT`, and `boiler`, and uses `mapfile -t files_need_boilerplate < <("${boiler}" --rootdir="${ROOT}" --verbose)`. It defines a `cleanup` trap that removes a temporary file, although that file is not used by the final check.

## Control Flow, State, and Persistence
It ensures a `python` command exists by installing an alternatives link to Python 3 when missing, resolves the target root, runs the boilerplate scanner, prints each offending file, exits 1 on any violation, and prints `Done` otherwise. Persistent side effects can include modifying `/usr/bin/python` alternatives when run with sufficient privilege.

## Dependencies and Integration Points
It depends on Bash, Python, `update-alternatives`, the release-tools `boilerplate.py`, and repository source files. It is normally called from `make verify` or release-tools CI.

## Risks and Test Signals
Risks include requiring root privileges for `update-alternatives`, a cleanup trap declared before function definition but valid at exit time, and relying entirely on `boilerplate.py` for file filtering. Test signals are zero files returned by the scanner and the `Done` message.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-go-version.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-go-version.sh

## Purpose
`verify-go-version.sh` warns when a provided Go binary's major.minor version differs from the release-tools configured build version. It is advisory rather than failing.

## Important APIs, Types, and Functions
The script accepts one argument, the Go binary path/name. It defines `die`, parses `$("$GO" version)` with `sed`, and obtains the expected version by sourcing `release-tools/prow.sh` and echoing `CSI_PROW_GO_VERSION_BUILD`.

## Control Flow, State, and Persistence
If no Go binary argument is supplied or `go version` fails, it exits 1. Otherwise it compares `majorminor` against the expected release-tools build version and prints a warning block on mismatch. It does not mutate files or exit nonzero for mismatch.

## Dependencies and Integration Points
It depends on `release-tools/prow.sh` being available relative to the current working directory, a working Go binary, and shell sourcing. `update-vendor.sh` invokes it before module tidy/vendor operations.

## Risks and Test Signals
Risks include path sensitivity because it sources `release-tools/prow.sh` rather than the script's own directory, and parsing failures if `go version` output changes. The signal is a visible warning when local Go differs from CI's configured Go version.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-go-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-logcheck.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-logcheck.sh

## Purpose
`verify-logcheck.sh` installs and runs Kubernetes `logcheck` to verify contextual klog usage in Go code.

## Important APIs, Types, and Functions
It accepts an optional `LOGCHECK_VERSION` argument, defaults to `0.10.0`, resolves `CSI_LIB_UTIL_ROOT` as the parent of release-tools, creates `CSI_LIB_UTIL_TEMP`, installs `sigs.k8s.io/logtools/logcheck@v${LOGCHECK_VERSION}` with `go install`, and runs `logcheck -check-contextual -check-with-helpers "${CSI_LIB_UTIL_ROOT}/..."`.

## Control Flow, State, and Persistence
The script exits on errors and removes its temporary install directory via trap. It does not persist tool binaries in the repository; all state is temporary except Go module cache downloads.

## Dependencies and Integration Points
It depends on Bash, Go module installation, the `sigs.k8s.io/logtools/logcheck` module, and repository Go packages. It integrates with verification targets that enforce klog contextual logging conventions.

## Risks and Test Signals
Risks include network/module proxy failure, version drift of logcheck rules, and scanning too broad a package tree when vendored or generated Go is present under the parent root. Signals are the install log and a clean logcheck exit.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-logcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-shellcheck.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-shellcheck.sh

## Purpose
`verify-shellcheck.sh` lints repository shell scripts with a pinned ShellCheck version, using either a host binary or a pinned Docker image.

## Important APIs, Types, and Functions
Important functions are `join_by`, `create_container`, and `remove_container`. It sources `util.sh`, sets `SHELLCHECK_VERSION=0.6.0`, `SHELLCHECK_IMAGE` with digest, `SHELLCHECK_CONTAINER=k8s-shellcheck`, disables rules `SC1090` and `SC2230`, discovers `*.sh` files excluding `_`, `.git`, and `vendor` paths and git-ignored files, then runs shellcheck on each script.

## Control Flow, State, and Persistence
The script changes to the target root, builds `all_shell_scripts`, detects whether the host ShellCheck exactly matches the pinned version, otherwise starts a long-lived Docker container with the root mounted and registers cleanup through `kube::util::trap_add`. It collects lint output in an array, prints success when empty, or prints all errors and exits false.

## Dependencies and Integration Points
It depends on Bash, Docker when the host ShellCheck version is absent or different, `git check-ignore`, `find`, and the pinned shellcheck image. It integrates with release-tools `make verify` style checks and uses `util.sh` cleanup helpers.

## Risks and Test Signals
Risks include Docker availability, a fixed container name colliding with concurrent runs, old ShellCheck rules missing modern issues, and script discovery excluding only some generated/cache paths. Signals are per-script lint output or the success message stating all shell files pass lint.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-spelling.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-spelling.sh

## Purpose
`verify-spelling.sh` runs `misspell` over tracked repository files, excluding vendor, to catch common spelling mistakes.

## Important APIs, Types, and Functions
It pins `TOOL_VERSION=v0.3.4`, resolves `TOOLS` and `ROOT`, creates `TMP_DIR`, defines `exitHandler`, installs `github.com/client9/misspell/cmd/misspell@${TOOL_VERSION}` into the temp dir if `misspell` is missing, and writes scanner output to `errors.log`.

## Control Flow, State, and Persistence
The script creates a temporary directory, optionally installs misspell there, changes to `ROOT`, runs `git ls-files | grep -v vendor | xargs misspell`, prefixes errors for CI visibility, sets `RES=1` when the log is non-empty, and exits with that result. It cleans temporary state on exit.

## Dependencies and Integration Points
It depends on Bash, Go for on-demand tool install, Git tracked files, `grep`, `xargs`, and misspell. It integrates with repository verification targets.

## Risks and Test Signals
Risks include false positives, inadequate `grep -v vendor` filtering for paths containing the word vendor, unquoted xargs behavior for unusual filenames, and network failure during tool install. Signals are `error:` lines for misspell findings or a zero exit with an empty error log.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-subtree.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-subtree.sh

## Purpose
`verify-subtree.sh` checks that a directory managed by `git subtree` contains no local non-upstream commits outside subtree merge commits.

## Important APIs, Types, and Functions
It is a POSIX `sh -e` script with one required argument, `DIR`. The key command is `git log -n1 --remove-empty --format=format:%H --no-merges -- "$DIR"` to detect non-merge commits touching the directory.

## Control Flow, State, and Persistence
The script validates the argument, computes `REV`, and if non-empty prints a failure header plus `git log --no-merges -- "$DIR"` before exiting 1. If empty, it prints that the directory is a clean copy of upstream. It does not mutate state.

## Dependencies and Integration Points
It depends on Git history preserving subtree merge commits and on the release-tools convention that subtree updates are merge commits while local modifications are ordinary commits. It is suitable for repositories that import release-tools as a subtree.

## Risks and Test Signals
Risks include false negatives if developers modify subtree files inside merge commits, false positives after history rewriting, and dependence on local clone history depth. Signals are a clean-copy message or a log of offending non-merge commits.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-vendor.sh -->
# sources/control-plane/external-snapshotter/release-tools/verify-vendor.sh

## Purpose
`verify-vendor.sh` verifies that Go module files and, when present, the `vendor/` directory are up to date with `go mod tidy` and `go mod vendor`.

## Important APIs, Types, and Functions
The script runs only when `go.mod` exists. In Prow presubmit jobs it can skip dependency checks when the diff does not touch `go.mod`, `go.sum`, `vendor`, `release-tools`, or Go import blocks. Otherwise it runs `GO111MODULE=on go mod tidy`, checks `git status --porcelain -- go.mod go.sum`, optionally runs `go mod vendor`, then checks `git status --porcelain -- vendor`.

## Control Flow, State, and Persistence
The script mutates the worktree during verification, then fails if the mutation produced differences. It prints diffs/status for stale `go.mod`, `go.sum`, or `vendor` and exits nonzero. In no-vendor repos it only validates module files.

## Dependencies and Integration Points
It depends on Bash, Go modules, Git, and Prow variables `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA` for the skip optimization. It is part of release-tools verification and pairs with `update-vendor.sh`.

## Risks and Test Signals
Risks include skip logic missing dependency-affecting changes, failures in shallow or non-Prow clones where base SHA is unavailable, and environment-specific module tidy output. Signals are clean `git status` for module/vendor paths and success messages for up-to-date dependencies.
<!-- END_FILE_RESEARCH: sources/control-plane/external-snapshotter/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/check-latest-image-required.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/check-latest-image-required.sh

## Purpose
`check-latest-image-required.sh` decides whether the JuiceFS CSI Driver `latest` Docker image should be rebuilt/pushed by comparing upstream JuiceFS release time, CSI driver release time, and Docker Hub `latest` image update time.

## Important APIs, Types, and Functions
Functions are `image_update_required` and `main`. It queries GitHub release APIs with `curl`, parses JSON with `jq`, derives the latest CSI driver tag from `git describe --tags --match 'v*' | grep -oE`, queries Docker Hub tag metadata, converts timestamps with `date -d`, and prints `yes` or `no`.

## Control Flow, State, and Persistence
`image_update_required` exits on missing upstream/CSI release tags, returns true if any publication timestamp is missing, and otherwise returns true when Docker Hub `latest` is older than or equal to either latest JuiceFS or latest CSI driver release. `main` maps return status to `yes`/`no`. It has no persistent local state.

## Dependencies and Integration Points
It depends on network access to GitHub and Docker Hub, `jq`, GNU `date`, Git tags in the checked-out repository, and Docker Hub's `last_updated` field. `latest-ignore.yaml` invokes it inside a GitHub Actions workflow to gate `make image-latest` and `make push-latest`.

## Risks and Test Signals
Risks include API rate limits, tag regex not matching versions with zero minor components, timestamp parse differences outside GNU date, Docker Hub eventual consistency, and returning `yes` on partial metadata. Signals are the printed `IMAGE_REQUIRED` value in the workflow and successful conditional image build/push.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/check-latest-image-required.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/config.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/config.py

## Purpose
`config.py` centralizes environment-derived settings, constants, logging, and global cleanup registries for JuiceFS CSI Driver GitHub CI e2e scripts.

## Important APIs, Types, and Functions
It exports constants such as `KUBE_SYSTEM`, `META_URL`, `ACCESS_KEY`, `SECRET_KEY`, `STORAGE`, `BUCKET`, `TOKEN`, `JUICEFS_MODE`, `IS_CE`, `Beta`, `MOUNT_MODE`, `RESOURCE_PREFIX`, `IN_CCI`, `CCI_APP_IMAGE`, `CCI_MOUNT_IMAGE`, `IN_VCI`, `GLOBAL_MOUNTPOINT`, `SECRET_NAME`, `STORAGECLASS_NAME`, `FS_NAME`, and `CONFIG_NAME`. It configures logger `LOG`. Mutable lists `SECRETs`, `STORAGECLASSs`, `DEPLOYMENTs`, `JOBs`, `PODS`, `PVCs`, and `PVs` track created Kubernetes objects for test cleanup.

## Control Flow, State, and Persistence
All behavior occurs at import time by reading environment variables and configuring logging. There is no file persistence; state is in module globals shared by `model.py`, `util.py`, and tests. `RESOURCE_PREFIX` combines mount mode and JuiceFS mode, so all model-created resources get predictable per-mode names.

## Dependencies and Integration Points
It depends on Python `os` and `logging`, the CI environment, JuiceFS credentials/secrets, and optional CCI/VCI settings. It is imported by `model.py`, `e2e-test.py`, and related test helpers.

## Risks and Test Signals
Risks include importing with missing environment variables producing empty credential fields, `TEST_MODE` access without a default causing errors if unset, and module-level mutable lists being shared across tests. Signals are resource names and logs reflecting expected mode, plus successful cleanup by consumers of the global lists.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/deploy-csi-in-k8s.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/deploy-csi-in-k8s.sh

## Purpose
`deploy-csi-in-k8s.sh` installs system storage dependencies and deploys the JuiceFS CSI Driver into a MicroK8s cluster for different CI deployment modes: normal CSI, without-kubelet, webhook, and webhook-provisioner.

## Important APIs, Types, and Functions
Functions are `main`, `prepare_pkg`, `deploy_csi`, `deploy_csi_without_kubelet`, `deploy_webhook`, and `deploy_webhook_provisioner`. Inputs are positional `deployMode` and `withoutKubelet`, plus environment variables `GITHUB_WORKSPACE` and `dev_tag`. It uses `kustomize build`, `sed` image/path substitutions, `microk8s.kubectl apply/delete/label/get/describe/cp`, and helper scripts `hack/update_install_script.sh` and `scripts/juicefs-csi-webhook-install.sh`.

## Control Flow, State, and Persistence
`main` always runs `prepare_pkg`, then chooses deployment path. `prepare_pkg` installs Ceph, FoundationDB, and GlusterFS packages via apt/wget/dpkg. Non-webhook paths disable namespace injection, delete previous webhook YAML, apply kustomized manifests, poll up to roughly five minutes for four ready CSI pods, export `JUICEFS_CSI_NODE_POD` into `$GITHUB_ENV`, and copy `juicefs` binaries from the plugin container to host paths. Webhook paths enable injection, remove the node DaemonSet if present, generate or overwrite `deploy/webhook.yaml`, update install scripts, apply generated webhook manifests, wait for controller readiness, and copy binaries from the controller pod.

## Dependencies and Integration Points
It depends on Ubuntu apt, root/sudo, MicroK8s, kustomize, `bc`, repository deploy overlays under `deploy/kubernetes/csi-ci`, GitHub Actions env files, JuiceFS image naming, dashboard image naming, and kubelet path replacement for MicroK8s. It integrates with later e2e Python tests by deploying the driver and making the `juicefs` CLI available on the host.

## Risks and Test Signals
Risks include unquoted shell variables, deprecated `apt-key`, external package repository availability, a likely typo `sudo mkdir mkdir`, brittle readiness counting via `kubectl get pods | awk '{print $2}' | tr '/' '-' | bc`, hard-coded expected pod/container counts, and mutation of `deploy/webhook.yaml`. Signals are readiness messages, described pods on timeout, copied `juicefs -V` and `/usr/bin/juicefs version`, and a populated `JUICEFS_CSI_NODE_POD`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/deploy-csi-in-k8s.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/e2e-test.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/e2e-test.py

## Purpose
`e2e-test.py` is the CI orchestrator for JuiceFS CSI Driver e2e test cases. It loads kubeconfig, prepares a clean JuiceFS filesystem, deploys default test Secret/StorageClass, selects a test matrix based on `TEST_MODE`, and unmounts the host mountpoint afterward.

## Important APIs, Types, and Functions
The file imports many test-case functions from `test_case`, including deployment/PV/PVC, cache cleanup, delete policy, mount image, quota, expansion, multi-PVC, webhook, sidecar config, config reload, owner-reference, and controller quota tests. It imports `die`, `mount_on_host`, `umount`, `clean_juicefs_volume`, `deploy_secret_and_sc`, and `check_do_test` from `util`, plus `GLOBAL_MOUNTPOINT`, `LOG`, `IN_CCI`, and `IS_CE` from `config`.

## Control Flow, State, and Persistence
Under `__main__`, it reads `TEST_MODE` and `WITHOUT_KUBELET`. If `check_do_test()` is true, it loads kubeconfig, mounts JuiceFS on the host, cleans the test volume, deploys baseline secret/storageclass, then runs a mode-specific sequence for `pod`, `pod-mount-share`, `fs-mount-share`, `pod-provisioner`, `webhook`, `webhook-provisioner`, or `process`. It catches exceptions through `die(e)` and always unmounts `GLOBAL_MOUNTPOINT` in `finally`. Persistent effects are Kubernetes resources and JuiceFS data created by imported test cases, with cleanup delegated to those helpers.

## Dependencies and Integration Points
It depends on the Kubernetes Python client, local kubeconfig, JuiceFS host mount utilities, the `test_case` module, the model/config/util modules in the same script directory, and CI environment variables. It assumes the driver is already deployed by `deploy-csi-in-k8s.sh` and supporting services are ready from `k8s-deps.sh`.

## Risks and Test Signals
Risks include long sequential test runtime, test-order coupling through shared cluster state and cleaned filesystem, mode strings needing exact matches, skipped dynamic tests in CCI, and cleanup reliance on imported helpers. Signals are `LOG` output, exceptions passed to `die`, Kubernetes resource readiness inside individual tests, and the final host unmount.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/e2e-test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/k8s-deps.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/k8s-deps.sh

## Purpose
`k8s-deps.sh` prepares a CI host for JuiceFS CSI Driver e2e tests by installing MicroK8s, kustomize, client packages, DNS forwarding, and in-cluster Redis/MinIO services.

## Important APIs, Types, and Functions
Functions are `die`, `install_deps`, `add_kube_resolv`, `deploy_services`, `wait_for_ready`, and `main`. It pins `KUSTOMIZE_URL` to kustomize v4.2.0 and resolves `SCRIPTS_DIR` before applying `services.yaml`.

## Control Flow, State, and Persistence
`install_deps` installs apt packages and Python Kubernetes bindings, downloads kustomize to `/usr/local/bin`, installs and starts MicroK8s, enables DNS/storage/RBAC, and writes kubeconfig to `$HOME/.kube/config`. `add_kube_resolv` discovers the kube-dns service IP, writes `/etc/systemd/resolved.conf.d/microk8s.conf`, restarts systemd-resolved, and waits until host DNS resolves cluster names correctly. `deploy_services` applies `services.yaml`, and `wait_for_ready` polls Redis and MinIO pod IPs then TCP-connects to their ports.

## Dependencies and Integration Points
It depends on sudo/root, Ubuntu apt/snap, curl/tar, MicroK8s, systemd-resolved, `dig`, `nc`, `services.yaml`, Redis, MinIO, and host networking. It provides the cluster and object-store/cache backing services consumed by later deployment and e2e scripts.

## Risks and Test Signals
Risks include requiring privileged host mutation, overwriting kubeconfig permissions to 777, no explicit timeout in several wait loops, hard-coded kustomize version, MicroK8s snap availability, and DNS changes affecting the runner. Signals are kustomize version output, MicroK8s start/enable success, kube-dns resolution verification, Redis/MinIO pod IP logs, and successful TCP checks.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/k8s-deps.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/latest-ignore.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/latest-ignore.yaml

## Purpose
`latest-ignore.yaml` is a GitHub Actions workflow definition for testing the JuiceFS CSI Driver and conditionally publishing the Docker `latest` image on release creation or daily schedule.

## Important APIs, Types, and Functions
The workflow defines triggers `release: created` and cron `0 0 * * *`. Job `test` sets up Go 1.14.x, checks out code, runs `make`, `make verify`, `make test`, and `make test-sanity`. Job `publish-latest` depends on `test`, checks out full history, runs `.github/scripts/check-latest-image-required.sh`, writes `IMAGE_REQUIRED` to `$GITHUB_ENV`, and conditionally runs `make image-latest`, Docker Hub login, and `make push-latest`.

## Control Flow, State, and Persistence
Workflow state is GitHub Actions job environment and Docker credentials. `publish-latest` only builds/pushes when the helper prints `yes`; otherwise it exits after the check. The `fetch-depth: 0` checkout is required so `git describe --tags` can find release tags.

## Dependencies and Integration Points
It depends on GitHub Actions runners, `actions/setup-go@v2`, `actions/checkout@v2`, Makefile targets, Docker Hub secret `DOCKERHUB_ACCESS_TOKEN`, and `check-latest-image-required.sh`. It integrates release cadence from GitHub and Docker image publication.

## Risks and Test Signals
Risks include old action versions and Go 1.14.x, Docker password passed on command line, workflow filename suggesting ignore/legacy status, and helper-script network sensitivity. Signals are successful test job, logged `IMAGE_REQUIRED`, conditional Docker build/login/push steps, and published Docker Hub `latest`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/latest-ignore.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/model.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/model.py

## Purpose
`model.py` defines Python Kubernetes object wrappers used by JuiceFS CSI Driver e2e tests. It turns common test resources into create/delete/watch helper classes while registering created objects in global cleanup lists from `config.py`.

## Important APIs, Types, and Functions
Classes are `Secret`, `StorageClass`, `PVC`, `PV`, `Deployment`, `Job`, and `Pod`. `Secret` creates CE or EE secret data and can wait for webhook `initconfig` injection or read owner references. `StorageClass` creates a CSI storage class with JuiceFS secret refs, mount options, resource parameters, and expansion enabled. `PVC` creates claims, updates capacity, checks deletion/bind state, and resolves bound volume IDs. `PV` creates static CSI persistent volumes with `juicefs/mount-*` attributes and secret refs. `Deployment`, `Job`, and `Pod` create Ubuntu or cloud-provider app workloads that continuously or once write timestamps into mounted PVCs, with CCI/VCI labels/annotations and resources when configured.

## Control Flow, State, and Persistence
Each `create` method builds Kubernetes Python client objects and submits them to `CoreV1Api`, `StorageV1Api`, `AppsV1Api`, or `BatchV1Api`, then appends `self` to the appropriate global list (`SECRETs`, `STORAGECLASSs`, `PVCs`, `PVs`, `DEPLOYMENTs`, `JOBs`, `PODS`). Delete methods call Kubernetes delete APIs and remove the instance from the list. Watch methods use polling or `watch.Watch().stream` for secret injection, job completion, pod readiness, and pod deletion. Kubernetes cluster resources are the durable state; module globals are in-process cleanup state.

## Dependencies and Integration Points
The file depends on the Kubernetes Python client, `watch`, `ConflictError`, base64 encoding, `time`, and config globals for credentials, namespaces, resource prefixes, images, and environment mode. It is consumed by `test_case.py` and e2e orchestration to create dynamic/static volume resources and workloads against the deployed CSI driver.

## Risks and Test Signals
Risks include mutable default argument `pvcs=[]`, fragile readiness logic requiring all pod conditions true, incomplete conflict handling in `Deployment.update_replicas` if exceptions lack `reason`, no timeouts in some API reads beyond watch stream limits, base64-secret construction with empty environment values, and object-list cleanup desynchronization if Kubernetes delete fails. Signals are Kubernetes API success, owner-reference/initconfig checks, job completion, pod ready/delete watch events, PVC bound state, and PV/PVC volume-handle reads.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/services.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/services.yaml

## Purpose
`services.yaml` deploys simple Redis and MinIO dependencies into the default namespace for JuiceFS CSI Driver e2e tests.

## Important APIs, Types, and Functions
It defines two headless Services, `redis` on port 6379 selecting `app: redis-server` and `minio` on port 9000 selecting `app: minio-server`. It also defines one-replica StatefulSets `redis-server` and `minio-server`. Redis uses image `redis` with `/data` mounted from hostPath `/data/redis`; MinIO uses image `minio/minio`, args `server /data`, and hostPath `/data/minio`.

## Control Flow, State, and Persistence
Applying the YAML creates services and stateful pods. Persistence is hostPath-backed on the MicroK8s node under `/data/redis` and `/data/minio`, so data may survive pod recreation on the same runner unless the host path is cleaned.

## Dependencies and Integration Points
It depends on Kubernetes apps/v1 and core/v1 APIs, image pulls from Docker registries, writable host paths, and MicroK8s scheduling. `k8s-deps.sh` applies this file and then waits for pod IPs and TCP ports before e2e tests continue.

## Risks and Test Signals
Risks include unpinned images, no resource limits, no readiness probes, no MinIO credentials in this manifest, and hostPath state leakage between CI runs. Signals are StatefulSet pod IP assignment, TCP availability on 6379 and 9000, and service DNS resolution through the MicroK8s DNS setup.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/services.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/sync.sh -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/sync.sh

## Purpose
`sync.sh` mirrors container images to multiple Aliyun Container Registry regions under `juicedata`, with special handling for JuiceFS mount, CSI driver/dashboard, and operator images and optional multi-platform manifest creation.

## Important APIs, Types, and Functions
Functions are `sync_image`, `sync_multi_platform_image`, `parse_image_name`, and `main`. Inputs are `ACR_USERNAME`, `ACR_TOKEN`, positional `image_input`, and optional `platform`. `REGIONS` lists active Aliyun registry endpoints. It uses Docker pull/tag/push/login/manifest commands and parses image strings into registry, image, and tag.

## Control Flow, State, and Persistence
`main` parses the image, then routes known images. `mount` tags containing `latest`, `nightly`, `min`, or `std` are single-platform synced; other mount tags are synced as `amd64` and `arm64` then combined into a manifest. `juicefs-csi-driver` syncs both driver and `csi-dashboard`, using single-platform for `nightly` and multi-platform otherwise. `juicefs-operator` follows similar nightly/multi-platform logic. Other images use `platform=all` for multi-platform or single `sync_image` for a specific platform. Persistent state is pushed tags/manifests in each target registry and local Docker image cache.

## Dependencies and Integration Points
It depends on Bash arrays, Docker CLI with manifest support, ACR credentials, network access to source and target registries, and source images under Docker Hub or a parsed registry. It integrates image release pipelines with China-region registry mirrors.

## Risks and Test Signals
Risks include unquoted Docker arguments, credentials passed via `--password`, `parse_image_name` mishandling image paths with namespaces because it treats everything before the last slash as registry, ignored `platform` parameter in some special cases, no cleanup of local arch tags, and manifest creation assuming both arch pushes succeeded. Signals are per-region login/pull/tag/push logs and successful `docker manifest push`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/sync.sh -->
