# subset-b-009155 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/gettool/autodownload/autodownload.go -->
# sources/sync-backup/kopia/tools/gettool/autodownload/autodownload.go

Purpose: package `autodownload` is Kopia's embedded replacement for `curl`, `sha256sum`, `gunzip`, `tar`, and `unzip` during tool bootstrapping. It downloads an archive URL, verifies a SHA-256 checksum, and extracts `.tar.gz` or `.zip` contents into a target directory without external binaries.

Important APIs/types/functions: `Download(url, dir, checksum, stripPathComponents)` is the public entry point. `downloadInternal` performs HTTP GET, checksum computation, archive selection, and extraction. `InvalidChecksumError` distinguishes missing and mismatched checksums so callers can regenerate baselines. `untar`, `unzip`, `createFile`, `createSymlink`, and `stripLeadingPath` implement extraction details.

Control flow: `Download` retries `downloadInternal` up to eight times with exponential backoff, removing the output directory between retryable attempts. HTTP 404 and checksum failures are treated as non-retryable. `downloadInternal` buffers the entire response, validates or records the checksum, optionally wraps the reader in gzip, then dispatches to tar or zip extraction by URL suffix.

State/persistence: it creates/removes files under the caller-provided output directory, preserves archive file modes and modification times for regular files, and records discovered checksums by mutating the supplied checksum map. Extraction uses `os.OpenRoot`, which reduces path traversal exposure by operating relative to a directory root.

Dependencies/integration: depends on Go archive, gzip, HTTP, crypto, and `github.com/pkg/errors`. It is used by Kopia `tools/gettool` and `tools.mk` to install pinned build tools.

Risks/test signals: zip downloads are buffered fully in memory. Archive support is intentionally narrow, and unsupported entries fail the install. Checksums are keyed by full URL, so URL-template changes require checksum regeneration. There are no local tests in this subset; coverage is indirect through gettool checksum verification targets.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/gettool/autodownload/autodownload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/gettool/gettool.go -->
# sources/sync-backup/kopia/tools/gettool/gettool.go

Purpose: `gettool` is a small Kopia build helper that downloads pinned, platform-specific third-party tools from upstream release archives. It centralizes tool URL templates, OS/architecture translations, extraction stripping, checksum verification, and checksum regeneration.

Important APIs/types/functions: `ToolInfo` stores a URL template plus OS/arch maps and unsupported platform rules. `ToolInfo.actualURL` expands `VERSION`, `GOOS`, `GOARCH`, and `EXT`. Global `tools` defines linter, Hugo, gotestsum, Kopia, rclone, goreleaser, git-chglog, and node. `parseEmbeddedChecksums` reads embedded `checksums.txt`. `downloadTool` executes normal, `--test-all`, or `--regenerate-checksums` modes.

Control flow: `main` parses flags, loads embedded checksums, then loops over comma-separated `tool:version` specs. Normal mode downloads one archive for selected `--goos/--goarch`. `--test-all` probes a fixed platform matrix and counts failures. `--regenerate-checksums` preserves existing checksums and downloads missing ones so `autodownload.InvalidChecksumError` can populate discovered hashes.

State/persistence: writes tools into `--output-dir`; optional checksum regeneration writes the sorted URL-to-hash lines to the requested file. It exits fatally on unsupported specs or normal-mode download failures.

Dependencies/integration: uses `embed`, `flag`, runtime platform values, and package `tools/gettool/autodownload`. `tools.mk` invokes it for local/CI tool installation and checksum maintenance.

Risks/test signals: platform metadata is hardcoded, so upstream naming changes break downloads. `parseEmbeddedChecksums` assumes each line contains `": "`. Regeneration has side effects both in output directories and checksum files. Test signals are the Make targets `verify-all-tool-checksums` and `regenerate-checksums`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/gettool/gettool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/homebrew-publish.sh -->
# sources/sync-backup/kopia/tools/homebrew-publish.sh

Purpose: publishes or test-publishes Kopia Homebrew formula updates by computing release artifact hashes, rendering a Ruby formula template, and pushing it to the configured Homebrew tap repository.

Control flow/APIs: positional args are distribution directory and version. The script selects production repos when `CI_TAG` is present and test-build repos otherwise. It exits successfully without publishing when `GITHUB_TOKEN` is missing. It computes SHA-256 hashes for macOS and Linux tarballs, clones `$REPO_OWNER/homebrew-kopia` or `$REPO_OWNER/homebrew-test-builds`, applies `sed` substitutions to `tools/kopia-homebrew.rs.template`, commits, and pushes.

State/persistence: creates a temporary clone with `mktemp -d`, writes `kopia.rb`, commits to a remote GitHub repository, and removes the temporary directory at the end.

Dependencies/integration: requires bash, `sha256sum`, `git`, network access, `GITHUB_TOKEN`, `REPO_OWNER`, optional `CI_TAG`, release artifacts, and the Homebrew template. It is part of Kopia release automation.

Risks/test signals: most variables and paths are unquoted, so paths containing whitespace can break. Failures before `rm -rf` leave temp clones. The token is embedded in the clone URL, so CI log redaction must be relied on. There is no dedicated test; release CI and successful tap updates are the signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/homebrew-publish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/htmlui_changelog.sh -->
# sources/sync-backup/kopia/tools/htmlui_changelog.sh

Purpose: generates a changelog for Kopia HTML UI changes between release points by tracing the `htmluibuild` module hash change in `go.mod` back to commits in the `htmlui` repository.

Control flow/APIs: chooses `start_commit` and `end_commit` from `CI_TAG` or the previous tag. It diffs `go.mod` for `htmluibuild`, extracts old/new htmluibuild hashes, clones `kopia/htmluibuild`, reads automated commit messages to derive old/new htmlui commit hashes, clones `kopia/htmlui`, creates temporary tags on those commits, and runs `$gitchglog --sort=semver --config=... v0.2.0`, appending output to the requested file.

State/persistence: uses fixed temporary directories `/tmp/tmp-htmluibuild` and `/tmp/tmp-htmlui`, deleting any existing directories at those paths. It appends changelog text to the user-provided output file.

Dependencies/integration: requires Git, `realpath`, `grep`, `cut`, an installed `gitchglog` binary exposed as `$gitchglog`, and Kopia changelog config `.chglog/config-htmlui.yml`. Integrated into release-note generation.

Risks/test signals: fixed `/tmp` paths can collide with concurrent runs. Parsing depends on exact `go.mod` diff shape and automated commit-message format. The script uses `set -xe`, so command traces can be noisy. No local tests; release changelog output is the observable signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/htmlui_changelog.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/make-tgz.sh -->
# sources/sync-backup/kopia/tools/make-tgz.sh

Purpose: packages a Kopia binary plus `LICENSE` and `README.md` into a gzip-compressed tarball with a versioned top-level directory.

Control flow/APIs: positional args are output directory, base filename, and binary path. It creates a temp directory, stages `$basefname`, copies the binary and project metadata into it, runs `tar -C $temp_dir -cvz $basefname > $output_dir/$basefname.tar.gz`, then removes the temp directory.

State/persistence: writes exactly one archive under the output directory and creates/removes one temporary staging tree. Archive contents are rooted at `$basefname`.

Dependencies/integration: requires POSIX shell, `mktemp`, `cp`, and `tar`. It is used by release packaging to produce tar artifacts consumed by publishing scripts and package managers.

Risks/test signals: arguments are mostly unquoted, so paths with spaces can break. Cleanup is not trap-protected, leaving temporary directories on failure. It assumes `LICENSE` and `README.md` exist in the current working directory. Release packaging success is the practical test signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/make-tgz.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/node_env.sh -->
# sources/sync-backup/kopia/tools/node_env.sh

Purpose: configures a shell environment so Kopia's pinned Node.js installation under `tools/.tools` is first on `PATH`.

Control flow/APIs: resolves the script directory with `realpath $(dirname $0)`, extracts `NODE_VERSION` from `tools.mk`, logs both values, and prepends `$toolsdir/.tools/node-$node_version/bin` to `PATH`.

State/persistence: mutates only the current shell process environment when sourced. If executed as a subprocess, the exported `PATH` does not affect the caller.

Dependencies/integration: depends on `realpath`, `grep`, `head`, and `cut`; integrates with `tools.mk`'s Node version and installed node directory layout.

Risks/test signals: it does not `export PATH`, though shell assignment affects child commands from the same shell. It uses backticks and unquoted paths. Consumers must source it or otherwise run subsequent commands in the same process context.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/node_env.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/recovery-job.sh -->
# sources/sync-backup/kopia/tools/recovery-job.sh

Purpose: orchestrates a Kopia recovery test job by building a Kopia binary, embedding source/test git metadata into robustness engine ldflags, and running the recovery test Make target in a separate recovery repository.

Control flow/APIs: required args are recovery repo directory, Kopia repo directory, test duration, test timeout, and repository path prefix. It logs selected environment variables, optionally displays local fio data directory usage, builds `kopia` from the Kopia repo, gathers git revision/branch/dirty/build-time metadata from both repos, constructs `-ldflags`, and invokes `make -C "$kopia_recovery_dir" KOPIA_EXE=... GO_TEST='go test' TEST_FLAGS=... recovery-tests`.

State/persistence: writes the built Kopia executable into the Kopia repo directory. The invoked Make target likely writes test/recovery state under the provided repository path prefix and fio data paths.

Dependencies/integration: requires bash, Go, Git, Make, and environment credentials for S3-backed repositories when used. It integrates Kopia's executable with the robustness/recovery test harness under `tests/robustness/engine`.

Risks/test signals: no trap restores directories after partial failure, though `pushd/popd` are used. Quoting inside `TEST_FLAGS` is fragile due embedded `-ldflags` string. It prints presence of secret variables but masks `AWS_SECRET_ACCESS_KEY`. The recovery Make target's success is the signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/recovery-job.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/retry.sh -->
# sources/sync-backup/kopia/tools/retry.sh

Purpose: small POSIX-shell wrapper to retry a command up to three times.

Control flow/APIs: loops attempts 1, 2, and 3, echoes the command and attempt number, executes `"$@"`, exits 0 on first success, and exits 1 if all attempts fail.

State/persistence: no direct persistence; all side effects come from the wrapped command and may happen multiple times.

Dependencies/integration: used from `tools.mk` as `retry` on non-Windows platforms to make transient build/download commands more robust.

Risks/test signals: there is no sleep/backoff and no distinction between retryable and non-retryable failures. The wrapped command must be idempotent or tolerate repeated execution. Behavior is simple enough to be covered by users of the wrapper rather than its own tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/retry.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/robustness-job.sh -->
# sources/sync-backup/kopia/tools/robustness-job.sh

Purpose: orchestrates Kopia randomized robustness testing by building the Kopia binary, embedding repo metadata, optionally sourcing test runtime configuration, and invoking the robustness Make target.

Control flow/APIs: required args are robustness repo directory, Kopia repo directory, test duration, timeout, and repo path prefix. It logs environment, optionally inspects fio data storage, builds `kopia`, collects git metadata for both repos, builds ldflags for `tests/robustness/engine`, chooses `robustness-server-tests` when `ENGINE_MODE=SERVER` otherwise `robustness-tests`, sources `$TEST_RC` if it names a file, then runs `make -C`.

State/persistence: writes the Kopia executable, may source arbitrary shell from `TEST_RC`, and delegates repository/test state creation to the robustness tests under the provided path prefix.

Dependencies/integration: bash, Go, Git, Make, optional fio/Docker, S3-related environment, and the Kopia robustness test repo. It is CI or cron-style validation glue.

Risks/test signals: `source ${TEST_RC}` is unquoted and intentionally executes external code. Complex `TEST_FLAGS` quoting can be fragile. Long-running randomized tests may be flaky if storage credentials, fio paths, or timeouts are wrong. Test success/failure is the direct output of the Make target.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/robustness-job.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/rpm-publish.sh -->
# sources/sync-backup/kopia/tools/rpm-publish.sh

Purpose: publishes Kopia RPMs to Google Cloud Storage-backed RPM repositories, signs new packages, prunes old unstable packages, regenerates repo metadata, and synchronizes results.

Control flow/APIs: validates package dir and `PACKAGES_HOST`, picks `stable testing` only for tagged CI releases otherwise `unstable`, creates `/tmp/rpm-publish`, `gsutil rsync`s existing distribution trees, prunes old RPMs per arch, classifies input RPM filenames by version and architecture, signs copies with `rpm --addsign`, regenerates metadata via `createrepo_c`, uploads with `gsutil rsync`, and disables caching on `repodata`.

State/persistence: mutates `/tmp/rpm-publish`, remote `gs://$PACKAGES_HOST/rpm`, and RPM signatures. It keeps only a few older unstable RPMs in working copies before sync.

Dependencies/integration: bash, `gsutil`, `rpm`, `createrepo_c`, GPG/RPM signing setup, package naming conventions, `PACKAGES_HOST`, and optional `CI_TAG`. Used in release publication.

Risks/test signals: filename regex controls release-channel classification, so packaging name drift can silently skip files. `delete_old_rpms` with empty globs can behave poorly. `WORK_DIR` is not cleared at start. Signing credentials and cloud permissions are external. Validation comes from package repository metadata and install tests downstream.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/rpm-publish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/scoop-publish.sh -->
# sources/sync-backup/kopia/tools/scoop-publish.sh

Purpose: publishes or test-publishes Kopia's Scoop manifest by hashing the Windows zip artifact, rendering a JSON template, and pushing to the configured Scoop bucket repository.

Control flow/APIs: positional args are dist directory and version. Production target is `$REPO_OWNER/scoop-bucket`; non-tagged builds use `$REPO_OWNER/scoop-test-builds`. Missing `GITHUB_TOKEN` causes a successful no-op. It computes the Windows amd64 zip SHA-256, clones the target repo, substitutes version/source/hash into `tools/scoop-kopia.json.template`, commits `kopia.json`, and pushes.

State/persistence: creates a temporary clone, writes `kopia.json`, commits/pushes to GitHub, and removes the temp clone on success.

Dependencies/integration: bash, `sha256sum`, `git`, `GITHUB_TOKEN`, `REPO_OWNER`, optional `CI_TAG`, and release artifacts. It is part of Kopia Windows package publication.

Risks/test signals: unquoted variables can break on spaces. Temp cleanup is not protected by traps. The commit message prefixes `v$ver`, so callers must pass a version without duplicate `v` if that matters. Package manager consumers and bucket CI are the downstream test signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/scoop-publish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/sign.sh -->
# sources/sync-backup/kopia/tools/sign.sh

Purpose: signs Kopia release artifacts by adding RPM signatures, regenerating `dist/checksums.txt`, and creating a detached GPG signature for the checksum file.

Control flow/APIs: loops over `dist/*rpm` and runs `rpm --define "%_gpg_name Kopia Builder" --addsign`. Then it reads filenames from the existing checksum file, regenerates checksums inside `dist`, and writes `dist/checksums.txt.sig` via `gpg --detach-sig`.

State/persistence: mutates RPM files in place by signing them, rewrites `dist/checksums.txt`, and writes `dist/checksums.txt.sig`.

Dependencies/integration: bash, RPM signing configuration, GPG key setup, `sha256sum`, and a populated `dist` directory. Used at the release-signing stage before publishing.

Risks/test signals: assumes `dist/checksums.txt` exists and contains filenames matching current dist artifacts. Only RPMs are modified before checksum regeneration. Failure halfway can leave some RPMs signed and checksum/signature stale. Verification is external: `rpm --checksig`, `sha256sum -c`, and GPG signature checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/sign.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tools/tools.mk -->
# sources/sync-backup/kopia/tools/tools.mk

Purpose: shared Makefile fragment for Kopia development and release tooling. It detects platform traits, computes build/version metadata, installs pinned tools into `tools/.tools`, configures npm/node, and defines helper targets for signing and checksum maintenance.

Important targets/variables: platform variables include `GOOS`, `GOARCH`, suffixes, path separators, dates, and hostnames. CI variables derive `IS_PULL_REQUEST`, `CI_TAG`, `REPO_OWNER`, and `KOPIA_VERSION`. Tool versions pin golangci-lint, checklocks, Node, Hugo, gotestsum, goreleaser, rclone, and gitchglog. Targets install tools via `go run github.com/kopia/kopia/tools/gettool` or `go install`; `all-tools`, `clean-tools`, `verify-all-tool-checksums`, and `regenerate-checksums` are key aggregate operations.

Control flow/state: Make lazily materializes binaries under `TOOLS_DIR`. It prepends the pinned Node bin directory to `PATH`, exports version strings for web UI builds, installs Windows signing tools when configured, imports macOS certificates into a temporary keychain in CI, and computes release/nightly version identifiers from tags or commit timestamps.

Dependencies/integration: integrates with `gettool`, Go, npm, GitHub Actions environment variables, Windows PowerShell tools, macOS `security`, and release scripts. Consumers include Kopia build, lint, docs, web UI, backward compatibility, and release workflows.

Risks/test signals: platform branching is broad and fragile on unusual shells. Some targets fetch `@latest` tools, reducing reproducibility. Signing targets depend on secret environment variables. Checksum verification/regeneration targets provide the strongest automated signal for downloaded tool integrity.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tools/tools.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.github/ISSUE_TEMPLATE/config.yml -->
# sources/sync-backup/restic/.github/ISSUE_TEMPLATE/config.yml

Purpose: GitHub issue-template configuration that redirects general support questions to the restic forum.

Control flow/state: it declares one `contact_links` entry named `restic forum` with URL `https://forum.restic.net` and explanatory text asking users not to open issues for usage questions. It has no executable logic and no persistence outside GitHub's issue UI behavior.

Dependencies/integration: consumed by GitHub Issues when rendering the new-issue page. It complements issue templates elsewhere in the repository by adding an external support route.

Risks/test signals: the only risk is stale forum URL or guidance. Validation is GitHub accepting the YAML and displaying the contact link.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.github/dependabot.yml -->
# sources/sync-backup/restic/.github/dependabot.yml

Purpose: Dependabot configuration for restic dependency update automation.

Control flow/state: version 2 config schedules monthly checks for Go module dependencies in `/` and GitHub Actions dependencies in `/`. It groups `golang.org/x/*` module updates under `golang-x-deps`.

Dependencies/integration: consumed by GitHub Dependabot. It interacts with `go.mod`, `go.sum`, and workflow action references, then creates pull requests when updates are available.

Risks/test signals: monthly cadence can delay security updates. Only `golang.org/x/*` dependencies are grouped; other ecosystems may create separate PRs. Validation occurs through Dependabot logs and generated PRs.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.github/workflows/codespell.yml -->
# sources/sync-backup/restic/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow that checks spelling with codespell.

Control flow/state: runs on pushes to `master`, pull requests, and merge queue events. It grants read-only contents permission, checks out the repository, then invokes a pinned `codespell-project/actions-codespell` action. Codespell's detailed settings live in `.codespellrc`.

Dependencies/integration: depends on GitHub Actions, `actions/checkout@v6`, and the pinned codespell action. It is a quality gate for text/code spelling regressions.

Risks/test signals: the third-party action is pinned by commit, reducing supply-chain drift but requiring manual updates. The workflow is small and has no repository mutations. A passing job is the validation signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.github/workflows/docker.yml -->
# sources/sync-backup/restic/.github/workflows/docker.yml

Purpose: release/nightly workflow for building and publishing multi-architecture Docker images to GitHub Container Registry and generating SLSA provenance.

Control flow/state: triggers on `v*` tags and `master` pushes. The build job only runs in `restic/restic`, checks out code, logs into GHCR, generates Docker metadata, sets up QEMU and Buildx, removes `.git` for non-master release consistency, then builds and pushes `docker/Dockerfile.release` for linux/386, amd64, arm, and arm64. A dependent reusable SLSA job signs/provides provenance for the pushed digest.

Dependencies/integration: uses Docker official actions, GHCR permissions, `secrets.GITHUB_TOKEN`, and `slsa-framework/slsa-github-generator`. Outputs include image name and digest.

Risks/test signals: action versions are pinned by commit for build dependencies but SLSA workflow is version-tagged. Removing `.git` changes version embedding behavior for releases. Validation comes from successful image push and provenance generation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.github/workflows/docker.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.github/workflows/tests.yml -->
# sources/sync-backup/restic/.github/workflows/tests.yml

Purpose: main restic CI workflow for tests, cross-compilation, linting, Docker build validation, and aggregate status analysis.

Control flow/state: triggers on pushes to `master`, pull requests, and merge queue. The `test` matrix runs Windows, macOS, Linux latest, Linux race, and Linux minimum-Go lanes. It installs Go, rest-server, minio, rclone, and Windows tar dependencies, builds via `go run build.go`, runs a minimal init/backup smoke test, runs `go test -cover`, optionally tests cloud backends using secrets, and optionally checks changelog files. `cross_compile` runs release binary builds in three platform subsets. `lint` runs golangci-lint for PRs and verifies `go mod tidy`. `analyze` gates all required jobs with `re-actors/alls-green`. A separate `docker` job validates `docker/Dockerfile`.

Dependencies/integration: GitHub Actions, Go 1.25/1.26, external tool downloads, cloud secrets, backend test environment variables, Buildx/QEMU, and restic helper build scripts.

Risks/test signals: uses some moving upstream downloads and `@master/@latest` Go installs. Cloud tests are skipped for untrusted PRs/Dependabot. This workflow is the strongest automated signal for files in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.github/workflows/tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.golangci.yml -->
# sources/sync-backup/restic/.golangci.yml

Purpose: golangci-lint v2 configuration defining restic's static-analysis and formatting policy.

Important settings: disables default linters and enables selected checks: `asciicheck`, `bodyclose`, `depguard`, `copyloopvar`, `errcheck`, `govet`, `importas`, `ineffassign`, `nolintlint`, `revive`, `staticcheck`, and `unused`. Formatters enable `gofmt`. `depguard` enforces package-layer boundaries for `internal/backend` and `internal/repository`. `importas` requires `internal/test` alias `rtest`.

Control flow/state: no runtime state; it configures `golangci-lint-action` in CI and local lint runs. Exclusion rules suppress known noisy revive/staticcheck findings and exclude third-party/builtin/examples paths.

Dependencies/integration: consumed by golangci-lint v2. It integrates directly with `.github/workflows/tests.yml`.

Risks/test signals: exclusions can hide real issues if patterns are too broad. Architectural `depguard` rules are important because command files in this subset depend on repository internals only through permitted layers. Passing CI lint is the validation signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/.readthedocs.yaml -->
# sources/sync-backup/restic/.readthedocs.yaml

Purpose: Read the Docs configuration for building restic documentation.

Control flow/state: uses config version 2, Ubuntu 22.04, Python 3.11, and Sphinx config `doc/conf.py`. It requests `htmlzip` output and installs Python requirements from `doc/requirements.txt`.

Dependencies/integration: consumed by Read the Docs infrastructure and tied to restic's `doc/` Sphinx project.

Risks/test signals: documentation builds depend on requirements staying compatible with Python 3.11 and RTD's Ubuntu image. Validation is a successful RTD build and generated HTMLZip artifact.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/.readthedocs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/Makefile -->
# sources/sync-backup/restic/Makefile

Purpose: minimal developer Makefile for common restic build, clean, and test operations.

Control flow/state: declares phony targets `all`, `clean`, `test`, and `restic`. `all` depends on `restic`; `restic` runs `go run build.go`; `clean` removes the `restic` binary; `test` runs `go test ./cmd/... ./internal/...`.

Dependencies/integration: delegates real build logic to `build.go` and Go's test runner. It is a convenience interface for local users and CI-like manual runs.

Risks/test signals: `test` omits helper packages outside `cmd` and `internal` if any exist. `clean` removes only the Unix binary name, not `restic.exe`. Success of `go run build.go` and `go test` is the signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/build.go -->
# sources/sync-backup/restic/build.go

Purpose: `go run build.go` build helper for restic. It enforces a minimum Go version, sets default build tags, embeds version information, supports cross-compilation flags, and optionally runs tests.

Important APIs/types/functions: `Config` describes binary name, namespace, main package, default tags, tests, and minimum Go version. `GoVersion`, `ParseGoVersion`, and `AtLeast` implement version checks. `build` and `test` wrap `go build`/`go test` with controlled env. `getVersionFromFile`, `getVersionFromGit`, `getVersion`, and `Constants.LDFlags` compute `main.version` ldflags.

Control flow: `main` rejects old Go versions, parses flags manually, builds env defaults, computes output path, strips symbols unless `debug` or `profile` tags are present, invokes `go build -trimpath` with default tags `selfupdate,disable_grpc_modules`, then optionally runs configured tests.

State/persistence: writes the binary to `restic`, `restic.exe`, or `--output`. It does not modify source state. It reads `VERSION` and Git metadata when available.

Dependencies/integration: Go toolchain, Git, runtime environment variables, and CI `Makefile`/workflow build steps.

Risks/test signals: manual flag parsing has limited bounds checks for options requiring values. Empty/unparseable Go versions are treated as satisfying all versions. CI's `Build with build.go` and cross-platform matrix exercise this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cleanup.go -->
# sources/sync-backup/restic/cmd/restic/cleanup.go

Purpose: central signal and process-exit helpers for the restic CLI.

Important APIs/functions: `createGlobalContext(stderr)` returns a cancellable root context and registers a goroutine for SIGINT/SIGTERM. `cleanupHandler` logs and prints the signal, optionally dumps stack traces when `RESTIC_DEBUG_STACKTRACE_SIGINT` is set, then cancels the context. `Exit(code)` logs and calls `os.Exit`.

Control flow/state: the signal channel receives one signal and cancels the global context used by commands. Stack traces are written to stderr only on explicit debug environment configuration.

Dependencies/integration: uses Go `os/signal`, `syscall`, and restic `internal/debug`. Command implementations observe context cancellation during repository walks, backup, check, copy, find, and diff operations.

Risks/test signals: only one signal is consumed by the handler; repeated signals follow normal process behavior only if elsewhere configured. The goroutine lives for process lifetime. CI's minimal test sets `RESTIC_DEBUG_STACKTRACE_SIGINT`, but direct signal behavior is usually integration/manual tested.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_backup.go -->
# sources/sync-backup/restic/cmd/restic/cmd_backup.go

Purpose: implements `restic backup`, creating snapshots from filesystem targets, stdin, or command stdout, with filtering, parent selection, progress reporting, and partial-error semantics.

Important APIs/types/functions: `BackupOptions` holds source, filter, metadata, VSS, stdin, dry-run, and incremental options. `newBackupCommand` registers flags and pre-run defaults for host/read concurrency. `collectTargets`, `readLines`, `readFilenamesRaw`, and `filterExisting` collect source paths. `collectRejectByNameFuncs` and `collectRejectFuncs` assemble archive filters. `findParentSnapshot` locates incremental parents. `runBackup` performs the operation.

Control flow: validates incompatible stdin/password/files-from options, collects existing targets, parses timestamp, opens repository with append lock, loads parent/index, builds target FS including Windows VSS or stdin reader, sets scanner and archiver filters, optionally scans in a goroutine, snapshots with `archiver.New`, reports progress, and returns `ErrInvalidSourceData` when some items failed but a snapshot was created.

State/persistence: creates snapshot, tree, data, index, and lock state in the repository unless `--dry-run`. It may create/delete VSS snapshots and reads local filesystem metadata. Stdin-command execution is external process state.

Dependencies/integration: cobra/pflag, `internal/archiver`, `data`, `fs`, `filter`, `repository`, `restic`, and UI backup progress. Tests and many other commands depend on backup-created repositories.

Risks/test signals: complex option interactions and partial failures are high-risk. Raw filenames require NUL terminators. Parent matching depends on group-by host/path/tags. Tests cover files-from modes, VSS, dry-run, missing files, self-healing, excludes, stdin-command, hardlinks, tags, incremental behavior, and skip-if-unchanged.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_backup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_backup_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_backup_integration_test.go

Purpose: integration coverage for `runBackup` against real test repositories and filesystem fixtures.

Important helpers/tests: `testRunBackupAssumeFailure` and `testRunBackup` invoke `runBackup` through terminal/test environment helpers. Tests cover normal backup/restore/check cycles, filesystem snapshots on Windows, relative-path parent selection, VSS snapshot isolation, dry-run non-persistence, missing source errors, self-healing after deleted packs, tree load repair behavior, exclude patterns, unreadable files, incremental repository growth, tags, program version, quiet mode, hardlinks, stdin-from-command variants, empty passwords, and `--skip-if-unchanged`.

Control flow/state: tests initialize repositories, create backup fixtures, run backup, list snapshots, run check, restore contents, remove packs for damage scenarios, and compare filesystem outputs. Several tests mutate repository internals to exercise repair/self-healing behavior.

Dependencies/integration: uses `withTestEnvironment`, restore/list/check helpers, `internal/data`, `internal/fs`, `internal/restic`, and tar fixtures.

Risks/test signals: platform-specific tests skip when prerequisites are absent, especially Windows VSS and hardlink fixture availability. These tests are the primary behavioral signal for backup's repository mutations and partial failure semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_backup_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_backup_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_backup_test.go

Purpose: focused unit tests for backup target collection and raw filename parsing.

Important tests: `TestCollectTargets` creates files and verifies that `--files-from` trims/comments/globs, `--files-from-verbatim` preserves literal names including spaces/special chars, `--files-from-raw` reads NUL-separated names, command-line args merge with file inputs, and missing sources return `ErrInvalidSourceData`. `TestReadFilenamesRaw` validates exact byte preservation for raw names, empty input, empty filename rejection, and missing trailing NUL rejection.

State/persistence: creates temporary files only. It does not open a repository.

Dependencies/integration: uses `rtest.TempDir`, OS filesystem operations, and `collectTargets`/`readFilenamesRaw` from `cmd_backup.go`.

Risks/test signals: this directly protects user-facing edge cases around filenames that contain whitespace, glob characters, invalid UTF-8, and embedded newlines. It does not cover full archiver behavior; integration tests do that.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_backup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_cache.go -->
# sources/sync-backup/restic/cmd/restic/cmd_cache.go

Purpose: implements `restic cache`, listing and cleaning local repository cache directories.

Important APIs/types/functions: `CacheOptions` includes `Cleanup`, `MaxAge`, and `NoSize`. `runCache` validates arguments/cache settings, chooses default cache directory, removes old cache dirs in cleanup mode, or renders a table of cache IDs, age, old status, and size. `dirSize` recursively sums file sizes.

Control flow/state: refuses arguments and disabled cache. In cleanup mode it calls `cache.OlderThan` and `os.RemoveAll` for each old cache directory. In list mode it reads `cache.All`, sorts by modification time, computes sizes unless disabled, shortens normal repo IDs to 10 chars, and prints a summary.

Dependencies/integration: `internal/backend/cache`, UI progress/table helpers, and global cache options. It mutates only local cache directories, not repositories.

Risks/test signals: `os.RemoveAll` on computed paths is destructive if cache directory discovery is wrong. `dirSize` can be slow for large caches. No dedicated tests in this subset; behavior is indirectly exercised by command integration and cache package tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_cat.go -->
# sources/sync-backup/restic/cmd/restic/cmd_cat.go

Purpose: implements `restic cat`, a diagnostic command for printing raw or JSON representations of internal repository objects.

Important APIs/functions: `catAllowedCmds` defines supported object classes. `validateCatArgs` checks object type and required IDs. `runCat` opens a read lock, parses IDs where needed, and dispatches config, index, snapshot, key, masterkey, lock, pack, blob, and tree output.

Control flow/state: JSON-like objects are marshaled with indentation and printed through the terminal printer. Raw pack/blob/tree bytes are written to `term.OutputRaw`. Pack output intentionally returns bytes even if hash validation fails, while printing a warning. Blob lookup loads the index and searches data then tree blob types. Tree lookup resolves `snapshot:subfolder` before loading the tree blob.

Dependencies/integration: repository loading, snapshot lookup, key/lock loaders, restic ID parsing, and terminal raw output. It is read-only except for repository lock files.

Risks/test signals: raw output can be binary and unsuitable for terminals. `masterkey` exposes sensitive key material to stdout. Tests cover argument validation only; object loading behavior relies on repository integration/manual diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_cat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_cat_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_cat_test.go

Purpose: unit tests for `restic cat` argument validation.

Important tests: `TestCatArgsValidation` verifies missing type, accepted `masterkey`, invalid type errors, missing snapshot ID, and accepted snapshot ID shape.

State/dependencies: no repository is opened; it calls `validateCatArgs` directly and checks error substrings with `rtest`.

Risks/test signals: protects only CLI validation, not repository object output. Raw pack/blob/tree behavior remains covered by broader integration/manual use rather than this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_cat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_check.go -->
# sources/sync-backup/restic/cmd/restic/cmd_check.go

Purpose: implements `restic check`, validating repository indexes, packs, snapshots, tree/blob structure, and optional data contents.

Important APIs/types/functions: `CheckOptions` controls `--read-data`, `--read-data-subset`, `--with-cache`, and snapshot filters. `checkFlags`, `stringToIntSlice`, and `parsePercentage` validate subset syntax. `prepareCheckCache` configures temporary or existing caches. `runCheck` executes the checker. `buildPacksFilter` selects all, bucket, percentage, or size-based pack subsets. `checkSummary` and `jsonErrorPrinter` support JSON output.

Control flow: validates flags, prepares cache, opens exclusive lock, loads filtered snapshots/indexes, reports index hints/errors, checks pack metadata, checks snapshot/tree/blob structure concurrently, optionally checks unused blobs, reads selected data packs, collects salvage pack IDs, prints repair guidance, and returns a fatal error if damage is found.

State/persistence: creates/removes temporary check cache directories unless `--with-cache` or `--no-cache`. It does not repair repositories; it only reports. Lock state is exclusive during checks.

Dependencies/integration: `internal/checker`, `repository`, `cache`, `data`, `restic`, and UI progress. Backup/copy/forget tests call check as a repository integrity oracle.

Risks/test signals: random subset selection is nondeterministic. Damaged pack guidance must stay aligned with repair commands. Tests cover parsing, subset selection, cache preparation, and snapshot-filtered read-data behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_check_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_check_integration_test.go

Purpose: integration helpers and tests for `runCheck`.

Important helpers/tests: `testRunCheck`, `testRunCheckMustFail`, `testRunCheckOutput`, and `testRunCheckOutputWithOpts` wrap `runCheck` in captured terminal environments. `TestCheckWithSnaphotFilter` creates two backups and verifies full and latest-only `--read-data` output counts, plus `--read-data-subset` filtered-output signaling.

State/persistence: creates repositories through backup helpers and reads them with check. It does not repair state.

Dependencies/integration: relies on backup fixtures, `global.Options`, captured stdout helpers, and `CheckOptions`.

Risks/test signals: output substring assertions can be brittle if progress formatting changes. The file provides an important integration signal that snapshot filtering affects both snapshot and pack counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_check_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_check_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_check_test.go

Purpose: unit tests for check option parsing, pack-subset selection, and temporary cache handling.

Important tests: `TestParsePercentage`, `TestStringToIntSlice`, `TestSelectPacksByBucket`, `TestSelectRandomPacksByPercentage`, `TestSelectNoRandomPacksByPercentage`, `TestSelectRandomPacksByFileSize`, and `TestSelectNoRandomPacksByFileSize` cover subset helper behavior. `TestPrepareCheckCache` and `TestPrepareDefaultCheckCache` validate creation and cleanup of temporary cache directories.

State/persistence: uses temporary directories and generated restic IDs. Cache tests create and remove `restic-check-cache-*` dirs and verify cleanup.

Dependencies/integration: uses `global.Options`, `progress.NewNoopPrinter`, `internal/restic`, and `rtest`.

Risks/test signals: random selection tests assert counts but not deterministic identity. Cache cleanup assertions protect against stale check caches and accidental use of persistent cache when `--with-cache` is absent.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_check_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_copy.go -->
# sources/sync-backup/restic/cmd/restic/cmd_copy.go

Purpose: implements `restic copy`, copying snapshots and referenced blobs from one repository to another, re-encrypting data for the destination repository.

Important APIs/types/functions: `CopyOptions` embeds `SecondaryRepoOptions` and snapshot filters. `collectAllSnapshots` filters source snapshots and skips already-copied equivalents based on `Original` IDs and `similarSnapshots`. `runCopy` opens source/destination repos and loads indexes. `copyTreeBatched`, `copyTree`, `copyStats`, and `copySaveSnapshot` copy referenced tree/data blobs and save copied snapshot metadata.

Control flow: resolves whether secondary options represent source or destination, opens source read lock and destination append lock, memorizes snapshot lists, loads both indexes, builds a destination map by original/current IDs, iterates source snapshots, copies missing blobs in batches through destination blob uploader, then saves snapshots with parent cleared and original ID preserved.

State/persistence: writes data/tree blobs, pack files, indexes, and snapshot files to the destination repository. Source repository is read-only. Destination snapshots get new IDs and retain source identity in `Original`.

Dependencies/integration: repository copy helpers, data snapshot filtering, blob indexes, progress UI, and secondary repo global options.

Risks/test signals: deduplication is limited by chunker compatibility and existing destination blobs. Snapshot equivalence ignores parent/original. Tests cover full copy integrity, incremental copy skipping, unstable JSON/symlink data, reverse copy, and empty-password destination.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_copy_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_copy_integration_test.go

Purpose: integration tests for cross-repository snapshot copy.

Important helpers/tests: `testRunCopy` configures source/destination global options via `SecondaryRepoOptions`. `TestCopy` creates three backups, copies them, checks destination integrity, restores source/destination snapshots for content comparison, and verifies batching produced expected pack counts. `TestCopyIncremental` verifies repeated copy skips existing snapshots and later copies only new snapshots, including reverse direction. `TestCopyUnstableJSON` covers copied metadata containing difficult symlink JSON. `TestCopyToEmptyPassword` verifies copying into a repository with no password.

State/persistence: creates two repositories, writes snapshots/blobs into both, restores content to temp dirs, and reads pack/blob counts.

Dependencies/integration: backup, restore, check, list, repository pack-handle listing, and progress helpers.

Risks/test signals: asserts pack-count expectations that can change if batching/pack sizing changes. Provides strong coverage that copy preserves file content and avoids duplicate snapshot copies.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_copy_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_debug.go -->
# sources/sync-backup/restic/cmd/restic/cmd_debug.go

Purpose: debug-build-only command registration and implementations for repository introspection and pack examination.

Important APIs/types/functions: build tag `debug` enables `registerDebugCommand`, `newDebugCommand`, `newDebugDumpCommand`, and `newDebugExamineCommand`. `DebugExamineOptions` controls extraction, reupload, and repair attempts. `runDebugDump` dumps indexes, snapshots, packs, or combined data. `runDebugExamine` resolves pack IDs and calls `repository.ExaminePack`.

Control flow/state: dump opens a read lock and writes JSON/index/pack metadata. examine opens an append lock, loads indexes, then examines each requested pack. Options can extract blobs to the current directory or reupload repaired blobs, making examine potentially mutating.

Dependencies/integration: compiled only with `-tags debug`; uses repository dump/examine internals, data snapshot iteration, restic ID lookup, and UI progress.

Risks/test signals: debug commands expose internals and repair/extract flags can write local files or repository blobs. The file has no direct tests in this subset and is excluded from normal builds unless debug tags are enabled.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_debug_disabled.go -->
# sources/sync-backup/restic/cmd/restic/cmd_debug_disabled.go

Purpose: non-debug build stub for debug command registration.

Control flow/state: build tag `!debug` compiles a `registerDebugCommand` function that accepts the root command/global options and intentionally registers nothing.

Dependencies/integration: paired with `cmd_debug.go` so the restic command tree can call `registerDebugCommand` unconditionally while normal builds omit debug commands.

Risks/test signals: very low risk; correctness is compile-time. Normal CI builds exercise this path.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_debug_disabled.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_diff.go -->
# sources/sync-backup/restic/cmd/restic/cmd_diff.go

Purpose: implements `restic diff`, comparing two snapshots or snapshot subfolders and reporting file additions, removals, modifications, type changes, metadata updates, and summary statistics.

Important APIs/types/functions: `DiffOptions` controls metadata reporting. `Comparer` owns repository access and output callbacks. `Change`, `DiffStat`, and `DiffStatsContainer` model output and JSON statistics. `diffTree`, `printDir`, `collectDir`, `addBlobs`, and `updateBlobs` traverse trees and compute changed blob stats. `runDiff` wires snapshot loading, index loading, output mode, and final stats.

Control flow: requires two snapshot descriptors, opens a read lock, memoizes snapshot listing, finds snapshots/subfolders, loads index, resolves tree directories, recursively dual-iterates tree nodes, prints changes, tracks blob sets before/after/common, updates stats for non-common blobs, and prints text or JSON summary. Quiet mode suppresses individual changes.

State/persistence: read-only except locks/cache. It loads tree blobs and index metadata.

Dependencies/integration: `internal/data` tree iterators, repository blob lookup, UI progress, JSON encoder, and snapshot descriptor parsing.

Risks/test signals: bitrot marker depends on content changes with unchanged metadata and can be affected by backup ignore flags. Recursive error handling prints some child errors without aborting. Integration tests validate text regexes, quiet behavior, JSON change/stat records, and summary counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_diff.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_diff_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_diff_integration_test.go

Purpose: integration tests for snapshot diff output and JSON format.

Important helpers/tests: `setupDiffRepo` creates a repository with two snapshots containing renamed, added, removed, and modified files/directories. `TestDiff` verifies invalid snapshot handling, regex patterns for text output, summary counts, and quiet mode shortening. `TestDiffJSON` parses line-delimited JSON, counts change messages, checks final `DiffStatsContainer`, and verifies quiet JSON emits only statistics.

State/persistence: creates/modifies temp filesystem content, runs backups, and reads diff output.

Dependencies/integration: backup helpers, snapshot map helpers, captured stdout, JSON decoding, and regex matching.

Risks/test signals: regexes are coupled to human-readable output. JSON tests provide a more stable contract for automated consumers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_diff_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_dump.go -->
# sources/sync-backup/restic/cmd/restic/cmd_dump.go

Purpose: implements `restic dump`, extracting a file to stdout or dumping a directory/snapshot subtree as tar or zip.

Important APIs/types/functions: `DumpOptions` contains snapshot filters, archive format, and target path. `splitPath` converts a cleaned POSIX path into path components. `printFromTree` recursively locates the requested node and writes file content or archive data using `dump.Dumper`. `runDump` handles CLI validation, repository access, snapshot lookup, index/tree loading, and output destination. `checkStdoutArchive` refuses archive bytes to an interactive terminal.

Control flow: validates two args and archive type, opens read lock, finds snapshot/subfolder, loads index and tree, chooses raw stdout or `--target` file writer, constructs dumper, and prints selected file or directory. Directory output checks that stdout is redirected unless a target file was specified.

State/persistence: read-only repository access; optionally creates/truncates the target output file. Raw stdout can contain binary archive data.

Dependencies/integration: `internal/dump`, `data` tree loaders, repository blob loading, terminal raw output, and snapshot filters.

Risks/test signals: target file is created before dumping succeeds, so failed dumps may leave partial files. Path handling is POSIX-style inside snapshots. Tests cover `splitPath`; full dump behavior is integration-tested elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_dump.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_dump_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_dump_test.go

Purpose: unit tests for dump path splitting.

Important tests: `TestDumpSplitPath` verifies empty, relative, nested, root, and absolute path inputs produce expected component arrays.

State/dependencies: no repository access; uses `splitPath` and `rtest.Equals`.

Risks/test signals: protects a small but important helper used to locate nodes in snapshot trees. It does not validate archive generation or file content output.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_dump_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_features.go -->
# sources/sync-backup/restic/cmd/restic/cmd_features.go

Purpose: implements `restic features`, listing available feature flags and their state/default/description.

Control flow/APIs: `newFeaturesCommand` registers a no-argument advanced command. It errors if args are supplied, prints a heading, retrieves `feature.Flag.List()`, builds a table with name, type, default, and description, and writes it to terminal output.

State/persistence: read-only; feature enabling/disabling happens elsewhere through `RESTIC_FEATURES`.

Dependencies/integration: `internal/feature`, `internal/ui/table`, global terminal output, and cobra command tree. It documents runtime feature flag availability to users.

Risks/test signals: output depends on feature registry order/content. There are no local tests in this subset; compile and manual command output are the signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_features.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_find.go -->
# sources/sync-backup/restic/cmd/restic/cmd_find.go

Purpose: implements `restic find`, searching snapshots by path patterns, blob IDs, tree IDs, or pack IDs, with optional JSON output and time/snapshot filters.

Important APIs/types/functions: `FindOptions` captures pattern, ID-mode, pack display, sorting, listing, and snapshot filters. `findPattern` stores time range and normalized patterns. `statefulOutput` formats grouped normal/JSON output. `Finder` implements `findInSnapshot`, `findIDs`, `findTree`, `packsToBlobs`, `indexPacksToBlobs`, `findObjectPack`, and `findObjectsPacks`. `runFind` validates options and orchestrates the search.

Control flow: parses time bounds, rejects mixed ID modes, opens read lock, memoizes snapshots, loads index, initializes finder maps for blob/tree/pack modes, resolves pack IDs to blob/tree IDs from repository or index, filters and sorts snapshots, then either walks paths with pattern pruning or walks IDs. JSON output is emitted as arrays grouped by snapshot or object matches.

State/persistence: read-only repository access. It uses the loaded index and snapshot tree walks; no repository mutation.

Dependencies/integration: `internal/walker`, `filter.Match/ChildMatch`, snapshot filtering, repository pack/blob indexes, UI formatting, and JSON encoding.

Risks/test signals: JSON output is manually stateful and must close arrays correctly. Pack lookup falls back to index for missing pack files. Time parsing accepts multiple local formats. Integration tests cover path find, JSON output, sorting/reverse, invalid time range, pack/tree/data lookup, and pack ID resolution.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_find_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_find_integration_test.go

Purpose: integration tests for `restic find` path, JSON, ordering, time validation, and pack/object lookup modes.

Important tests: `TestFind` checks normal path pattern results. `TestFindJSON` verifies JSON match grouping and tree ID searches. `TestFindSorting` checks default newest-first and `--reverse` oldest-first ordering. `TestFindInvalidTimeRange` validates oldest/newest guardrails. `TestFindPackfile` and `TestFindPackID` inspect repository indexes to locate pack IDs, then verify `--pack` JSON output maps pack contents back to snapshot paths and object types.

State/persistence: creates backups in temp repositories, loads indexes, and captures command output. It reads pack/blob metadata but does not mutate repositories after backup.

Dependencies/integration: backup helpers, repository read locks, JSON decoding, progress printers, and platform path normalization.

Risks/test signals: Windows path normalization requires trimming drive-specific prefixes. These tests are a strong contract for JSON consumers and troubleshooting workflows.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_find_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_forget.go -->
# sources/sync-backup/restic/cmd/restic/cmd_forget.go

Purpose: implements `restic forget`, removing snapshot objects explicitly or according to retention policies, and optionally running prune afterward.

Important APIs/types/functions: `ForgetPolicyCount` parses keep counts including `unlimited`; `ForgetOptions` stores count, duration, tag, safety, snapshot filter, grouping, dry-run, and prune options. `verifyForgetOptions` rejects invalid negative counts/durations. `runForget` applies filters/policies and removes snapshots. `ForgetGroup`, `KeepReason`, `asJSONSnapshots`, `asJSONKeeps`, and `printJSONForget` implement JSON output.

Control flow: validates forget and prune options, rejects unsafe `--no-lock` except dry-run, opens an exclusive lock, loads filtered snapshots, either removes explicitly named snapshots or groups snapshots and applies `data.ExpirePolicy`, enforces safety rails against deleting an entire group unless explicitly allowed with filters, removes selected snapshot files in parallel unless dry-run, emits JSON groups, returns a distinct error if any removals failed, and invokes prune when requested.

State/persistence: deletes snapshot files from the repository and may trigger prune to remove unreferenced data. Dry-run avoids deletion. Exclusive locking protects repository mutation.

Dependencies/integration: snapshot filters/grouping/policy logic in `internal/data`, repository remove primitives, prune command, UI progress, and JSON snapshot wrappers.

Risks/test signals: retention policy safety is critical; empty policy plus unsafe remove-all is constrained. Failed partial deletes return `ErrFailedToRemoveOneOrMoreSnapshots`. Tests cover policy count parsing, negative values, host defaulting, and safety-net integration.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_forget.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_forget_integration_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_forget_integration_test.go

Purpose: integration tests for forget safety behavior.

Important helpers/tests: `testRunForgetMayFail` and `testRunForget` invoke `runForget` with a small prune max-unused option. `TestRunForgetSafetyNet` creates two snapshots for a host, verifies invalid keep-tag policy refuses to delete the last snapshot in a group, verifies bare `--unsafe-allow-remove-all` is rejected without filters, verifies forget without policy is rejected, and verifies filtered unsafe remove-all deletes matching snapshots.

State/persistence: creates a real test repository, runs backups, then deletes snapshot objects during the accepted unsafe-filter case.

Dependencies/integration: backup, snapshot listing, `data.SnapshotGroupByOptions`, `data.SnapshotFilter`, and prune option validation.

Risks/test signals: focused on safety rails rather than all retention policy combinations. It is important because forget is destructive.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_forget_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_forget_test.go -->
# sources/sync-backup/restic/cmd/restic/cmd_forget_test.go

Purpose: unit tests for forget option parsing and host filter defaulting.

Important tests: `TestForgetPolicyValues` validates numeric, unlimited, empty, negative, and non-numeric values for `ForgetPolicyCount`. `TestForgetOptionValues` validates allowed and rejected negative keep counts and `keep-within` durations. `TestForgetHostnameDefaulting` verifies `RESTIC_HOST` defaulting, `--host` override, and empty `--host` clearing.

State/persistence: uses environment variable mutation through `t.Setenv` and local pflag parsing only; no repository mutation.

Dependencies/integration: `data.ParseDurationOrPanic`, `pflag`, snapshot filter finalization, and `rtest`.

Risks/test signals: protects destructive-command validation paths before repository access. Does not test actual deletion; integration file handles safety-net deletion behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/cmd/restic/cmd_forget_test.go -->
