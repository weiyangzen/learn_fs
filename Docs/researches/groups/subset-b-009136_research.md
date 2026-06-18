# Research Report: subset-b-009136

This grouped report covers Kopia workflow, build, release, licensing, and Electron UI packaging files. Each section is wrapped in the required source-path markers so it can be split into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/endurance-test.yml -->
# sources/sync-backup/kopia/.github/workflows/endurance-test.yml

## Purpose
Defines the "Endurance Test" GitHub Actions workflow for long-running Kopia endurance coverage. It runs on pushes to `master` and `test/endurance`, tags matching `v*`, a six-hour schedule, and manual dispatch with a `ref` input defaulting to `test/endurance`.

## APIs, Control Flow, and Integration Points
The workflow uses pinned `actions/checkout` and `actions/setup-go`, reads the Go version from `go.mod`, then delegates all test behavior to `make endurance-tests`. The job is guarded with `if: github.repository == 'kopia/kopia'`, so forks do not run the expensive scheduled endurance lane. `KOPIA_KEEP_LOGS=true` is set at job scope, and logs are uploaded from `.logs/**/*.log` through `actions/upload-artifact` under `always()`.

## State, Persistence, and Dependencies
Persistent state is limited to GitHub artifact retention and any logs emitted by the Makefile target. Runtime state comes from the checked-out repository, Go toolchain cache, and generated `.logs` files. The concurrency group is `${{ github.workflow }}-${{ github.ref }}` with cancellation enabled, preventing overlapping endurance runs for the same ref.

## Risks and Test Signals
The main risk is that `workflow_dispatch.inputs.ref` is defined but checkout uses the default ref rather than the input, so manual dispatch may not test the requested branch unless GitHub supplies that ref implicitly elsewhere. The test signal is strong for repository-level endurance behavior because `make endurance-tests` builds an integration binary and runs `tests/endurance_test` with logs preserved.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/endurance-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/htmlui-tests.yml -->
# sources/sync-backup/kopia/.github/workflows/htmlui-tests.yml

## Purpose
Runs Kopia HTML UI end-to-end coverage on macOS for pull requests to `master`, pushes to `master` and `artifacts-pr`, and version tags. It specifically validates the Electron-backed UI path by invoking the repository's Makefile target.

## APIs, Control Flow, and Integration Points
The workflow sets shared Makefile environment flags, including `UNIX_SHELL_ON_WINDOWS`, `ENABLE_UNICODE_FILENAMES` from secrets, and `ENABLE_LONG_FILENAMES=false` because simulated keystrokes can be unreliable with long filenames. The single job checks out the full repository history, installs Go from `go.mod`, installs `gotestsum` via `make install-gotestsum`, then runs `make htmlui-e2e-test`. Screenshots under `.screenshots/**/*.png` are uploaded on every outcome.

## State, Persistence, and Dependencies
State is mostly transient: checked-out source, Go tooling, npm/Electron dependencies reached through Makefile targets, screenshots, and generated logs. The `concurrency` key cancels superseded UI runs for the same workflow/ref pair.

## Risks and Test Signals
The workflow only runs on `macos-latest`, so Linux-specific AppArmor and Windows UI packaging behaviors are outside this lane. It relies on Makefile and app package scripts to provision Node dependencies. The test signal is focused and user-facing: `HTMLUI_E2E_TEST=1` exercises `tests/htmlui_e2e_test`, while screenshot artifacts support debugging visual or interaction failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/htmlui-tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/license-check.yml -->
# sources/sync-backup/kopia/.github/workflows/license-check.yml

## Purpose
Runs dependency license validation for pull requests and pushes to `master`. It verifies both Go and Electron UI dependency license policy through the top-level `make license-check` target.

## APIs, Control Flow, and Integration Points
The workflow checks out full history, installs Go based on `go.mod`, runs `go mod vendor`, and then calls `make license-check`. The Makefile target combines `wwhrd check` for Go modules with `npx license-checker --summary --production --onlyAllow "$(ALLOWED_LICENSES)"` for app production dependencies.

## State, Persistence, and Dependencies
The workflow mutates the workspace by creating a `vendor/` tree before license checking. It does not upload artifacts. The policy is split between `.wwhrd.yml` for Go dependency allow/deny behavior and `ALLOWED_LICENSES` in the Makefile for npm production dependency checks.

## Risks and Test Signals
Because `go mod vendor` runs before `wwhrd`, license results may depend on module graph resolution at the current commit. The npm lane uses production dependencies only, so dev tooling licenses are not covered by this CI gate. The signal is a compliance gate rather than functional test coverage; failures indicate a dependency policy issue or a dependency metadata mismatch.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/license-check.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/lint.yml -->
# sources/sync-backup/kopia/.github/workflows/lint.yml

## Purpose
Runs static analysis, vulnerability checking, formatting checks, lock checks, and cross-OS lint coverage for pull requests to `master`.

## APIs, Control Flow, and Integration Points
The workflow declares read-only repository permissions by default, then grants `security-events: write` at the job level so SARIF can be uploaded. The matrix runs on Ubuntu and macOS. Each job installs Go, runs `govulncheck` twice to produce SARIF and fail on findings, uploads the SARIF via CodeQL, then delegates to `make lint`, `make lint-windows` on Ubuntu, `make check-locks`, and `make check-prettier`.

## State, Persistence, and Dependencies
It creates `govulncheck.sarif`, uses pinned GitHub actions, and relies on the top-level Makefile plus `.golangci.yml` for lint policy. Shared environment variables enable Makefile behavior and optional filename-stress modes controlled by secrets.

## Risks and Test Signals
The workflow grants SARIF upload permission even on macOS; this is required for CodeQL upload but should remain scoped. `govulncheck` is installed at a fixed version, which improves reproducibility but can stale vulnerability knowledge. The signal is broad: Go vulnerability analysis, golangci-lint, Windows cross-linting, custom lock vetting, and app Prettier checks all run before merge.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/lint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/make.yml -->
# sources/sync-backup/kopia/.github/workflows/make.yml

## Purpose
Defines the main multi-platform build and publish workflow. It builds CLI and UI artifacts for Windows, Linux, macOS, and Ubuntu ARM, then stages and publishes releases from a separate Ubuntu job when the event is not a pull request and the repository is `kopia/kopia`.

## APIs, Control Flow, and Integration Points
The build matrix checks out full history, installs Go, installs platform packages, runs `make -j4 ci-setup`, installs macOS certificates when eligible, installs Windows signing tools on Windows, and runs `make ci-build` with signing/notarization secrets. It uploads packaged artifacts and raw binaries separately. The publish job downloads those artifacts, installs QEMU and Docker Buildx, imports GPG and GCS credentials through Makefile targets, runs `make stage-release`, pushes GitHub releases, publishes APT/RPM/Homebrew/Scoop/Docker, and bumps Homebrew for final non-rc tags.

## State, Persistence, and Dependencies
Build outputs persist through GitHub artifacts under `dist` and `dist_binaries`. Secret-derived state includes Apple API key files, macOS certificates, Windows signing tools, GPG keyrings, GCS credentials, and Docker login. The workflow depends heavily on Makefile release targets, `electron-builder`, GoReleaser, GitHub CLI, Docker, and cloud tooling.

## Risks and Test Signals
This file is the highest-blast-radius CI surface in the subset because it handles code signing, notarization, release publication, package repositories, Docker pushes, and formula updates. Secrets are passed only to the specific steps that need them, which limits accidental exposure. Artifact upload patterns are broad and should be reviewed when new dist files are added. The build signal includes compilation, UI packaging, UI tests, changelog generation, and release staging.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/make.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/ossf-scorecard.yml -->
# sources/sync-backup/kopia/.github/workflows/ossf-scorecard.yml

## Purpose
Runs OpenSSF Scorecard analysis for supply-chain posture. It is triggered by branch protection changes, pushes to `master`, and a weekly schedule so the "Maintained" check stays current.

## APIs, Control Flow, and Integration Points
The workflow uses `permissions: read-all` by default and grants `security-events: write` plus `id-token: write` to the analysis job. It checks out the repository without persisted credentials, runs pinned `ossf/scorecard-action`, emits SARIF to `results.sarif`, uploads that SARIF to GitHub code scanning with category `ossf`, and also stores the SARIF as a short-retention artifact.

## State, Persistence, and Dependencies
Persistent state appears in GitHub code scanning, the Scorecard published result, and a five-day artifact. The workflow depends on Scorecard's external checks and GitHub's SARIF ingestion.

## Risks and Test Signals
The permissions are intentionally narrow except for OIDC publication and SARIF upload. Because Scorecard behavior evolves outside this repo, pinned action versions help stability but may lag new checks. The signal is not functional testing; it is a governance and supply-chain health indicator for branch protection, token permissions, maintained status, dependency update behavior, and related repository practices.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/ossf-scorecard.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/providers-core.yml -->
# sources/sync-backup/kopia/.github/workflows/providers-core.yml

## Purpose
Runs cloud and remote storage provider integration tests for core backends: Azure, GCS, S3, and SFTP. It is scheduled daily, runs on pushes to `master`, `test/providers`, and version tags, and supports manual dispatch.

## APIs, Control Flow, and Integration Points
The job is guarded to `kopia/kopia` and non-fork pull request contexts. It checks out the requested ref expression, installs Go, runs `make provider-tests-deps`, then runs `make provider-tests` with `PROVIDER_TEST_TARGET` values. Provider credentials are injected per step via repository secrets. Later provider steps use `if: success() || failure()`, so a failure in Azure does not prevent GCS, S3, and SFTP from running.

## State, Persistence, and Dependencies
External persistent state exists in cloud buckets, immutable containers, S3-compatible endpoints, and any SFTP test service. Local state includes downloaded provider test tooling such as rclone and minio client. No artifacts are uploaded.

## Risks and Test Signals
The ref expression uses `github.event.inputs.ref_name || github.ref`, while the dispatch input is named `ref`; this may prevent manual selection from working as intended. Secret availability and external service flakiness can dominate results. The signal is high value because it exercises real provider implementations under `repo/blob/<target>` using the same Makefile target and environment variables used by developers.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/providers-core.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/providers-extra.yml -->
# sources/sync-backup/kopia/.github/workflows/providers-extra.yml

## Purpose
Runs integration tests for less central providers: B2, Google Drive, Rclone, and WebDAV. It is scheduled twice weekly, runs on `test/providers` and version tags, and supports manual dispatch.

## APIs, Control Flow, and Integration Points
The workflow mirrors the core provider lane: checkout, Go setup, `make provider-tests-deps`, then sequential `make provider-tests PROVIDER_TEST_TARGET=...` invocations with provider-specific secrets. Each provider step after setup uses `if: success() || failure()` to collect as many independent provider results as possible in one run.

## State, Persistence, and Dependencies
It depends on external provider accounts, buckets, folders, WebDAV credentials, and rclone configuration supplied by secrets. Test tooling is prepared by the Makefile, and no log artifacts are explicitly persisted.

## Risks and Test Signals
Like the core provider workflow, checkout references `github.event.inputs.ref_name` even though the dispatch input is `ref`, which is a likely manual-dispatch bug. Provider credentials and remote service rate limits are operational risks. The test signal is narrower than core providers but important for compatibility with optional storage targets and rclone-backed repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/providers-extra.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/race-detector.yml -->
# sources/sync-backup/kopia/.github/workflows/race-detector.yml

## Purpose
Runs Go unit tests with the race detector for pull requests and pushes to `master`.

## APIs, Control Flow, and Integration Points
The workflow checks out full source history, installs Go from `go.mod`, and executes `make -j2 test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s`. The Makefile target routes through `gotestsum`, adds `-tags testing`, and runs the repository test suite while skipping the index blob stress test in the regular `test` target.

## State, Persistence, and Dependencies
State is local and transient: Go build/test cache, `.tmp.unit-tests.json`, and any logs from tests. There is no artifact upload. Concurrency cancellation prevents duplicated race runs on the same ref.

## Risks and Test Signals
The race detector materially increases runtime and resource use, which is why the workflow is Linux-only and uses `-j2`. It does not cover all integration targets, but it is an important signal for shared-memory bugs in core Go packages. Missing artifact upload means debugging depends on GitHub logs unless tests persist their own logs elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/race-detector.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/stale.yml -->
# sources/sync-backup/kopia/.github/workflows/stale.yml

## Purpose
Automates stale issue and pull request management. It runs on a Sunday/Wednesday schedule and can be manually dispatched.

## APIs, Control Flow, and Integration Points
The workflow grants `issues: write` and `pull-requests: write`, then invokes pinned `actions/stale`. Configuration processes older items first, caps operations to 100 per run, labels stale issues and PRs with `stale`, exempts issues labeled `bug` or `keep-open`, exempts PRs labeled `keep-open`, and posts close messages explaining how to reopen and remove the stale label.

## State, Persistence, and Dependencies
Persistent state is GitHub issue/PR labels, comments, and closures. There is no code checkout and no artifact state. The behavior depends entirely on the versioned stale action and repository labels.

## Risks and Test Signals
The workflow can close community work without human intervention, so label policy accuracy is important. The absence of explicit stale day settings means defaults from `actions/stale` control timing; future action version changes could affect behavior. This is an operations workflow, not a test signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/stress-test.yml -->
# sources/sync-backup/kopia/.github/workflows/stress-test.yml

## Purpose
Runs Kopia stress tests on pushes, pull requests, tags, and a two-hour schedule. The job is restricted to the upstream `kopia/kopia` repository.

## APIs, Control Flow, and Integration Points
The workflow checks out full history, installs Go from `go.mod`, executes `make stress-test`, and uploads `.logs/**/*.log` artifacts on every outcome. The Makefile target sets `KOPIA_STRESS_TEST=1`, `KOPIA_DEBUG_MANIFEST_MANAGER=1`, `KOPIA_LOGS_DIR`, and `KOPIA_KEEP_LOGS=1`, then runs `tests/stress_test` and `tests/repository_stress_test` with one-hour timeouts.

## State, Persistence, and Dependencies
Local test state includes logs under `.logs`, Go test cache, and repository data produced by stress tests. Artifacts preserve logs for diagnosis. Concurrency cancels older runs for the same ref.

## Risks and Test Signals
The scheduled cadence is aggressive and may consume CI capacity, but the upstream guard prevents forks from running it. Stress tests can be flaky if they depend on timing, filesystem behavior, or resource availability. The signal is valuable for repository consistency, manifest-manager behavior, and long-running concurrent operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/stress-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/tests.yml -->
# sources/sync-backup/kopia/.github/workflows/tests.yml

## Purpose
Defines the main cross-platform test workflow for pull requests, pushes, tags, and a weekly schedule. It validates unit tests, selected stress coverage, and integration tests across Windows, Linux, macOS, and Ubuntu ARM.

## APIs, Control Flow, and Integration Points
The matrix installs platform prerequisites, runs `make -j4 ci-setup`, then executes `make test-index-blob-v0`, `make ci-tests`, and `make -j2 ci-integration-tests`. `ci-tests` expands to `vet test`; integration tests include robustness tool tests and socket activation tests where platform conditions allow them. Logs from `.logs/**/*.log` are uploaded per matrix OS.

## State, Persistence, and Dependencies
The workflow relies on Makefile-managed Go tools, Node app modules on supported architectures, and platform package managers. It persists logs as artifacts and otherwise keeps test state local. Filename stress options are controlled through secrets.

## Risks and Test Signals
The workflow is broad but still skips or conditions certain expensive or platform-specific targets inside the Makefile. ARM runners may skip UI node module setup because the Makefile limits `app-node-modules` to amd64. The test signal is the primary merge gate for Go unit behavior, index blob stress, vet checks, integration test binaries, socket activation, and robustness tooling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/volume-shadow-copy-test.yml -->
# sources/sync-backup/kopia/.github/workflows/volume-shadow-copy-test.yml

## Purpose
Validates Windows Volume Shadow Copy snapshot behavior on pushes, tags, and pull requests to `master`.

## APIs, Control Flow, and Integration Points
The workflow runs on `windows-latest`, checks out full source, installs Go, installs `gsudo` with Chocolatey, adds it to `GITHUB_PATH`, then runs `make os-snapshot-tests` twice: once elevated and once with `gsudo -i Medium` to simulate non-admin medium-integrity execution. Logs are uploaded on every result.

## State, Persistence, and Dependencies
State includes Windows-specific test artifacts, Go build outputs, and `.logs`. The Makefile target builds a testing binary and executes `tests/os_snapshot_test`. The workflow depends on Chocolatey, gsudo, Windows privilege behavior, and the host's VSS support.

## Risks and Test Signals
Privilege boundaries are the main risk: changes in hosted runner policy or gsudo behavior can affect the test independently of Kopia. Running both elevated and medium-integrity variants gives strong coverage for snapshot code that must behave under different user privileges.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.github/workflows/volume-shadow-copy-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.golangci.yml -->
# sources/sync-backup/kopia/.golangci.yml

## Purpose
Configures golangci-lint v2 for Kopia. It enables all linters by default, then disables noisy or intentionally rejected checks, and sets formatter behavior for `gci` and `gofumpt`.

## APIs, Control Flow, and Integration Points
Key settings include complexity thresholds for `cyclop`, `gocyclo`, and `gocognit`; dependency policy through `depguard` and `gomodguard`; `forbidigo` bans for `filepath.IsAbs`, direct time APIs, and raw `Envar("...")`; `govet` enables all vet checks with zap printf function declarations; `loggercheck` enforces zap-style logging; and formatters enforce import grouping plus gofumpt extra rules. The Makefile's `lint`, cross-OS lint targets, and GitHub `lint.yml` consume this configuration.

## State, Persistence, and Dependencies
This file has no runtime persistence, but it encodes project-wide static policy. Exclusions relax checks for tests and fault/test helper paths, generated code, known false positives, duplicate lines, TODOs, specific unwrapped external errors, field alignment, shadowing, and other accepted patterns.

## Risks and Test Signals
Because `default: all` is used, new golangci-lint releases can introduce new lint failures unless disabled or configured. The broad test-path exclusions reduce noise but can hide real defects in tests. The signal is strong for code style, import hygiene, dependency policy, logging practices, time abstraction discipline, and cross-platform path handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.goreleaser.yml -->
# sources/sync-backup/kopia/.goreleaser.yml

## Purpose
Defines GoReleaser packaging for Kopia CLI Linux, FreeBSD, and OpenBSD artifacts plus archive, checksum, package, signing, and changelog behavior.

## APIs, Control Flow, and Integration Points
The build disables CGO, targets `linux`, `freebsd`, and `openbsd` across `amd64`, `arm`, and `arm64`, uses `-trimpath`, and injects `repo.BuildVersion`, `repo.BuildInfo`, and `repo.BuildGitHubRepo` through ldflags. Archive naming maps OS/architecture labels to Kopia-friendly names and includes `LICENSE` and `README.md`. `nfpms` produces deb and rpm packages under `/usr/bin` with architecture replacements. Checksums are named `checksums.txt`, snapshots use `KOPIA_VERSION_NO_PREFIX`, and checksums are signed through `tools/sign.sh`.

## State, Persistence, and Dependencies
Outputs are under GoReleaser's dist directory, then consumed by Makefile targets and the build/publish workflow. Package metadata persists in release archives, deb/rpm packages, checksums, and signatures.

## Risks and Test Signals
The config does not build macOS or Windows; those are handled manually in the Makefile. Packaging correctness depends on GoReleaser version compatibility, external signing scripts, and architecture replacement names. The main signal is release artifact reproducibility and metadata correctness for Unix-like CLI distributions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.goreleaser.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/.wwhrd.yml -->
# sources/sync-backup/kopia/.wwhrd.yml

## Purpose
Defines Go dependency license policy for `wwhrd`, used by `make license-check-go`.

## APIs, Control Flow, and Integration Points
The denylist blocks GPL-2.0, GPL-3.0, and AGPL 1.0 through 3.0 licenses. The allowlist permits Apache-2.0, MIT, BSD-3-Clause, BSD-2-Clause, MPL-2.0, CC0-1.0, and ISC. A single exception allows `github.com/Azure/azure-sdk-for-go/sdk/internal/...`, reflecting a dependency metadata or internal-package special case.

## State, Persistence, and Dependencies
This file is policy state consumed by the `wwhrd` tool. It does not mutate repository state directly; CI invokes it after vendoring dependencies in the license-check workflow.

## Risks and Test Signals
The allowlist is narrower than the Makefile's npm `ALLOWED_LICENSES`, so Go and npm dependency policy can diverge. The Azure exception should be periodically revalidated because exceptions can mask transitive changes. The signal is a compliance gate for the Go module graph.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/.wwhrd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/Makefile -->
# sources/sync-backup/kopia/Makefile

## Purpose
Central build, test, lint, release, provider-test, UI, and publication orchestrator for Kopia. GitHub Actions mostly delegate to targets in this Makefile, making it the main integration point for CI and developer workflows.

## APIs, Control Flow, and Integration Points
The Makefile includes `tools/tools.mk`, computes Go source lists, defines build flags that inject version/commit/repository metadata, and chooses `kopia_ui_embedded_exe` paths by `GOOS`/`GOARCH`. Core targets include `install`, `lint`, `lint-*`, `check-locks`, `ci-setup`, `kopia-ui`, `kopia-ui-test`, platform-specific binary builds, `ci-build`, `goreleaser`, `ci-tests`, `provider-tests`, `license-check`, endurance/recovery/robustness/stress/VSS tests, HTML UI E2E tests, release staging, GitHub release pushes, package repository publishing, Docker publishing, and performance benchmark automation.

## State and Persistence
It creates and consumes `dist/`, `dist_binaries/`, `.logs/`, `.tmp.*.json`, `.release/`, coverage files, downloaded tools under `tools/.tools`, node modules under `app/`, GPG/GCS credentials, Apple API key files, signed binaries, checksums, package repositories, and cloud benchmark instances. Several targets export environment variables to test binaries, including `KOPIA_EXE`, `KOPIA_LOGS_DIR`, `KOPIA_PROVIDER_TEST`, and stress/debug flags.

## Risks and Test Signals
The file has high operational blast radius because release targets can sign and publish artifacts to GitHub, package repositories, Docker Hub, Homebrew, and Scoop. Conditional platform branches are dense, and typos in paths or architecture mappings can break packaging. It provides the repository's strongest test signals through unit, race, provider, stress, robustness, socket activation, VSS, compatibility, coverage, and HTML UI E2E targets.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/Makefile -->
# sources/sync-backup/kopia/app/Makefile

## Purpose
Builds and tests the Kopia Electron UI application. It handles npm dependency installation, development commands, E2E execution, Electron packaging, and formatting checks.

## APIs, Control Flow, and Integration Points
The file includes `../tools/tools.mk` to reuse pinned tool variables and retry behavior. `deps` creates `node_modules/.up-to-date` by running npm install/ci without audit, then runs `npm audit --omit=dev`. `electron_builder_flags` injects the version from `KOPIA_VERSION`, publish owner/repo, signing behavior, and platform architecture choices. Pull requests normally disable installer publishing and unset signing/notarization variables unless `FORCE_KOPIA_UI_SIGN` is set. `build-electron` depends on the embedded Kopia binary, node modules, public files, and resources, then runs `npm run build-electron`.

## State and Persistence
State includes `node_modules/.up-to-date`, `../dist/kopia-ui/.up-to-date`, packaged UI artifacts under `../dist/kopia-ui`, and Electron Builder side effects. Environment variables such as `CSC_LINK`, `CSC_KEY_PASSWORD`, `KOPIA_UI_NOTARIZE`, `NON_TAG_RELEASE_REPO`, `REPO_OWNER`, `GOOS`, and `KOPIA_UI_CURRENT_ARCH_ONLY` control build state and output shape.

## Risks and Test Signals
The Makefile carefully unsets signing secrets when inappropriate, but signing/notarization behavior remains sensitive to environment leakage. The dependency stamp can become stale if inputs are missed. Test signals include `npm audit --omit=dev`, Playwright E2E via `make e2e-test`, and Prettier checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/notarize.mjs -->
# sources/sync-backup/kopia/app/notarize.mjs

## Purpose
Electron Builder `afterSign` hook that submits macOS KopiaUI builds for Apple notarization when explicitly enabled.

## APIs, Functions, and Control Flow
The module imports `dotenv/config`, `notarize` from `@electron/notarize`, and also imports `fs` and `crypto` though they are unused. It exports default async function `notarizing(context)`. The function returns immediately unless `context.electronPlatformName` is `darwin`. It then checks `process.env.KOPIA_UI_NOTARIZE`; if unset, it logs and skips notarization. Otherwise it builds the `.app` path from `appOutDir` and `context.packager.appInfo.productFilename`, logs progress every 30 seconds, and calls `notarize` with bundle id `io.kopia.ui` plus Apple API issuer, key id, and key path/content from environment variables.

## State, Persistence, and Dependencies
The hook depends on Electron Builder's context object and Apple notarization credentials. It may read `.env` through dotenv side effects. State persists externally in Apple's notarization service and in the signed app bundle after stapling/processing by the notarization library.

## Risks and Test Signals
`clearTimeout(timerId)` is used for an interval; it works in Node because timer clear functions are interchangeable, but `clearInterval` would be clearer. There is no `try/finally`, so a thrown notarization error can leave the interval active until process exit. The app packaging lane is the primary test signal; no standalone tests target this hook.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/notarize.mjs -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/package-lock.json -->
# sources/sync-backup/kopia/app/package-lock.json

## Purpose
Locks the Electron UI npm dependency graph for reproducible installs. It is a npm lockfile version 3 for package `kopia-ui` version `1.0.0`, with 401 package entries.

## APIs, Structure, and Integration Points
The root package matches `package.json` and locks production dependencies `auto-launch`, `electron-log`, `electron-store`, `electron-updater`, `minimist`, `semver`, and `uuid`, plus dev dependencies including `@electron/notarize`, `@playwright/test`, `asar`, `concurrently`, `dotenv`, `electron`, `electron-builder`, `playwright`, `playwright-core`, and `prettier`. Important locked versions include Electron `42.3.0`, Electron Builder `26.14.0`, Electron Updater `6.8.8`, Playwright test `1.60.0`, `@electron/notarize` `3.1.1`, and Prettier `3.8.3`.

## State, Persistence, and Dependencies
The lockfile pins registry tarball URLs, integrity hashes, dependency edges, optional dependency flags, binaries, engine constraints, and platform filters. Optional entries include Windows signing helpers, `fsevents` for Darwin, and several optional transitive packages. Two packages declare install scripts: `electron-winstaller` and `fsevents`. Some locked packages require modern Node versions, including `concurrently` requiring Node `>=22` and several Electron-related packages requiring `>=22.12.0` or Node 18/20+ ranges.

## Risks and Test Signals
The lockfile is a supply-chain boundary: changes should be reviewed for new install scripts, optional native packages, registry sources, and engine shifts. The Makefile's `npm audit --omit=dev`, CI license checks, Prettier checks, and Electron build/test jobs are the main signals that the lock remains compatible and acceptable.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/package-lock.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/package.json -->
# sources/sync-backup/kopia/app/package.json

## Purpose
Defines KopiaUI's Electron package metadata, runtime dependencies, build packaging configuration, and npm scripts.

## APIs, Control Flow, and Integration Points
The package is ESM (`type: module`) with main process entry `public/electron.js`. Runtime dependencies support auto-start integration, logging, local store, updater behavior, CLI argument parsing, semver handling, and UUID generation. Dev dependencies cover notarization, Electron, Electron Builder, Playwright E2E, asar, dotenv, concurrency helpers, and Prettier. Npm scripts expose Electron development, prebuilt start, Playwright E2E, Electron packaging, platform-specific packaging, directory builds, and formatting.

## State and Packaging Behavior
The `build` block configures product `KopiaUI`, app id `io.kopia.ui`, GitHub release publishing, packaged files, preload/resource copying, output directory `../dist/kopia-ui`, Windows NSIS/zip targets, macOS hardened runtime/entitlements/universal embedded server resource, Linux AppImage/deb/rpm targets, AppArmor profiles, and `afterSign: notarize.mjs`. Platform build sections embed the Kopia server binary from `../dist/kopia_*` into app resources.

## Risks and Test Signals
Packaging correctness depends on the top-level Makefile building the expected server binary paths before Electron Builder runs. The package includes `react-scripts` scripts but does not list `react-scripts` as a dependency in this file, suggesting legacy or unused HTML build scripts. Test signals are `npm run e2e`, `npm run prettier:check`, Electron Builder execution, and `npm audit --omit=dev`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/package.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/auto-launch.js -->
# sources/sync-backup/kopia/app/public/auto-launch.js

## Purpose
Implements Electron main-process helpers for enabling, disabling, and querying KopiaUI launch-at-startup behavior.

## APIs, Functions, and Control Flow
The module imports `ipcMain` from Electron, `electron-log`, and `auto-launch`. It constructs an `AutoLaunch` instance named `Kopia`, using a macOS LaunchAgent. Module state `enabled` caches the current launch-at-startup status. `willLaunchAtStartup()` returns the cached value. `toggleLaunchAtStartup()` calls `autoLauncher.disable()` or `.enable()` based on the cache, logs the operation, updates `enabled`, and emits `launch-at-startup-updated` on success. Errors are logged. `refreshWillLaunchAtStartup()` calls `isEnabled()`, refreshes the cache, and emits the same update event.

## State, Persistence, and Dependencies
Persistent state is owned by platform auto-start mechanisms: LaunchAgent on macOS and the platform-specific behavior of `auto-launch` elsewhere. In-process state is the `enabled` cache, synchronized asynchronously from platform state. IPC events notify other main-process listeners or renderer bridges that UI state should refresh.

## Risks and Test Signals
Because toggles are asynchronous and the cache updates only on promise success, rapid repeated toggles can race against stale `enabled` state. The code emits through `ipcMain.emit`, which is suitable for internal main-process eventing but not direct renderer IPC unless bridged elsewhere. Test coverage likely comes from Electron UI E2E paths rather than unit tests for this module.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/auto-launch.js -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/app/public/config.js -->
# sources/sync-backup/kopia/app/public/config.js

## Purpose
Manages KopiaUI repository configuration discovery and in-memory repository list state in the Electron main process.

## APIs, Functions, and Control Flow
The module dynamically imports Node `fs`, `path`, Electron, and `electron-log`; `log` is imported but unused. `portableConfigDirs()` returns candidate portable repository directories from `KOPIA_UI_PORTABLE_CONFIG_DIR`, app-relative macOS paths, and executable-relative non-macOS paths. `globalConfigDir()` lazily chooses the first existing portable directory, marks `isPortable`, or falls back to Electron `appData/kopia`. `loadConfigs()` creates the directory with mode `0700`, scans for files ending in `.config`, stores repo IDs in `configs`, and creates a default `repository` entry with `firstRun=true` when none exist.

## State and Persistence
Persistent state is the config directory and `*.config` files shared with the Kopia CLI. In-memory state includes `configs`, `myConfigDir`, `isPortable`, and `firstRun`. IPC handler `config-list-fetch` emits `config-list-updated-event` with all repo IDs. `deleteConfigIfDisconnected(repoID)` removes non-default in-memory repo IDs if their config file no longer exists. `configForRepo(repoID)` ensures an ID exists in memory and emits an update, but returns the preexisting value, so it returns `undefined` for newly added IDs.

## Risks and Test Signals
The `addNewConfig()` check `if (!configs)` never triggers because `configs` starts as `{}`, so the first manually added repo gets a timestamped ID rather than `repository`; `loadConfigs()` handles the default path separately. Lazy global directory selection means environment and app path must be stable before first use. Test signals come from UI/E2E flows that create, list, disconnect, and delete repository configurations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/app/public/config.js -->
