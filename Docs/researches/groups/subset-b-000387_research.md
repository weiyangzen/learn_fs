# subset-b-000387 Research

Grouped research report for the requested JuiceFS CSI driver files. Each section is bounded by the required markers so reconciliation can split it into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/test_case.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/test_case.py

## Purpose
This Python module is the main end-to-end test case library for the JuiceFS CSI driver GitHub Actions jobs. It defines top-level `test_*` functions that exercise dynamic and static provisioning, mount pod lifecycle management, webhook sidecar mode, process mode, quota behavior, cache cleanup, path pattern deletion, mount image selection, config reloads, secret owner references, and release-specific compatibility checks. It is not a standalone runner; it is imported or invoked by the surrounding `.github/scripts/e2e-test.py` harness and relies on `config.py`, `model.py`, and helpers from `util.py`.

## Important APIs, Types, and Functions
The module exports 37 top-level test functions. The most important groups are:

- Basic storage path tests: `test_deployment_using_storage_rw`, `test_quota_using_storage_rw`, `test_deployment_using_storage_ro`, `test_deployment_use_pv_rw`, and `test_deployment_use_pv_ro`.
- Deletion and mount pod reference tests: `test_delete_one`, `test_delete_all`, `test_delete_pvc`, `test_dynamic_delete_pod`, `test_static_delete_pod`, `test_mountpod_recreated`.
- Multi-volume and shared mount tests: `test_multi_pvc`, `test_share_mount`, `test_webhook_two_volume`.
- Cache and quota tests: `test_cache_client_conf`, `test_static_cache_clean_upon_umount`, `test_dynamic_cache_clean_upon_umount`, `test_dynamic_expand`, `test_set_quota_in_controller`.
- PV mutation and webhook equivalents: `test_deployment_dynamic_patch_pv`, `test_deployment_static_patch_pv`, `test_deployment_dynamic_patch_pv_with_webhook`, `test_deployment_static_patch_pv_with_webhook`.
- Image and sidecar tests: `test_dynamic_mount_image`, `test_static_mount_image`, `test_dynamic_mount_image_with_webhook`, `test_static_mount_image_with_webhook`, `test_sidecar_config_with_node_selector`.
- Config and ownership tests: `test_config`, `test_recreate_mountpod_with_template_config`, `test_recreate_mountpod_reload_config`, `test_secret_has_owner_reference`, `test_secret_has_owner_reference_shared_mount`.

The tests depend heavily on `model.PVC`, `PV`, `Pod`, `StorageClass`, `Deployment`, `Job`, and `Secret`, which encapsulate Kubernetes object creation, deletion, polling, and inspection. Helper functions imported from `util.py` provide mount-point polling, mount-pod lookup, readiness checks, quota checks, config map patching, and random name generation.

## Control Flow
Each test follows a create-wait-assert-cleanup pattern. It creates Kubernetes resources through model wrappers, waits for binding or readiness with bounded loops, validates filesystem state through the host JuiceFS mount at `GLOBAL_MOUNTPOINT`, and deletes resources at the end. Several tests branch on `MOUNT_MODE`, `TEST_MODE`, `IS_CE`, `IN_CCI`, and feature probes such as `is_quota_supported()`.

Dynamic PVC tests create a StorageClass-backed PVC and derive the expected volume id from the bound PV. Static tests create PVs directly with `volume_handle`, then bind PVCs to those PVs. Webhook-mode tests inspect injected `jfs-mount` containers or init containers, while pod mount mode tests inspect separate mount pods in `KUBE_SYSTEM`. Some tests mutate PV mount options, delete application pods, and verify that newly created mount pods or sidecars pick up updated `subdir` options.

Config tests patch the CSI driver ConfigMap through `update_config`, annotate controller or node pods with `updatedAt` to force refresh, then create PVCs and application pods to verify the resulting mount pod templates. Upgrade-sensitive tests recreate mount pods and compare labels, host namespace settings, mount images, and resource requests against the updated config.

## State and Persistence Behavior
The tests create real Kubernetes objects and real files in the JuiceFS filesystem. Persistent state includes PV/PVC bindings, Jobs, Secrets, StorageClasses, mount pods, per-volume cache directories, and ConfigMap data. Many tests rely on global model lists such as `PVs` for teardown coordination. The module frequently validates deletion by polling for Kubernetes 404s, empty cache directories, vanished subpaths under `GLOBAL_MOUNTPOINT`, or the absence of mount pods.

The test suite mutates global cluster configuration in `test_config`, `test_sidecar_config_with_node_selector`, and the mount pod recreate tests; those tests reset the config back to `{}` afterward. Several tests depend on a host-mounted JuiceFS filesystem and assume the CSI driver, microk8s kubelet path, MinIO, Redis, and optional EE token credentials were installed by earlier CI setup steps.

## Dependencies and Integration Points
Direct dependencies include the Kubernetes Python client, `subprocess` calls to `kubectl`, host filesystem operations through `pathlib` and `os`, and helper/model modules in `.github/scripts`. It integrates with GitHub Actions workflows `go.yaml`, `nightly.yaml`, `release_check_ce.yaml`, and `release_check_ee.yaml` through the E2E runner. It also integrates indirectly with CSI driver behavior implemented in Go controllers, mount pods, webhook sidecar injection, volume deletion jobs, and ConfigMap-driven mount pod patching.

## Risks
The tests are slow and environment-sensitive: most checks use fixed loops with sleeps and can fail under overloaded runners. Some paths are microk8s-specific, especially `/var/snap/microk8s/common/var/lib/kubelet/...`, so portability to kubeadm or managed clusters is limited. Cleanup is mostly manual per test; failures before cleanup can leave PVs, PVCs, mount pods, config changes, or filesystem content behind until global teardown runs. Several assertions assume one pod or one mount pod exists, which can be brittle in shared-mount modes. There is also a likely logic bug in owner-reference checks that uses `if len(owner_references) != 1 and owner_references[0].uid != ...`; with zero references this can index out of range only if the first condition is false, and semantically it should likely be `or`.

## Test Signals
This file is itself the E2E test signal. Passing it proves CSI provisioning, node mount, webhook injection, cache cleanup, quota, volume expansion, deletion, and config reload behavior against a live Kubernetes cluster. Failure diagnostics are often collected through `kubectl get`, `kubectl logs`, and helper functions in `util.py`, but this file does not define unit tests for its own helper logic.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/test_case.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/util.py -->
# sources/control-plane/juicefs-csi-driver/.github/scripts/util.py

## Purpose
This module provides shared utility functions for the Python E2E tests. It handles feature gating, failure diagnostics, host-side JuiceFS mount and unmount, mount-point polling, quota assertions, mount pod discovery, mount pod reference counting, test resource deployment and teardown, filesystem cleanup, random naming, JuiceFS UUID lookup, quota feature probing, and CSI driver ConfigMap read/write operations.

## Important APIs, Types, and Functions
`check_do_test()` gates EE tests on `TOKEN`. `die(e)` emits CSI node/controller logs and cluster object state before raising. `mount_on_host()` formats/authenticates and mounts CE or EE JuiceFS on the host. `check_mount_point()`, `wait_dir_empty()`, and `wait_dir_not_empty()` poll filesystem state. `check_quota()` and `check_quota_in_host()` parse `df -h` output from pods or host paths. `get_only_mount_pod_name()`, `wait_get_only_mount_pod_name()`, `get_mount_pods()`, and `get_voldel_job()` query Kubernetes by labels or generated job names. `check_pod_ready()` and `check_mount_pod_refs()` implement readiness and reference assertions. `deploy_secret_and_sc()`, `tear_down()`, and `clean_juicefs_volume()` manage shared test resources. `get_config()` and `update_config()` read and patch the CSI ConfigMap YAML.

## Control Flow
Most helpers are polling loops with explicit timeouts. Mount-pod discovery uses `client.CoreV1Api().list_namespaced_pod` with `volume-id=<id>` and filters out terminating pods. Volume-delete job lookup hashes the volume id with SHA-256, truncates to match the job naming convention, then polls `BatchV1Api.read_namespaced_job`. Quota checks repeatedly run `df -h`, parse lines beginning with `JuiceFS:`, and compare the reported size to the expected value.

Host mounting branches on CE versus EE: CE runs `juicefs format` and `juicefs mount` against `META_URL`, while EE runs `juicefs auth` and mounts by secret/name. Teardown walks the global model registries in a fixed order, deleting Pods, Deployments, PVCs, StorageClasses, PVs, Secrets, and then filesystem contents.

## State and Persistence Behavior
The module creates and deletes cluster resources and can mutate the CSI ConfigMap. It also touches host mount state through `mount_on_host()` and `umount()`, and filesystem contents through `clean_juicefs_volume()`. Cleanup preserves recent EE files for up to three days but removes all visible CE files with `juicefs rmr`.

## Dependencies and Integration Points
Dependencies include `kubernetes.client`, `subprocess`, `yaml`, host JuiceFS binaries under `/usr/local/bin/juicefs` or `/usr/bin/juicefs`, `kubectl`, global constants from `config.py`, and model registries from `model.py`. It integrates directly with the E2E test cases and with Kubernetes APIs for Pods, Jobs, ConfigMaps, and events.

## Risks
Many subprocess calls use `sudo` and assume exact binary paths and cluster tooling. Some commands use `shell=True` for wildcard cleanup. Polling timeouts are fixed and can be flaky under slow CI. `check_mount_pod_refs()` assumes annotation values containing `/var/lib/kubelet/pods` represent mount references, which may not cover all kubelet path variants. `wait_get_only_mount_pod_name()` returns `None` silently on timeout instead of raising.

## Test Signals
The helper functions are validated indirectly by every E2E run. There are no standalone unit tests in this file, so helper regressions usually appear as environment-level E2E failures.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/scripts/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/check-doc.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/check-doc.yaml

## Purpose
This GitHub Actions workflow validates documentation-only changes on `master` pushes and pull requests. It runs markdown linting, autocorrect linting, and broken-link checks for files under `docs/` plus related documentation tooling config.

## Important Jobs and Steps
The single `check-doc` job runs on `ubuntu-latest`, checks out the repository, installs Node.js 24 with npm cache, runs `npm ci`, runs `npm run markdown-lint`, invokes `huacnlee/autocorrect-action@main` with `--lint ./docs/`, and runs `npm run check-broken-link`.

## Control Flow
Path filters limit execution to documentation and doc tooling changes. The job is linear; any lint or link-check failure fails the workflow.

## State and Persistence Behavior
The workflow does not publish artifacts or mutate repository state. Dependency state is limited to GitHub runner npm cache.

## Dependencies and Integration Points
It depends on `package.json` scripts, `.autocorrectrc`, `.markdownlint-cli2.jsonc`, and the third-party autocorrect action. It aligns with the `Makefile` `check-docs` target, which performs similar commands locally.

## Risks
The workflow pins Node to a future/latest major line (`24.x`) and uses `huacnlee/autocorrect-action@main`, so upstream changes can affect reproducibility. Path filtering means documentation generated outside `docs/` is not checked unless it matches listed paths.

## Test Signals
Passing status indicates Markdown style and link integrity for docs changes. It does not test application code.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/check-doc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/codeql-analysis.yml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/codeql-analysis.yml

## Purpose
This workflow runs GitHub CodeQL static analysis for Go code on pushes, pull requests, and a weekly schedule.

## Important Jobs and Steps
The `analyze` job requests `actions:read`, `contents:read`, and `security-events:write` permissions. It checks out code, initializes CodeQL for `go`, uses CodeQL autobuild, and runs `github/codeql-action/analyze`.

## Control Flow
Pushes to `master` run when Go files change while excluding docs and markdown-related files. Pull requests to `master` run on Go changes. A scheduled weekly run catches issues independent of recent PR path filters.

## State and Persistence Behavior
The workflow uploads CodeQL security results to GitHub code scanning. It does not change repository files.

## Dependencies and Integration Points
It depends on GitHub's CodeQL actions and the Go build being discoverable by autobuild. It complements `go.yaml` tests and `golangci` linting by providing security-oriented static analysis.

## Risks
The action versions are older major versions (`checkout@v3`, CodeQL `@v2`). Autobuild may miss custom build flags or generated assets. Path filters may skip relevant security changes outside `**.go` on PRs.

## Test Signals
The workflow emits code scanning alerts and pass/fail status for CodeQL analysis. It does not run runtime tests or E2E suites.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-ci.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-ci.yaml

## Purpose
This workflow validates dashboard frontend/backend changes. It runs pnpm dependency install, dashboard lint, and dashboard UI build for changes touching dashboard code, Dockerfiles, or Makefile targets.

## Important Jobs and Steps
The single `build` job installs pnpm 9, discovers the pnpm store path, caches it by `pnpm-lock.yaml`, installs dependencies in `dashboard-ui-v2`, runs `pnpm run lint`, and invokes `make dashboard-dist`.

## Control Flow
It triggers on pushes and pull requests to `master` with path filters for dashboard UI, `cmd/dashboard`, `pkg/dashboard`, and dashboard Docker/build files. Concurrency cancels older runs for the same workflow/ref.

## State and Persistence Behavior
Only pnpm cache state persists between runs. Build output is generated in the runner workspace but not uploaded.

## Dependencies and Integration Points
The workflow depends on pnpm, dashboard UI package scripts, and the `Makefile` `dashboard-dist` target. It is the fast CI signal for the dashboard before image workflows build and publish container images.

## Risks
The job checks dashboard UI lint/build but does not compile `cmd/dashboard` itself. A Go dashboard backend regression could be missed unless `go.yaml` also runs. The pnpm store cache is broad by OS and lock hash, which is typical but still can hide transient package registry issues.

## Test Signals
Passing status indicates the dashboard frontend lint and static build succeeded for the changed code.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-ci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-image.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-image.yaml

## Purpose
This manually dispatched workflow builds and pushes the CSI dashboard image, optionally using an operator-provided dashboard image tag.

## Important Jobs and Steps
The `publish-image` job checks out full history, installs pnpm 9, builds the dashboard UI via `make dashboard-dist`, logs into Docker Hub with `DOCKERHUB_FUSE_ACCESS_TOKEN`, sets up QEMU and Buildx, then runs `make -C docker dashboard-buildx` with `DASHBOARD_TAG` from workflow input. It opens an upterm session on failure.

## Control Flow
The workflow only runs on `workflow_dispatch`. Steps are linear; image publishing depends on successful UI build and Docker login.

## State and Persistence Behavior
The workflow publishes Docker images to external registries through Docker Hub credentials and whatever registry logic exists in the Docker Makefile. It does not write repository state.

## Dependencies and Integration Points
It integrates with `dashboard-ui-v2`, the root `Makefile`, `docker/dashboard.Dockerfile`, and Docker Buildx multi-platform build targets.

## Risks
It relies on a personal-looking Docker Hub username and secret. Failure debug via upterm exposes a live shell for up to 60 minutes and should be considered privileged. Because it is manual, it does not protect PRs by itself.

## Test Signals
Success indicates the dashboard UI can be built into a publishable image. Runtime dashboard behavior is not exercised.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/dashboard-image.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/go.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/go.yaml

## Purpose
This is the main CI workflow for Go, Python, shell, module, Docker, and Makefile changes. It builds the CSI driver, runs verification and unit/sanity tests, then runs broad CE and EE E2E matrices across mount modes with and without kubelet integration.

## Important Jobs and Steps
The `test` job sets up Go 1.25, builds with `make`, runs `make verify`, `make test`, `make test-sanity`, combines coverage, and uploads it to Codecov. `build-matrix` produces two JSON matrices: full modes (`pod`, `pod-mount-share`, `fs-mount-share`, `pod-provisioner`, `webhook`, `webhook-provisioner`, `process`) and without-kubelet modes. Four E2E jobs run CE/EE and kubelet/without-kubelet combinations. Each E2E job cleans runner disk, prepares microk8s, builds dashboard dist and dev images, deploys CSI, and runs `.github/scripts/e2e-test.py` with mode-specific environment variables.

## Control Flow
Path filters trigger CI for code and build script changes. Concurrency cancels superseded runs per ref. The matrix job fans out E2E jobs. `success-all-test` depends on CE and EE full E2E jobs and fails if the workflow conclusion action reports failure.

## State and Persistence Behavior
The workflow builds Docker images locally, imports them into microk8s or pushes/caches them depending on Makefile settings, and uses MinIO/Redis services installed by scripts. No repository files are committed, but Codecov receives coverage output.

## Dependencies and Integration Points
It depends on Go, Docker, pnpm, microk8s setup scripts, root and Docker Makefile targets, dashboard UI build, E2E Python scripts, Docker Hub or local image handling, Codecov, and secrets for EE tests. It is the main integration point for `test_case.py` and `util.py`.

## Risks
This workflow is expensive and fragile because it builds images and runs full Kubernetes E2E matrices on GitHub-hosted runners. The disk cleanup step removes large preinstalled directories, which is necessary but runner-image dependent. The `success-all-test` only needs full CE/EE E2E jobs, not the without-kubelet jobs, so it may not aggregate every matrix lane. Action versions are mixed and some are old.

## Test Signals
Passing `test` gives build, verify, unit, sanity, and coverage signals. Passing E2E jobs gives the strongest signal that CSI controller/node/webhook/process modes work in microk8s for CE and EE.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/go.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/juicefs-image.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/juicefs-image.yaml

## Purpose
This workflow builds and publishes JuiceFS mount images for CE and EE. It can be manually dispatched with explicit CE or EE package inputs and also runs daily.

## Important Jobs and Steps
`publish-ce-mount-image` discovers or accepts a CE JuiceFS version, checks whether `juicedata/mount:ce-<version>` already exists, builds latest and versioned CE images when missing, and syncs them to Alibaba Cloud registries. `publish-ee-4_0-mount-image` downloads the EE 4.9 binary endpoint, derives a version, builds `ee-<version>` images if missing, and syncs them. `publish-ee-5_0-mount-image` downloads a full/std/min EE package, derives `mount_version` plus binary hash, chooses a package type, builds the appropriate image target, sends Slack notifications for manual-dispatch success/failure, and syncs the image.

## Control Flow
Each job checks image existence with `docker pull` and gates build/sync steps on `MOUNT_IMAGE_EXIST == 'false'`. Buildx and QEMU are set up before multi-platform builds. The CE job has a special branch for v1.1 image targets. EE 5.0 chooses full Buildx builds for full packages and non-Buildx `ee-image` for std/min packages.

## State and Persistence Behavior
The workflow publishes external Docker Hub images and syncs them to multiple Alibaba Cloud registries using secrets. It also emits Slack notifications for manually dispatched EE 5.0 builds.

## Dependencies and Integration Points
It depends on Docker Hub credentials, ACR credentials, Slack secrets/vars, Docker Buildx, `docker` Makefile targets, `.github/scripts/sync.sh`, GitHub releases API for CE versions, and JuiceFS static package endpoints for EE versions.

## Risks
Version detection is shell/grep based and can break on upstream output changes. Some `if [ ${{ env.VAR }} ]` patterns may behave badly with empty or special values. Secrets are broadly used in shell scripts. The workflow uses live external endpoints and registry availability as control-flow inputs, so transient network failures can skip or fail builds.

## Test Signals
Success indicates mount images were either already present or built and synced. It does not run CSI E2E tests against the produced images; release check workflows provide that validation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/juicefs-image.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/nightly.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/nightly.yaml

## Purpose
This nightly workflow builds the CSI driver nightly image, runs CE and EE E2E matrices, and publishes nightly CSI and mount images after successful full E2E validation.

## Important Jobs and Steps
`build-matrix` emits full and without-kubelet test mode matrices. The CE/EE E2E jobs build `docker image-nightly`, import `juicedata/juicefs-csi-driver:nightly` into microk8s, deploy CSI with `dev_tag=nightly`, and run `.github/scripts/e2e-test.py`. `success-all-test` checks the workflow conclusion, builds dashboard dist, logs into Docker Hub, builds and pushes nightly CSI/dashboard/mount images, syncs selected images, and prints success.

## Control Flow
The workflow runs on manual dispatch, pushes to `master`, and daily schedule. E2E jobs fan out by matrix. Publishing happens after the full CE and EE E2E jobs complete successfully according to the conclusion action.

## State and Persistence Behavior
It builds and imports local images during tests, then publishes nightly images to Docker Hub and syncs them to Alibaba Cloud registries. It does not modify repo files.

## Dependencies and Integration Points
It depends on the Docker Makefile nightly targets, dashboard UI build, microk8s setup scripts, E2E Python tests, Docker Hub credentials, ACR credentials, and image sync script.

## Risks
Because it runs on every push to master and schedule, it can consume significant CI resources. It duplicates much of `go.yaml` E2E logic but uses nightly image paths. Publishing is tied to workflow conclusion logic and selected dependencies; without-kubelet lanes are not listed in the `success-all-test` needs array. External registry and secret failures can make test-passing builds fail at publish time.

## Test Signals
Passing E2E jobs validate nightly images in microk8s across CE/EE and supported mount modes. Passing final publish steps indicates nightly artifacts are available in registries.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/nightly.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ce.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ce.yaml

## Purpose
This workflow validates a candidate CE JuiceFS version against the CSI driver E2E suite before release.

## Important Jobs and Steps
It accepts `ce_juicefs_version` on manual dispatch and also runs on `release_check*` branch pushes. `build-matrix` produces mount mode matrices. `e2e-ce-test` prepares microk8s, logs into Docker Hub, builds dashboard dist, builds a CE mount image with `CEJUICEFS_VERSION`, builds/imports release-check CSI images, deploys CSI, and runs `e2e-test.py` in CE mode. `success-all-test` fails the workflow if the matrix failed.

## Control Flow
The test matrix covers `pod`, `pod-mount-share`, `pod-provisioner`, `webhook`, `webhook-provisioner`, and `process`. All matrix cells share the provided CE version and local release-check image tags.

## State and Persistence Behavior
Images are built/imported into microk8s for validation. No files are committed. External Docker Hub login is used for image pulls/builds.

## Dependencies and Integration Points
It depends on Docker Makefile release-check targets, dashboard build, microk8s setup, E2E scripts, and CE environment variables for MinIO/Redis-backed JuiceFS.

## Risks
Only CE paths are covered. The workflow assumes the supplied CE version can be consumed by Docker targets. Runner disk pressure is mitigated by cleanup, but image builds remain expensive.

## Test Signals
Success means the supplied CE JuiceFS version works with CSI E2E scenarios in the configured microk8s matrix.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ce.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ee.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ee.yaml

## Purpose
This workflow validates an EE release-check mount image against CSI E2E tests.

## Important Jobs and Steps
`build-matrix` emits the standard release-check test modes. `e2e-ee-test` cleans disk, prepares microk8s, logs into Docker Hub, builds dashboard dist, builds EE and CSI release-check images with `JFSCHAN=beta`, imports them, deploys CSI, and runs `.github/scripts/e2e-test.py` with EE token credentials. `success-all-test` gates the final conclusion.

## Control Flow
It runs on manual dispatch and pushes to the `release_check` branch. The E2E matrix covers pod, shared pod mount, pod provisioner, webhook, webhook provisioner, and process modes.

## State and Persistence Behavior
It builds and imports local images into microk8s and uses secrets for Docker Hub and EE volume token. It does not persist repo changes.

## Dependencies and Integration Points
Dependencies include Docker Makefile targets, dashboard UI, microk8s setup, E2E scripts, EE JuiceFS credentials, and the CSI deploy script.

## Risks
The push trigger is narrower than CE (`release_check` exactly). Upterm failure sessions are shorter than other workflows but still expose a live debugging environment. The workflow assumes beta-channel EE assets and secrets are available.

## Test Signals
Success indicates the EE candidate image works with the CSI E2E matrix.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/release_check_ee.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/sync_image.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/sync_image.yaml

## Purpose
This manual workflow syncs JuiceFS-related images from Docker Hub to Alibaba Cloud registries. It supports mount images, CSI images, operator images, and arbitrary images.

## Important Jobs and Steps
`mount-image-sync` syncs a provided mount tag or discovers latest CE and EE mount tags, checking Alibaba registry existence before syncing. `csi-image-sync` syncs a provided CSI tag or discovers the latest CSI release. `operator-image-sync` syncs a provided operator tag or discovers the latest operator release. `other-image-sync` syncs an arbitrary input image with an optional platform argument.

## Control Flow
Each job checks out the repo, logs into Docker Hub, enters `.github/scripts`, and runs `sync.sh` with the selected image/tag. Jobs are independent and may run even when unrelated inputs are empty. Concurrency cancels superseded runs per ref.

## State and Persistence Behavior
The workflow writes no repository state but publishes/syncs images to external Alibaba Cloud registries using ACR credentials.

## Dependencies and Integration Points
It depends on Docker Hub credentials, ACR credentials, GitHub release APIs, JuiceFS static package downloads for EE version detection, and `.github/scripts/sync.sh`.

## Risks
Several shell tests interpolate optional inputs directly into `[ ... ]`, which can be fragile for empty values or special characters. All four jobs run on every dispatch, so a request to sync one image still performs setup for other lanes and may hit external endpoints. Version discovery is grep based.

## Test Signals
Success indicates requested or latest images were found and synced, or already existed in target registries. It does not validate runtime behavior of the synced images.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/sync_image.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/version.yaml -->
# sources/control-plane/juicefs-csi-driver/.github/workflows/version.yaml

## Purpose
This release workflow builds and publishes versioned CSI driver and dashboard images, bundling selected CE and EE JuiceFS mount image versions.

## Important Jobs and Steps
The `publish-version` job checks out full history, builds dashboard dist, logs into Docker Hub, resolves CE, EE, and CSI versions from inputs or upstream sources, configures QEMU/Buildx, runs `make -C docker image-version` and `make -C docker dashboard-buildx`, then syncs the CSI image through `.github/scripts/sync.sh`.

## Control Flow
It runs on manual dispatch and GitHub release creation. Input versions override auto-detected latest versions. CE version detection queries GitHub releases, EE version detection downloads and inspects a static package, and CSI version detection uses `git describe --tags --match 'v*'`.

## State and Persistence Behavior
The workflow publishes versioned container images and syncs them externally. It does not create commits or tag changes; it consumes release/tag state.

## Dependencies and Integration Points
It depends on pnpm/dashboard build, Docker Hub credentials, Docker Buildx, Docker Makefile release targets, GitHub release/tag metadata, JuiceFS static package endpoints, and ACR sync credentials.

## Risks
Version parsing is shell/grep based and can fail on unexpected upstream formats. If release creation happens before assets or upstream mount images are ready, build may fail. The workflow does not run E2E tests; it assumes release checks already validated combinations.

## Test Signals
Success indicates versioned images were built and the CSI image was synced. Functional validation must come from CI/release-check workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.github/workflows/version.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.golangci.yml -->
# sources/control-plane/juicefs-csi-driver/.golangci.yml

## Purpose
This configuration defines golangci-lint behavior for the CSI driver repository.

## Important Settings
It uses config `version: "2"`. Under `linters.settings.staticcheck.checks`, it enables all Staticcheck checks then disables selected quick-fix and style checks: `QF1003`, `QF1007`, `QF1008`, `QF1012`, `ST1003`, `ST1012`, `ST1016`, and `ST1019`. Under exclusions, it applies `comments`, `legacy`, and `std-error-handling` presets.

## Control Flow
This file is consumed by golangci-lint when verification scripts or local lint commands run. It has no runtime control flow.

## State and Persistence Behavior
No state is stored by this file; it only configures lint diagnostics.

## Dependencies and Integration Points
It integrates with `make verify` via `./hack/verify-all` if that script invokes golangci-lint. It affects Go quality gates in `go.yaml`.

## Risks
Disabling style and error-handling checks reduces noise but can hide consistency issues. The version-2 config requires compatible golangci-lint versions.

## Test Signals
Passing lint with this config means configured static checks and exclusions succeeded. It is not a substitute for unit or E2E tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/Makefile -->
# sources/control-plane/juicefs-csi-driver/Makefile

## Purpose
The root Makefile centralizes build, test, dashboard, manifest generation, dev deployment, image, mock generation, npm install, and documentation-check commands for the JuiceFS CSI driver.

## Important Targets and Variables
Key variables include `IMAGE`, `REGISTRY`, `DASHBOARD_IMAGE`, `TARGETARCH`, `VERSION`, `GIT_BRANCH`, `GIT_COMMIT`, `DEV_TAG`, `BUILD_DATE`, `PKG`, `CLIENT_GO_PKG`, and `LDFLAGS`. The `juicefs-csi-driver` target builds `./cmd/` for Linux with embedded version metadata. `test` runs Go package tests under `./pkg/...`; `test-sanity` runs CSI sanity tests. Dashboard targets build UI dist, lint UI, build `cmd/dashboard`, and build dashboard images. `yaml` regenerates deploy manifests through kustomize and updates install scripts. Dev targets build images, import or push them to local clusters, generate kustomize overlays, and deploy with `kapp`.

## Control Flow
Targets compose build steps through dependencies. `install-dev` chains verify, tests, dev image build/push, and deployment. The `push-dev` target branches on `DEV_K8S` to support microk8s image import, kubeadm registry push, or minikube cache add. Manifest generation uses `kustomize build`, `sed` substitutions, and script updates.

## State and Persistence Behavior
The Makefile writes binaries under `bin/`, generated manifests under `deploy/`, dev overlays under `deploy-dev/`, coverage files through test targets, image tarballs transiently in microk8s flows, and Docker images in local/remote registries. It can mutate generated YAML files in the source tree.

## Dependencies and Integration Points
It depends on Go, Docker, pnpm/npm, kustomize, kubectl, kapp, minikube or microk8s tooling, mockgen, and repository scripts under `hack/`. GitHub workflows call `make`, `make verify`, `make test`, `make test-sanity`, `make dashboard-dist`, and several Docker Makefile targets.

## Risks
Many targets assume specific local tools and cluster types. Generated manifest targets use `sed -i.orig` for macOS compatibility but can leave `.orig` artifacts. Version metadata depends on git state and can produce dirty tags. Image target behavior varies by `DEV_K8S`, so local and CI flows can diverge.

## Test Signals
`make verify`, `make test`, `make test-sanity`, `make dashboard-lint`, and `make check-docs` are the primary local signals. CI workflows exercise these targets and image build paths.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/app/controller_manager.go -->
# sources/control-plane/juicefs-csi-driver/cmd/app/controller_manager.go

## Purpose
This Go file defines the controller-runtime manager used by the CSI controller process for mount management, webhook-sidecar management, cache client config watching, and controller metrics.

## Important APIs, Types, and Functions
`ControllerManager` stores a `ctrl.Manager`, feature flags for mount manager and webhook, and a `k8sclient.K8sClient`. `NewControllerManager(...)` builds the manager from in-cluster config with metrics on `0.0.0.0:8084`, optional leader election, cached Pod and Job informers, optional webhook server, and a shared Kubernetes client. `Start(ctx)` registers controllers according to enabled flags and starts the manager.

## Control Flow
Construction gets Kubernetes config, builds `ctrl.Options`, optionally attaches a webhook server when `config.Webhook` is true, creates the controller-runtime manager, then creates the project-specific Kubernetes client. Startup registers webhook handlers and `AppController` in sidecar mode, registers `MountController` and `JobController` when mount management is enabled, registers `PVController` and `SecretController` when `config.CacheClientConf` is enabled, then calls `mgr.Start(ctx)`.

## State and Persistence Behavior
The manager itself persists no files. It watches Pods and Jobs, writes metrics, participates in leader election through Kubernetes Leases, and delegates state changes to registered controllers that create/update/delete mount pods, jobs, PV/Secret cache state, and webhook-admitted pods.

## Dependencies and Integration Points
It depends on controller-runtime, Kubernetes core and batch APIs, JuiceFS common labels, global config, `pkg/controller`, `pkg/k8sclient`, and `pkg/webhook/handler`. It is called from `cmd/controller.go` when the controller process enables mount manager or webhook mode.

## Risks
`NewControllerManager` calls `os.Exit(1)` on `ctrl.NewManager` failure instead of returning the error, which makes it harder to unit test and reason about caller cleanup. The `enableWebhook` parameter controls registration, while `config.Webhook` controls whether the webhook server is configured; a mismatch could register handlers without a server or vice versa. Cache filters Jobs by `common.PodTypeKey=common.JobTypeValue`, so mislabeled jobs are invisible to the manager cache.

## Test Signals
There are no direct tests in this file. It is covered by Go build, controller package tests, and E2E modes that exercise mount manager, webhook, cache client config, and volume deletion jobs.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/app/controller_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/app/pod_manager.go -->
# sources/control-plane/juicefs-csi-driver/cmd/app/pod_manager.go

## Purpose
This file defines the node-side pod manager that watches Pods scheduled to the current node and wires the CSI node pod reconciler.

## Important APIs, Types, and Functions
`PodManager` holds a controller-runtime manager, project Kubernetes client, and uncached API reader. `NewPodManager()` creates a manager with metrics on `0.0.0.0:8082`, lease-based leader election ID `pod.juicefs.com`, and a Pod cache filtered by `spec.nodeName == config.NodeName`. `Start(ctx)` registers `mountctrl.NewPodController(m.client, m.cacheReader)` and starts the manager.

## Control Flow
Package `init()` registers core Kubernetes objects into the shared scheme. Construction gets in-cluster config, creates the manager with a filtered Pod cache, creates a `k8sclient.K8sClient`, and returns the manager wrapper. Start registers the pod controller, logs startup, and blocks on `mgr.Start(ctx)`.

## State and Persistence Behavior
The pod manager does not persist local state. It watches Pods assigned to a node and delegates reconciliation state to `PodController`, which is responsible for mount behavior and Kubernetes object changes.

## Dependencies and Integration Points
It depends on controller-runtime, Kubernetes schemes, the global `config.NodeName`, project controller package, and project k8s client. It is used by the CSI node command path when node pod management is enabled.

## Risks
If `config.NodeName` is empty or wrong, the cache will miss target pods and reconciliation will not occur. Metrics bind address `8082` overlaps with dashboard manager metrics if both run in the same network namespace. Leader election namespace is not explicitly set here, so cluster RBAC/namespace defaults matter.

## Test Signals
Coverage is primarily E2E: pod-mount, process, webhook, and mount-pod lifecycle tests depend on node-side pod reconciliation working.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/app/pod_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/controller.go -->
# sources/control-plane/juicefs-csi-driver/cmd/controller.go

## Purpose
This file implements the CSI controller process path. It parses controller-related runtime configuration, starts optional controller-runtime managers, exposes metrics/pprof, and starts the CSI driver service.

## Important APIs, Types, and Functions
`parseControllerConfig()` maps Cobra flags and environment variables into `pkg/config` globals. `controllerRun(ctx)` calls the parser, starts pprof and Prometheus metrics HTTP servers, optionally starts `app.ControllerManager`, creates `driver.NewDriver(...)`, and runs it.

## Control Flow
`parseControllerConfig` sets process/webhook/provisioner/cache/validation flags, reads `DRIVER_NAME`, disables mount manager/webhook/provisioner in by-process mode, parses `JUICEFS_IMMUTABLE`, reads node/namespace/mount/config paths, resolves CE/EE mount images from specific or generic env vars, enables share-mount modes, parses provisioner worker threads, and when not in webhook sidecar mode attempts to inherit CSI node pod attributes by listing `app=juicefs-csi-node` Pods or falling back to the `juicefs-csi-node` DaemonSet template.

`controllerRun` requires `nodeID`, starts pprof on localhost starting at port 6060, starts `/metrics` on `config.WebPort`, launches `ControllerManager` when mount manager or webhook is enabled, then starts the CSI driver. It stops the driver when the context is cancelled.

## State and Persistence Behavior
The file writes configuration into global `pkg/config` variables. It starts HTTP servers and controller-runtime managers, creates Kubernetes clients, and reads live Pods/DaemonSets to populate `config.CSIPod`. Persistent cluster mutations are delegated to the CSI driver and controllers.

## Dependencies and Integration Points
It depends on Prometheus, Kubernetes API types, project `app`, `config`, `driver`, `k8sclient`, and `util.ImageResol`. It is selected from `cmd/main.go` when `POD_NAME` contains `csi-controller`.

## Risks
The pprof goroutine exits the process on the first `ListenAndServe` error inside an infinite loop, so the port-increment logic is effectively unreachable after failure. Many config values are global and process-wide, which complicates tests and concurrent modes. If no CSI node Pod or DaemonSet is found in non-webhook mode, the controller exits. Environment parsing failures are fatal.

## Test Signals
Go build covers compilation. E2E controller modes exercise provisioning, mount manager, webhook, metrics-adjacent startup, and config inheritance.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/controller.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/dashboard/main.go -->
# sources/control-plane/juicefs-csi-driver/cmd/dashboard/main.go

## Purpose
This file is the main entrypoint for the JuiceFS CSI dashboard binary. It serves the dashboard API and optional static frontend, supports local dev kubeconfig, optional basic auth, optional controller-runtime manager support for cache/index resources, pprof, graceful shutdown, and version output.

## Important APIs, Types, and Functions
`main()` defines the Cobra command `juicefs-csi-dashboard`, registers `upgradeCmd`, reads `USERNAME`/`PASSWORD`, and defines persistent flags for version, port, dev mode, static dir, leader election, and manager enablement. `run()` resolves Kubernetes config, creates a controller-runtime manager or direct client, constructs `dashboard.NewAPI`, registers routes under `/api/v1`, serves static assets and SPA fallback, starts HTTP and pprof servers, and starts the dashboard manager when enabled. `getLocalConfig()` loads `$HOME/.kube/config`; `newManager()` creates the controller-runtime manager.

## Control Flow
The binary exits early for `--version`. Runtime namespace defaults to `kube-system` but can be overridden by `SYS_NAMESPACE`. In dev mode it uses local kubeconfig and enables permissive CORS; otherwise it uses in-cluster config and Gin release mode. Basic auth is installed only when both username and password are present. Static serving maps `/assets/...` to the dist assets and non-API fallback to `index.html`. Shutdown uses a two-signal flow: first signal triggers server shutdown; a second signal exits immediately.

## State and Persistence Behavior
The process stores runtime choices in `pkg/config` globals (`Namespace`, `DisableGraceUpgrade`, `DriverName`) and runs HTTP/manager goroutines. Persistent Kubernetes state is read/written by `pkg/dashboard` API handlers and optional manager controllers. It does not write local files.

## Dependencies and Integration Points
Dependencies include Gin, CORS middleware, Cobra, klog, controller-runtime, Kubernetes schemes, the cache-group-operator API scheme, `pkg/dashboard`, and `pkg/driver`. It integrates with `dashboard-ci.yaml`, dashboard image workflows, and `Makefile` dashboard targets.

## Risks
Basic auth is enabled only if both env vars are non-empty; missing one leaves the dashboard unauthenticated. The static `NoRoute` handler can call `c.File` twice for asset requests if the URI also is not `/api`, depending on Gin behavior after the first call. The pprof server logs errors but does not stop the main process. Metrics bind on `8082`, which can conflict with other managers in shared namespaces.

## Test Signals
Build and dashboard CI cover compilation and UI packaging indirectly. Runtime API behavior is likely covered by dashboard package tests or manual/E2E use, not by this file directly.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/dashboard/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/dashboard/upgrade.go -->
# sources/control-plane/juicefs-csi-driver/cmd/dashboard/upgrade.go

## Purpose
This file implements the dashboard `upgrade` subcommand, which orchestrates smooth batch upgrades of JuiceFS mount pods by loading a batch config, triggering CSI node-side upgrade commands via Kubernetes exec, monitoring replacement pods, and writing upgrade status back to the batch config.

## Important APIs, Types, and Functions
`upgradeCmd` is the Cobra command. `BatchUpgrade` holds namespace, loaded `BatchConfig`, Kubernetes REST config/clientset/project client, grouped pod batches, status lock, per-pod status map, overall status, current/next batch status, and current batch index. `PodUpgrade` stores the original Pod, hash label, and upgrade UUID. Main methods are `Run`, `fetchPods`, `processBatch`, `triggerUpgrade`, `waitForUpgrade`, `flushStatus`, `handleSignal`, `panic`, and `Write`.

## Control Flow
The command refuses to run when `DISABLE_GRACE_UPGRADE=true`. It resolves namespace and Kubernetes config, creates clients, loads batch config from `common.JfsUpgradeConfig`, initializes every configured pod to pending, flushes status, fetches live mount pods, starts signal handling, and calls `Run`.

`Run` ticks once per second. It advances batches when the current batch is pending/success or failed with `IgnoreError`, stops on pause/stop/fail, and writes final success/failure status. `processBatch` groups current batch entries by CSI node pod, triggers one exec per CSI node, and waits for relevant mount pods on each node. `triggerUpgrade` runs `juicefs-csi-driver upgrade BATCH --batchConfig ... --batchIndex ...` inside the CSI node `juicefs-plugin` container over SPDY. `waitForUpgrade` watches mount pods on the target node, matches old/new pods by upgrade UUID, and marks pod success when a replacement is ready.

The `Write` method implements `io.Writer` for remote exec streams. It prints output and parses `POD-START`, `POD-SUCCESS`, and `POD-FAIL` messages with regexes to update per-pod status.

## State and Persistence Behavior
Upgrade status is persisted by `config.UpdateUpgradeConfig` back to the named upgrade ConfigMap. Runtime state is protected partly by `sync.Mutex`. The command also reacts to process signals: `SIGUSR1` toggles pause/resume and `SIGTERM` stops future batches.

## Dependencies and Integration Points
It depends on Gin for dev/release config behavior, Cobra, Kubernetes client-go REST/clientset/informers/remotecommand, controller-runtime config, project `common`, `config`, `k8sclient`, and `util/resource`. It integrates with CSI node pods that must support the internal `juicefs-csi-driver upgrade BATCH` command and emit parseable log markers.

## Risks
`setNextBatchStatus` writes without locking while other status fields are locked, so signal and ticker interactions can race. `processBatch` launches goroutines that close over loop variables without passing them as parameters; in Go versions with old loop semantics this would be a bug, and even with newer semantics care is needed around shared `u.crtBatch`. The command calls `os.Exit` in failure paths, limiting cleanup. Regex parsing of stream output is a brittle status channel. The 300-second wait is fixed and may be too short for large clusters.

## Test Signals
There are no direct tests in this file. Signals come from dashboard build, Go tests in related packages, and any manual/automated smooth-upgrade workflows that exercise batch ConfigMaps and CSI node exec.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/dashboard/upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/main.go -->
# sources/control-plane/juicefs-csi-driver/cmd/main.go

## Purpose
This is the main entrypoint for the `juicefs-csi` binary. It defines CLI flags, handles version output, starts optional config reloading, probes bundled JuiceFS CLI versions, sets up signal handling, and dispatches to controller or node runtime based on the current pod name.

## Important APIs, Types, and Functions
Global variables hold CLI flag values for CSI endpoint, node id, format-in-pod, by-process mode, config path, controller features, node manager features, leader election, and logging. `main()` defines the Cobra command, registers flags, attaches klog flags, registers `upgradeCmd`, and executes. `run()` starts config reloading, probes CE/EE binary versions asynchronously, obtains a signal-aware context, and calls `controllerRun(ctx)` or `nodeRun(ctx)` based on `POD_NAME`.

## Control Flow
If `--version` is set, it prints `driver.GetVersionJSON()` and exits. If `--config` is provided, `config.StartConfigReloader` is started before runtime dispatch. A goroutine runs `juicefs version` commands for CE and EE binaries and records output in global config variables. The process then checks whether `POD_NAME` contains `csi-controller` or `csi-node` and invokes the matching run path.

## State and Persistence Behavior
The file mutates package-level config for built-in JuiceFS versions and starts a config reloader if requested. It does not persist files directly. All durable cluster state is managed by controller/node run paths and driver/controllers.

## Dependencies and Integration Points
It depends on Cobra, klog, controller-runtime logging/signal handling, `pkg/config`, `pkg/driver`, and `k8s.io/utils/exec`. It integrates with `cmd/controller.go`, the node runtime in another source file, and the upgrade command.

## Risks
Dispatch relies on `POD_NAME` string containment; if the binary is run outside the expected pod naming scheme, neither controller nor node path starts and the process exits after `run()` returns. The asynchronous version probe can race with code that reads `BuiltinCeVersion` or `BuiltinEeVersion` immediately after startup. Global CLI variables make isolated tests harder.

## Test Signals
Compilation is covered by `make` and CI. Runtime behavior is covered by E2E deployments that set `POD_NAME` through Kubernetes manifests and exercise controller/node modes.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/main.go -->
