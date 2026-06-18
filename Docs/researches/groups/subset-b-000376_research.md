# subset-b-000376 Research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.github/dependabot.yaml -->
# sources/control-plane/csi-lib-utils/release-tools/.github/dependabot.yaml

## Purpose

This Dependabot configuration enables automated dependency update pull requests for GitHub Actions used by the `release-tools` repository. It opts into beta ecosystems, scans the repository root daily, and caps open Dependabot PRs at ten.

## Important Behavior

The only configured `package-ecosystem` is `github-actions` with `directory: "/"`. Dependabot-created PRs get the labels `area/dependency`, `release-note-none`, and `ok-to-test`, which integrate with Kubernetes CSI triage and Prow/GitHub automation conventions.

## State, Dependencies, and Integration

There is no runtime state. The file is interpreted by GitHub Dependabot. It directly affects update cadence for workflow pins such as checkout, codespell, Trivy, and other actions in this repository.

## Risks and Test Signals

The main risk is update noise or action breakage from daily PRs. The explicit PR limit reduces queue growth, and labels make updates easier to route. Validation is indirect: GitHub accepts or rejects the YAML, and generated PRs exercise CI workflows.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.github/workflows/codespell.yml -->
# sources/control-plane/csi-lib-utils/release-tools/.github/workflows/codespell.yml

## Purpose

This GitHub Actions workflow runs `codespell` on pushes and pull requests for the release-tools repository. It provides a repository-level spelling gate outside of Prow.

## Important Behavior

The workflow has one `codespell` job on `ubuntu-latest`. It checks out the repository using a pinned `actions/checkout` commit and invokes a pinned `codespell-project/actions-codespell` commit. Inputs enable filename checks and skip binary/image/checksum files, `.git`, the workflow file itself, and `./prow.sh`.

## State, Dependencies, and Integration

There is no persistent state. Dependencies are GitHub Actions, the checkout action, and the codespell action. It overlaps with `verify-spelling.sh`, but uses a different tool/action path than the shell verifier, giving an additional spelling signal for GitHub-native changes.

## Risks and Test Signals

Pinned action SHAs reduce supply-chain drift but require updates. The broad skip for `prow.sh` avoids noisy false positives in a large shell script, but spelling mistakes there will not be caught by this workflow. The only test signal is the workflow result in GitHub Actions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.github/workflows/trivy.yaml -->
# sources/control-plane/csi-lib-utils/release-tools/.github/workflows/trivy.yaml

## Purpose

This GitHub Actions workflow scans the configured Go build image for vulnerabilities. It runs on pushes to `master` and daily on a schedule.

## Important Behavior

The workflow checks out the repo, extracts `CSI_PROW_GO_VERSION_BUILD` from `prow.sh` by grepping the `configvar` assignment, then scans `golang:<version>` with the pinned `aquasecurity/trivy-action`. The scanner uses table output, fails with exit code `1` on findings, ignores unfixed issues, and includes all listed severities from unknown through critical.

## State, Dependencies, and Integration

State is limited to workflow outputs. It depends on the shell structure of `prow.sh`; if the `configvar CSI_PROW_GO_VERSION_BUILD` line changes shape, the extracted version can be empty or wrong. It integrates release-tool Go version policy with container vulnerability monitoring.

## Risks and Test Signals

The parsing pipeline is fragile because it is text-based. Trivy database updates can change results without source changes. The workflow itself is the test signal, and failures indicate either vulnerable base Go images or extraction/action issues.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.prow.sh -->
# sources/control-plane/csi-lib-utils/release-tools/.prow.sh

## Purpose

This repository-local Prow entrypoint tests `csi-release-tools` itself. Other CSI repositories usually source `release-tools/prow.sh`, but this repo is release tooling rather than normal Go component code, so it runs direct verification scripts.

## Important Behavior

The script is a short `bash -e` wrapper. It invokes `verify-shellcheck.sh`, `verify-spelling.sh`, and `verify-boilerplate.sh`, passing the current working directory as the root to check.

## State, Dependencies, and Integration

It has no persistent state. It depends on the three verifier scripts and their transitive tools: shellcheck or Docker, misspell/Go, Python, and boilerplate reference files. It is called by Prow jobs for the release-tools repository.

## Risks and Test Signals

Because it uses `bash -e`, the first verifier failure exits the job. It intentionally does not run the large `prow.sh` build/E2E pipeline. The test signal is the Prow job result and the individual verifier output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/csi-lib-utils/release-tools/boilerplate/boilerplate.py

## Purpose

`boilerplate.py` checks source files for Kubernetes copyright/license boilerplate headers. It can scan a supplied file list or walk a root directory, compare each supported file type against `boilerplate.*.txt` references, and print files that fail.

## Important APIs and Flow

The script parses `--rootdir`, `--boilerplate-dir`, `--verbose`, and optional filenames. `get_refs` loads boilerplate templates keyed by extension or basename. `get_files` walks the tree, prunes ignored directories, filters files by template keys, and returns candidates. `file_passes` opens each file, chooses the matching reference, strips Go build tags and script shebangs, normalizes the first copyright year to `YEAR`, and compares only the header-length prefix. `main` prints failing filenames and exits `0`; callers decide whether non-empty output is an error.

## State, Dependencies, and Integration

State is in local template files and transient scan results. Dependencies are Python standard library modules: argparse, difflib, glob, os, re, sys, and date. `verify-boilerplate.sh` wraps this script and treats printed filenames as a failing verification signal.

## Risks and Test Signals

The script assumes all scanned extensions have a loaded reference and can raise a `KeyError` if filtering and template keys diverge. It ignores many vendored/generated paths by substring, which can skip unexpected paths with matching names. Its year regex only allows years from 2014 through the current date. Test coverage is indirect through `verify-boilerplate.sh` and Prow.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/cloudbuild.sh -->
# sources/control-plane/csi-lib-utils/release-tools/cloudbuild.sh

## Purpose

This shell wrapper is the default Cloud Build entrypoint for repositories importing CSI release tools. It sources the shared Prow/release script and delegates to `gcr_cloud_build`.

## Important Behavior

The script sources `release-tools/prow.sh`, then calls `gcr_cloud_build`. That function configures Docker credentials with `gcloud`, creates work directories, optionally enables QEMU user emulation for Dockerfiles with `RUN` steps, derives `REV` from `GIT_TAG`, and runs `make push-multiarch` with the configured Go version, registry, revision, and build platforms.

## State, Dependencies, and Integration

Persistent state is created by the downstream `make push-multiarch` and Docker registry push, not by this wrapper. It depends on Cloud Build environment variables from `cloudbuild.yaml`, `gcloud`, Docker, Go, and the imported `release-tools/prow.sh`.

## Risks and Test Signals

The file assumes it is invoked from a repo that has `release-tools/prow.sh` and compatible Makefile targets. Any breakage in `prow.sh` or missing Cloud Build substitutions will surface during image publishing. Test signals are Cloud Build logs and image push results.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/cloudbuild.yaml -->
# sources/control-plane/csi-lib-utils/release-tools/cloudbuild.yaml

## Purpose

This Google Cloud Build configuration runs multi-architecture image publishing for CSI repositories that import release tools. It is intended to be symlinked or copied by component repositories.

## Important Behavior

The build timeout is two hours. `substitution_option: ALLOW_LOOSE` tolerates unused substitutions. A single build step runs `./.cloudbuild.sh` in the `gcr.io/k8s-staging-test-infra/gcb-docker-gcloud` image and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME=/root`. Default substitutions provide placeholder `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

## State, Dependencies, and Integration

State is external: built images and registry pushes. Dependencies include the Cloud Build service, staging project permissions, Docker, gcloud, and a repo-provided `.cloudbuild.sh` wrapper. It integrates with Kubernetes image-pushing jobs and k8s staging registries.

## Risks and Test Signals

The step image pin is a major supply-chain and reproducibility anchor. Repos must accept `binary` build arguments and implement `make push-multiarch` behavior expected by `prow.sh`. Cloud Build success, registry artifacts, and downstream promotion are the operational test signals.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/csi-lib-utils/release-tools/contrib/get_supported_version_csi-sidecar.py

## Purpose

This contributor utility queries GitHub releases for CSI sidecar repositories and reports supported versions according to Kubernetes CSI support policy timing. It can also print Docker image references for supported releases to help update documentation.

## Important APIs and Flow

`check_gh_command` ensures the GitHub CLI is present. `parse_version` accepts `vMAJOR.MINOR.PATCH` tags. `get_versions_from_releases` runs `gh release -R <repo> list`, parses tab-separated output and publication timestamps, and groups releases by major/minor. `end_of_life_grouped_versions` sorts each group and returns the latest patch when the first release is less than a year old or the latest patch is less than three months old. `get_release_docker_image` runs `gh release view` and regexes `docker pull ...` from release notes. `main` parses repeated `--repo`, optional display/doc flags, then prints version/date/age and optionally image names.

## State, Dependencies, and Integration

The script keeps only in-memory release lists. It depends on `gh`, Python `dateutil.relativedelta`, GitHub release formatting, and network/auth state. It integrates with manual maintenance of Kubernetes CSI documentation, especially sidecar container support tables.

## Risks and Test Signals

The release-list parser assumes `gh release list` column order and ISO timestamp format. Docker image extraction assumes release notes contain a matching `docker pull` line. The support-window logic depends on current wall-clock time. There are no automated tests; manual output sanity and `gh` failures are the test signals.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/filter-junit.go -->
# sources/control-plane/csi-lib-utils/release-tools/filter-junit.go

## Purpose

`filter-junit.go` is a small command-line tool that reads one or more JUnit XML files, keeps test cases whose names match a regular expression, de-duplicates skipped cases, and writes a merged JUnit suite. `prow.sh` uses it to reduce noisy Ginkgo/Prow artifacts.

## Important APIs and Flow

Flags are `-o` for output path or stdout and `-t` for the test-name regexp. `TestResults`, `TestSuite`, `TestCase`, and `SkipReason` model the XML needed from Ginkgo and Spyglass. `SkipReason` preserves present-but-empty `<skipped></skipped>` elements through custom marshal/unmarshal. `main` compiles the regexp, reads each input, unmarshals old `<testsuite>` or newer `<testsuites><testsuite>` formats, filters by `testcase.Name`, and replaces all-skipped entries with a real run when available.

## State, Dependencies, and Integration

The tool has no state beyond in-memory XML structures. It depends on Go `encoding/xml`, `flag`, `os`, and `regexp`. It integrates with `prow.sh` through `run_filter_junit`, which invokes `go run release-tools/filter-junit.go`.

## Risks and Test Signals

The stdin branch calls `os.Stdin.Read(data)` with a nil buffer, so stdin input is effectively not implemented correctly; Prow call sites pass files. Map iteration makes output testcase order nondeterministic. XML modeling is intentionally incomplete and may drop unknown attributes/elements. Test signals are indirect through Prow JUnit artifact generation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/generate-patch-release-notes.sh -->
# sources/control-plane/csi-lib-utils/release-tools/generate-patch-release-notes.sh

## Purpose

This bash utility automates changelog pull request creation for Kubernetes CSI patch releases. It is configured by editing an in-script `releases` array.

## Important Behavior

The script requires `CSI_RELEASE_TOKEN`, `GITHUB_USER`, `gh`, and `release-notes`. `gen_patch_relnotes` runs Kubernetes `release-notes` between the previous patch tag and the release branch. For each configured `repo version`, it parses minor and patch numbers, computes the previous patch tag, checks out an upstream release branch into a temporary changelog branch, prepends generated notes to `CHANGELOG-<minor>.md`, commits, force-pushes to the user's fork, and creates a GitHub PR with `release-note NONE`.

## State, Dependencies, and Integration

It mutates local git checkouts, temporary files, branches, remote refs, and GitHub PR state. It depends on repo remotes named `upstream` and `origin`, the GitHub CLI, the release-notes binary, GitHub auth, and changelog file conventions.

## Risks and Test Signals

The script is deliberately manual and edits need to be made before use. It force-pushes, deletes local branches, and does not update existing PRs. Regex parsing assumes numeric `MAJOR.MINOR.PATCH` without a `v` prefix in the array. Test signals are command failures, generated changelog diffs, and created PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/generate-patch-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/csi-lib-utils/release-tools/go-get-kubernetes.sh

## Purpose

This script updates Kubernetes-related Go module dependencies in CSI repositories to a target Kubernetes version or branch. It is used directly and by batch update scripts.

## Important Behavior

The script accepts `-p` to prune unused Kubernetes staging module replacements and `-h` for help, then requires one positional Kubernetes version such as `1.34.0`. It downloads the target Kubernetes `go.mod` from GitHub, extracts `k8s.io/* => ./staging/src/k8s.io/*` replacements, and for each staging module resolves the corresponding `kubernetes-<version>` module version. It writes `go mod edit -replace=<module>=<module>@<resolved-version>` entries, optionally dropping unused replacements when `-p` is enabled. It then obtains imported Kubernetes packages with `go list all`, falling back to dependency listing for `./...`, filters packages whose modules are covered by the replacements, and runs one `go get` over those packages with `@kubernetes-<version>` or `@v<version>` for `k8s.io/kubernetes/...`.

## State, Dependencies, and Integration

It mutates `go.mod` and `go.sum`; vendoring is handled by callers such as `go-modules-update.sh`. It depends on bash, curl, sed, Go modules, network access to `raw.githubusercontent.com` and Go module download endpoints, and a local Go module checkout. It integrates with manual and scripted CSI dependency update workflows.

## Risks and Test Signals

Dependency updates can introduce API incompatibilities that the script cannot resolve. The initial staging-module extraction is tied to Kubernetes `go.mod` formatting. The `go list all` fallback can still fail if the repository cannot load packages before dependency updates. Test signals are successful replacement edits, successful final `go get`, resulting module diffs, and downstream tidy/vendor/test runs in caller scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/go-modules-targeted-update.sh -->
# sources/control-plane/csi-lib-utils/release-tools/go-modules-targeted-update.sh

## Purpose

This bash utility batch-updates a specific list of Go modules across selected Kubernetes CSI repositories and release branches, then creates pull requests.

## Important Behavior

The script defines `org`, `modules`, and `releases` arrays in the file. For each configured `repo branch`, it fetches upstream, recreates a `module-update-<branch>` branch from `upstream/<branch>`, runs `go get` for every module, runs `go mod tidy` and `go mod vendor`, commits all changes, force-pushes to the user's fork, and creates a GitHub PR with a release-note-none body.

## State, Dependencies, and Integration

It mutates local repository worktrees, branches, remotes, module files, vendor trees, and GitHub PR state. It depends on Go, git, `gh`, a configured `GITHUB_USER`, an `upstream` remote, and a sibling directory layout where each target repo can be entered by name.

## Risks and Test Signals

The script does not run tests and explicitly warns that interface incompatibilities must be fixed manually. The `[ "$repo" != "#" ]` skip check only skips rows whose first field is exactly `#`, while most commented array lines are inactive shell comments. Test signals are command success, generated diffs, successful commits/pushes, and later CI on created PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/go-modules-targeted-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/go-modules-update.sh -->
# sources/control-plane/csi-lib-utils/release-tools/go-modules-update.sh

## Purpose

This shell script batch-updates Kubernetes dependencies for many CSI sidecar repositories and creates PRs. It is a broader workflow around `release-tools/go-get-kubernetes.sh`.

## Important Behavior

Options `-u` and `-v` set the GitHub username and Kubernetes target version. It runs `gh auth login`, then loops through a hardcoded here-doc of repo/branch pairs. For each branch it recreates `module-update-<branch>`, pulls the latest `release-tools` subtree, automatically replaces the subtree if a squash conflict only affects release-tools, retries `go-get-kubernetes.sh -p <version>` up to `MAX_RETRY`, runs tidy/vendor, commits, changes `origin` to the user's fork, runs `make test`, force-pushes, and creates a PR.

## State, Dependencies, and Integration

It mutates many local git checkouts, `release-tools/` subtrees, Go module/vendor files, remotes, and GitHub PRs. Dependencies include git subtree, Go, `gh`, Makefile test targets, network access, and a sibling checkout layout.

## Risks and Test Signals

The PR creation command uses `--head "$username:module-update-master"` and `--base "master"` even inside a loop over branches, which is risky for non-master branches. `git branch -d` may fail for unmerged branches. Dependency/API incompatibilities require manual fixes. Test signals are `make test`, module diffs, PR CI, and retry logs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/go-modules-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/prow.sh -->
# sources/control-plane/csi-lib-utils/release-tools/prow.sh

## Purpose

`prow.sh` is the shared CI and release-tool driver imported by Kubernetes CSI repositories. It builds components, runs unit and E2E tests in KinD, installs CSI drivers and snapshot components, runs csi-sanity, produces JUnit artifacts, and supports Cloud Build multiarch image publishing.

## Important APIs and Control Flow

Configuration is centralized through `configvar`, which sets default environment variables while allowing repo-level `.prow.sh` or job settings to override them. Helpers include `tests_enabled`, `version_to_git`, `get_versioned_variable`, `regex_join`, `ensure_paths`, `run`, `die`, and `run_with_go`. Tool installers fetch or build `kind`, `ginkgo`, `dep`, Kubernetes E2E binaries, and csi-sanity. Git helpers check out or clone external repositories.

Cluster flow uses `start_cluster` to choose or build a KinD node image, write `kind-config.yaml`, and create a two-worker cluster. Driver setup uses `find_deployment` and `install_csi_driver`, optionally loading locally built images and overriding stable/canary tags. Snapshot setup installs CRDs and snapshot-controller manifests, with special handling for external-snapshotter PRs and canary images. Test flow runs unit `make test` through `make_test_to_junit`, E2E suites through `run_e2e`, csi-sanity through `run_sanity`, and final JUnit merging through `run_filter_junit`. `main` coordinates all of this and preserves a nonzero return for failed nonfatal tests. `gcr_cloud_build` is the Cloud Build entrypoint for multiarch pushes.

## State, Dependencies, and Integration

The script creates temporary work directories under `$GOPATH/pkg`, artifact directories, KinD clusters, Docker images/tags, generated helper scripts, kubeconfig state, fetched repos, and JUnit/log artifacts. It depends on bash, Go with toolchain support, Docker, kind, kubectl, git, curl, make, ginkgo, csi-sanity, Kubernetes source, CSI hostpath/snapshotter repos, and repository Makefile conventions. It is sourced by component `.prow.sh` files and by Cloud Build wrappers.

## Risks and Test Signals

This file is high blast-radius: environment defaults, version matrices, image tags, feature gates, and regex selections define CI behavior across many repositories. Shell parsing of Makefile `CMDS`, deployment YAML image rewriting, branch/tag checkout logic, and JUnit XML generation are fragile areas. The script intentionally continues from unit failures to E2E tests but returns failure at the end. Test signals are Prow logs, JUnit artifacts, KinD cluster logs, csi-sanity output, `make` results, and Cloud Build/image push results.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/pull-test.sh -->
# sources/control-plane/csi-lib-utils/release-tools/pull-test.sh

## Purpose

This script tests a pull request against `csi-release-tools` by importing the updated release-tools subtree into another CSI repository and then running that repository's Prow entrypoint.

## Important Behavior

It enables `GIT_NO_LAZY_FETCH=0` because Prow's blobless checkout can break `git subtree pull`. It records the current release-tools directory, changes to `$PULL_TEST_REPO_DIR`, hard-resets the target worktree, pulls the release-tools subtree from the PR checkout into `release-tools`, prints recent log entries, and `exec`s `./.prow.sh`.

## State, Dependencies, and Integration

It mutates the target test repository's worktree and history. It depends on `PULL_TEST_REPO_DIR`, git subtree, Prow checkout layout, and a target repo with `.prow.sh`. It integrates release-tools PR validation with real consumer repository tests.

## Risks and Test Signals

`git reset --hard` is destructive in the target checkout but expected in disposable Prow workspaces. Subtree conflicts or missing blob fetch support fail early. The test signal is the target repository's Prow run after importing the PR version of release-tools.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/update-vendor.sh -->
# sources/control-plane/csi-lib-utils/release-tools/update-vendor.sh

## Purpose

This helper updates dependency vendoring for repositories using either legacy `dep` or Go modules.

## Important Behavior

If `Gopkg.toml` exists, it prints that the repo uses dep and runs `dep ensure`. If `go.mod` exists, it verifies the Go version through `release-tools/verify-go-version.sh "go"`, then runs `GO111MODULE=on go mod tidy` and `GO111MODULE=on go mod vendor`.

## State, Dependencies, and Integration

The script mutates dependency lock/module/vendor files. It depends on `dep` for legacy repos, Go modules for modern repos, and `release-tools/verify-go-version.sh`. It integrates with Makefile or manual maintenance flows that want a single vendoring command.

## Risks and Test Signals

It has no explicit `set -e`, but failing commands in simple scripts may still need caller handling. It silently does nothing when neither `Gopkg.toml` nor `go.mod` exists. Test signals are command exit status and resulting git diffs for module/vendor files.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/util.sh -->
# sources/control-plane/csi-lib-utils/release-tools/util.sh

## Purpose

`util.sh` provides shared bash helper functions for release-tools verifier scripts. Its most visible role is trap composition so cleanup handlers can be registered without overwriting existing traps.

## Important Behavior

The file defines Kubernetes-style shell utility helpers. `kube::util::sourced_variable` documents intentionally sourced globals for ShellCheck. `kube::util::sortable_date` emits sortable timestamps. `kube::util::array_contains` checks membership in an argument list. `kube::util::trap_add` prepends a command to existing traps for one or more signals. `kube::util::download_file` retries curl downloads up to five times. `kube::util::wait-for-jobs` waits for all current background jobs and returns a count-based failure status. `kube::util::join` joins arguments with a delimiter. `kube::util::check-file-in-alphabetical-order` diffs a file against `LC_ALL=C sort` and prints a repair command. The file also declares reusable ANSI color constants.

## State, Dependencies, and Integration

The helpers manipulate shell state in the current process: traps, readonly color variables, and function definitions. They have no file persistence except through commands that callers invoke. Integration points are verifier scripts that need cleanup, retrying downloads, background job waits, sorted-file checks, and shared shell UI conventions.

## Risks and Test Signals

Trap manipulation is subtle because quoting and signal lists must preserve existing handlers. `download_file` removes the destination before retrying, so callers should not point it at valuable files without expecting replacement. `wait-for-jobs` waits for all background jobs in the current shell, not just jobs started by one helper. Test signals are indirect through verifier scripts that source `util.sh`, particularly `verify-shellcheck.sh`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-boilerplate.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-boilerplate.sh

## Purpose

This verifier enforces Kubernetes boilerplate headers across the repository. It wraps `boilerplate/boilerplate.py` and fails when any file needs a corrected header.

## Important Behavior

The script enables strict bash options, finds the release-tools directory, defaults the checked root to the parent directory, and ensures a `python` command exists by installing a `python3` alternative if needed. It runs the boilerplate script with `--verbose`, captures failing filenames with `mapfile`, and exits nonzero after printing each bad file.

## State, Dependencies, and Integration

It creates one temporary file and installs a cleanup trap, though the captured unit-test output is not used. It depends on bash, Python, `update-alternatives` when `python` is absent, boilerplate templates, and the Python checker. It is called by `.prow.sh`.

## Risks and Test Signals

Installing `/usr/bin/python` may require privileges and is surprising outside CI containers. The script treats any output from `boilerplate.py` as failure. Test signals are printed bad filenames and the final exit code.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-go-version.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-go-version.sh

## Purpose

This script warns when a caller's Go binary does not match the Go major/minor version configured for CSI Prow builds.

## Important Behavior

It requires a path to a Go binary, runs `<go> version`, extracts major/minor with `sed`, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, and prints a large warning if the versions differ. It does not exit nonzero for mismatches.

## State, Dependencies, and Integration

There is no persistence. It depends on bash, Go, `sed`, and the side effects of sourcing `release-tools/prow.sh`. It is used by vendoring/update flows to highlight versions that can affect `gofmt`, `go mod tidy`, and vendor output.

## Risks and Test Signals

Sourcing `prow.sh` executes many `configvar` assignments and can print configuration to stdout, though the script redirects source output to `/dev/null`. Because mismatches are warnings only, callers must decide whether to enforce. The test signal is visible warning text.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-go-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-logcheck.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-logcheck.sh

## Purpose

This verifier runs `sigs.k8s.io/logtools/logcheck` to check contextual klog usage in the CSI lib utils source tree.

## Important Behavior

It accepts an optional logcheck version, defaulting to `0.10.0`. It canonicalizes the repository root as the parent of release-tools, creates a temporary `GOBIN`, installs `logcheck` with `go install`, and runs it with `-check-contextual -check-with-helpers` over the repository.

## State, Dependencies, and Integration

It creates a temporary directory removed by trap. Dependencies are bash, Go, network/module access, and the logcheck module. It integrates with CI or local verification for klog contextual logging standards.

## Risks and Test Signals

Installing a tool on every run can be slow and sensitive to module proxy/network issues. The fixed default version stabilizes checks. Test signal is the logcheck exit code and diagnostics.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-logcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-shellcheck.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-shellcheck.sh

## Purpose

This verifier runs ShellCheck across repository shell scripts, using a host binary only when it matches the required version, otherwise using a pinned Docker image.

## Important Behavior

The script sources `util.sh`, computes the root directory, disables selected ShellCheck rules, finds `*.sh` files excluding generated/vendor/git paths and git-ignored files, and decides between host `shellcheck 0.6.0` and `koalaman/shellcheck-alpine:v0.6.0` by digest. In Docker mode it starts a long-lived container, execs ShellCheck for each script, aggregates failures, and cleans up through `kube::util::trap_add`.

## State, Dependencies, and Integration

It creates a temporary Docker container named `k8s-shellcheck` and removes it at exit. Dependencies are bash, git, ShellCheck or Docker, and `util.sh`. It is one of the core `.prow.sh` checks for release-tools.

## Risks and Test Signals

The fixed container name can collide with stale or parallel runs. Running Docker requires privileges. Aggregating all failures gives complete diagnostics but can produce large logs. Test signal is the failure list and nonzero exit when any script has lint output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-spelling.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-spelling.sh

## Purpose

This verifier checks tracked repository files for spelling errors with `misspell`.

## Important Behavior

It creates a temporary directory, installs `github.com/client9/misspell/cmd/misspell@v0.3.4` if `misspell` is absent, prepends the temp dir to `PATH`, then runs `git ls-files | grep -v vendor | xargs misspell`. Misspell output is stored in a temp error log; non-empty output is prefixed with `error:` and exits nonzero.

## State, Dependencies, and Integration

Temporary state is removed by trap. Dependencies are bash, git, Go if the tool must be installed, and misspell. It is called by `.prow.sh` and complements the GitHub Actions codespell workflow.

## Risks and Test Signals

The `grep -v vendor` filter can exclude any path containing `vendor`, not just vendor directories. `xargs` behavior with unusual filenames is not fully robust. Test signals are misspell diagnostics and the final exit code.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-subtree.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-subtree.sh

## Purpose

This POSIX shell script verifies that a directory managed by `git subtree` has no local non-upstream modifications.

## Important Behavior

It requires a directory argument. It finds the newest non-merge commit that touched the directory with `git log -n1 --remove-empty --no-merges -- <dir>`. If such a commit exists, it prints the non-merge history for that directory and exits nonzero; otherwise it reports the directory is a clean upstream copy.

## State, Dependencies, and Integration

It has no persistent state and depends only on git and shell. It integrates with repositories that vendor `release-tools` or other upstream content through `git subtree` and want to ensure local edits are not made inside the imported tree.

## Risks and Test Signals

The check trusts merge commits as subtree imports, so a developer could hide local changes in a merge commit. It also assumes the subtree history is represented by merges. Test signal is the printed offending git log and exit status.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-vendor.sh -->
# sources/control-plane/csi-lib-utils/release-tools/verify-vendor.sh

## Purpose

This verifier checks that dependency metadata and the vendor directory are up to date for dep-based or Go module repositories.

## Important Behavior

For `Gopkg.toml`, it requires dep version `v0.5+` and runs `dep check`. For `go.mod`, it may skip dependency checks in Prow presubmit jobs when the diff does not touch `go.mod`, `go.sum`, `vendor`, `release-tools`, or import declarations. Otherwise it runs `GO111MODULE=on go mod tidy`, verifies `go.mod`/`go.sum` are clean, and when `vendor/` exists runs `go mod vendor` and verifies vendor is clean.

## State, Dependencies, and Integration

It mutates the worktree during verification and then checks for diffs. Dependencies include bash, git, dep or Go modules, and Prow env vars such as `JOB_NAME`, `JOB_TYPE`, and `PULL_BASE_SHA`. It integrates with Makefile `test-vendor` style targets.

## Risks and Test Signals

The Prow skip heuristic is complex and can miss dependency-affecting changes outside import hunks. Running tidy/vendor can be Go-version sensitive. Test signals are git status/diff output and a nonzero exit if files change or commands fail.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/rpc/common.go -->
# sources/control-plane/csi-lib-utils/rpc/common.go

## Purpose

This Go package provides common client-side CSI RPC helpers for querying driver identity, plugin/controller/group-controller capabilities, and probing readiness.

## Important APIs and Flow

`GetDriverName` calls Identity `GetPluginInfo` and rejects an empty name. `PluginCapabilitySet`, `ControllerCapabilitySet`, and `GroupControllerCapabilitySet` are maps keyed by CSI enum types. `GetPluginCapabilities`, `GetControllerCapabilities`, and `GetGroupControllerCapabilities` call the corresponding CSI service, skip nil capability wrappers, and populate set maps. `Probe` calls Identity `Probe` once and treats a missing `ready` field as ready per CSI spec. `ProbeForever` loops once per second, using `probeOnce` with a per-call timeout. It retries only `DeadlineExceeded` and `ready=false`; non-gRPC errors and other gRPC errors are returned.

## State, Dependencies, and Integration

There is no persistent state. Runtime state is the caller's context, gRPC connection, ticker, and transient capability maps. Dependencies include `google.golang.org/grpc`, gRPC status codes, CSI generated Go bindings, and `k8s.io/klog/v2` for contextual logging. It integrates with CSI sidecars and libraries that need standardized driver interrogation.

## Risks and Test Signals

`ProbeForever` can run indefinitely until context cancellation if a driver repeatedly times out or reports unready. Capability helpers intentionally ignore nil entries, which avoids panics but can hide malformed responses. Tests in `common_test.go` cover success, errors, empty names, nil capability entries, missing ready fields, timeout retry, unready retry, and probe-call counts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/rpc/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/rpc/common_test.go -->
# sources/control-plane/csi-lib-utils/rpc/common_test.go

## Purpose

This test file validates the RPC helper behavior in `common.go` using real gRPC servers bound to Unix sockets and fake CSI service implementations.

## Important APIs and Flow

`tmpDir` creates temporary socket directories. `startServer` creates a `grpc.Server`, conditionally registers fake Identity, Controller, and GroupController services, serves on a Unix socket in a goroutine, and returns a cleanup function that stops the server and removes the socket. Table tests cover `GetDriverName`, plugin capabilities, controller capabilities, group-controller capabilities, and `ProbeForever`. Fake service structs embed unimplemented CSI servers and return configured responses or errors. `fakeIdentityServer.Probe` consumes a planned sequence and counts calls.

## State, Dependencies, and Integration

Each test owns temp filesystem state, a Unix socket, a gRPC server goroutine, and a client connection created through the package's `connection.Connect` helper with a metrics manager. Dependencies include Go testing, gRPC, CSI generated types, wrapperspb, testify `require`, klog test contexts, and csi-lib-utils connection/metrics packages.

## Risks and Test Signals

The tests exercise real network/socket plumbing, which is stronger than pure mocks but can be sensitive to cleanup timing. They verify nil capability skipping and retry counts, but do not test context cancellation in `ProbeForever`. Passing `go test ./rpc` is the primary signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/rpc/common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/slowset/slowset.go -->
# sources/control-plane/csi-lib-utils/slowset/slowset.go

## Purpose

`slowset` implements an in-memory, concurrency-safe set of API object keys that should be retried or synchronized at a slower rate until a retention period expires.

## Important APIs and Flow

`SlowSet` embeds an RWMutex and stores `retentionTime`, `resyncPeriod`, and `workSet map[string]ObjectData`. `ObjectData` records a timestamp and storage class UID. `NewSlowSet` initializes the map and a default 100 ms resync period. `Add` inserts only if absent and returns whether it added. `Get`, `Contains`, `Remove`, and `TimeRemaining` provide map access under locks. `Contains` returns false for expired entries even before cleanup. `removeAllExpired` deletes expired keys. `Run` starts a ticker and repeatedly removes expired entries until `stopCh` closes.

## State, Dependencies, and Integration

All state is process-local memory. There is no persistence. Dependencies are Go `sync` and `time`. The package is intended for controllers or sidecars that need temporary throttling keyed by namespace/name or similar object identifiers.

## Risks and Test Signals

`TimeRemaining` can return a negative duration for expired-but-not-cleaned entries. `Run` depends on callers to provide and close a stop channel. Tests cover idempotent add behavior, expiration, pre-expiration contains, time remaining, and contains behavior for expired entries.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/slowset/slowset.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/slowset/slowset_test.go -->
# sources/control-plane/csi-lib-utils/slowset/slowset_test.go

## Purpose

This test file verifies `SlowSet` insertion, expiration, and timing behavior.

## Important Behavior

`TestSlowSet` defines table-driven cases with retention/resync durations and closures that operate on a `SlowSet`. Each subtest creates a set, overrides `resyncPeriod`, starts `Run` in a goroutine, defers closing the stop channel, then executes the scenario. Cases verify that repeated `Add` does not change stored data, keys expire after retention, keys remain before retention, `TimeRemaining` is positive and below retention, and `Contains` returns false once a present key is expired.

## State, Dependencies, and Integration

Tests use real time sleeps from 100 to 301 ms and direct access to `s.workSet` because they are in the same package. There is no external dependency beyond Go testing/time.

## Risks and Test Signals

Real-time sleeps can be flaky on overloaded CI systems, especially boundary tests around 300/301 ms. The tests cover public methods and `Run` cleanup indirectly, but they do not stress concurrent access. Passing `go test ./slowset` is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/slowset/slowset_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/standardflags/automaxprocs.go -->
# sources/control-plane/csi-lib-utils/standardflags/automaxprocs.go

## Purpose

This file adds a shared `-automaxprocs` flag for CSI sidecars and drivers. When enabled, it uses Uber's `automaxprocs` library to set `GOMAXPROCS` according to Linux container CPU quota.

## Important APIs and Flow

`AddAutomaxprocs` registers `flag.BoolFunc("automaxprocs", ...)` with `handleAutomaxprocs`. It also wraps an optional logging function into a `maxprocs.Logger`-compatible printf. `EnableAutomaxprocs` is a programmatic equivalent of setting the flag true and avoids re-enabling if already active. `automaxprocsIsEnabled` checks whether an undo function is stored. `handleAutomaxprocs` treats an empty string as enabled, parses explicit booleans, calls `maxprocs.Set` with optional logger when true, and calls the undo function and clears state when false.

## State, Dependencies, and Integration

Package-level globals hold `logFunc` and `undoAutomaxprocs`. Dependencies are Go `flag`, `fmt`, `strconv`, and `go.uber.org/automaxprocs/maxprocs`. Integration is through process-global command-line flags and runtime `GOMAXPROCS`.

## Risks and Test Signals

This is process-global state, so repeated tests or libraries registering flags must guard against duplicate registration. `EnableAutomaxprocs` calls `flag.Set`, so `AddAutomaxprocs` must have been called first. Tests cover true/false/empty/invalid values and enable/disable state transitions.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/standardflags/automaxprocs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/standardflags/automaxprocs_test.go -->
# sources/control-plane/csi-lib-utils/standardflags/automaxprocs_test.go

## Purpose

This test file verifies parsing and state transitions for the shared `-automaxprocs` flag.

## Important Behavior

`TestAutomaxprocsArgument` ensures the flag is registered, then calls `flag.Set("automaxprocs", value)` for `true`, `false`, empty string, and invalid text, expecting only the invalid text to error. `TestEnableDisableAutomaxprocs` ensures the flag exists, disables it if already enabled, calls `EnableAutomaxprocs`, checks enabled state, then disables via `handleAutomaxprocs("false")` and checks state again.

## State, Dependencies, and Integration

The tests mutate Go's global default `flag.CommandLine` and the package-level `undoAutomaxprocs` state. They depend on the real `maxprocs.Set` behavior but do not assert exact `GOMAXPROCS` values.

## Risks and Test Signals

Global flag state means these tests can interact with other tests in the same process if run with conflicting flag registrations. They check error paths and enabled-state plumbing, but not logger output or container quota detection. Passing `go test ./standardflags` is the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/standardflags/automaxprocs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-lib-utils/standardflags/flags.go -->
# sources/control-plane/csi-lib-utils/standardflags/flags.go

## Purpose

This file defines common command-line flags and configuration storage for CSI sidecars and drivers.

## Important APIs and Flow

`SidecarConfiguration` stores common values: version display, kubeconfig, CSI socket address, leader election settings, leader-election labels, Kubernetes API QPS/burst, HTTP diagnostics endpoint, deprecated metrics address, and metrics path. The package-level `Configuration` is initialized with an empty `stringMap`. `RegisterCommonFlags` binds fields to a supplied `*flag.FlagSet`, though `metrics-path` is registered on the global `flag` package rather than the supplied set. `stringMap` implements `flag.Value`: `Set` parses comma-separated `key:value` labels into the map, and `String` formats the map.

## State, Dependencies, and Integration

State is global in `Configuration` and is mutated by flag parsing. Dependencies are Go `flag`, `fmt`, `strings`, and `time`. Integration points include sidecar `main` packages, Kubernetes client QPS/burst configuration, leader election setup, diagnostics/metrics HTTP servers, and version handling.

## Risks and Test Signals

The `metrics-path` registration uses `flag.StringVar` instead of `flags.StringVar`, which can surprise callers using custom FlagSets. The help text contains a spelling error in "comma seperated". `stringMap.Set` splits on every colon and does not support values containing colons. No direct tests are listed for this file in the subset.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-lib-utils/standardflags/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/.github/workflows/build.yaml -->
# sources/control-plane/csi-spec/.github/workflows/build.yaml

## Purpose

This GitHub Actions workflow verifies that CSI spec generated files are current and buildable.

## Important Behavior

It runs on pull requests and pushes. The single build job sets up Go `^1.19`, checks out code, touches `spec.md` to force regeneration timestamps, runs `make`, then runs `git diff --exit-code`. If generated files changed, it prints a message telling contributors to run `make` and commit updates.

## State, Dependencies, and Integration

State is the checked-out worktree and generated files such as `csi.proto` and Go bindings. Dependencies are GitHub Actions, setup-go, checkout, Go, Make, protoc download rules, and the repo Makefiles. It integrates spec Markdown, proto extraction, and generated language bindings.

## Risks and Test Signals

The workflow uses older unpinned major-version actions (`setup-go@v3`, `checkout@v3`). The timestamp touch is important because Makefile dependencies rely on modification times. The signal is a clean `make` plus clean git diff.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/.github/workflows/build.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/.github/workflows/codespell.yml -->
# sources/control-plane/csi-spec/.github/workflows/codespell.yml

## Purpose

This GitHub Actions workflow runs codespell for the CSI specification repository on pushes and pull requests.

## Important Behavior

It checks out the repository with `actions/checkout@v3`, then runs `codespell-project/actions-codespell@master` with filename checks enabled. It skips Git internals, the workflow file, common image/checksum files, and `go.sum`.

## State, Dependencies, and Integration

There is no persistent state. Dependencies are GitHub Actions and the codespell action. It integrates with documentation/spec quality because most of the repository content is specification text and generated bindings.

## Risks and Test Signals

Using `@master` makes behavior less reproducible than a pinned release/SHA. Skips reduce false positives in generated or binary files. The workflow pass/fail result is the test signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/Makefile -->
# sources/control-plane/csi-spec/Makefile

## Purpose

The top-level CSI spec Makefile extracts `csi.proto` from `spec.md`, builds C++ and Go bindings, and checks basic proto formatting constraints.

## Important Targets and Flow

`all` maps to `build`. `$(CSI_PROTO)` depends on `spec.md` and `Makefile`; it writes a generated-code header and extracts the fenced `protobuf` block from `spec.md` with `sed`. `build` runs `check`, `build_cpp`, and `build_go`. `build_cpp` delegates to `lib/cxx`. Go binding build delegates to `lib/go`, then downloads modules, installs/builds `./lib/go/csi`, and emits `csi.a`. `clean` removes `csi.a` and delegates cleanup; `clobber` also removes generated `csi.proto`. `check` runs an awk line-length check on the newly generated proto.

## State, Dependencies, and Integration

Generated state includes `csi.proto`, Go generated files, and `csi.a`. Dependencies are Make, sed, awk, Go modules, and subdirectory Makefiles. It integrates the human-readable spec with generated language APIs and the GitHub Actions build workflow.

## Risks and Test Signals

The proto extraction depends on exact Markdown fence markers. The `check` target only checks `$?`, so it primarily evaluates files newer than the target in the current make invocation. Test signals are successful `make`, clean generated diffs, and generated binding compilation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/csi.proto -->
# sources/control-plane/csi-spec/csi.proto

## Purpose

This generated proto file is the CSI v1 gRPC API contract. It defines services, messages, enums, annotations for alpha APIs and secrets, and all request/response shapes used between container orchestrators and storage plugins.

## Important APIs and Flow

Services are `Identity`, `Controller`, `GroupController`, alpha `SnapshotMetadata`, and `Node`. Identity exposes plugin info, capabilities, and readiness probe. Controller covers volume lifecycle, publish/unpublish, validation, listing, capacity, capabilities, snapshots, expansion, alpha get-volume/get-snapshot, and modify-volume. GroupController covers group snapshot capabilities and group snapshot create/delete/get. SnapshotMetadata streams allocated or changed block metadata. Node covers staging, publishing, stats, expansion, capabilities, and node info.

Core messages include `PluginCapability`, `VolumeCapability`, `CapacityRange`, `Volume`, `TopologyRequirement`, `Topology`, controller publish/validate/list/capability messages, `Snapshot`, node publish/stage/stat messages, `VolumeCondition`, group snapshot structures, and block metadata structures. Custom protobuf options mark secret fields (`csi_secret`) and alpha enums, fields, messages, methods, and services.

## State, Dependencies, and Integration

The file has no runtime state itself, but it defines persistent wire compatibility. Dependencies are protobuf compiler support, gRPC generators, `google.protobuf.Timestamp`, wrappers, and descriptor extensions. It integrates with generated Go bindings in `lib/go/csi`, external CSI implementations, Kubernetes sidecars, and docs generated from `spec.md`.

## Risks and Test Signals

Field numbers and service/method names are compatibility-critical and must not be changed casually. Secret annotations are important because COs and plugins must avoid logging sensitive maps. Alpha annotations warn that APIs can change. Risks include generated file drift from `spec.md`, line-length formatting failures, and breaking generated bindings. Test signals are top-level `make`, clean git diff in CI, and downstream CSI conformance/sanity tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/csi.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/lib/cxx/Makefile -->
# sources/control-plane/csi-spec/lib/cxx/Makefile

## Purpose

This placeholder Makefile represents C++ binding build and cleanup hooks for the CSI spec repository.

## Important Behavior

`all` maps to `build`. The `build` target prints `cxx bindings & validation`. The `clean` target prints `clean cxx`. Both are phony.

## State, Dependencies, and Integration

It creates no files and has no external dependencies beyond Make. The top-level Makefile invokes `$(MAKE) -C lib/cxx` during `build_cpp` and cleanup paths, so this file preserves the build interface even when no C++ generation is currently performed.

## Risks and Test Signals

Because it is a stub, it can give a false sense that C++ bindings are validated. The test signal is simply that the delegated target exists and returns success.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/lib/cxx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/lib/go/Makefile -->
# sources/control-plane/csi-spec/lib/go/Makefile

## Purpose

This Makefile generates Go protobuf and gRPC bindings for the CSI spec.

## Important Targets and Flow

It normalizes `GOPATH` and `GOBIN`, sets `PROTOC_VER` default `25.2`, maps OS/architecture names to protoc release naming, downloads and unzips protoc into `.protoc`, and installs `protoc-gen-go` plus `protoc-gen-go-grpc@v1.3.0`. It prepends `GOBIN` to `PATH` so protoc can find plugins. `$(CSI_GO)` and `$(CSI_GRPC)` depend on `../../csi.proto` and tool binaries, create the output directory, and run protoc with source-relative Go and Go-gRPC outputs into `csi/`. `clean` removes generated package files via `go clean -i ./...` and `rm -rf csi`; `clobber` also removes `.protoc`.

## State, Dependencies, and Integration

Generated state includes `.protoc/` and `lib/go/csi/*.pb.go`/`*_grpc.pb.go`. Dependencies are Make, Go, curl, unzip, protoc, and Go generator modules. It is invoked by the top-level Makefile and build workflow.

## Risks and Test Signals

The protoc architecture mapping handles common `i386` and `arm64` cases but may miss other names. Downloads are network-sensitive. Tool versions define generated-code output and API compatibility. Test signals are successful protoc generation and clean git diffs after `make`.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/lib/go/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-spec/lib/go/csi.go -->
# sources/control-plane/csi-spec/lib/go/csi.go

## Purpose

This tiny Go file anchors the `csi` Go package so it exists as a package alongside generated protobuf files.

## Important Behavior

The file declares `package csi` and contains no exported APIs, functions, variables, or init behavior. Generated files such as `csi.pb.go` and `csi_grpc.pb.go` provide the actual types and clients/servers.

## State, Dependencies, and Integration

There is no state and no imports. It integrates with Go package discovery and build targets that install or build `./lib/go/csi`, including cases before generated files exist.

## Risks and Test Signals

The file is intentionally minimal. The main risk is assuming it contains the API; the real contract comes from generated files. Test signal is successful `go build ./lib/go/csi` after generation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-spec/lib/go/csi.go -->
