# subset-b-000423 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/canary-integration-test.yml -->
# sources/control-plane/rook/.github/workflows/canary-integration-test.yml

## Purpose

Reusable GitHub Actions workflow for broad Rook/Ceph canary coverage. It is invoked by other workflows through `workflow_call` and matrixes over Ceph images and Kubernetes versions to exercise raw device, partitioned device, LVM, PVC, encryption, KMS, mirroring, Multus, object, and NVMe-oF scenarios.

## Important APIs, Types, and Functions

The workflow exposes `ceph_images` and `kubernetes-version` JSON string inputs. Jobs include `canary`, `raw-disk-with-object`, `two-osds-in-device`, metadata-device variants, encryption and encrypted PVC variants, Vault and IBM Key Protect KMS paths, `lvm-pvc`, `multi-cluster-mirroring`, `rgw-multisite-testing`, `nvmeof-protocol`, `multus-public-and-cluster`, and `two-object-one-zone`. It depends heavily on local composite actions `tmate_debug`, `upterm_debug`, `integration-test-setup-cluster-resources`, `collect-logs`, and `encryption-pvc-kms-ibm-kp`.

## Control Flow

Each job checks out the full repository, optionally opens pre-job debugging, provisions cluster resources, rewrites manifests for the selected Ceph image, prepares block devices or PVCs, deploys Rook/Ceph manifests, waits for readiness, runs scenario-specific checks, collects logs on `always()`, and optionally opens post-job debugging. The main `canary` job also validates `create-external-cluster-resources.py` idempotency, dry-run behavior, restricted auth, topology flags, rados namespaces, RGW endpoint validation, multisite flags, key rotation, csi-addons, owner references, and OSD purge behavior.

## State and Persistence Behavior

State is external to the YAML and lives in the GitHub Actions runner, Kubernetes cluster, Ceph cluster, local disks, loop devices, generated manifests, secrets, and uploaded artifacts. Some jobs intentionally delete and redeploy clusters to verify cleanup policies and persistence or removal of disk headers. KMS jobs create external secrets and must delete the CephCluster to clean up remote keys.

## Dependencies and Integration Points

The file integrates with `tests/scripts/github-action-helper.sh`, `tests/scripts/validate_cluster.sh`, `tests/scripts/create-bluestore-partitions.sh`, Vault validation scripts, Multus scripts, Kubernetes `kubectl`, `yq`, `jq`, Ceph CLI, `rbd`, `radosgw-admin`, minikube, and GitHub secrets for tmate and IBM Key Protect. It is called from nightly and release workflows and supplies check names that Mergify references for backport automerge.

## Risks and Edge Cases

The workflow is large and shell-heavy, so manifest mutations can leak between steps if reset logic is incomplete. Many waits assume specific labels, namespace names, object names, device sizes, service names, and Ceph output formats. Debug actions can expose interactive sessions when enabled. External services and secrets make IBM and Vault paths conditional and potentially flaky. The matrix creates many long-running jobs, so check-name changes can break Mergify rules.

## Test Signals

Successful job completion signals a live end-to-end Rook deployment across the covered scenarios. Failure artifacts from `collect-logs` and per-step `kubectl`/Ceph output are the primary diagnostics. Scenario checks include readiness waits, Ceph CLI assertions, key existence checks, object replication tests, CSI workload restart tests, and explicit negative tests that expect bad inputs to fail.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/canary-integration-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/checkmake.yaml -->
# sources/control-plane/rook/.github/workflows/checkmake.yaml

## Purpose

Runs CheckMake against the repository `Makefile` for pull requests to `master` and release branches.

## Important APIs, Types, and Functions

The workflow has one `checkmake` job using pinned `actions/checkout` and `Uno-Takashi/checkmake-action` with `Makefile: Makefile` and `debug: true`.

## Control Flow

Pull request events trigger the job, concurrency cancels older runs for the same PR, checkout fetches the repository, and the action parses the Makefile using the local `checkmake.ini` configuration.

## State and Persistence Behavior

The workflow writes no repository state. Its only durable state is the GitHub check result and logs.

## Dependencies and Integration Points

It integrates with `checkmake.ini`, the root `Makefile`, branch protection, and Mergify check names. It requires only read access to contents.

## Risks and Edge Cases

The external action and CheckMake parser may lag Makefile syntax. With `debug: true`, logs are more verbose but still do not modify files.

## Test Signals

A passing `CheckMake` check indicates Makefile linting passed for the PR.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/checkmake.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/codegen.yml -->
# sources/control-plane/rook/.github/workflows/codegen.yml

## Purpose

Verifies generated Go/API code is up to date on pushes, tags, and pull requests.

## Important APIs, Types, and Functions

The `codegen` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make codegen`, and validates with `tests/scripts/validate_modified_files.sh codegen`.

## Control Flow

After checkout with full history, the workflow installs Go, runs the Makefile `codegen` target, then fails if generated files differ from committed content.

## State and Persistence Behavior

Generated files are only created or changed in the ephemeral runner. The validation script turns a dirty worktree into a failed check rather than persisting changes.

## Dependencies and Integration Points

It depends on `build/codegen/codegen.sh`, controller/code generator tooling from the Makefile, Go modules, and the validation script. Mergify requires the `codegen` check for release backport automerge.

## Risks and Edge Cases

Generator output can vary with Go/tool versions, so the pinned Go version and Makefile generator versions are important. The job is skipped for PRs labeled `skip-ci`.

## Test Signals

Passing means `make codegen` is deterministic and committed generated sources match the current code.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/codegen.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/codespell.yaml -->
# sources/control-plane/rook/.github/workflows/codespell.yaml

## Purpose

Runs spelling checks with both Codespell and Misspell over the repository.

## Important APIs, Types, and Functions

The workflow has `codespell` and `misspell` jobs. Codespell uses an explicit skip list for generated assets, images, license, dashboards, CRDs, and chart resources, plus a curated ignore word list and filename/hidden-file checks. Misspell uses `reviewdog/action-misspell`.

## Control Flow

Push and pull request triggers start independent jobs. Each checks out full history, then invokes the respective pinned spelling action.

## State and Persistence Behavior

No repository state is persisted. Findings are emitted as check annotations and logs.

## Dependencies and Integration Points

It integrates with generated file policy, dashboard generation, CRD generation, and Mergify-required checks `codespell` and `misspell`.

## Risks and Edge Cases

Skip and ignore lists encode project-specific vocabulary; stale entries can hide real mistakes or cause false positives. The Codespell action is pinned to a master commit rather than a semantic version.

## Test Signals

Passing indicates no unignored spelling findings in filenames or file content for the scanned paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/codespell.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/collect-logs/action.yaml -->
# sources/control-plane/rook/.github/workflows/collect-logs/action.yaml

## Purpose

Composite action that collects common canary logs and uploads them as a GitHub artifact.

## Important APIs, Types, and Functions

Inputs are required `name` and optional `additional-namespace`. Steps sanitize the artifact name into `ARTIFACT_NAME`, run `tests/scripts/collect-logs.sh`, log the artifact name, and upload the `test` directory with pinned `actions/upload-artifact`.

## Control Flow

The caller normally invokes this action under `if: always()`. The action normalizes `:` and `/` in the provided name, exports `ADDITIONAL_NAMESPACE`, executes the collector script, then uploads artifacts.

## State and Persistence Behavior

Runner-local logs under `test` become persisted workflow artifacts. The action writes `ARTIFACT_NAME` to `$GITHUB_ENV`.

## Dependencies and Integration Points

It integrates with all canary jobs, cluster namespaces, Kubernetes logs, and the local `collect-logs.sh` script. It is not intended for Go integration tests whose log directory differs.

## Risks and Edge Cases

Artifact names are only partially sanitized. If `collect-logs.sh` expects cluster state that no longer exists, the action can fail or produce incomplete artifacts unless the script tolerates missing resources.

## Test Signals

An uploaded artifact with the expected sanitized name and collected `test` contents is the success signal.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/collect-logs/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/commitlint.yml -->
# sources/control-plane/rook/.github/workflows/commitlint.yml

## Purpose

Validates commit message format for pushes and pull requests using the repository commitlint config.

## Important APIs, Types, and Functions

The `lint` job grants `contents: read` and `pull-requests: read`, exports `GITHUB_TOKEN`, checks out full history, and runs `wagoid/commitlint-github-action` with `.commitlintrc.json` and a Rook docs help URL.

## Control Flow

The workflow triggers on master/release pushes, tags, and PRs. Concurrency cancels older PR runs. Commitlint reads PR commit metadata through the token and reports violations.

## State and Persistence Behavior

No repository state is written. Results live as GitHub check status and logs.

## Dependencies and Integration Points

It integrates with `.commitlintrc.json`, GitHub PR APIs, branch protection, and contributor documentation.

## Risks and Edge Cases

Fetch depth is zero to expose commit history. Misconfigured PR permissions or token scope would prevent the action from reading commits.

## Test Signals

Passing `lint` means all commits in scope comply with Rook's commit message convention.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/commitlint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/crds-gen.yml -->
# sources/control-plane/rook/.github/workflows/crds-gen.yml

## Purpose

Verifies Kubernetes CRD manifests and CRD API reference docs are regenerated and committed.

## Important APIs, Types, and Functions

The `crds-gen` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make crds`, and checks generated changes via `tests/scripts/validate_modified_files.sh crd`.

## Control Flow

Checkout with full history is followed by Go setup, Makefile CRD generation, and a dirty-worktree validation gate.

## State and Persistence Behavior

Generated CRD artifacts exist only in the CI worktree; any uncommitted diff fails the job.

## Dependencies and Integration Points

It depends on the Makefile `crds` target, `controller-gen`, `yq`, `build/crds/build-crds.sh`, `build/crds/generate-crd-docs.sh`, and validation scripts. Mergify requires `crds-gen`.

## Risks and Edge Cases

CRD generation may be sensitive to controller-gen versions, Go tags, or docs generation toggles. The workflow does not explicitly skip `skip-ci`.

## Test Signals

Passing means generated CRDs and CRD docs match committed sources.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/crds-gen.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/daily-nightly-jobs.yml -->
# sources/control-plane/rook/.github/workflows/daily-nightly-jobs.yml

## Purpose

Runs scheduled and manually dispatched nightly Rook tests against ARM64 and development Ceph images.

## Important APIs, Types, and Functions

Jobs include `canary-arm64`, smoke suites for `squid-devel`, `tentacle-devel`, and Ceph `main`, object suites with and without TLS for Ceph `main`, upgrade suites from stable to development Ceph versions, and `canary-tests` which calls the reusable canary workflow with five Ceph images. `GOFLAGS=-tags=ceph_preview` is set globally.

## Control Flow

The workflow runs daily at midnight or on manual dispatch. Every job is gated to `github.repository == 'rook/rook'`, checks out full history, can enable tmate, provisions cluster resources at Kubernetes `v1.35.5`, runs a targeted `go test` or canary workflow, collects logs, and uploads failure artifacts.

## State and Persistence Behavior

Cluster and test state is ephemeral. Logs under the integration output directory and canary `test` directory are persisted only when uploaded. The reusable canary receives secrets by inheritance.

## Dependencies and Integration Points

It integrates with the reusable canary, setup and debug composite actions, Go integration tests, `tests/scripts/github-action-helper.sh`, `tests/scripts/collect-logs.sh`, GitHub secrets, and ARM runners.

## Risks and Edge Cases

Nightlies are sensitive to external Ceph development image availability and behavior. ARM64 jobs disable liveness probes due to slow environment assumptions. The workflow exercises more images than PR CI, so check names and runtime cost are substantial.

## Test Signals

Passing nightlies indicate current Rook works against latest/development Ceph images and ARM64 canary coverage. Failure artifacts are the key diagnostic signal.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/daily-nightly-jobs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/docs-check.yml -->
# sources/control-plane/rook/.github/workflows/docs-check.yml

## Purpose

Validates markdown style, generated docs, generated CRD docs, and mkdocs build output.

## Important APIs, Types, and Functions

The `docs-check` job sets up Go 1.26 and Python 3.9, runs `DavidAnson/markdownlint-cli2-action` against `Documentation/**/*.md` excluding Helm charts, then runs `make gen.docs`, `make generate-docs-crds`, `make docs-build`, and validation/diff checks.

## Control Flow

After checkout and tool setup, markdownlint checks docs style. Generated Helm docs are validated with `validate_modified_files.sh docs`. CRD docs are regenerated and compared with `git diff --ignore-matching-lines='on git commit'`. Finally mkdocs builds in strict mode.

## State and Persistence Behavior

Generated docs are runner-local. Dirty generated docs or CRD docs fail the job rather than persisting changes.

## Dependencies and Integration Points

It integrates with `.markdownlint-cli2.cjs`, custom markdownlint rules, Makefile docs targets, `build/release/Makefile` docs deps, mkdocs config, and generated CRD docs templates.

## Risks and Edge Cases

Ignoring lines containing `on git commit` is deliberate but can hide only that class of generated timestamp/hash noise. Python and mkdocs dependency changes can break docs without code changes.

## Test Signals

Passing means docs are lint-clean, generated docs are current, CRD docs are reproducible, and mkdocs can build the site.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/docs-check.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/encryption-pvc-kms-ibm-kp/action.yml -->
# sources/control-plane/rook/.github/workflows/encryption-pvc-kms-ibm-kp/action.yml

## Purpose

Composite action that runs the encrypted PVC IBM Key Protect KMS canary path.

## Important APIs, Types, and Functions

Inputs are IBM instance ID, IBM API key, artifact name, Ceph image, and Kubernetes version. Steps validate credentials, set up cluster resources, rewrite Ceph image, prepare disks and local PVs, generate IBM KMS manifests via `envsubst`, deploy an encrypted PVC cluster, wait for OSD readiness, collect logs, and delete the CephCluster.

## Control Flow

The caller supplies secrets and matrix values. The action performs cluster setup, injects IBM credentials into generated manifest files, appends and merges KMS spec content into `test-cluster-on-pvc-encrypted.yaml`, creates the cluster, deploys toolbox, waits, inspects pods/secrets/block devices, uploads logs, and tears down.

## State and Persistence Behavior

State lives in generated manifest files, Kubernetes secrets, CephCluster resources, local PVs, and remote IBM KMS keys. Final teardown is intended to remove keys from KMS.

## Dependencies and Integration Points

It integrates with IBM Key Protect secrets, `integration-test-setup-cluster-resources`, `collect-logs`, `tests/scripts/github-action-helper.sh`, `localPathPV.sh`, `envsubst`, `yq`, `kubectl`, and Ceph encrypted PVC manifests.

## Risks and Edge Cases

The credential guard prints an error but exits `0`, so callers rely on an outer `if` to skip missing secrets. Remote KMS cleanup depends on successful cluster deletion. Generated manifest mutation happens in-place, so order matters.

## Test Signals

Readiness of two OSDs, visible pods/secrets, successful log upload, and successful CephCluster deletion indicate the path worked.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/encryption-pvc-kms-ibm-kp/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/golangci-lint.yaml -->
# sources/control-plane/rook/.github/workflows/golangci-lint.yaml

## Purpose

Runs Go static analysis, vulnerability checks, and Kubernetes API linting.

## Important APIs, Types, and Functions

Jobs are `golangci` using `golangci/golangci-lint-action` version `v2.12.2`, `govulncheck` using `golang/govulncheck-action`, and `kube-api-lint` running `make go.kube-api-lint KUBE_API_LINT_OPTIONS="--new"`.

## Control Flow

Push and PR triggers run independent jobs. Go 1.26 is installed in each job. `golangci` and `kube-api-lint` check out the repo; `govulncheck` only sets up Go and runs the action with `GOFLAGS=-tags=ceph_preview`.

## State and Persistence Behavior

No repository state is modified. Findings are reported as GitHub checks.

## Dependencies and Integration Points

It integrates with `.golangci.yaml`, Makefile lint targets, Go modules, kube-api-linter tooling, and Mergify-required checks.

## Risks and Edge Cases

`govulncheck` lacks an explicit checkout step, which may rely on action defaults or fail depending on action behavior. Static analysis output can change with tool versions.

## Test Signals

Passing `golangci-lint`, `govulncheck`, and `kube-api-lint` indicate Go lint, vulnerability, and API lint gates are clean.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/golangci-lint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/helm-lint.yaml -->
# sources/control-plane/rook/.github/workflows/helm-lint.yaml

## Purpose

Lints Rook Helm charts on pushes and pull requests.

## Important APIs, Types, and Functions

The `lint-test` job checks out the repo and runs `make lint.helm`.

## Control Flow

The workflow uses standard push/PR triggers and PR concurrency cancellation. The Makefile handles chart-testing, helm template output, and kustomize validation.

## State and Persistence Behavior

Temporary templated files are created and removed by the Makefile in the runner. No persistent state is written.

## Dependencies and Integration Points

It integrates with the Makefile `lint.helm` target, chart-testing, Helm, kustomize, and `deploy/charts/rook-ceph*`.

## Risks and Edge Cases

The action has an extra blank line but no behavioral effect. Tool versions are pinned in Makefile variables, so Makefile changes alter CI behavior.

## Test Signals

Passing `lint-test` indicates chart linting and rendering validation succeeded.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/helm-lint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-helm-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-helm-suite.yaml

## Purpose

Runs the Go `CephHelmSuite` integration tests for Helm installs on PRs that touch non-doc/design paths.

## Important APIs, Types, and Functions

The `TestCephHelmSuite` job matrixes Helm `v3.13.3` and `v3.18.3` against Kubernetes `v1.35.5`, sets `GOFLAGS=-tags=ceph_preview`, installs Helm, invokes the setup composite, creates a Helm tag, and runs `go test -run CephHelmSuite`.

## Control Flow

PRs to master/release branches trigger the workflow unless docs/design-only. The job is skipped on `skip-ci` and on direct master refs. It collects udev logs, determines a device filter, runs tests with cleanup disabled, collects logs, uploads failure artifacts, and can open post-job upterm debugging.

## State and Persistence Behavior

State lives in the temporary minikube cluster, generated Helm tag, local block device, and integration output directory. Artifacts persist only on failure.

## Dependencies and Integration Points

It integrates with Azure Helm setup, cluster setup composite, Go integration tests, `github-action-helper.sh`, and `collect-logs.sh`.

## Risks and Edge Cases

The workflow uses a narrow Kubernetes matrix but a two-version Helm matrix. Device discovery and cleanup behavior are runner-sensitive.

## Test Signals

Passing means Helm-based deployment and upgrade/cleanup paths in `CephHelmSuite` work for the matrix.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-helm-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-keystone-auth-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-keystone-auth-suite.yaml

## Purpose

Runs RGW Keystone authentication integration tests on supported Kubernetes versions.

## Important APIs, Types, and Functions

The `TestCephKeystoneAuthSuite` job matrixes Kubernetes `v1.31.14` and `v1.35.5`, installs Helm `v3.18.2`, uses the setup composite with `github-token`, and runs `go test -run CephKeystoneAuthSuite`.

## Control Flow

Eligible PRs trigger the workflow. The job checks out, installs Helm, optionally enables tmate, sets up cluster resources, collects udev logs, chooses a device by `lsblk` size pattern, runs the test suite, collects logs for `keystoneauth-ns`, uploads artifacts on failure, and can open upterm debugging.

## State and Persistence Behavior

Ephemeral state includes minikube resources, Keystone/RGW test namespaces, block devices, and integration logs. Only artifacts persist.

## Dependencies and Integration Points

It integrates with the Go integration package, Helm, local setup composite, GitHub token, and log collection scripts.

## Risks and Edge Cases

Device selection uses `lsblk` matching `14G` or `64G`, which is less abstract than `find_extra_block_dev` and may be runner-shape-sensitive.

## Test Signals

Passing indicates Keystone auth object-store integration works across oldest/latest supported Kubernetes versions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-keystone-auth-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-mgr-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-mgr-suite.yaml

## Purpose

Runs the Ceph manager integration suite when explicitly requested.

## Important APIs, Types, and Functions

The `TestCephMgrSuite` job runs on PRs and a daily schedule but has an `if` requiring the PR label `run-mgr-suite`. It uses Kubernetes `v1.35.5` and runs `go test -run CephMgrSuite`.

## Control Flow

After checkout, optional debugging, and cluster setup, the job collects udev logs, selects an extra block device, runs the manager suite, collects logs for `mgr-ns`, uploads artifacts on failure, and optionally opens post-job upterm.

## State and Persistence Behavior

All cluster/test state is ephemeral. Failure artifacts preserve integration output.

## Dependencies and Integration Points

It integrates with PR labels, the setup composite, Go integration tests, and the mgr namespace/operator namespace log collector settings.

## Risks and Edge Cases

The schedule trigger may not satisfy `github.event.pull_request.labels`, making the job effectively label-gated and likely skipped outside PR context. This is intentional or a possible schedule misconfiguration.

## Test Signals

Passing after label selection means the manager integration suite succeeded on Kubernetes `v1.35.5`.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-mgr-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-multi-cluster-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-multi-cluster-suite.yaml

## Purpose

Runs the Ceph multi-cluster deployment integration suite for PRs.

## Important APIs, Types, and Functions

The `TestCephMultiClusterDeploySuite` job uses Kubernetes `v1.35.5`, exports `BLOCK`, `TEST_SCRATCH_DEVICE`, and `DEVICE_FILTER`, then runs `go test -run CephMultiClusterDeploySuite`.

## Control Flow

The job checks out, optionally opens debugging, sets up minikube resources, collects udev logs, derives a device name through `find_extra_block_dev`, runs tests, collects logs from both `multi-core` and `multi-external`, always uploads artifacts, and supports post-job debugging.

## State and Persistence Behavior

The test creates multiple namespaces/clusters in the runner's Kubernetes environment and writes logs under the integration output tree. Artifacts always persist, not only on failure.

## Dependencies and Integration Points

It integrates with local setup, Go integration tests, multi-cluster namespaces, block device environment variables, and log collection.

## Risks and Edge Cases

Multi-cluster tests are sensitive to device reuse, namespace cleanup, and resource pressure. Always uploading artifacts increases storage use but improves diagnostics.

## Test Signals

Passing means internal and external multi-cluster deployment flows work for the selected Kubernetes version.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-multi-cluster-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-object-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-object-suite.yaml

## Purpose

Runs Ceph object storage integration tests with non-TLS coverage on the oldest supported Kubernetes version and TLS coverage on the latest.

## Important APIs, Types, and Functions

Jobs are `TestCephObjectSuite` with Kubernetes `v1.31.14` and `go test -run CephObjectSuite/TestWithoutTLS`, and `TestCephObjectSuiteTLS` with Kubernetes `v1.35.5` and `go test -run CephObjectSuite/TestWithTLS`.

## Control Flow

Each job checks out, optionally opens tmate, sets up cluster resources, collects udev logs, selects a block device, runs the object test subset with `SKIP_CLEANUP_POLICY=false`, collects `object-ns` logs, uploads failure artifacts, and can open upterm.

## State and Persistence Behavior

Object-store resources, pools, buckets, secrets, and logs are runner-local. Only failure artifacts persist.

## Dependencies and Integration Points

It integrates with go-ceph preview APIs through `GOFLAGS`, local setup, object integration tests, and log collection scripts.

## Risks and Edge Cases

Splitting TLS and non-TLS by Kubernetes version optimizes coverage but may miss cross-version TLS-specific regressions. Object tests are long-running and depend on RGW readiness.

## Test Signals

Passing confirms RGW object workflows work without TLS on oldest supported Kubernetes and with TLS on latest supported Kubernetes.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-object-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-setup-cluster-resources/action.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-setup-cluster-resources/action.yaml

## Purpose

Composite action that prepares a GitHub runner for Rook canary and integration tests.

## Important APIs, Types, and Functions

Input `kubernetes-version` controls minikube. Steps free disk space, set up Go 1.26, install `cri-dockerd`, set up minikube `1.38.0` with Docker runtime, Calico CNI, ingress addon, 6 GB memory and 2 CPUs, install dependencies, print cluster status, prepare local disk for integration tests, and build Rook.

## Control Flow

The action runs sequentially before test jobs. It removes selected tool-cache content, installs runtime tooling, creates a single-node minikube cluster using `driver: none`, installs project dependencies, prepares disks, then builds local images/binaries.

## State and Persistence Behavior

It mutates runner disk, system packages, minikube state, local Docker/runtime state, and Rook build outputs. All state is ephemeral to the job but consumed by later steps.

## Dependencies and Integration Points

It integrates with `jlumbroso/free-disk-space`, `actions/setup-go`, Mirantis cri-dockerd release packages, `medyagh/setup-minikube`, `tests/scripts/github-action-helper.sh`, and every canary/integration workflow using it.

## Risks and Edge Cases

Network fetches for `.deb` packages and minikube setup are external points of failure. Disk cleanup choices are tuned for GitHub runners. The action always runs `use_local_disk_for_integration_test`, which can be redundant for canary jobs that prepare disks separately.

## Test Signals

A ready minikube cluster, installed dependencies, prepared local disk, and successful Rook build are the setup success signals.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-setup-cluster-resources/action.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-smoke-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-smoke-suite.yaml

## Purpose

Runs the core Ceph smoke integration suite on oldest and latest supported Kubernetes versions for PRs.

## Important APIs, Types, and Functions

The `TestCephSmokeSuite` job matrixes Kubernetes `v1.31.14` and `v1.35.5`, sets `GOFLAGS=-tags=ceph_preview`, and runs `go test -run CephSmokeSuite`.

## Control Flow

Eligible PRs trigger checkout, optional tmate, cluster setup, udev log collection, device discovery, smoke tests with `SKIP_CLEANUP_POLICY=false`, log collection for `smoke-ns`, failure artifact upload, and optional upterm.

## State and Persistence Behavior

State is limited to the ephemeral Kubernetes cluster, local block device, and integration log output. Failure artifacts persist.

## Dependencies and Integration Points

It integrates with the common setup composite, Go integration package, block device helper, and log collector.

## Risks and Edge Cases

Smoke tests are foundational and can fail from environment setup, storage device discovery, or broad Ceph/Rook regressions. The job is skipped for `skip-ci`.

## Test Signals

Passing indicates the baseline Rook/Ceph deployment path succeeds on both supported Kubernetes bounds.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-smoke-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-upgrade-suite.yaml -->
# sources/control-plane/rook/.github/workflows/integration-test-upgrade-suite.yaml

## Purpose

Runs Rook and Helm upgrade integration tests on PRs.

## Important APIs, Types, and Functions

The workflow has `TestCephUpgradeSuite` running `CephUpgradeSuite/TestUpgradeRook` and `TestHelmUpgradeSuite` running `CephUpgradeSuite/TestUpgradeHelm`. Both matrix Kubernetes `v1.31.14` and `v1.35.5`; the Helm job installs Helm `v3.18.2` and creates a Helm tag.

## Control Flow

Each job follows checkout, optional debugging, setup composite, udev log collection, block-device discovery, targeted `go test`, log collection for the `upgrade` namespace, artifact upload on failure, and optional upterm.

## State and Persistence Behavior

Upgrade state is held in the ephemeral test cluster, old/new Rook deployment artifacts, Helm release metadata, and integration output logs.

## Dependencies and Integration Points

It integrates with Go upgrade tests, Helm, setup and debug composites, Make/build outputs from setup, and collection scripts.

## Risks and Edge Cases

Upgrade tests are order-sensitive and resource-intensive. The Helm upgrade path depends on `create_helm_tag` and installed Helm version. Both jobs skip on `skip-ci`.

## Test Signals

Passing indicates Rook binary/manifest upgrade and Helm upgrade paths work across the supported Kubernetes matrix.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-test-upgrade-suite.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-tests-on-release.yaml -->
# sources/control-plane/rook/.github/workflows/integration-tests-on-release.yaml

## Purpose

Runs the main integration test matrix on pushes to `master`, release branches, and version tags.

## Important APIs, Types, and Functions

Jobs cover Helm suite, multi-cluster deploy, smoke suite, Rook upgrade, Helm upgrade, object without TLS, and object with TLS. Most jobs matrix Kubernetes `v1.31.14`, `v1.32.13`, `v1.33.12`, and `1.35.5`; object jobs use oldest/latest split.

## Control Flow

Release branch or tag pushes trigger full checkout, cluster setup, targeted Go tests, namespace-specific log collection, and failure artifact upload. This workflow omits PR debug composites and failfast flags present in PR workflows.

## State and Persistence Behavior

State is per-job and ephemeral in minikube, devices, Helm tags/releases, namespaces, and integration output logs. Failure artifacts persist.

## Dependencies and Integration Points

It integrates with the setup composite, all core Go integration suites, `github-action-helper.sh`, and release branch gating. Its check names are referenced by Mergify backport automerge rules.

## Risks and Edge Cases

Several matrix values use `1.35.5` without the `v` prefix while other workflows use `v1.35.5`; minikube may accept it, but it is inconsistent. The multi-cluster job sets `export BLOCK="$/dev/${DEVICE_NAME}"`, which looks like a typo and may produce an invalid block path if the test consumes `BLOCK`.

## Test Signals

Passing indicates the release branches pass the full integration suite across the configured Kubernetes versions.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/integration-tests-on-release.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/linters.yaml -->
# sources/control-plane/rook/.github/workflows/linters.yaml

## Purpose

Runs YAML and Python linting plus Python formatting checks.

## Important APIs, Types, and Functions

Jobs are `yaml-linter`, which runs `make lint.yaml`, and `pylint`, which sets up Python 3.12, installs `pylint`, `requests`, and `pygit2`, runs `make lint.python`, then invokes `psf/black`.

## Control Flow

Push and PR triggers start both jobs with PR concurrency cancellation. Each checks out full history before running Makefile/action-based linting.

## State and Persistence Behavior

No persistent state is written. Python packages are installed in the ephemeral runner.

## Dependencies and Integration Points

It integrates with `Makefile` lint targets, `.yamllint`, Python scripts across the repo, and Mergify check names `yaml-linter` and `pylint`.

## Risks and Edge Cases

The `psf/black` action is invoked after pylint without explicit arguments; its exact default behavior matters. Installing `pylint` twice is redundant but harmless.

## Test Signals

Passing jobs indicate YAML files and Python scripts satisfy current lint and formatting gates.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/linters.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/mod-check.yml -->
# sources/control-plane/rook/.github/workflows/mod-check.yml

## Purpose

Verifies Go module files are tidy and generated module state is current.

## Important APIs, Types, and Functions

The `modcheck` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make -j $(nproc) mod.check`, then validates with `tests/scripts/validate_modified_files.sh modcheck`.

## Control Flow

After checkout and Go setup, the Makefile `go.mod.check` target is run in parallel, and the worktree is checked for unexpected module changes.

## State and Persistence Behavior

Any `go.mod` or `go.sum` updates happen only in the runner and fail validation if not committed.

## Dependencies and Integration Points

It integrates with Go modules, Makefile `mod.check`, validation scripts, and Mergify-required `modcheck`.

## Risks and Edge Cases

Module resolution depends on network access and proxy availability. Parallelism can expose nondeterminism in module checks.

## Test Signals

Passing means module files and generated module metadata are already committed.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/mod-check.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/multus.yaml -->
# sources/control-plane/rook/.github/workflows/multus.yaml

## Purpose

Runs focused Multus validation tests for user-facing CLI and stretch cluster networking behavior.

## Important APIs, Types, and Functions

The `test-validation-tool` job triggers on pushes and PRs touching Multus-related paths, sets `NUMBER_OF_COMPUTE_NODES=5`, creates a KinD cluster from `tests/scripts/multus/kind-config.yaml`, builds `rook` with `go build -tags=ceph_preview`, and runs several shell tests from `tests/scripts/multus`.

## Control Flow

The job checks out, sets up Go, creates KinD, optionally enables debugging, installs Multus and NADs, builds the binary, runs CLI validation, labels nodes, runs overlap and cleanup tests, taints nodes, then runs public+cluster, public-only, and cluster-only stretch tests. Later tests use `if` dependencies on earlier step outcomes.

## State and Persistence Behavior

State is held in the KinD cluster, node labels/taints, Multus resources, NADs, and the built `rook` binary. No artifacts are uploaded by this workflow.

## Dependencies and Integration Points

It integrates with `cmd/rook/userfacing`, `pkg/daemon/multus`, KinD, Multus scripts, Kubernetes manifests under `tests/scripts/multus`, and debug composites.

## Risks and Edge Cases

The path filter excludes many general code changes that could still affect Multus indirectly. Conditional step chaining means one early failure skips dependent coverage, which is useful diagnostically but reduces signals in a single run.

## Test Signals

Passing means Multus setup, CLI validation, stretch overlap detection, cleanup, and public/cluster network validation scripts succeeded in KinD.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/multus.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/push-build.yaml -->
# sources/control-plane/rook/.github/workflows/push-build.yaml

## Purpose

Builds, signs, and releases Rook images on pushes to master, release branches, and version tags.

## Important APIs, Types, and Functions

The `push-image-to-container-registry` job runs only in `rook/rook`, grants `contents: read`, `packages: write`, and `id-token: write`, logs into Docker Hub, Quay, and GHCR, configures AWS credentials, installs cosign and Python dependencies, configures git identity, then runs `tests/scripts/build-release.sh`.

## Control Flow

Checkout disables persisted credentials, Go 1.26 and QEMU are set up, registry and AWS credentials are configured from secrets, `BRANCH_NAME` and `GITHUB_REF` are exported, Python dependencies are installed, git identity is set to Rook, and the release script handles the actual build/publish flow.

## State and Persistence Behavior

State is written outside the runner to registries, AWS-backed release destinations, GitHub packages, signatures, and possibly release metadata. Runner-local build state is ephemeral.

## Dependencies and Integration Points

It integrates with Docker/QEMU, cosign OIDC keyless signing, Docker Hub, Quay, GHCR, AWS, Python `pygit2`, and the release script.

## Risks and Edge Cases

This workflow has high-impact credentials and publish permissions. Failures can leave partial registry state. The release script is the main behavior owner, so reviewing only this YAML is insufficient for release safety.

## Test Signals

Successful completion means the release script built and published images/artifacts for the pushed ref.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/push-build.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/rbac-gen.yaml -->
# sources/control-plane/rook/.github/workflows/rbac-gen.yaml

## Purpose

Verifies generated RBAC manifests derived from Helm charts are current.

## Important APIs, Types, and Functions

The `gen-rbac` job sets up Go 1.26, runs `GOPATH=$(go env GOPATH) make gen-rbac`, and validates with `tests/scripts/validate_modified_files.sh gen-rbac`.

## Control Flow

Checkout with full history is followed by Go setup, RBAC generation through the Makefile, then dirty-worktree validation.

## State and Persistence Behavior

Generated RBAC output is runner-local and must match committed files.

## Dependencies and Integration Points

It integrates with Helm charts, `build/rbac/gen-common.sh`, Makefile Helm dependencies, `yq`, validation scripts, and Mergify-required `gen-rbac`.

## Risks and Edge Cases

Chart or Helm rendering changes can cascade into generated RBAC. The workflow does not honor `skip-ci`.

## Test Signals

Passing means generated RBAC manifests are reproducible from current Helm charts.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/rbac-gen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/scorecards.yml -->
# sources/control-plane/rook/.github/workflows/scorecards.yml

## Purpose

Runs OpenSSF Scorecard supply-chain analysis and uploads results as SARIF.

## Important APIs, Types, and Functions

The `analysis` job triggers on branch protection changes, weekly schedule, and pushes to `master`. It uses read-all default permissions, elevates `security-events: write` and `id-token: write`, runs `ossf/scorecard-action` with SARIF output and `publish_results: true`, uploads the SARIF artifact, and uploads SARIF to code scanning.

## Control Flow

The workflow checks out without persisted credentials, runs Scorecard, stores `results.sarif`, uploads it as a short-retention artifact, and sends it to GitHub code scanning.

## State and Persistence Behavior

Persistent outputs are OpenSSF published results, GitHub artifact, and code scanning alerts. The repo worktree is not modified.

## Dependencies and Integration Points

It integrates with OpenSSF Scorecard, GitHub code scanning, branch protection checks, and public Scorecard result publishing.

## Risks and Edge Cases

Publishing results is public for public repositories. Some Scorecard checks need additional tokens for complete branch-protection analysis, but the optional PAT is commented out.

## Test Signals

Success produces a SARIF artifact and code-scanning upload; the Scorecard score and findings are the primary security signal.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/scorecards.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/shellcheck.yaml -->
# sources/control-plane/rook/.github/workflows/shellcheck.yaml

## Purpose

Runs ShellCheck over shell scripts on pushes and pull requests.

## Important APIs, Types, and Functions

The `shellcheck` job checks out the repo and runs `make lint.shell`.

## Control Flow

Standard push/PR triggers with PR concurrency cancellation execute the job. The Makefile locates shell scripts and invokes the pinned ShellCheck binary/tool target.

## State and Persistence Behavior

No state is persisted; results are check logs/annotations.

## Dependencies and Integration Points

It integrates with the Makefile `lint.shell` target, `build/reset`, `build/sed-in-place`, and Mergify-required `Shellcheck`.

## Risks and Edge Cases

Only files found by the Makefile are checked. ShellCheck version is controlled by Makefile variables, not the workflow.

## Test Signals

Passing means shell scripts meet the configured ShellCheck warning threshold.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/shellcheck.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/snyk.yaml -->
# sources/control-plane/rook/.github/workflows/snyk.yaml

## Purpose

Runs Snyk vulnerability scanning for the main Rook repository on pushes to master, release branches, and tags.

## Important APIs, Types, and Functions

The `security` job gates on `github.repository == 'rook/rook'`, checks out full history, sets up Go 1.26, installs Snyk CLI `v1.1302.1`, and runs `snyk test --debug` with `SNYK_TOKEN` and `GOFLAGS=-buildvcs=false`.

## Control Flow

Pushes trigger setup, CLI install, and vulnerability scan. There is no PR trigger.

## State and Persistence Behavior

No repository state is written. Scan results are persisted only as GitHub check logs and Snyk-side records if the CLI reports them.

## Dependencies and Integration Points

It integrates with Snyk secrets, Go modules, Snyk CLI, and release branch security checks.

## Risks and Edge Cases

`--debug` can produce verbose logs. The scan is unavailable in forks or without `SNYK_TOKEN`. Vulnerability database updates can change results without code changes.

## Test Signals

Passing means Snyk did not find blocking vulnerabilities under the current policy and dependency graph.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/snyk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/stale.yaml -->
# sources/control-plane/rook/.github/workflows/stale.yaml

## Purpose

Automates marking and closing stale issues and pull requests.

## Important APIs, Types, and Functions

The `stale` job runs daily at 20:00 UTC in `rook/rook`, grants issue and PR write permissions, and uses `actions/stale` with separate stale/close windows for issues and PRs plus label exemptions.

## Control Flow

On schedule, the action scans issues and PRs, applies `wontfix` to stale issues and `stale` to stale PRs, comments with configured messages, and closes after the configured inactivity windows unless exempt labels are present.

## State and Persistence Behavior

Persistent state is GitHub issue/PR labels, comments, and closed status.

## Dependencies and Integration Points

It integrates with GitHub Issues/PRs, `GITHUB_TOKEN`, and labels `keepalive`, `security`, and `reliability`.

## Risks and Edge Cases

The stale issue label is `wontfix`, which carries semantic meaning beyond stale state. Incorrect label exemptions could close work that should stay active.

## Test Signals

Successful scheduled runs update stale candidates according to policy and leave exempt items untouched.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/stale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/tmate_debug/action.yml -->
# sources/control-plane/rook/.github/workflows/tmate_debug/action.yml

## Purpose

Composite action that conditionally starts a detached tmate SSH session for CI debugging.

## Important APIs, Types, and Functions

Inputs are required `use-tmate` and optional `debug-ci`. The first step sets `ENABLE_TMATE=1` when runner debug or `debug-ci` is true and the repository owner is `rook`, `use-tmate` is non-empty, or the run attempt is greater than one. The second step uses `mxschmitt/action-tmate` with `detached: true`.

## Control Flow

Callers place this near the beginning of a job. If conditions are met, environment state is exported and the tmate action starts an SSH session.

## State and Persistence Behavior

It writes `ENABLE_TMATE` to `$GITHUB_ENV` and creates an external interactive SSH session for the live job only.

## Dependencies and Integration Points

It integrates with runner debug mode, PR `debug-ci` labels, repository secrets, GitHub run attempt metadata, and many integration/canary workflows.

## Risks and Edge Cases

`limit-access-to-actor: false` allows broader access than actor-only sessions. This is intentionally powerful and must stay gated by repository/secret/rerun conditions.

## Test Signals

When enabled, logs should show a detached tmate connection string; otherwise the action should be a no-op.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/tmate_debug/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/unit-test.yml -->
# sources/control-plane/rook/.github/workflows/unit-test.yml

## Purpose

Runs Rook unit tests and verifies jq-dependent liveness probe tests are not skipped.

## Important APIs, Types, and Functions

The `unittests` job sets up Go 1.26, installs jq through `dcarbone/install-jq-action` using workflow-dispatch input `version` defaulting to `1.7`, exports `ROOK_UNIT_JQ_PATH`, unsets `AZURE_EXTENSION_DIR`, runs `make -j $(nproc) test`, tees output, then greps for a skip message.

## Control Flow

Push, PR, and manual dispatch events trigger the job unless `skip-ci` is present. After tests run, a second step fails if the output indicates the MDS liveness probe jq tests were skipped because jq was unknown.

## State and Persistence Behavior

No repository state persists. Test output is in runner-local `output.txt` and GitHub logs.

## Dependencies and Integration Points

It integrates with Makefile unit tests, Go modules, jq-dependent unit tests, Azure KMS tests affected by `AZURE_EXTENSION_DIR`, and Mergify-required `unittests`.

## Risks and Edge Cases

The grep check assumes exact skip-message text. Manual dispatch can test alternate jq versions. Unsetting `AZURE_EXTENSION_DIR` prevents host runner configuration from influencing unit tests.

## Test Signals

Passing means unit tests completed and jq-backed MDS liveness probe tests actually ran.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/unit-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/upterm_debug/action.yml -->
# sources/control-plane/rook/.github/workflows/upterm_debug/action.yml

## Purpose

Composite action that conditionally starts an upterm SSH debugging session near job completion.

## Important APIs, Types, and Functions

Input `debug-ci` enables the action when runner debug or the PR label is true and the repository owner is `rook` or the run attempt is greater than one. It uses `owenthereal/action-upterm` with `limit-access-to-actor: false` and a five-minute wait timeout.

## Control Flow

Callers invoke this as a post-job step. The first step exports `ENABLE_UPTERM`, and the second starts the session if that env var is set.

## State and Persistence Behavior

It only affects the live runner by opening an interactive session. No repository state is written.

## Dependencies and Integration Points

It integrates with PR labels, runner debug, reruns, GitHub repository owner metadata, and canary/integration workflows.

## Risks and Edge Cases

Because detached mode is not implemented and access is not actor-limited, this action is security-sensitive and can hold jobs for interactive access until timeout.

## Test Signals

When enabled, logs show an upterm session; otherwise the action is skipped.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.github/workflows/upterm_debug/action.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.golangci.yaml -->
# sources/control-plane/rook/.golangci.yaml

## Purpose

Configures golangci-lint for Rook's Go codebase.

## Important APIs, Types, and Functions

The config uses golangci version schema `2`, sets build tag `ceph_preview`, disables default linters, enables `errcheck`, `govet`, `gosec`, `ineffassign`, `staticcheck`, and `unused`, applies common exclusion presets, suppresses specific staticcheck quick-fix/deprecation texts, and enables `gofmt` and `gofumpt` formatters.

## Control Flow

The golangci workflow/action reads this file to determine build tags, lint set, exclusions, and formatters. Build tags allow go-ceph preview account APIs to compile during analysis.

## State and Persistence Behavior

The file has no runtime persistence. It controls CI lint output and local lint behavior.

## Dependencies and Integration Points

It integrates with `.github/workflows/golangci-lint.yaml`, Makefile `golangci-lint`, go-ceph preview APIs, and staticcheck/gosec behavior.

## Risks and Edge Cases

Text-based exclusions can hide future unrelated diagnostics matching the same text. Keeping default linters disabled makes the enabled list explicit but requires maintenance when new linters are desired.

## Test Signals

Passing golangci checks reflect this exact linter and formatter configuration.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.golangci.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.markdownlint-cli2.cjs -->
# sources/control-plane/rook/.markdownlint-cli2.cjs

## Purpose

Defines Rook's markdownlint-cli2 rules for documentation.

## Important APIs, Types, and Functions

The CommonJS module disables default rules, enables selected rules for list indentation, tab handling, ordered list prefixes, blank lines around lists/fences, fenced code style and language, duplicate headings, link fragments, trailing newline, and maximum blank lines. It also loads custom rules `markdownlint-admonitions.js` and `markdownlint-tab-spacing.js`.

## Control Flow

Docs linting actions and Makefile targets pass this config to markdownlint-cli2. Custom rules enforce mkdocs-specific admonition and tab spacing behavior.

## State and Persistence Behavior

The file is static lint policy. It does not write state.

## Dependencies and Integration Points

It integrates with `docs-check.yml`, Makefile `lint.markdown`, mkdocs rendering requirements, and custom scripts under `tests/scripts`.

## Risks and Edge Cases

Disabling defaults means only explicitly enabled rules run. The `language_only` property is unquoted while other keys are quoted, which is valid JavaScript but stylistically mixed.

## Test Signals

Passing docs markdownlint checks indicate docs conform to this mkdocs-oriented policy.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.markdownlint-cli2.cjs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/.mergify.yml -->
# sources/control-plane/rook/.mergify.yml

## Purpose

Automates conflict comments, release-branch guidance, backport creation, and automerge of Mergify-created backport PRs.

## Important APIs, Types, and Functions

Rules comment on conflicts and direct PRs to release branches. Four automerge rules cover `release-1.17` through `release-1.20`, requiring author `mergify[bot]`, no `do-not-merge` label, DCO, many CI status/check successes, canary matrix jobs, and integration suite checks. Backport rules map labels `backport-release-*` to target branches.

## Control Flow

Mergify evaluates pull request conditions. Matching conflict/release-branch rules comment. Matching backport labels create backport PRs. Matching automerge rules merge with method `merge` and dismiss reviews after all checks pass.

## State and Persistence Behavior

Persistent state is PR comments, generated backport PRs, merges into release branches, and dismissed reviews.

## Dependencies and Integration Points

It is tightly coupled to GitHub Actions workflow names, job names, matrix labels, DCO status, release branch names, and repository labels.

## Risks and Edge Cases

Hard-coded check names are brittle; workflow rename, matrix version change, or job split can block automerge. Large repeated condition lists require careful branch-specific maintenance. The rule comments on any non-Mergify PR opened against a release branch, even legitimate direct release fixes.

## Test Signals

Correct behavior is observable through Mergify comments, created backport PRs, and automerge only after all listed checks are green.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/.mergify.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/Documentation/gen-crd-api-reference-docs/template/placeholder.go -->
# sources/control-plane/rook/Documentation/gen-crd-api-reference-docs/template/placeholder.go

## Purpose

Placeholder Go file that makes Go tooling include or vendor the CRD API reference docs template directory.

## Important APIs, Types, and Functions

The file declares `package template` and contains no functions, types, or variables.

## Control Flow

There is no runtime control flow. Go tooling sees the directory as a package because this file exists.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It integrates indirectly with Go module/package discovery and CRD docs generation assets under `Documentation/gen-crd-api-reference-docs/template`.

## Risks and Edge Cases

Removing the file can cause the directory to be ignored by Go vendoring or packaging behavior. Adding logic here would be surprising because the package is only a marker.

## Test Signals

The relevant signal is successful CRD docs generation and repository packaging that includes the template directory.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/Documentation/gen-crd-api-reference-docs/template/placeholder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/Makefile -->
# sources/control-plane/rook/Makefile

## Purpose

Top-level build, test, lint, generation, docs, and cleanup entrypoint for the Rook repository.

## Important APIs, Types, and Functions

Important variables include tool versions for controller-gen, chart-testing, kustomize, markdownlint, shellcheck, yamllint image SHA, `GOBIN`, build flags, `TAGS=ceph_preview`, platform lists, package lists, `GO_PROJECT`, and linker version injection. Targets include `build.common`, `build`, `build.all`, `install`, `test`, `test-integration`, `lint.*`, `codegen`, `mod.check`, `clean`, `crds.*`, `gen-rbac`, `docs`, `docs-build`, `generate`, and `help`.

## Control Flow

The Makefile includes shared makelib files, normalizes locale and shell behavior, configures Go build/test variables, and composes high-level targets from lower-level makelib targets. Build paths generate version files, Helm deps, module checks, CRD manifests, RBAC, Go init/validation, binaries, and images. Lint and generation targets call pinned local tools and scripts.

## State and Persistence Behavior

It writes build output under `$(OUTPUT_DIR)`, working/cache directories, generated CRDs/docs/RBAC/code, temporary Helm/kustomize files, and image build artifacts. `clean`, `distclean`, and `prune` remove build/cache/image state.

## Dependencies and Integration Points

It integrates with `build/makelib/common.mk`, `helm.mk`, `golang.mk`, scripts under `build/`, Helm charts, images, Go modules, docs tooling, CI workflows, and validation scripts.

## Risks and Edge Cases

Many CI workflows rely on target names and generated-output determinism. `build.all` only supports cross-platform image build on amd64 hosts. Tool versions embedded here can break CI if updated without corresponding generated file refreshes.

## Test Signals

CI workflows exercise `make codegen`, `make crds`, `make gen-rbac`, `make lint.*`, `make mod.check`, `make test`, `make docs-build`, and Helm/chart targets. Passing workflows validate most key Makefile paths.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/checkmake.ini -->
# sources/control-plane/rook/checkmake.ini

## Purpose

Configures CheckMake's maximum recipe body length rule for the root Makefile.

## Important APIs, Types, and Functions

The file has a `[maxbodylength]` section setting `maxBodyLength = 8`.

## Control Flow

CheckMake reads this file when linting Makefile targets and applies the body-length threshold.

## State and Persistence Behavior

No state is written.

## Dependencies and Integration Points

It integrates with `checkmake.yaml`, `Uno-Takashi/checkmake-action`, and the Makefile `lint.make` target.

## Risks and Edge Cases

The low threshold encourages short targets but can require exceptions or refactors for legitimate multi-step recipes.

## Test Signals

Passing CheckMake means Makefile recipes satisfy this and other CheckMake rules.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/checkmake.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/ceph.go -->
# sources/control-plane/rook/cmd/rook/ceph/ceph.go

## Purpose

Defines the hidden top-level `rook ceph` Cobra command and shared Ceph command configuration.

## Important APIs, Types, and Functions

`Cmd` is the hidden parent command for Ceph operator and daemon commands. Package globals include `cfg`, `clusterInfo`, and `logger`. The `config` struct stores device, metadata device, data dir, force format, CRUSH location, config override, OSD store config, monitor endpoints, node name, and PVC-backed flags. `createContext()` returns a Rook cluster context with config directory/override. `addCephFlags()` registers shared Ceph flags and reads namespace from the pod namespace environment variable.

## Control Flow

Package `init()` attaches cleanup, operator, OSD, mgr, and config subcommands. Subcommands call `createContext` and `addCephFlags` as needed to share cluster identity and config handling.

## State and Persistence Behavior

This file initializes process-level globals and reads environment state. Persistent effects are produced by subcommands, not by this parent file directly.

## Dependencies and Integration Points

It integrates with Cobra, Rook context creation, Ceph client cluster info, OSD store config, Kubernetes namespace environment conventions, and all Ceph subcommands.

## Risks and Edge Cases

Global mutable `cfg` and `clusterInfo` simplify CLI wiring but couple subcommands within one process. Namespace is captured during flag registration, so callers must ensure the pod namespace environment variable exists before command execution.

## Test Signals

Coverage is indirect through command/unit tests and integration tests that launch `rook ceph operator`, OSD, mgr, cleanup, and config subcommands.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/ceph.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/cleanup.go -->
# sources/control-plane/rook/cmd/rook/ceph/cleanup.go

## Purpose

Defines `rook ceph clean` subcommands for host cleanup, filesystem subvolume group cleanup, block pool rados namespace cleanup, and block pool cleanup.

## Important APIs, Types, and Functions

Commands are `cleanUpCmd`, `cleanUpHostCmd`, `cleanUpSubVolumeGroupCmd`, `cleanUpRadosNamespaceCmd`, and `cleanUpBlockPoolCmd`. Flags include host data path, namespace dir, monitor secret, cluster FSID, sanitize method/source/iteration. Entry points are `startHostCleanUp`, `startSubVolumeGroupCleanUp`, `startRadosNamespaceCleanup`, and `startBlockPoolCleanup`.

## Control Flow

`init()` wires flags, env-derived flags, subcommands, and RunE handlers. Host cleanup removes host path/mon store when configured, builds admin cluster info, creates a disk sanitizer, and starts disk sanitization. Resource cleanup subcommands read required names from operator controller environment variables, build context/admin cluster info, and call the corresponding cleanup package function; missing environment values terminate fatally.

## State and Persistence Behavior

The file can delete host data directories, monitor store state, sanitize disks, and remove Ceph resources associated with subvolume groups, rados namespaces, or block pools. It reads Kubernetes namespace and cleanup target names from environment variables.

## Dependencies and Integration Points

It integrates with `pkg/daemon/ceph/cleanup`, Ceph API clients, Ceph CRD types, operator controller env constants, Rook logging/flag env helpers, and Kubernetes pod namespace conventions.

## Risks and Edge Cases

Cleanup is destructive by design. Incorrect environment variables or flags can target the wrong resource or disk. `startBlockPoolCleanup` logs startup info using `cleanUpRadosNamespaceCmd.Flags()` instead of block pool flags, which looks like a copy/paste bug affecting logs.

## Test Signals

Integration/canary OSD removal and cleanup policy tests provide end-to-end signals. Unit tests for cleanup package functions cover lower-level behavior outside this command wrapper.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/config.go -->
# sources/control-plane/rook/cmd/rook/ceph/config.go

## Purpose

Implements `rook ceph config-init`, a helper that writes a minimal Ceph config for non-Ceph daemons such as nfs-ganesha.

## Important APIs, Types, and Functions

`configCmd` requires `--keyring` and `--username`. `initConfig()` validates flags, reads `ROOK_CEPH_MON_HOST`, builds a minimal `[global]` plus user section config, writes it to `cephclient.DefaultConfigFilePath()` with mode `0444`, and logs the file.

## Control Flow

`init()` registers required flags and assigns `RunE`. Execution sets log level, logs startup flags, validates values, reads the monitor host env var, writes the config file, and returns.

## State and Persistence Behavior

The command writes `/etc/ceph/ceph.conf` or the default path returned by the Ceph client package. The config contains monitor hosts and keyring path for the supplied user.

## Dependencies and Integration Points

It integrates with Cobra, Rook logging, Ceph client default config path, utility file logging, and pod environment variables shared by Ceph daemon pods.

## Risks and Edge Cases

The config is built by string concatenation from CLI/env values; these are expected controlled pod inputs. Missing keyring, username, or monitor host terminates fatally. The written file is world-readable, but it contains a keyring path rather than the key itself.

## Test Signals

Tests should verify required flag handling, missing env failure, file content, permissions, and default path behavior. Integration signals come from daemons that rely on generated config.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/mgr.go -->
# sources/control-plane/rook/cmd/rook/ceph/mgr.go

## Purpose

Defines the Ceph manager sidecar command that watches the active mgr daemon and updates Kubernetes labels accordingly.

## Important APIs, Types, and Functions

Commands are `mgrCmd` and `mgrSidecarCmd` (`watch-active`). Flags include dashboard and monitoring enablement, update interval, cluster ID/name, daemon name, raw Ceph version, and shared Ceph flags. `runMgrSidecar()` initializes cluster info and loops forever. `reconcileMgr()` compares current active mgr to the previous active mgr and calls `mgr.SetMgrRoleLabel`.

## Control Flow

On startup, the sidecar reads the mounted Ceph secret, parses monitor endpoints, logs flags, builds owner info, writes Ceph config, parses the update interval and Ceph version, then repeatedly reconciles labels and sleeps. Reconciliation fetches active mgr from Ceph, skips label updates when unchanged, refreshes the current CephCluster spec from Kubernetes, constructs a mgr controller helper, and updates the local daemon's `mgr_role` label based on active status.

## State and Persistence Behavior

The command writes Ceph config locally and persistently mutates Kubernetes pod/service labels through the mgr controller. It tracks only `activeMgr` in process memory between loops.

## Dependencies and Integration Points

It integrates with Ceph monitor secrets, Rook clientsets, Ceph mgr client APIs, Kubernetes owner references, Ceph version parsing, operator mgr controller logic, and monitoring/dashboard label preservation.

## Risks and Edge Cases

Invalid intervals or Ceph version strings terminate startup. The infinite loop only logs reconcile errors and continues. Label correctness depends on active mgr names matching daemon names and on being able to refresh the CephCluster spec each time active mgr changes.

## Test Signals

Unit tests can target `reconcileMgr` with fake mgr/client behavior; integration tests validate active mgr label updates and service routing during mgr failover.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/mgr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/operator.go -->
# sources/control-plane/rook/cmd/rook/ceph/operator.go

## Purpose

Defines the `rook ceph operator` command that starts the Rook-Ceph Kubernetes operator.

## Important APIs, Types, and Functions

`operatorCmd` registers `--enable-machine-disruption-budget`, imports Go standard flags, sets flags from `ROOK_` environment variables, and runs `startOperator()`. `containerName` is `rook-ceph-operator`.

## Control Flow

Execution sets logging, logs flags, creates a cluster context, forces config dir to `k8sutil.DataDir`, validates the pod namespace env var, checks operator resources, discovers the operator image and base Ceph version, stores the base version in controller global state, gets the service account name, constructs the Ceph operator, and calls `op.Run()`.

## State and Persistence Behavior

The command starts long-lived controller loops that reconcile Kubernetes and Ceph resources. This wrapper also updates process-global `opcontroller.OperatorCephBaseImageVersion`.

## Dependencies and Integration Points

It integrates with Cobra, Rook command helpers, Kubernetes clientsets, operator resource discovery, image/service-account discovery, Ceph base image version detection, and `pkg/operator/ceph`.

## Risks and Edge Cases

Missing pod namespace is fatal. Failure to detect base image Ceph version is logged but not fatal, so downstream logic must tolerate an empty or unknown version. Adding standard flags to Cobra can expose klog/client flags through the operator command.

## Test Signals

Operator startup unit tests and integration canaries validate command wiring indirectly by deploying the operator and reconciling clusters.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/cmd/rook/ceph/operator.go -->
