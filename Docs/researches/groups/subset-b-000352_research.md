# Research: subset-b-000352

Grouped research for CSI hostpath snapshot metadata/state files, shared CSI release-tools files, and the csi-driver-iscsi node plugin, manifests, workflows, and maintenance scripts. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned per-file output.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata_test.go -->
## sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata_test.go

Purpose: unit-tests hostpath snapshot metadata block scanning for both delta and allocated metadata. The tests exercise `newFileBlockReader`, `seekToStartingOffset`, and `getChangedBlockMetadata` with synthetic sparse-like image files built from fixed-size 4096-byte blocks.

Control flow is table-driven. Delta cases create source and target files, overwrite selected target blocks, then loop until `io.EOF`, collecting pages and validating both total metadata and page count under `maxResult`. Allocated cases use an empty base path and validate that all target blocks are reported, with variable-length metadata coalescing contiguous ranges.

State and persistence are temporary files only; helpers create and mutate block contents with `os.CreateTemp`, `Seek`, and `Write`. Dependencies include CSI `BlockMetadata`, hostpath `state.BlockSizeBytes`, and the unlisted block reader implementation. Risks covered include off-by-one offsets, different source/target sizes, pagination, starting offsets, and variable-length coalescing. Gaps include gRPC stream behavior, cancellation/deadline handling, invalid offsets, and real sparse file allocation semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadata_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadataserver.go -->
## sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadataserver.go

Purpose: implements CSI SnapshotMetadata streaming APIs for the hostpath driver. `GetMetadataAllocated` returns allocated blocks for one ready block-mode snapshot; `GetMetadataDelta` returns changed blocks between two ready snapshots of the same source volume.

Control flow validates IDs, fetches snapshots and volume records from `hp.state`, enforces `ReadyToUse` and `state.BlockAccess`, defaults `MaxResults` to 256, initializes a file block reader with snapshot paths, seeks to `StartingOffset`, then streams response pages until EOF. Cancellation and deadlines are treated as clean early exits; EOF sends any final partial block list; other reader errors become `Internal`.

State is read-only driver state plus snapshot files under `hp.getSnapshotPath`. Persistence is delegated to the state package and file snapshots. Dependencies include CSI generated interfaces, gRPC status codes, klog, and hostpath state constants. Risks include returning raw `GetVolumeByID` errors without normalizing codes, no explicit validation of negative `MaxResults`, suppressed cancellation as success, and block metadata correctness depending on the file reader. Test signal is mostly through `snapshotmetadata_test.go`, which covers lower-level scanning rather than server argument/status paths.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/hostpath/snapshotmetadataserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/state/state.go -->
## sources/control-plane/csi-driver-host-path/pkg/state/state.go

Purpose: defines the persistent in-driver state model for hostpath volumes, snapshots, and group snapshots. It exposes the `State` interface used by the driver to retrieve, list, update, and delete resources while keeping optional JSON state on disk synchronized.

Important types are `Volume`, `Snapshot`, `GroupSnapshot`, `AccessType`, and `resources`. `New` constructs a `state`, restores JSON from the configured path, and each update/delete mutation calls `dump`, which marshals all resources and writes the whole state file with mode `0600`. Getters scan slices by ID or name and return gRPC `NotFound` statuses. Listing methods return shallow copies of the slices.

State and persistence are simple whole-file JSON snapshots; there is no locking, transactional write/rename, or duplicate-name enforcement. `equalIDs` sorts slices in place when comparing group snapshot source/snapshot IDs, which mutates caller-owned slices. Dependencies are standard JSON/os/sort plus gRPC status and protobuf timestamps. Risks include lost updates under concurrent calls, partial statefile writes, shallow-copy aliasing of nested `Strings`/slices, and unintentional mutation from `Matches*`. Tests cover persistence, not-found codes, deletion idempotency, multiple snapshots per source, and group snapshot basics.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/state/state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/state/state_test.go -->
## sources/control-plane/csi-driver-host-path/pkg/state/state_test.go

Purpose: verifies the hostpath state store's basic CRUD and restore behavior for volumes, snapshots, and group snapshots. The tests create a temporary `state.json`, mutate state, reconstruct with `New`, and assert resources survive reload.

Control flow is direct and resource-specific: `TestVolumes`, `TestSnapshots`, and `TestVolumeGroupSnapshots` check empty initial lists, `NotFound` error codes/messages, add/update visibility by ID/name, reconstruction, delete, idempotent second delete, and final empty lists. `TestSnapshotsFromSameSource` asserts two snapshots can share one source volume ID.

State is local temp-file JSON created by `state.dump`. Dependencies include `testify/require` and gRPC `status.Convert`. Risks covered are persistence regression and accidental uniqueness constraints on snapshot source. Gaps include update replacement semantics, corrupted JSON, empty statefile path behavior, group snapshot match helpers, slice-copy aliasing, concurrent access, and statefile write failure handling.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/state/state_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/state/strings.go -->
## sources/control-plane/csi-driver-host-path/pkg/state/strings.go

Purpose: provides `Strings`, an ordered string-set-like helper used on `Volume.Staged` and `Volume.Published` paths. It supports append, membership, emptiness, and removing the first matching entry.

The API is intentionally small: `Add` appends without de-duplication, `Has` scans linearly, `Empty` checks length, and `Remove` deletes the first occurrence by slice splicing. State is in-memory slice contents, persisted only when embedded in a volume and passed to `UpdateVolume`.

Dependencies are none beyond Go slices. Risks are naming: the comment says set, but duplicate values are possible and only one duplicate is removed per call. Because methods mutate through a pointer receiver, callers must persist the owning `Volume` after modifications. Test signal is indirect through node publish/stage behavior outside this file; there are no focused tests for duplicates or ordering.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/pkg/state/strings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.github/dependabot.yaml -->
## sources/control-plane/csi-driver-host-path/release-tools/.github/dependabot.yaml

Purpose: configures Dependabot for the csi-release-tools repository copy. It enables beta ecosystems and checks GitHub Actions in the repository root daily.

Control flow is declarative: Dependabot opens up to ten action-update PRs and labels them `area/dependency`, `release-note-none`, and `ok-to-test`. There is no runtime state besides GitHub's dependency update queue.

Dependencies and integration points are GitHub Dependabot and the workflows in `.github/workflows`. Risks include action churn from daily updates and the high PR limit compared with application repos. Test signal is GitHub platform validation of the YAML and actual Dependabot PR creation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.github/workflows/codespell.yml -->
## sources/control-plane/csi-driver-host-path/release-tools/.github/workflows/codespell.yml

Purpose: runs spelling checks on pushes and pull requests for csi-release-tools. It checks out the repo and invokes `codespell-project/actions-codespell`.

Control flow is a single Ubuntu job with pinned action SHAs. It checks filenames and skips binary/image files, checksums, `.git`, the workflow itself, and `prow.sh`. State is GitHub Actions job state only.

Dependencies are GitHub Actions, `actions/checkout`, and codespell. Risks include stale pinned action SHAs, broad skip patterns hiding typos in important scripts, and spelling-only coverage. Test signal is workflow pass/fail on PRs and pushes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.github/workflows/trivy.yaml -->
## sources/control-plane/csi-driver-host-path/release-tools/.github/workflows/trivy.yaml

Purpose: scans the Go toolchain image used by csi-release-tools for vulnerabilities. It runs on master pushes and daily schedule.

Control flow checks out code, extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh` with shell tools, then scans `golang:<version>` using `aquasecurity/trivy-action` with all severity levels and `ignore-unfixed`. State is workflow output and Trivy database cache managed by the action.

Dependencies are GitHub Actions, pinned checkout and Trivy actions, Docker Hub `golang` tags, and the exact `prow.sh` config line format. Risks include fragile grep/awk parsing, false positives or failures when upstream Go image tags disappear, and scanning only the Go image rather than repo-built images. Test signal is scheduled/push CI failure on vulnerability detection.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.prow.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/.prow.sh

Purpose: custom Prow entrypoint for testing csi-release-tools itself. Unlike consuming repos that source `prow.sh`, this repository validates its own scripts and boilerplate.

Control flow is sequential with `bash -e`: run `verify-shellcheck.sh`, `verify-spelling.sh`, and `verify-boilerplate.sh` against the current working tree. It has no persistent state and depends on those scripts to install or find their tools.

Integration points are Prow jobs for the release-tools repo. Risks include limited coverage: it does not execute the large `prow.sh` e2e orchestration, cloud build path, or Go helper behavior beyond lint/headers/spelling. Test signal is direct Prow pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/boilerplate/boilerplate.py -->
## sources/control-plane/csi-driver-host-path/release-tools/boilerplate/boilerplate.py

Purpose: validates source file license headers against template files in the boilerplate directory. It is used by `verify-boilerplate.sh`.

Important functions are `get_refs`, `file_passes`, `file_extension`, `normalize_files`, `get_files`, `get_regexs`, and `main`. Control flow loads `boilerplate.*.txt` references by extension, walks the root directory unless filenames are passed, skips vendor/generated/cache-like paths, strips Go build constraints and shell/Python shebangs, normalizes the first detected year to `YEAR`, and prints files whose headers do not match.

State is process-local file lists and regexes; it does not modify files. Dependencies are Python standard libraries: argparse, difflib, glob, os, re, sys, and `date`. Risks include substring-based skip matching, `refs[extension]` lookup failures for unsupported extensions, only replacing the first year-like line, and Python 2 style compatibility expectations. Test signal is indirect through verify script failure and diff output in verbose mode.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.sh

Purpose: thin entrypoint for Google Cloud Build image publishing in repos that import csi-release-tools.

Control flow sources `release-tools/prow.sh` from the current repository and calls `gcr_cloud_build`, which configures Docker credentials, optional QEMU emulation, and `make push-multiarch`. State and persistence are Cloud Build workspace files, Docker credentials, and pushed images controlled by the sourced function.

Dependencies are bash, the release-tools subtree location, gcloud, Docker, Go, and Make targets in the consuming repo. Risks include assuming the script is invoked from repo root and that `release-tools/prow.sh` is available; all substantial behavior is hidden in the sourced script. Test signal is Cloud Build success/failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.yaml -->
## sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.yaml

Purpose: shared Google Cloud Build configuration for multi-architecture CSI image builds. It documents the required symlink/import pattern for consuming repos.

Control flow is declarative: a two-hour timeout, loose substitutions, one `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud` step executing `./.cloudbuild.sh`, and env values for git tag, base ref, staging registry, and HOME. Substitutions define placeholder `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

State is Cloud Build execution state and pushed images. Dependencies include the image builder container, `.cloudbuild.sh`, release-tools `gcr_cloud_build`, Docker buildx, and repo Makefile targets. Risks include stale builder image pin, loose substitutions masking missing inputs, and a single entrypoint coupling all repos to shared release-tools behavior. Test signal is image-pushing job result.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/contrib/get_supported_version_csi-sidecar.py -->
## sources/control-plane/csi-driver-host-path/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper for maintainers to list supported Kubernetes CSI sidecar versions and, optionally, release Docker images for documentation updates.

Important APIs are `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`. Control flow uses `gh release list` to group releases by major/minor, treats latest minor as supported, supports older minors if first release is under one year old or latest patch under three months old, and can scrape `docker pull` lines from release notes.

State is remote GitHub release metadata read through the `gh` CLI. Dependencies include `dateutil.relativedelta`, subprocess, regex parsing, and authenticated/available GitHub CLI. Risks include policy drift, timezone/current-date dependence, fragile tab field parsing of `gh` output, and regex assumptions in release notes. Test signal is manual output review; no automated tests are present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/filter-junit.go -->
## sources/control-plane/csi-driver-host-path/release-tools/filter-junit.go

Purpose: command-line tool that filters and merges JUnit XML files so Prow artifacts contain only relevant testcases. It is used by `prow.sh` for E2E and sanity result post-processing.

Important types are `TestResults`, `TestSuite`, `TestCase`, and `SkipReason`. Control flow parses flags `-o` and `-t`, compiles the testcase regex, reads input files, supports both `<testsuite>` and Ginkgo v2 `<testsuites><testsuite>` formats, filters testcase names, de-duplicates by name, and prefers a non-skipped result over an all-skipped one before marshaling XML.

State is in-memory XML structs. Dependencies are standard `encoding/xml`, `flag`, `os`, and `regexp`. Risks include broken stdin reading because `os.Stdin.Read(data)` reads into a nil slice, missing JUnit attributes not represented in structs, map iteration nondeterminism, and panic-based error handling. Test signal is indirect via Prow artifact generation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/generate-patch-release-notes.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/generate-patch-release-notes.sh

Purpose: maintainer automation for generating patch release changelog PRs across Kubernetes CSI repos.

Control flow defines a commented `releases` array, computes previous patch version from each target, checks out a `release-x.y` branch, runs the Kubernetes `release-notes` tool with `CSI_RELEASE_TOKEN`, prepends generated notes to `CHANGELOG-x.y.md`, commits, force-pushes to the user's fork, and opens a GitHub PR with `release-note NONE`.

State and persistence include local repo branches, changelog files, commits, pushed branches, and PRs. Dependencies are bash, git remotes named upstream/origin, `gh`, `release-notes`, GitHub credentials, and repo layout. Risks include destructive branch deletion/force push, empty default release list hiding non-use, fragile semantic version parsing, and no update path for existing PRs. Test signal is manual; it is not part of normal CI.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/generate-patch-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/go-get-kubernetes.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/go-get-kubernetes.sh

Purpose: updates Go module dependencies that originate from `kubernetes/kubernetes` staging modules to a target Kubernetes version.

Control flow parses `-p` for pruning unused replaces, fetches the target Kubernetes `go.mod`, extracts staging modules, adds or drops `replace` directives using `go mod edit`, discovers imported `k8s.io` packages via `go list all` or dependency fallback, maps package modules to replaced staging modules, and runs `go get` with `@kubernetes-x.y.z` or `@vX.Y.Z` for `k8s.io/kubernetes` packages.

State is `go.mod` and module cache changes in the consuming repo. Dependencies include curl, sed/grep, Go modules, network access to GitHub/proxies, and Kubernetes staging module version conventions. Risks include partial go.mod edits before failure, brittle text parsing, package/module ambiguity, and pruning based on potentially failing `go mod graph`. Test signal is downstream `go mod tidy`, vendor checks, and CI builds.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/go-modules-targeted-update.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/go-modules-targeted-update.sh

Purpose: batch maintenance script for updating selected Go modules across release branches of CSI sidecar repos.

Control flow defines organization, target modules, and a commented repo/branch list. For each enabled entry it fetches upstream, recreates a `module-update-$branch` branch from upstream, runs `go get` for each module, tidies and vendors, commits all changes, force-pushes, and opens a PR using `gh`.

State is local repo checkouts, branches, go.mod/go.sum/vendor changes, commits, remote branches, and PRs. Dependencies are bash, git, Go modules, vendoring, GitHub CLI, `GITHUB_USER`, and repo remotes. Risks include force push, no build/test step, no incompatibility handling beyond comments, and inactive default config. Test signal is downstream CI on opened PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/go-modules-targeted-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/go-modules-update.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/go-modules-update.sh

Purpose: broad batch updater that refreshes release-tools and Kubernetes dependencies across many Kubernetes CSI repos.

Control flow logs into GitHub CLI, iterates a here-doc repo/branch matrix, updates each local checkout, pulls csi-release-tools as a git subtree with conflict fallback that replaces the subtree from `FETCH_HEAD`, retries `release-tools/go-get-kubernetes.sh -p <version>` with tidy/vendor repair, commits all changes, runs `make test`, force-pushes, and opens a PR.

State includes local branches, release-tools subtree files, module/vendor files, commits, remotes, and PRs. Dependencies are git subtree, gh, Go, make, network access, and a fork username. Risks include destructive branch deletion, force push, branch/base mismatch in PR creation for non-master branches, merge conflict auto-resolution by wholesale subtree replacement, and partial updates after failed retries. Test signal is `make test` and downstream PR CI.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/go-modules-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/prow.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/prow.sh

Purpose: shared CSI Prow and Cloud Build orchestration script. It builds repo binaries/images, runs unit tests, provisions kind clusters, deploys CSI drivers and snapshotter components, runs Kubernetes E2E and csi-sanity, collects artifacts, and supports multi-arch image publishing.

Important APIs are configuration helpers (`configvar`, `get_versioned_variable`, `version_to_git`), tool installers (`install_kind`, `install_ginkgo`, `install_dep`), git helpers, cluster lifecycle (`start_cluster`, `delete_cluster_inside_prow_job`), deployment helpers (`find_deployment`, `install_csi_driver`, snapshot CRD/controller installers), test runners (`run_e2e`, `run_sanity`, `make_test_to_junit`), `main`, and `gcr_cloud_build`.

State spans temp work dirs under GOPATH, ARTIFACTS, Docker images, kind clusters, kubeconfig, checked-out external repos, generated scripts/JUnit XML, and pushed multi-arch images. Dependencies include bash, Go toolchains, Docker, kind, kubectl, ginkgo, csi-sanity, GitHub/git, Kubernetes E2E, and repo Makefile conventions. Risks are high operational coupling, many version pins/defaults, fragile shell parsing and sed YAML edits, potential cluster cleanup gaps outside Prow, and broad environment assumptions. Test signal is Prow job success, JUnit artifacts, cluster logs, and Cloud Build results.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/pull-test.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/pull-test.sh

Purpose: validates csi-release-tools changes by importing the current checkout into another repository and running that repository's Prow script.

Control flow enables lazy blob fetches for Prow partial clones, records the current release-tools directory, changes to `$PULL_TEST_REPO_DIR`, hard-resets the target repo, pulls the release-tools subtree from the local directory, prints recent commits, and execs `./.prow.sh`.

State and persistence include destructive target repo working tree reset and subtree merge commit state. Dependencies are git subtree, environment variable `PULL_TEST_REPO_DIR`, and the target repo's `.prow.sh`. Risks include the explicit `git reset --hard`, assuming target repo has clean disposable checkout, and testing only one consuming repo at a time. Test signal is downstream `.prow.sh` outcome.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/update-vendor.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/update-vendor.sh

Purpose: normalizes vendored dependencies for repos using either dep or Go modules.

Control flow checks for `Gopkg.toml` and runs `dep ensure`; otherwise if `go.mod` exists, it warns about the configured Go version through `verify-go-version.sh`, then runs `go mod tidy` and `go mod vendor` with modules enabled.

State is dependency metadata and vendor directory changes. Dependencies are dep, Go modules, and release-tools location. Risks include no `set -e`, so some failures may not stop later commands depending on shell behavior; it assumes invocation from repo root and a `release-tools` subtree. Test signal is follow-up `verify-vendor.sh` or git diff.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/util.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/util.sh

Purpose: shared shell utility library, mostly inherited from Kubernetes scripts. It provides helpers for sourced variables, dates, array membership, trap composition, resilient downloads, background-job waiting, joining, sorted-file checks, and color constants.

Control flow is function-only; sourcing the file defines helpers and readonly color variables if unset. `download_file` retries curl five times, `wait-for-jobs` aggregates background job failures, and `trap_add` prepends a command to existing traps.

State is shell function/variable namespace and caller traps. Dependencies are bash, date, curl, diff, sort, awk, and jobs. Risks include global namespace pollution, trap command quoting complexity, a suspicious `rm "${destination_file}" 2&> /dev/null` redirection typo, and process-substitution dependency in the sort checker. Test signal is indirect via scripts such as `verify-shellcheck.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-boilerplate.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-boilerplate.sh

Purpose: CI verifier for license boilerplate headers in repos importing csi-release-tools.

Control flow enables strict bash modes, ensures a `python` command exists by linking python3 through `update-alternatives` when missing, resolves tool and root paths, runs `boilerplate.py --verbose`, and fails if any file paths are returned. It creates a temp file and trap cleanup, but does not use the temp file for actual unit tests despite the comment.

State is temp file only, plus potential system `update-alternatives` modification. Dependencies are bash, Python, boilerplate templates, and root path layout. Risks include requiring privileges for `update-alternatives`, unused temp-file/unit-test logic, and filename splitting if boilerplate output contains spaces. Test signal is printed failing file list.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-go-version.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-go-version.sh

Purpose: warns developers when their Go major/minor version differs from the version configured for CSI Prow builds.

Control flow requires a Go binary path, extracts major.minor from `go version` with sed, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a large warning if versions differ. It does not fail on mismatch.

State is none beyond sourced shell variables. Dependencies are bash, sed, the Go binary, and release-tools path. Risks include sourcing the very large `prow.sh` for one variable, version parsing drift, and warning-only behavior allowing incompatible local runs. Test signal is console output during update/vendor scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-go-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-logcheck.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-logcheck.sh

Purpose: verifies contextual klog usage with `sigs.k8s.io/logtools/logcheck`.

Control flow uses strict bash, accepts an optional logcheck version defaulting to 0.10.0, resolves the repo root above release-tools, creates a temp GOBIN, installs `logcheck@v<version>`, then runs it with `-check-contextual -check-with-helpers` over the repo.

State is a temporary install directory removed on exit. Dependencies are Go install, network/module proxy, and logcheck's static analysis rules. Risks include toolchain/network failures, analyzing all packages under the parent root including generated/vendor-adjacent files unless excluded by logcheck, and version drift. Test signal is command exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-logcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-shellcheck.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-shellcheck.sh

Purpose: runs shellcheck over shell scripts in a repo, using either a matching host binary or a pinned Docker image.

Control flow sources `util.sh`, finds non-ignored `*.sh` files outside excluded directories, detects shellcheck 0.6.0, otherwise starts a long-lived Docker container mounted at the root, runs shellcheck with disabled rules 1090 and 2230 for each script, collects all lint outputs, and fails if any exist. Cleanup removes the container through a composed trap.

State is a Docker container named `k8s-shellcheck` when host shellcheck is unavailable. Dependencies are bash, git check-ignore, Docker, shellcheck image, and util trap helper. Risks include fixed container name collisions, old shellcheck version, dependency on Docker in CI, and excluding only `*.sh` files while some executable shell snippets may lack extension. Test signal is aggregate lint output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-spelling.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-spelling.sh

Purpose: runs spelling checks over tracked files with `misspell`.

Control flow creates a temporary directory, installs `github.com/client9/misspell/cmd/misspell@v0.3.4` there when missing, runs `git ls-files | grep -v vendor | xargs misspell`, prints any findings prefixed with `error:`, and exits nonzero when the error log is non-empty.

State is temp install/log directory removed by trap. Dependencies are bash, Go install, git, xargs, and misspell. Risks include filenames with spaces, broad vendor-only exclusion, old misspell module path, and network install during verification. Test signal is CI failure plus printed misspell suggestions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-subtree.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-subtree.sh

Purpose: verifies that a git-subtree-managed directory has no local non-upstream modifications.

Control flow requires a directory argument, finds the most recent non-merge commit touching that directory with `git log --remove-empty --no-merges`, and fails with the non-merge log if one exists; otherwise it reports the directory as a clean upstream copy.

State is git history only. Dependencies are POSIX shell and git. Risks include trusting merge commits completely, so local edits hidden in merge commits bypass the check; also, legitimate downstream patches are rejected. Test signal is CI failure with relevant commit history.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-vendor.sh -->
## sources/control-plane/csi-driver-host-path/release-tools/verify-vendor.sh

Purpose: verifies dependency metadata and vendor directories are up to date for dep or Go module repos.

Control flow uses `dep check` for supported dep versions. For Go modules, Prow presubmits can skip the check when diffs do not touch dependency-relevant files/imports. Otherwise it runs `go mod tidy`, fails if go.mod/go.sum change, optionally runs `go mod vendor`, and fails if vendor changes.

State is potentially modified go.mod/go.sum/vendor in the working tree during verification. Dependencies are bash, git, dep or Go modules, and Prow environment variables for skip logic. Risks include `${JOB_NAME}` under unset-variable shells, imperfect import-diff heuristic, and leaving modified files after failure. Test signal is git diff/status output and exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-host-path/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.cloudbuild.sh -->
## sources/control-plane/csi-driver-iscsi/.cloudbuild.sh

Purpose: csi-driver-iscsi Cloud Build entrypoint for image publishing.

Control flow sources `release-tools/prow.sh` and invokes `gcr_cloud_build`, inheriting the shared multi-arch build/push behavior. State is Cloud Build workspace, Docker/gcloud authentication, built binaries/images, and remote registry tags.

Dependencies are release-tools subtree, Makefile `push-multiarch` support from `release-tools/build.make`, Docker buildx, Go, and Cloud Build substitution variables. Risks are minimal in this wrapper but high through the sourced shared script; it assumes repo-root execution and correct release-tools import. Test signal is Cloud Build image-pushing job success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/dependabot.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/dependabot.yaml

Purpose: configures Dependabot for csi-driver-iscsi dependencies. It checks Go modules, GitHub Actions, and Dockerfile dependencies daily.

Control flow is declarative. Gomod and actions checks run at root with one open PR each; Docker checks run in `./` daily at 01:00 Asia/Shanghai and add `kind/cleanup` in addition to dependency labels.

State is GitHub Dependabot queue and PRs. Dependencies are GitHub's gomod/actions/docker ecosystems. Risks include low PR limit causing backlog, daily Docker churn, and timezone-specific scheduling. Test signal is Dependabot PR creation and downstream CI.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/codeql-analysis.yml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/codeql-analysis.yml

Purpose: runs CodeQL analysis for the Go codebase on master/release pushes, matching pull requests, and daily schedule.

Control flow sets up Go `^1.18`, checks out code, initializes CodeQL for Go, runs `make all` as autobuild, then performs analysis. Permissions allow security event upload.

State is GitHub Actions build and CodeQL database/upload state. Dependencies include pinned setup-go/checkout/codeql actions and Makefile compatibility with the chosen Go. Risks include old Go setup relative to newer lint/trivy workflows, CodeQL build failures when vendor/toolchain changes, and only Go language coverage. Test signal is CodeQL alerts or workflow failure.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/codespell.yml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/codespell.yml

Purpose: spelling check workflow for csi-driver-iscsi.

Control flow runs on push and pull_request, checks out code, and invokes codespell with filename checks. It skips Git metadata, the workflow, images/checksums, vendor, go.sum, release-tools/prow.sh, and the iSCSI library path, with ignored words for storage-specific terms.

State is workflow run output only. Dependencies are GitHub Actions and codespell action. Risks include broad skip of `./pkg/lib/iscsi/` path that may not match current `pkg/iscsilib`, stale ignore list, and spelling-only coverage. Test signal is workflow pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/darwin.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/darwin.yaml

Purpose: verifies the Go packages compile and unit tests pass on macOS.

Control flow runs on push and pull_request, sets up Go `^1.18`, checks out code, runs `make`, then `go test -v -race ./pkg/...`. State is Actions job output.

Dependencies are macos-latest, setup-go, Makefile, and Go tests. Risks include the iSCSI plugin being Linux-oriented, so meaningful mount/iscsiadm behavior is not exercised on Darwin; `make` builds linux binary by default. Test signal is compile/race-test status for packages that support macOS.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/darwin.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/golangci-lint.yml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/golangci-lint.yml

Purpose: runs golangci-lint as a static check on pushes and pull requests.

Control flow sets up Go `^1.22`, checks out the repository, and runs the pinned `golangci/golangci-lint-action` with default configuration. State is workflow output and linter cache managed by the action.

Dependencies are GitHub Actions, setup-go, checkout, and golangci-lint. Risks include different Go version than build workflows, default linter config drift through action version, and possible vendor/module behavior mismatch. Test signal is linter findings.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/golangci-lint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/linux.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/linux.yaml

Purpose: primary Linux CI workflow for build, csi-sanity, and repository verification.

Control flow sets up Go `^1.18`, checks out code, runs `make`, then `make sanity-test` with `$HOME/.local/bin` added, followed by `./hack/verify-all.sh`. State includes built binaries, any sanity-test cluster/process artifacts, and generated verification diffs if checks mutate files.

Dependencies are Ubuntu, Go, Makefile, `test/sanity/run-test.sh`, and hack verify scripts. Risks include old Go relative to current dependencies, sanity-test environmental assumptions, and verify scripts that may install tools with apt/go. Test signal is workflow pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/linux.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/pluto.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/pluto.yaml

Purpose: checks Kubernetes manifests for deprecated API versions using Pluto.

Control flow runs on push and pull_request, checks out code, downloads Pluto through `FairwindsOps/pluto/github-action`, and runs `pluto detect-files -d deploy`. State is workflow output only.

Dependencies are GitHub Actions and Pluto's API deprecation database. Risks include scanning only `deploy`, not `examples`, and action database drift. Test signal is failure when deploy manifests use deprecated or removed Kubernetes APIs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/pluto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/shellcheck.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/shellcheck.yaml

Purpose: runs ShellCheck for repository scripts on version-tag/master/release pushes and matching pull requests.

Control flow checks out code and invokes `ludeeus/action-shellcheck` with warning severity, together mode, GCC format, and `SHELLCHECK_OPTS=-e SC2034`. It ignores vendor, release-tools, and hack paths.

State is workflow output only. Dependencies are pinned shellcheck action. Risks include ignoring the `hack` directory where many repo scripts live, so this workflow misses most listed shell scripts; separate `hack/verify-all.sh` covers some of that on Linux. Test signal is shellcheck annotations for non-ignored scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/shellcheck.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/trivy.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/trivy.yaml

Purpose: builds the csi-driver-iscsi container and scans it for OS and library vulnerabilities with Trivy.

Control flow runs on master pushes and daily schedule, sets up Go 1.25.11, checks out code, builds a local `test/iscsi-csi:latest` image through `make test-container`, then scans it with pinned `aquasecurity/trivy-action`, all severities, and `ignore-unfixed`.

State is a local Docker image and Trivy database/cache. Dependencies include Docker buildx, Makefile, Dockerfile, Go, Trivy, and public ECR Trivy DB. Risks include Go version divergence from normal build workflows, full failure on all severities causing noise, and scan results depending on live vulnerability DB. Test signal is workflow failure on vulnerabilities or build errors.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/windows.yaml -->
## sources/control-plane/csi-driver-iscsi/.github/workflows/windows.yaml

Purpose: verifies Go package tests on Windows.

Control flow uses a matrix with Go `^1.18` and `windows-latest`, checks out code, prints `go version`, and runs `go test -v -race ./pkg/...`. State is workflow output only.

Dependencies are setup-go, checkout, and package portability. Risks include most runtime iSCSI behavior being Linux/host-specific and therefore untested; compile-only portability is still useful for shared code. Test signal is race-test pass/fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.github/workflows/windows.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.prow.sh -->
## sources/control-plane/csi-driver-iscsi/.prow.sh

Purpose: Prow entrypoint for csi-driver-iscsi using shared csi-release-tools.

Control flow disables Kubernetes E2E by setting `CSI_PROW_E2E_REPO=none`, defaults `CSI_PROW_TESTS` to `unit`, defaults Kubernetes version to 1.14.0 for potential sanity hostpath context, sources `release-tools/prow.sh`, and calls `main`.

State and persistence are inherited from `prow.sh`: build artifacts, unit test JUnit, Docker image if kind tests are enabled, and Prow artifacts. Dependencies are release-tools, Makefile targets, and Prow environment. Risks include controller/plugin functionality relying on unit tests only unless sanity is manually enabled; all behavior is sensitive to shared release-tools changes. Test signal is Prow job result.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/Dockerfile -->
## sources/control-plane/csi-driver-iscsi/Dockerfile

Purpose: builds the runtime image for the iSCSI CSI plugin.

Control flow starts from `registry.k8s.io/build-image/debian-base:bookworm-v1.0.8`, upgrades packages, unholds `libcap2`, installs filesystem/mount/iSCSI tools (`util-linux`, `e2fsprogs`, `mount`, `udev`, `xfsprogs`, `btrfs-progs`, `open-iscsi`), sets a default command to start `iscsid`, copies the architecture-specific `iscsiplugin` binary, and uses it as entrypoint.

State in the image includes installed packages and copied binary. Runtime state depends on privileged host mounts and `/var/run/iscsi.csi.k8s.io`. Dependencies are Debian package repositories, build args `ARCH` and `binary`, and Makefile build output. Risks include `CMD service iscsid start` being overridden by `ENTRYPOINT`, mutable `apt upgrade`, privileged runtime requirements, and vulnerability exposure from OS packages. Test signal is container build and Trivy workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/Makefile -->
## sources/control-plane/csi-driver-iscsi/Makefile

Purpose: defines build, container, sanity, module-check, and clean targets for the iSCSI CSI plugin.

Control flow includes `release-tools/build.make`, sets image/build variables, builds a static Linux `bin/${ARCH}/iscsiplugin` with vendor mode, builds Docker images via `docker buildx`, runs sanity through `./test/sanity/run-test.sh`, verifies modules, and cleans built artifacts. `all` maps to `iscsi`.

State includes `bin/<arch>/iscsiplugin`, Docker images, and Go module verification output. Dependencies are Go, vendor directory, Docker buildx, release-tools Make rules, and sanity scripts. Risks include Linux-only build target regardless of host, stale `CMDS=iscsiplugin` interactions with release-tools, `mod-check` using a fragile shell hash comparison, and clean removing only `bin/iscsiplugin` not `bin/${ARCH}`. Test signal comes from CI make, sanity, and container workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/cloudbuild.yaml -->
## sources/control-plane/csi-driver-iscsi/cloudbuild.yaml

Purpose: repo-local Cloud Build configuration, equivalent to the shared release-tools template, for publishing csi-driver-iscsi images.

Control flow uses a two-hour timeout, loose substitutions, a single builder step executing `./.cloudbuild.sh`, and environment variables for git tag, base ref, staging registry, and HOME. Placeholder substitutions define `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

State is Cloud Build job state and pushed images. Dependencies include `.cloudbuild.sh`, shared release-tools, Docker buildx, Makefile image targets, and staging project configuration. Risks mirror the shared template: stale builder image pin, loose substitutions hiding misconfiguration, and central coupling to `gcr_cloud_build`. Test signal is Cloud Build success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/cmd/iscsiplugin/main.go -->
## sources/control-plane/csi-driver-iscsi/cmd/iscsiplugin/main.go

Purpose: command-line entrypoint for the iSCSI CSI node plugin.

Control flow defines `--endpoint` defaulting to `unix:///csi/csi.sock` and `--nodeid`, initializes klog flags, parses flags, constructs a driver with `iscsi.NewDriver`, and blocks in `d.Run`. State is limited to parsed flags and the driver/server created by the package.

Dependencies are Go flag/os, klog, and `pkg/iscsi`. Integration points are container args in `deploy/csi-iscsi-node.yaml` and kubelet's CSI socket path. Risks include no validation that `nodeid` is non-empty before serving and unconditional `os.Exit(0)` after `handle`. Test signal is build/compile coverage; no dedicated main tests are present.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/cmd/iscsiplugin/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-driverinfo.yaml -->
## sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-driverinfo.yaml

Purpose: declares the CSI driver object for Kubernetes.

Control flow is Kubernetes declarative configuration: a `storage.k8s.io/v1` `CSIDriver` named `iscsi.csi.k8s.io` with `attachRequired: false` and both `Persistent` and `Ephemeral` lifecycle modes. There is no executable logic or local persistence.

Integration points are kubelet, external sidecars, and the node plugin DaemonSet. Risks include advertising ephemeral support even though controller operations are unimplemented and node-only behavior depends on volume attributes; attach is disabled so controller publish is skipped. Test signal is Pluto API-version checks and install script `kubectl apply`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-driverinfo.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-node.yaml -->
## sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-node.yaml

Purpose: deploys the iSCSI CSI node plugin as a privileged Linux DaemonSet with liveness and node-driver-registrar sidecars, plus a ConfigMap wrapper for host `iscsiadm`.

Control flow is Kubernetes declarative scheduling. The pod uses host networking, mounts kubelet plugin and registration directories, `/dev`, the host root, a writable run directory, and a ConfigMap-provided `/sbin/iscsiadm` that chroots into the host to find and run host iSCSI tools. The main container serves `/csi/csi.sock` and exposes a health port checked by the liveness sidecar.

State and persistence are hostPath directories, kubelet registration sockets, iSCSI sessions/devices on the host, and `/var/run/iscsi.csi.k8s.io` connector JSON files. Dependencies include privileged Linux nodes, host open-iscsi tooling, sidecar images, mount propagation, and kubelet plugin registration. Risks are high privilege, host root/device access, stale sidecar image versions, hostNetwork necessity, and failure when host `iscsiadm` paths differ. Test signal includes install scripts, Pluto, yamllint, and runtime Kubernetes rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/csi-iscsi-node.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/install-driver.sh -->
## sources/control-plane/csi-driver-iscsi/deploy/install-driver.sh

Purpose: installs the csi-driver-iscsi manifests into a cluster.

Control flow defaults version to `master`, builds a raw GitHub deploy URL or uses `./deploy` when the second argument contains `local`, appends `/$ver` for non-master, and applies driverinfo and node manifests with kubectl. State changes are Kubernetes API resources in the target cluster.

Dependencies are bash, kubectl, network access to GitHub for remote versions, and manifest paths. Risks include unquoted `[ $ver != "master" ]`, raw URL path assumptions for non-master versions, and applying privileged DaemonSet directly. Test signal is kubectl success and subsequent DaemonSet rollout.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/install-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/uninstall-driver.sh -->
## sources/control-plane/csi-driver-iscsi/deploy/uninstall-driver.sh

Purpose: removes csi-driver-iscsi manifests from a cluster.

Control flow mirrors install: choose master or specified version, optionally use local deploy files, append version subdirectory for non-master, then `kubectl delete -f` driverinfo and node manifests. State changes are deletion of Kubernetes resources.

Dependencies are bash, kubectl, manifest availability, and cluster access. Risks include unquoted version test, failures if resources already absent, and leaving host-side iSCSI sessions, mountpoints, sockets, or connector JSON if workloads are still using volumes. Test signal is kubectl delete status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/deploy/uninstall-driver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/pod.yaml -->
## sources/control-plane/csi-driver-iscsi/examples/pod.yaml

Purpose: example workload consuming the iSCSI CSI PersistentVolumeClaim.

Control flow is declarative: a Linux-selected `nginx` Pod mounts PVC `iscsiplugin-pvc` at `/var/www`. State is Kubernetes pod lifecycle and the mounted filesystem inside the container.

Dependencies are the PVC/PV example pair, a running CSI node plugin, an accessible iSCSI target, and Linux nodes. Risks include no readiness/cleanup guidance, fixed PVC name, and generic nginx image not validating writes. Test signal is manual pod readiness and mount inspection; `verify-yamllint.sh` may lint the file.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/pv.yaml -->
## sources/control-plane/csi-driver-iscsi/examples/pv.yaml

Purpose: example static PersistentVolume for an external iSCSI target.

Control flow declares a 1Gi `ReadWriteOnce` PV using CSI driver `iscsi.csi.k8s.io`, `volumeHandle: iscsi-data-id`, selector label `name=data-iscsiplugin`, and volume attributes consumed by `getISCSIInfo`: `targetPortal`, `portals`, `iqn`, `lun`, interface, discovery, and CHAP flags.

State is Kubernetes PV binding state and external iSCSI target state. Dependencies include a real target at the hard-coded portal, matching PVC selector, and driver node publish code. Risks include placeholder IP/IQN, `discoveryCHAPAuth: true` without secret attributes, `portals` encoded as JSON string, and no Secret object. Test signal is manual bind/publish success and yamllint.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/pv.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/pvc.yaml -->
## sources/control-plane/csi-driver-iscsi/examples/pvc.yaml

Purpose: example claim that binds to the static iSCSI PV.

Control flow declares a `ReadWriteOnce` 1Gi PVC in storage class `manual` with a selector matching label `name=data-iscsiplugin`. State is Kubernetes PVC binding state.

Dependencies are the PV example's label and storage class, and the default namespace unless applied elsewhere. Risks include static binding only, no dynamic provisioning despite StorageClass presence, and hard-coded name expected by the pod example. Test signal is PVC Bound status and yamllint.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/storageclass.yaml -->
## sources/control-plane/csi-driver-iscsi/examples/storageclass.yaml

Purpose: minimal StorageClass named `manual` for the static iSCSI example.

Control flow is declarative and sets `provisioner: manual`, indicating no CSI dynamic provisioning. State is Kubernetes StorageClass resource state.

Dependencies are PVC/PV examples that both reference `manual`. Risks include confusing users who expect dynamic provisioning through the iSCSI CSI driver; the driver controller CreateVolume is unimplemented. Test signal is successful apply and PVC binding to the static PV.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/examples/storageclass.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/boilerplate/boilerplate.py -->
## sources/control-plane/csi-driver-iscsi/hack/boilerplate/boilerplate.py

Purpose: repository-local boilerplate header checker for csi-driver-iscsi, adapted from Kubernetes scripts.

Important functions mirror the release-tools version: load header refs, enumerate files, strip Go build constraints and script shebangs, normalize years, diff against expected headers, and print failing paths. The root defaults three directories above the script, while the default boilerplate directory is built as `rootdir/csi-driver-nfs/hack/boilerplate`.

State is process-local file contents and regexes. Dependencies are Python standard libraries plus imported but unused `json` and `mmap`. Risks include the suspicious default boilerplate path referencing csi-driver-nfs, substring skip matching, unsupported extension key errors, and lack of focused tests. Test signal comes from `hack/verify-boilerplate.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/release-image.sh -->
## sources/control-plane/csi-driver-iscsi/hack/release-image.sh

Purpose: Azure Container Registry release helper, apparently copied from an NFS CSI workflow.

Control flow requires a registry name, exports ACR-derived registry variables, sets `IMAGENAME=public/k8s/csi/nfs-csi`, logs into Azure ACR, runs `make container push push-latest`, sleeps, pulls `mcr.microsoft.com/k8s/csi/nfs-csi:latest`, and inspects creation time.

State includes Docker login, pushed images, and local pulled image. Dependencies are Azure CLI, Docker, Make targets, and registry naming. Risks are severe for this repo: image names reference NFS rather than iSCSI, Makefile targets `push`/`push-latest` may not exist locally, variables are unquoted, and it can publish to external registries. Test signal is manual command success only.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/release-image.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/update-dependencies.sh -->
## sources/control-plane/csi-driver-iscsi/hack/update-dependencies.sh

Purpose: regenerates Go module pinning and vendor contents with explicit `require` and `replace` directives for all dependencies.

Control flow forces module mode, clears GOPATH/GOFLAGS, changes to repo root, creates temp workspace, defines optional vendor pruning, captures current require/replace JSON with `go mod edit -json` and jq, adds replace directives for versioned requirements, adds explicit indirect requires from `go list -m -json all`, pins unpinned modules, groups replace directives in go.mod with awk, runs `go mod tidy`, repeats pinning, and runs `go mod vendor`.

State is go.mod, go.sum, and vendor. Dependencies are Go modules, jq, awk, xargs, git, and network/module proxy. Risks include large invasive go.mod rewrites, xargs behavior with empty input, fragile awk regrouping, temp dir accumulation, and no tests before success. Test signal is subsequent `verify-gomod`, `verify-update`, and CI builds.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/update-dependencies.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/update-gofmt.sh -->
## sources/control-plane/csi-driver-iscsi/hack/update-gofmt.sh

Purpose: applies gofmt simplification to all non-vendor Go files.

Control flow runs `find . -name "*.go" | grep -v "/vendor/" | xargs gofmt -s -w` under strict bash. State is modified Go source files.

Dependencies are find, grep, xargs, and gofmt. Risks include filename splitting on whitespace, formatting generated files outside vendor, and requiring caller to run from repo root for intended scope. Test signal is `hack/verify-gofmt.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/update-gofmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/update-gomod.sh -->
## sources/control-plane/csi-driver-iscsi/hack/update-gomod.sh

Purpose: updates Kubernetes staging module replace directives to match a supplied Kubernetes version.

Control flow strips a leading `v` from the argument, fetches the target Kubernetes `go.mod`, extracts staging `k8s.io/*` modules, downloads each `@kubernetes-$VERSION` module, parses its resolved version, and writes a `replace` directive to go.mod.

State is go.mod and module cache. Dependencies are curl, sed, Go modules, and Kubernetes release conventions. Risks include no `go mod tidy/vendor`, brittle parsing, unquoted echo/variables, and partial updates after a network failure. Test signal is follow-up module verification and build.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/update-gomod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-all.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-all.sh

Purpose: aggregate verification entrypoint for csi-driver-iscsi.

Control flow resolves repo root and sequentially runs gofmt, govet, yamllint, boilerplate, spelling, and gomod verifiers. Golint is present but commented out. Strict bash stops on the first failure.

State may be modified by sub-checks such as `verify-gomod.sh`, which runs tidy/vendor before diffing. Dependencies are all hack verifier scripts and their tools. Risks include early exit hiding later failures, disabled golint, and checks that install tools with apt/go. Test signal is Linux workflow's verification step.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-boilerplate.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-boilerplate.sh

Purpose: validates license headers in the csi-driver-iscsi repo.

Control flow enables strict bash, ensures `python` exists by installing an alternative to python3 if missing, resolves `hack/boilerplate/boilerplate.py`, captures failing paths into an array, and prints/fails when any are present. It allocates a temp file and cleanup trap but does not use it.

State is temp file and potential system python alternative modification. Dependencies are bash, Python, boilerplate templates, and repo root detection. Risks include unquoted command substitution splitting paths, privileged `update-alternatives`, and the boilerplate script's possibly wrong default template directory. Test signal is `verify-all.sh` failure output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-examples.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-examples.sh

Purpose: applies and waits for example Kubernetes workloads, but the paths indicate it was copied from an NFS driver workflow.

Control flow defines `rollout_and_wait`, which applies a manifest, parses the created resource kind/name, then waits for rollout or ready condition. It applies `deploy/example/storageclass-nfs.yaml`, then NFS deployment/statefulset examples, and optionally an ephemeral NFS daemonset.

State is Kubernetes cluster resources. Dependencies are kubectl and example paths that are not part of the listed iSCSI examples. Risks are high mismatch with this repo, fragile parsing of `kubectl apply` output, unquoted variables, and trap typo using lowercase `err`. Test signal is manual only; it is not called by `verify-all.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-examples.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-gofmt.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-gofmt.sh

Purpose: checks that all non-vendor Go files are gofmt-simplified.

Control flow captures `gofmt -s -d` output over files found by `find|grep|xargs`, prints the diff and guidance when non-empty, and exits nonzero. State is read-only.

Dependencies are gofmt and shell utilities. Risks include filename splitting, checking generated files outside vendor, and command substitution storing large diffs in memory. Test signal is `verify-all.sh` and Linux workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-gofmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-golint.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-golint.sh

Purpose: legacy lint verifier using golangci-lint with only the deprecated `golint` linter enabled.

Control flow installs golangci-lint v1.31.0 via remote install script if missing, updates PATH, then runs `golangci-lint run --no-config --enable=golint --disable=typecheck --deadline=10m`. State is a binary installed under GOPATH/bin when absent.

Dependencies are curl, Go env, golangci-lint, and network access. Risks include remote shell install, old linter version, deprecated flags/linter, typecheck disabled, and this script not being called by `verify-all.sh`. Test signal is manual invocation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-golint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-gomod.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-gomod.sh

Purpose: verifies go.mod/go.sum/vendor are tidy and current.

Control flow enables module mode, runs `go mod tidy`, `go mod vendor`, then checks `git diff`; any diff is printed and treated as failure. State is intentionally mutated before diffing.

Dependencies are Go modules, vendor mode, git, and network/module cache. Risks include leaving working tree changes after failure, broad `git diff` detecting unrelated pre-existing modifications, backtick command substitution style, and no path-specific diff. Test signal is Linux verify-all workflow.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-gomod.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-govet.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-govet.sh

Purpose: runs `go vet` over all non-vendor packages.

Control flow executes `go vet $(go list ./... | grep -v vendor)` under strict bash. State is read-only except module cache.

Dependencies are Go tooling and successful package listing. Risks include shell word splitting, grep-based vendor exclusion, and failure if `go list` includes packages requiring platform-specific host tools. Test signal is `verify-all.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-govet.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-spelling.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-spelling.sh

Purpose: spelling verifier for tracked repository files.

Control flow resolves repo root, creates a temp directory, installs misspell v0.3.4 if needed, runs `git ls-files | grep -v vendor | xargs misspell`, prints findings prefixed with `error:`, and exits nonzero when findings exist. State is temp install/log directory.

Dependencies are bash, Go install, git, xargs, and misspell. Risks include filenames with spaces, old misspell path, broad vendor-only exclusion, and no custom domain word list unlike the GitHub codespell workflow. Test signal is `verify-all.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-update.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-update.sh

Purpose: verifies that dependency update operations did not leave uncommitted changes.

Control flow checks `git diff --shortstat`; if any diff exists it prints the full diff and exits nonzero, otherwise prints done. State is read-only git working tree inspection.

Dependencies are git. Risks include considering unrelated pre-existing user changes as update failures and ignoring untracked files. Test signal is manual or CI invocation after update scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-yamllint.sh -->
## sources/control-plane/csi-driver-iscsi/hack/verify-yamllint.sh

Purpose: lints deploy and example YAML files.

Control flow installs `yamllint` with apt when missing, loops over `deploy/*.yaml` and `examples/*.yaml`, runs `yamllint -f parsable`, filters out `line too long`, writes `/tmp/yamllint.log`, prints remaining issues, and fails if any remain.

State is `/tmp/yamllint.log` and possible apt package installation. Dependencies are apt, yamllint, glob expansion, and shell tools. Risks include no strict mode, unquoted variables, shared temp log path, ignoring line-length issues globally, and package installation requiring privileges. Test signal is `verify-all.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/hack/verify-yamllint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/controllerserver.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/controllerserver.go

Purpose: provides the CSI ControllerServer surface for the iSCSI plugin, mostly as explicit unimplemented methods.

Control flow returns `codes.Unimplemented` for create/delete/publish/list/capacity/snapshot/expand/get-volume operations. `ControllerGetCapabilities` logs and returns the driver's configured `cscap`, which is initialized to `UNKNOWN` in `NewDriver`.

State is read-only access to `Driver.cscap`. Dependencies are CSI generated interfaces, gRPC status codes, and klog. Integration point is driver registration in `Run`, and the `CSIDriver` manifest disables attach so controller publish is normally skipped. Risks include advertising controller service plugin capability from identity while all useful controller RPCs are unimplemented, and returning `UNKNOWN` capability. Test signal is compile coverage and potential csi-sanity behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/controllerserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/driver.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/driver.go

Purpose: defines the iSCSI CSI driver object, static driver name/version, capabilities, and server startup.

Important APIs are `NewDriver`, `NewNodeServer`, `Run`, `AddVolumeCapabilityAccessModes`, and `AddControllerServiceCapabilities`. Control flow logs configuration, creates `/var/run/iscsi.csi.k8s.io`, enables `SINGLE_NODE_WRITER`, adds controller `UNKNOWN`, then starts a non-blocking gRPC server with identity, controller, and node services.

State is driver metadata fields and capability slices; filesystem state is the run directory for connector JSON files. Dependencies are CSI types, os, klog, and server constructors. Risks include `panic` on run directory creation failure, global hard-coded version `0.2.0`, no validation of node ID/endpoint, and confusing controller capability configuration. Test signal is mostly build and runtime smoke/sanity.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/identityserver.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/identityserver.go

Purpose: implements CSI identity service for plugin discovery, probe, and plugin capabilities.

Control flow in `GetPluginInfo` validates driver name and version and returns them; `Probe` returns an empty success response; `GetPluginCapabilities` returns `CONTROLLER_SERVICE`. State is read-only driver metadata.

Dependencies are CSI types, gRPC status codes, and klog. Risks include advertising controller service even though controller RPCs are unimplemented, and no health details in `Probe`. Test signal comes from csi-sanity/registration behavior; no unit tests are listed.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/identityserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi.go

Purpose: parses CSI `NodePublishVolumeRequest` attributes into iSCSI connection structures and builds mounter/unmounter objects.

Important APIs include `getISCSIInfo`, `buildISCSIConnector`, `getISCSIDiskMounter`, `getISCSIDiskUnmounter`, `portalMounter`, `parseSecret`, `parseSessionSecret`, `parseDiscoverySecret`, and structs `iscsiDisk`, `iscsiDiskMounter`, `iscsiDiskUnmounter`. Control flow requires `targetPortal`, `iqn`, and `lun`; parses optional JSON `secret` and `portals`; defaults portals to port 3260; converts LUN; and builds a Kubernetes `SafeFormatAndMount`, exec interface, device handler, and iscsilib connector.

State is request-derived only. Dependencies include CSI request fields, `pkg/iscsilib`, Kubernetes mount/device utilities, JSON, strconv, and exec. Risks include secrets passed via volume context instead of CSI secrets, parseSecret silently returning nil on invalid JSON, CHAP booleans not gating required secret fields, no block-volume support, and portal strings detected by any colon which can mis-handle IPv6. Test signal is indirect via node publish and sanity tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi_util.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi_util.go

Purpose: performs the actual iSCSI attach/mount and unmount/disconnect workflow for node publish/unpublish.

`AttachDisk` validates connector presence, calls `Connect`, checks target mountpoint, creates the target directory, persists connector config to `/var/run/iscsi.csi.k8s.io/iscsi-<volumeID>.json`, builds ro/rw plus requested mount options, and calls `FormatAndMount`. `DetachDisk` resolves mount use count, skips when target path does not exist, reloads connector config, unmounts, disconnects only when count reaches zero, removes target path, and deletes the connector file.

State and persistence are host mount table, iSCSI sessions/devices, target directories, and connector JSON files. Dependencies are iscsilib, Kubernetes mount package, OS filesystem, gRPC status, and klog. Risks include persisted connector file remaining when mount fails after persistence, missing cleanup when connector file is absent, unmount-before-disconnect order assumptions, returning nil when device still in use, and sensitive connection data stored under `/var/run`. Test signal is runtime/sanity; no focused unit tests here.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/iscsi_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/nodeserver.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/nodeserver.go

Purpose: implements CSI node operations for publishing and unpublishing iSCSI volumes.

Control flow validates volume capability, volume ID, and target path in `NodePublishVolume`, parses iSCSI info, constructs a disk mounter, and calls `ISCSIUtil.AttachDisk`. `NodeUnpublishVolume` validates volume ID/target path, constructs an unmounter, and calls `DetachDisk`. `NodeStageVolume` and `NodeUnstageVolume` are no-op successes; `NodeGetInfo` returns configured node ID; `NodeGetCapabilities` returns `UNKNOWN`; stats and expand are unimplemented.

State is host mount/session state through the util layer. Dependencies include CSI generated APIs and gRPC status codes. Risks include returning `Internal` for user attribute parse errors, no staging semantics despite CSI methods succeeding, no idempotency check beyond mountpoint detection, and unknown node capability. Test signal is csi-sanity and package tests; implementation lacks direct unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/nodeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/server.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/server.go

Purpose: wraps gRPC server startup in a non-blocking interface for CSI services.

Important APIs are `NonBlockingGRPCServer`, `NewNonBlockingGRPCServer`, and methods `Start`, `Wait`, `Stop`, `ForceStop`, and `serve`. Control flow starts serving in a goroutine, parses endpoint, removes existing Unix socket, listens, installs a unary logging interceptor, registers non-nil identity/controller/node servers, and serves until fatal error.

State is a wait group and `*grpc.Server` pointer. Filesystem state includes Unix socket removal/creation. Dependencies are net, os, sync, grpc, CSI generated registration, klog, and `ParseEndpoint`. Risks include `Stop`/`ForceStop` nil panic if called before server assignment, fatal exits inside goroutine, no socket permission management, only unary interceptor, and no graceful handling of `Serve` returning after Stop. Test signal is runtime startup; no direct tests listed.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/utils.go -->
## sources/control-plane/csi-driver-iscsi/pkg/iscsi/utils.go

Purpose: utility constructors and middleware for the iSCSI CSI server.

APIs include `NewDefaultIdentityServer`, `NewControllerServer`, `NewControllerServiceCapability`, `ParseEndpoint`, and `logGRPC`. `ParseEndpoint` accepts `unix://` or `tcp://` prefixes and returns protocol/address when the address is non-empty. `logGRPC` logs method names at V(3), sanitized requests/responses at V(5), and errors.

State is none. Dependencies include CSI types, csi-lib-utils `protosanitizer`, grpc interceptors, klog, and strings/fmt. Risks include endpoint parsing that accepts arbitrary proto case as returned from input, no support for Windows named pipes or bare Unix paths, and possible log volume/noise at high verbosity. Test signal is indirect through server startup and logging behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-iscsi/pkg/iscsi/utils.go -->
