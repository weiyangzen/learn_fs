# subset-b-000219 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/src/main.rs -->
# sources/cloud-native/nydus-snapshotter/tools/optimizer-server/src/main.rs

## Purpose
This Rust binary is a small optimizer event server for nydus-snapshotter. It enters an optional target process namespace, starts Linux fanotify on a target mount, observes file open/access/execute events, emits one JSON line per unique accessed path to stdout, and exits cleanly on SIGTERM. The output is an access trace containing path, file size, and elapsed microseconds from process start.

## Important APIs, Types, and Functions
- `FanotifyEvent` mirrors `fanotify_event_metadata` with C layout and is read directly from the fanotify fd.
- `EventInfo` is the serialized output contract: `path`, `size`, and `elapsed`; equality intentionally compares only `path`.
- `get_pid()` reads `_MNTNS_PID`; `get_target()` reads `_TARGET` with `/` fallback.
- `set_ns()` wraps `setns(2)` for pid and mount namespaces; `join_namespace()` enters `/proc/<pid>/ns/pid` and `/proc/<pid>/ns/mnt`.
- `init_fanotify()` and `mark_fanotify()` call raw libc `fanotify_init` and `fanotify_mark`, registering `FAN_OPEN`, `FAN_ACCESS`, and `FAN_OPEN_EXEC` on the target mount.
- `read_fanotify()` reads batches of metadata into a raw allocation and converts them to `FanotifyEvent` values.
- `handle_fanotify_event()` polls both the fanotify fd and a SIGTERM socket pipe.
- `send_event()` serializes events with `serde_json` and writes newline-delimited JSON to stdout.

## Control Flow
`main()` optionally joins namespaces, then forks. The child initializes fanotify, marks the configured target mount, and enters the poll loop. The parent logs the child pid/pgid and waits for termination, reporting signaled or stopped status. In the child loop, fanotify readiness triggers event reads; each event fd is resolved via `/proc/self/fd/<fd>`, metadata is collected, unique paths are emitted, and the event fd is always closed. SIGTERM readiness prints a termination line and breaks the loop.

## State and Persistence
There is no durable state. Runtime state consists of `BEGIN_TIME`, a per-process duplicate vector of emitted paths, namespace membership, kernel fanotify marks, and open event fds. The only persisted side effect is stdout JSON consumed by the caller. Duplicate suppression grows in memory for the lifetime of the child process.

## Dependencies and Integration Points
The file depends on Linux-only fanotify, `/proc`, Unix sockets, and namespace APIs from `nix` and `libc`. It integrates with snapshotter optimization tooling through environment variables and stdout traces. Consumers must expect stderr diagnostics and stdout JSON lines interleaved with the SIGTERM message if they do not filter non-JSON output.

## Risks and Edge Cases
- `read_fanotify()` casts raw buffers and uses `sizeof as usize`; if `read` returns `-1`, conversion to `usize` can produce invalid slice length. Nonblocking reads that return `EAGAIN` are not handled.
- The code assumes event records are exactly `FanotifyEvent` sized and ignores variable-length metadata semantics.
- Duplicate tracking is O(n) path lookup and unbounded.
- Namespace joining occurs before fork and may surprise parent-side wait/log behavior if pid namespace semantics differ.
- `fanotify_init` and mount marks require privileges; failure is logged but not retried.
- `CString::new(path)` rejects targets containing interior NULs.

## Test Signals
No local tests are in this file. Practical coverage comes from integration use of the optimizer server under privileged Linux, verifying emitted JSON format, duplicate suppression, SIGTERM exit, and namespace-targeted access capture. Unit tests would need abstraction around raw syscalls to cover error paths safely.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/tools/optimizer-server/src/main.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/version/version.go -->
# sources/cloud-native/nydus-snapshotter/version/version.go

## Purpose
This Go package centralizes build identity values for nydus-snapshotter. It exposes package-level variables for semantic version, VCS revision, Go runtime version, and build timestamp.

## Important APIs, Types, and Functions
- `Version`, `Revision`, and `BuildTimestamp` default to `"unknown"` and are intended to be overridden at link time with `-ldflags -X`.
- `GoVersion` is initialized from `runtime.Version()` at program startup.
- There are no functions or custom types.

## Control Flow
Package initialization assigns the variable values. Downstream binaries import the package and include these variables in version output or diagnostics.

## State and Persistence
State is process-global and immutable by convention, though exported variables can be modified by other Go code. No persistence occurs.

## Dependencies and Integration Points
The only code dependency is Go's `runtime` package. Build scripts and release pipelines integrate by injecting the true values during linking.

## Risks and Edge Cases
If build flags are omitted, release binaries report `"unknown"` version, revision, and timestamp. Because the values are variables rather than constants, accidental mutation is possible in tests or runtime code.

## Test Signals
No tests are present in this file. Validation is typically through CLI `version` output in built artifacts and release jobs that assert ldflags were applied.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/bug-report.yml -->
# sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/bug-report.yml

## Purpose
This GitHub issue form captures structured bug reports for Nydus with the `bug` label. It asks for problem, expected behavior, actual behavior, reproduction steps, environment, additional context, and willingness to submit a PR.

## Important APIs, Types, and Functions
The file uses GitHub issue forms YAML fields: `name`, `title`, `description`, `labels`, and a `body` list of `markdown`, `textarea`, and `checkboxes` controls. Required validations exist for problem description, expected behavior, actual behavior, reproduction steps, and environment details.

## Control Flow
When a user chooses this template, GitHub renders the form, enforces required fields, and creates an issue with the configured title prefix and label. The environment textarea seeds fields for snapshotter version, Nydus version, container runtime, OS, and kernel.

## State and Persistence
The form itself has no runtime state. Submitted values become persisted GitHub issue content.

## Dependencies and Integration Points
It integrates with GitHub Issues, project triage labels, and maintainers' diagnostic workflow. The environment fields are tuned for container runtime and kernel-level issues.

## Risks and Edge Cases
The template does not require logs as a separate field, so important artifacts may be omitted despite being requested in text. The environment details are free-form, which keeps flexibility but prevents automatic parsing.

## Test Signals
Validation is through GitHub's issue-template parser and manual issue creation. Required fields provide basic input quality gates.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/bug-report.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/feature-request.yml -->
# sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/feature-request.yml

## Purpose
This GitHub issue form collects feature requests and applies the `feature` label. It focuses on desired behavior, the problem/use case, related issues, and potential contributor interest.

## Important APIs, Types, and Functions
The issue-form schema defines markdown guidance, required textareas for `Feature Description` and `Problem and Use Case`, an optional `Related issues` textarea, and a PR willingness checkbox.

## Control Flow
GitHub renders the form and blocks submission until the required feature and use-case fields are filled. The created issue receives a `[Feature]` title prefix and the configured label.

## State and Persistence
Submitted form fields become issue body content. No repository runtime state is affected.

## Dependencies and Integration Points
The template integrates with GitHub Issues and maintainer planning processes. Related issue capture helps connect requests to existing discussions.

## Risks and Edge Cases
There is no explicit acceptance criteria, design proposal, compatibility, or operational impact field, so high-level requests may still require follow-up. The related issue field is optional and unstructured.

## Test Signals
GitHub form validation covers schema correctness and required field enforcement. Maintainer review quality depends on human triage.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/feature-request.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/improvement-report.yml -->
# sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/improvement-report.yml

## Purpose
This issue form captures suggested improvements to existing Nydus behavior or process and labels them `improvement`.

## Important APIs, Types, and Functions
The template defines required `problem-summary` and `proposed-improvement` textareas, optional `additional-context`, and a PR willingness checkbox. It also declares an empty `assignees` list.

## Control Flow
GitHub presents the fields, requires summary and proposal, then stores the submitted issue with an `[Improvement]` title prefix.

## State and Persistence
Only GitHub issue content and labels are persisted.

## Dependencies and Integration Points
It fits GitHub Issues triage and separates refinement work from new feature requests and bugs.

## Risks and Edge Cases
The template does not ask for current behavior, expected measurable outcome, compatibility impact, or affected component. Improvements that are actually bugs or features may need relabeling.

## Test Signals
GitHub issue-form schema validation is the main test signal; required fields enforce minimum substance.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/ISSUE_TEMPLATE/improvement-report.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/codecov.yml -->
# sources/cloud-native/nydus/.github/codecov.yml

## Purpose
This config defines Codecov thresholds and comment behavior for Nydus coverage reporting.

## Important APIs, Types, and Functions
- Project coverage is enabled with a `70%` target and `0%` threshold.
- Patch coverage is enabled with an `80%` target and `0%` threshold.
- PR comments use layout `"reach, diff, flags, files"`, default behavior, and only post when coverage changes.
- `codecov.require_ci_to_pass` is false while `notify.wait_for_ci` is true.

## Control Flow
Codecov consumes this YAML after CI uploads coverage artifacts. It calculates project and patch statuses and controls whether a comment is posted.

## State and Persistence
Codecov stores coverage results externally. The repository file only controls policy.

## Dependencies and Integration Points
It integrates with `.github/workflows/smoke.yml`, whose coverage jobs upload `codecov.json`, Go `coverage.txt`, and smoke coverage files through `codecov/codecov-action`.

## Risks and Edge Cases
With `threshold: 0%`, any drop below target can fail the Codecov status. Since `require_ci_to_pass` is false, Codecov may process independently of CI success, but `wait_for_ci` delays notification. The validation comment notes the external Codecov validator should be used after changes.

## Test Signals
The config itself is validated by Codecov's validator endpoint and by observing PR coverage statuses/comments after workflow runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/dependabot.yml -->
# sources/cloud-native/nydus/.github/dependabot.yml

## Purpose
This Dependabot config schedules weekly dependency update checks for Go modules, Cargo crates, and GitHub Actions.

## Important APIs, Types, and Functions
The config is version `2` and has three update entries:
- `gomod` in `/contrib/`
- `cargo` in `/`
- `github-actions` in `/`
All run weekly.

## Control Flow
Dependabot scans the configured ecosystems on its schedule and opens update PRs when newer compatible versions are found.

## State and Persistence
Dependabot state lives in GitHub. The repository receives PRs and updated lock/config files when changes are proposed.

## Dependencies and Integration Points
This integrates with Cargo workspace dependencies, Go contrib modules, and workflow action versions. The smoke, release, convert, benchmark, and e2e workflows are the primary CI gates for resulting PRs.

## Risks and Edge Cases
Only `/contrib/` is scanned for Go modules, so Go modules elsewhere would be missed unless covered by that root. Weekly batching can create large update PRs. No groups, ignore rules, or labels are configured.

## Test Signals
Successful Dependabot PR creation and CI pass/fail on those PRs are the test signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/benchmark.yml -->
# sources/cloud-native/nydus/.github/workflows/benchmark.yml

## Purpose
This GitHub Actions workflow benchmarks OCI and Nydus image modes on a scheduled Monday/Wednesday cadence, on manual dispatch, and when the workflow file itself changes in PRs.

## Important APIs, Types, and Functions
Jobs include `contrib-build`, `nydus-build`, `benchmark-description`, four benchmark matrices (`benchmark-oci`, `benchmark-fsversion-v5`, `benchmark-fsversion-v6`, `benchmark-zran`), and `benchmark-result`. The image matrix covers wordpress, node, python, golang, ruby, and amazoncorretto. The workflow uses `actions/checkout`, `actions/setup-go`, `Swatinem/rust-cache`, `dsherret/rust-toolchain-file`, artifact upload/download actions, `misc/prepare.sh`, and `make smoke-benchmark`.

## Control Flow
The workflow builds `nydusify` and Nydus binaries, uploads them as artifacts, then each benchmark job downloads them and runs `sudo -E make smoke-benchmark` with `BENCHMARK_TEST_IMAGE`, `BENCHMARK_MODE`, and `BENCHMARK_METRIC_FILE`. The result job downloads JSON artifacts for each image and appends a markdown table to `GITHUB_STEP_SUMMARY` using `jq` and `awk`.

## State and Persistence
Artifacts carry built binaries and per-image benchmark JSON between jobs. Step summaries persist benchmark tables in the Actions UI. No repository files are changed.

## Dependencies and Integration Points
The workflow depends on Makefile `nydusify-release`, `release`, and `smoke-benchmark`, the smoke benchmark harness, Docker/container runtime setup from `misc/prepare.sh`, and `jq` for summary generation.

## Risks and Edge Cases
Benchmarks are sensitive to runner CPU, memory, network, registry availability, and Docker state. The summary shell has nested quoting for python/ruby workload descriptions that is fragile. It uploads separate artifacts per image and mode, so artifact naming consistency is critical for the final result job.

## Test Signals
Benchmark job success, uploaded metric JSON files, and rendered `GITHUB_STEP_SUMMARY` tables are the main signals. Comparing OCI, RAFS v5, RAFS v6, and zran rows exposes performance regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/benchmark.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/convert.yml -->
# sources/cloud-native/nydus/.github/workflows/convert.yml

## Purpose
This scheduled/manual workflow converts a curated list of top container images into several Nydus formats, validates them, uploads conversion metrics, and renders image-size/conversion-time summaries.

## Important APIs, Types, and Functions
Global env includes `REGISTRY=ghcr.io`, `ORGANIZATION=${{ github.repository }}`, `IMAGE_LIST_PATH`, and `FSCK_PATCH_PATH`. Jobs build `nydusify`, Nydus, and `fsck.erofs`; conversion jobs cover `convert-zran`, `convert-native-v5`, `convert-native-v6`, and `convert-native-v6-batch`; `convert-metric` aggregates outputs. The workflow invokes `nydusify convert`, `nydusify check`, a local Docker registry on port 5000, and `fsck.erofs`.

## Control Flow
Build jobs produce artifacts. The zran and v6 jobs additionally download `fsck.erofs`. Each convert job logs in to GHCR with `GITHUB_TOKEN`, downloads binaries into `/usr/local/bin`, starts a local registry, loops over `misc/top_images/image_list.txt`, converts/pushes/checks images, writes per-image JSON metrics, and uploads a metric directory. The final job downloads metric artifacts, uses `jq` and `bc` to calculate MB and ms values, writes summary tables, and deletes intermediate artifacts.

## State and Persistence
External state includes pushed GHCR tags such as `nydus-nightly-v5`, `nydus-nightly-v6`, `nydus-nightly-v6-batch`, and `nydus-nightly-oci-ref`. Local state includes Docker images/registry data and conversion output directories. Artifact state transports binaries and metrics.

## Dependencies and Integration Points
The workflow depends on GHCR permissions, Docker, Go, Rust builds, EROFS utilities at tag `v1.6` plus repository patch, `misc/top_images`, `nydusify` semantics, and Makefile release targets.

## Risks and Edge Cases
The workflow mutates registry tags nightly. It assumes `latest` exists for all listed images and that linux/amd64 and linux/arm64 conversion works. zran skips influxdb explicitly. External downloads, GHCR throttling, Docker disk pressure, local registry startup, and `fsck.erofs` patch application are failure points. The final summary assumes all metric JSON files exist for all images; skipped zran images can break aggregation unless the list excludes them or the file is otherwise present.

## Test Signals
Successful conversion/check loops, `fsck.erofs` validation for zran/v6 modes, uploaded metric artifacts, and final summary tables are the workflow's signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/convert.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/e2e-dragonfly.yml -->
# sources/cloud-native/nydus/.github/workflows/e2e-dragonfly.yml

## Purpose
This workflow validates Nydus integration with Dragonfly proxy/cache paths. It runs on pushes, PRs excluding documentation/image-only changes, daily schedule, and manual dispatch.

## Important APIs, Types, and Functions
It sets `DRAGONFLY_VERSION=2.4.3` and `CLIENT_VERSION=1.3.3`. Jobs include `nydus-build`, `dragonfly-download`, matrix `e2e-test` for `http-proxy`, `sdk-proxy`, `sdk-proxy-strict`, and `http-proxy-strict`, and `proxy-error-test`. It uses MySQL, Redis, manager, scheduler, dfdaemon, `crane`, `nydusd`, and Go tests under `smoke/dragonfly`.

## Control Flow
Nydus is built and uploaded. Dragonfly binaries are cached or downloaded and uploaded. The e2e job downloads both artifact sets, installs executables, starts MySQL and Redis with readiness loops, installs Dragonfly configs, installs `crane`, extracts a Nydus bootstrap layer from a matrix image, and runs `go test -run TestDragonflyE2E` with environment variables pointing at binaries, configs, cache/log dirs, and bootstrap. The proxy-error job extracts a bootstrap and runs `TestProxyErrorSimulation`. Both jobs collect logs and cleanup processes/mounts in `always()` steps.

## State and Persistence
Runtime state lives in Docker containers, `/tmp/dragonfly-*`, `/tmp/nydus-*`, `/etc/dragonfly`, and uploaded log artifacts. Artifact state passes Nydus and Dragonfly binaries across jobs.

## Dependencies and Integration Points
The workflow integrates with Dragonfly releases, Dragonfly client releases, GHCR image-service images, Go smoke tests, `misc/dragonfly` configs, and Nydus HTTP proxy/SDK proxy backend configuration.

## Risks and Edge Cases
It depends heavily on external downloads and image availability. Bootstrap extraction uses Python heuristics over image manifest layers and can fail if annotations/media types change. The cleanup kills only the newest process matching names, which may miss multiple stray processes. MySQL/Redis startup and port availability can cause flakiness. It requires privileged operations for mounts and daemon behavior.

## Test Signals
Signals include successful build/download jobs, matrix Go test pass/fail, proxy error simulation pass/fail, and uploaded diagnostic logs for all modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/e2e-dragonfly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/miri.yml -->
# sources/cloud-native/nydus/.github/workflows/miri.yml

## Purpose
This workflow runs Rust unit tests under Miri to detect undefined behavior in interpreter-supported code paths.

## Important APIs, Types, and Functions
It triggers on push, PR, daily schedule, and manual dispatch. The single job `nydus-unit-test-with-miri` checks out code, uses the Rust cache, installs cargo-nextest, sets up fscache, installs nightly Miri, installs protoc, and runs `sudo -E RUSTUP=<path> make miri-ut-nextest`.

## Control Flow
After setup, the Makefile target runs `cargo miri nextest` on workspace tests excluding integration and two known unsupported/heavy tests. Output is tee'd to `miri-ut.log`, and the workflow greps for `Undefined Behavior`.

## State and Persistence
State includes the Rust toolchain override to nightly in the workspace, cargo cache, fscache setup, and `miri-ut.log` in the Actions workspace. No artifacts are uploaded.

## Dependencies and Integration Points
This depends on the Makefile `miri-ut-nextest` target, `misc/fscache/setup.sh`, `misc/install-protoc.sh`, nightly Rust/Miri, and the workspace test suite.

## Risks and Edge Cases
The final `grep -C 2 'Undefined Behavior' miri-ut.log` returns nonzero when no match is found, which can make an otherwise clean run fail unless shell behavior or preceding pipeline masks it. Running with `sudo -E` and Miri isolation disabled changes environment assumptions. Nightly toolchain changes may introduce flakiness.

## Test Signals
The primary signal is Miri execution of unit tests and absence of UB reports. The workflow currently also treats grep behavior as a signal, so its exit semantics should be watched.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/miri.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/release.yml -->
# sources/cloud-native/nydus/.github/workflows/release.yml

## Purpose
This workflow builds release artifacts for tagged Nydus releases and daily sanity checks, covering Linux, macOS, Go contrib binaries, tarballs, GitHub releases, GoReleaser packaging, and SLSA provenance.

## Important APIs, Types, and Functions
Jobs include multi-arch `nydus-linux`, multi-arch `nydus-macos`, multi-arch `contrib-linux`, `prepare-tarball-linux`, `prepare-tarball-darwin`, `create-release`, `goreleaser`, and `provenance`. It uses `cross`, Docker Buildx for riscv64, a custom cross Dockerfile, `make static-release`, `make contrib-release`, `actions/upload-artifact`, `softprops/action-gh-release`, `goreleaser/goreleaser-action`, and SLSA generator.

## Control Flow
On tag push, schedule, or manual dispatch, Linux and macOS jobs build static binaries per arch and upload artifacts. Contrib jobs build Go tools. Tarball jobs download/merge artifacts, produce `nydus-static-<tag>-<os>-<arch>.tgz` and sha256sum files, and upload them. `create-release` downloads tarballs and creates a GitHub release only for push events. `goreleaser` runs only for tag pushes, prepares context from artifacts, runs checks and release, and emits base64-encoded subject hashes. `provenance` runs SLSA generation for tag pushes.

## State and Persistence
Persistent outputs are GitHub Actions artifacts, release assets, GoReleaser artifacts, checksums, and provenance attestations. Runtime state includes cross containers, cargo/go caches, and copied `misc/configs`.

## Dependencies and Integration Points
The workflow depends on the workspace Makefile, rust-toolchain, `Cross.toml`, Go workspace, `goreleaser.sh`, GoReleaser config, GitHub release permissions, and SLSA workflow interface.

## Risks and Edge Cases
The provenance job references `${{ needs.release.outputs.tag_name }}`, but there is no `release` job in `needs`; the tag output is defined by `goreleaser`, so this expression appears incorrect. The `provenance` job depends only on `goreleaser`; if draft upload tag is miswired, attestation upload may fail. Multi-arch builds rely on cross image/toolchain compatibility. Scheduled runs have no tag, so tarball naming from `GITHUB_REF` may produce branch-like names and release steps are skipped by event conditions.

## Test Signals
Signals include successful multi-arch binary builds, uploaded artifacts/tarballs/checksums, release asset creation on tag push, GoReleaser check/release success, and SLSA provenance completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/smoke.yml -->
# sources/cloud-native/nydus/.github/workflows/smoke.yml

## Purpose
This is the main CI smoke and quality workflow for Nydus. It builds Rust and Go components across architectures, runs lint/unit/smoke/performance/takeover tests, produces Rust and Go coverage, uploads coverage to Codecov, and runs cargo-deny.

## Important APIs, Types, and Functions
Major jobs include `contrib-build`, `contrib-lint`, `nydus-build`, `nydusd-build-macos`, `nydus-integration-test`, `nydus-unit-test`, `contrib-unit-test-coverage`, `nydus-unit-test-coverage`, `nydus-integration-test-coverage`, `upload-coverage-to-codecov`, `upload-pr-coverage-to-codecov`, `nydus-cargo-deny`, `performance-test`, and `takeover-test`. It uses setup-go, rust-cache, rust-toolchain-file, cross builds, Docker Buildx, cargo-nextest, cargo-llvm-cov, golangci-lint, Codecov, cargo-deny, and smoke Makefile targets.

## Control Flow
Build jobs produce amd64 artifacts for later tests while still validating several architectures. Integration tests download current artifacts, fetch older release binaries, prepare the runtime environment, export `NYDUS_*` paths for old/stable/latest versions, and run `make smoke-only`. Unit tests run nextest with fscache setup. Coverage jobs generate Rust and Go coverage artifacts; PR coverage also builds instrumented Nydus and nydusify binaries, wraps them to set `LLVM_PROFILE_FILE`, runs smoke tests, validates raw coverage files exist, converts Go covdata, and emits cargo llvm-cov reports. Upload jobs aggregate coverage line states for preview and call Codecov. Performance and takeover jobs run smoke harness subsets with built artifacts.

## State and Persistence
Artifacts persist binaries and coverage files between jobs. Runtime state includes Docker layers, downloaded release tarballs, `/usr/bin/nydus-*` installs, workdir/cache dirs, coverage raw files, and step logs. Codecov receives uploaded reports externally.

## Dependencies and Integration Points
The workflow ties together Cargo workspace builds, contrib Go projects, Makefile targets, smoke test harnesses, external GitHub release API calls, Docker-based environment preparation, Codecov, cargo-deny policy, and architecture-specific cross-build support.

## Risks and Edge Cases
This workflow is resource-heavy and sensitive to disk pressure; it uses an explicit free-disk-space action for integration paths. External latest-release downloads can introduce nondeterminism. Only amd64 artifacts are uploaded for downstream tests, even though build matrices validate other arches. Coverage instrumentation is complex and can fail if wrappers, sudo environment preservation, or raw profile generation changes. Codecov upload requires secrets for non-PR unit upload but PR upload runs without that credentials gate.

## Test Signals
A passing smoke workflow gives broad confidence: multi-arch compile, Go lint, Rust nextest, smoke integration across versions, coverage generation, cargo-deny, performance, and takeover tests. The workflow also prints coverage previews before uploading.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/smoke.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/stale.yaml -->
# sources/cloud-native/nydus/.github/workflows/stale.yaml

## Purpose
This scheduled/manual workflow marks inactive issues and PRs stale and closes them after additional inactivity.

## Important APIs, Types, and Functions
It grants `issues: write` and `pull-requests: write` and uses `actions/stale@v10`. Configuration marks both issues and PRs after 60 idle days, closes after 7 stale days, labels stale items with `stale`, exempts `bug` and `wip` labels, exempts all milestones, and posts configured stale/close messages.

## Control Flow
The workflow runs daily at midnight UTC or manually. The stale action scans issues and PRs, applies labels/messages based on age and exemptions, then closes stale items that remain inactive.

## State and Persistence
Persistent state is GitHub issue/PR labels, comments, and closed status. The repository tree is unchanged.

## Dependencies and Integration Points
This integrates with GitHub Issues/PRs and the repository labeling/milestone conventions. It relies on maintainers applying `bug`, `wip`, or milestones to prevent stale handling.

## Risks and Edge Cases
The workflow can close valid but inactive work if labels or milestones are missing. It treats PRs and issues with the same timing. It has no operation limit configured, so default action limits apply.

## Test Signals
Manual dispatch on a test repository or dry-run-style review of action logs validates behavior. In production, labels/comments/closures are the signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/.github/workflows/stale.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/Cargo.toml -->
# sources/cloud-native/nydus/Cargo.toml

## Purpose
This is the root Cargo manifest for the Nydus Rust workspace and main `nydus-rs` package. It defines binaries, library target, dependencies, feature flags, profiles, workspace members, and shared workspace dependency versions.

## Important APIs, Types, and Functions
The package exports binaries `nydusctl`, `nydusd`, and `nydus-image`, plus library `nydus`. Workspace members include `api`, `builder`, `clib`, `rafs`, `storage`, `service`, `upgrade`, and `utils`. Default features enable FUSE backend support, several storage backends, and dedup. Optional features include `virtiofs`, `block-nbd`, `block-uffd`, backend-specific flags, and `dedup`.

## Control Flow
Cargo uses this manifest to resolve workspace crates and build selected targets. Target-specific dependencies enable the Dragonfly proxy backend for x86_64/aarch64. Release profile sets `panic = "abort"`; dev profile uses `opt-level = 1` and debug info.

## State and Persistence
Cargo generates build artifacts under `target/` and lockfile state elsewhere in the repository. This file itself stores dependency and feature policy.

## Dependencies and Integration Points
The manifest ties together external crates such as `fuse-backend-rs`, `hyper`, `tokio`, `rusqlite`, `openssl` vendored, rust-vmm crates, and internal Nydus crates. CI Makefile targets and workflows call Cargo through this manifest.

## Risks and Edge Cases
Feature coupling is significant: default builds include many backend features, while `virtiofs` pulls several optional rust-vmm crates. Vendored OpenSSL improves static build reproducibility but increases build time. Target-specific Dragonfly proxy support means behavior can differ on unsupported architectures.

## Test Signals
`make build`, `make release`, `make ut-nextest`, `make miri-ut-nextest`, CI smoke builds, and cargo-deny are the key validation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/Cross.toml -->
# sources/cloud-native/nydus/Cross.toml

## Purpose
This config customizes `cross` pre-build setup for cross-compiling Nydus.

## Important APIs, Types, and Functions
The `[build].pre-build` list installs `cmake` and `unzip`, then downloads and installs protobuf `protoc` v29.6 into `/usr/local`.

## Control Flow
When `cross` builds a target, it runs these pre-build shell commands inside the build container before Cargo compilation.

## State and Persistence
State is container-local package installation and `/usr/local` protoc files. No repository files are modified.

## Dependencies and Integration Points
This integrates with release/smoke workflows that install `cross` and run `make static-release` for non-RISC-V Linux architectures. It supports crates or build scripts requiring protobuf generation.

## Risks and Edge Cases
The config downloads from GitHub during builds, so network availability and checksum trust matter. It assumes x86_64 Linux protoc is acceptable in the cross build environment. Apt package names must match the base image.

## Test Signals
Successful cross static builds in smoke/release workflows validate this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/Cross.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/Makefile -->
# sources/cloud-native/nydus/Makefile

## Purpose
This Makefile is the main developer and CI command surface for building, testing, installing, cleaning, coverage, smoke tests, and Go contrib components.

## Important APIs, Types, and Functions
Top-level targets include `all`, `all-build`, `all-release`, `all-static-release`, `all-install`, `build`, `release`, `static-release`, `clean`, `install`, `ut`, `ut-nextest`, `miri-ut-nextest`, `smoke-only`, `smoke-performance`, `smoke-benchmark`, `smoke-takeover`, coverage targets, and contrib build/test/lint/install targets. Variables include `TEST_WORKDIR_PREFIX`, `INSTALL_DIR_PREFIX`, `DOCKER`, `CARGO`, `RUSTUP`, `CARGO_COMMON`, `STATIC_TARGET`, `RUST_TARGET_STATIC`, and coverage-related env values.

## Control Flow
The Makefile derives OS/architecture, adjusts Cargo features and static targets, and dispatches Rust builds through Cargo. `build` first checks formatting, then builds and runs clippy with warnings denied and a small allowlist. `release` wraps `build`; `static-release` cleans stale libz-sys, selects a target, and builds. Test targets run Cargo test/nextest/Miri. Contrib targets call `build_golang`, which either runs Go make targets in Docker or directly with `make -C`.

## State and Persistence
Build artifacts are written under Cargo target directories, contrib output directories, coverage directories, and optional install prefix. Some test targets create workdirs under `/tmp` or configured prefixes. `clean` removes coverage and Cargo artifacts.

## Dependencies and Integration Points
This file is invoked by nearly every workflow in this subset. It integrates Cargo, rustup, nextest, cargo llvm-cov, grcov, Go contrib Makefiles, Docker, and smoke sub-Makefile targets.

## Risks and Edge Cases
`build` always runs formatting and clippy, so release builds include lint policy. `DOCKER` defaults to `"true"` for Go contrib builds, which can surprise local users. Static target selection has architecture-specific branches for ppc64le/riscv64/Darwin. Coverage flags are injected through environment-variable string expansion and must be preserved under `sudo -E` in workflows.

## Test Signals
The Makefile itself is validated by CI: smoke, release, benchmark, convert, miri, and coverage workflows all call these targets. Local signals are successful `make build`, `make ut-nextest`, and relevant smoke targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/Cargo.toml -->
# sources/cloud-native/nydus/api/Cargo.toml

## Purpose
This manifest defines the `nydus-api` crate, which contains API data types, HTTP request/response abstractions, endpoint handlers, configuration parsing types, and error helpers for Nydus.

## Important APIs, Types, and Functions
Package metadata sets name `nydus-api`, version `0.4.1`, Apache-2.0/BSD-3-Clause licensing, and homepage. Dependencies include `backtrace`, `dbs-uhttp`, `libc`, `log`, `serde`, `serde_json`, `thiserror`, and `toml`. Features are `error-backtrace` and `handler`.

## Control Flow
Cargo builds this crate as a workspace member and consumers enable optional features. `error-backtrace` activates richer logging in error macros; `handler` likely gates HTTP handler modules elsewhere in the crate.

## State and Persistence
No runtime state is stored in the manifest. It controls dependency resolution and feature compilation.

## Dependencies and Integration Points
The root `nydus-rs` crate depends on this crate with `error-backtrace` and `handler` features. HTTP modules integrate with `dbs-uhttp`; config modules integrate with serde/toml/json.

## Risks and Edge Cases
Feature-gated behavior means tests should cover both default and root-enabled feature sets if API consumers use different combinations. Version must remain synchronized with root manifest dependency expectations.

## Test Signals
Workspace builds and `nydus-api` unit tests validate the manifest. Root CI exercises it through `make build`, unit tests, smoke tests, and Miri.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/openapi/nydus-api-v1.yaml -->
# sources/cloud-native/nydus/api/openapi/nydus-api-v1.yaml

## Purpose
This OpenAPI 3.0.2 document describes the public Nydus v1 HTTP management API under `http://localhost/api/v1`.

## Important APIs, Types, and Functions
Endpoints include `/daemon` GET/PUT, `/daemon/events`, `/daemon/backend`, `/daemon/exit`, `/mount` POST/PUT/DELETE, `/metrics`, `/metrics/files`, `/metrics/pattern`, `/metrics/backend`, `/metrics/blobcache`, and `/metrics/inflight`. Schemas include `DaemonInfo`, `DaemonConf`, `DaemonFsBackend`, `MountCmd`, `ErrorMsg`, `RafsMetrics`, `RafsFilesMetrics`, `RafsLatestReadFiles`, `RafsFilesAccessPatterns`, `RafsBackend`, `Blobcache`, `FuseInflight`, and `Events`.

## Control Flow
Clients issue JSON HTTP requests to daemon endpoints. Mutating operations such as configure, exit, mount, remount, and unmount return `204` on success. Read operations return JSON schemas or error messages. Query parameters select mountpoint or optional filesystem id.

## State and Persistence
The API exposes and mutates daemon runtime state: log level, daemon lifecycle, mounts, backend configuration, metrics, file access state, and inflight requests. It does not itself define persistence semantics.

## Dependencies and Integration Points
The contract maps to Rust types in `api/src/http.rs` and endpoint handlers in `api/src/http_endpoint_common.rs` plus other handler modules outside this subset. It is used by clients, docs, and compatibility checks.

## Risks and Edge Cases
Some schema details are loose: many metric payloads are generic objects or string/integer arrays, `MountCmd.prefetch_files` is documented as string while Rust uses `Option<Vec<String>>`, and many failures are represented as `500` even for bad input. Drift between this file and handler behavior is a compatibility risk.

## Test Signals
Tests should compare OpenAPI operations with registered HTTP routes and Rust request/response types. Existing endpoint unit tests cover some method/query behavior but do not validate the OpenAPI file directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/openapi/nydus-api-v1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/openapi/nydus-api-v2.yaml -->
# sources/cloud-native/nydus/api/openapi/nydus-api-v2.yaml

## Purpose
This OpenAPI document sketches v2 service and management APIs under `https://localhost/v2`, focusing on daemon info/config and blob cache management.

## Important APIs, Types, and Functions
Endpoints include `/daemon` GET/PUT and `/blobs` GET/PUT/DELETE. Schemas present in the file include `DaemonInfo`, `DaemonConf`, and `ErrorMsg`; the paths reference additional schemas such as `BlobObjectList`, `BlobObjectConf`, `BlobObjectParam`, and `BlobId`.

## Control Flow
Clients can query/configure daemon state and manage blob cache objects through list/create/delete actions. Success is represented by JSON for reads and `204` for mutations.

## State and Persistence
The v2 API controls daemon runtime configuration and blob cache object state. The underlying blob cache may persist cached files/configs, but this file only defines the HTTP contract.

## Dependencies and Integration Points
The document aligns conceptually with `ApiRequest` v2 variants in `api/src/http.rs`: `GetDaemonInfoV2`, `CreateBlobObject`, `GetBlobObject`, `DeleteBlobObject`, and `DeleteBlobFile`.

## Risks and Edge Cases
The `/blobs` `delete` block appears malformed: it contains two `operationId`, `requestBody`, and `responses` mappings under the same HTTP method, so YAML parsing keeps only one set or OpenAPI validation fails depending on tooling. Referenced blob schemas are not defined in `components.schemas` in the visible file. The server URL uses HTTPS while v1 uses HTTP; implementation compatibility should be checked.

## Test Signals
OpenAPI validation should be run after changes. Tests should assert route registration and schema presence for all referenced v2 blob operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/openapi/nydus-api-v2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/config.rs -->
# sources/cloud-native/nydus/api/src/config.rs

## Purpose
This module defines Nydus daemon, backend, cache, RAFS, prefetch, proxy, overlay, and blob-cache configuration models. It parses current v2 JSON/TOML config, accepts selected legacy JSON formats, validates combinations, converts legacy structures into v2, and provides helpers for secret scrubbing and runtime flags.

## Important APIs, Types, and Functions
- `ConfigV2` is the top-level v2 config with `version`, `id`, optional `backend`, `external_backends`, optional `cache`, optional `rafs`, optional `overlay`, and skipped runtime `internal`.
- `ConfigV2::new`, `new_localfs`, `from_file`, `validate`, accessors, `clone_without_secrets`, `is_chunk_validation_enabled`, `is_fs_cache`, and `update_registry_auth_info` are the main user APIs.
- `BackendConfigV2` supports `localdisk`, `localfs`, `oss`, `s3`, `registry`, and `http-proxy` backend types and exposes typed getters.
- `CacheConfigV2` supports `blobcache`/`filecache`, `fscache`, `dummycache`, prefetch settings, and typed cache getters.
- `FileCacheConfig::get_work_dir` and `FsCacheConfig::get_work_dir` create missing cache dirs and reject non-directories.
- `RafsConfigV2`, `PrefetchConfigV2`, and `ProxyConfig` carry filesystem mode, validation, IO batching, metrics flags, prefetch concurrency/bandwidth, and Dragonfly/proxy health settings.
- `BlobCacheEntryConfigV2`, `BlobCacheEntry`, and `BlobCacheList` model cached bootstrap/datablob objects, domain isolation, legacy config compatibility, and metadata paths.
- Legacy-only structs `BackendConfig`, `CacheConfig`, `FactoryConfig`, `RafsConfig`, `FsPrefetchControl`, `BlobPrefetchConfig`, and `BlobCacheEntryConfig` provide conversion routes.

## Control Flow
Parsing first tries `serde_json::from_str::<ConfigV2>`, then TOML `ConfigV2`, then legacy JSON `RafsConfig` converted to `ConfigV2`. Blob cache entry config parsing separately tries JSON then TOML. Validation checks version, backend type and required fields, cache type and work dirs, RAFS mode and batch/thread limits, and blob type. Legacy conversion maps generic `Value` payloads into typed backend/cache structs based on `type` strings. Runtime callers fetch typed subconfigs using getters that distinguish wrong type from missing subconfig.

## State and Persistence
`from_file` reads config files up to 1 MiB. Cache `get_work_dir` helpers may create directories on disk, which is the module's main side effect. `ConfigV2Internal` stores a shared atomic `blob_accessible` runtime probe flag that is skipped during serialization and compared by loaded value. Secret scrubbing clones configs and removes OSS access keys and registry auth/token fields.

## Dependencies and Integration Points
The module depends on serde, serde_json, toml, `std::fs`, `std::io`, `log`, and atomics. It feeds Nydus daemon startup, backend construction, blob cache management APIs, snapshotter-generated configs, Dragonfly proxy settings, and tests in this crate.

## Risks and Edge Cases
- `clone_without_secrets` clears OSS and registry secrets only on the primary backend; S3 access keys and `external_backends` may still carry sensitive values.
- `FileCacheConfig::get_work_dir` and `FsCacheConfig::get_work_dir` mutate the filesystem while looking like accessors.
- Validation accepts empty/no-op cache type and optional backend/cache/rafs sections; callers must enforce their own required sections.
- HTTP proxy validation requires an absolute existing Unix socket path when using a socket, so configs can fail validation before the socket is created.
- Multiple legacy and v2 representations increase drift risk.
- The 1 MiB file limit protects against oversized configs but can reject large generated configs.

## Test Signals
The module has extensive unit tests covering default values, backend/cache/RAFS TOML parsing, OSS/S3/registry/localfs/localdisk/proxy configs, legacy conversion, v2 blob cache parsing, from-file behavior, validation failures, getter error kinds, secret scrubbing, chunk validation logic, fscache detection, and prefetch defaults. CI runs these through workspace unit tests, nextest, Miri, smoke, and coverage workflows.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/error.rs -->
# sources/cloud-native/nydus/api/src/error.rs

## Purpose
This module provides standardized `std::io::Error` construction macros for the Nydus API crate, with optional feature-gated backtrace/error-location logging.

## Important APIs, Types, and Functions
- `make_error(err, raw, file, line)` logs debug context and optional backtrace when `error-backtrace` is enabled and `RUST_BACKTRACE` is not `0`, then returns the original error.
- `define_error_macro!` and `define_libc_error_macro!` generate exported macros.
- Exported macros include `einval!`, `enoent!`, `ebadf!`, `eacces!`, `enotdir!`, `eisdir!`, `ealready!`, `enosys!`, `epipe!`, `eio!`, `last_error!`, and `eother!`.
- `bail_einval!` and `bail_eio!` return early with formatted errors.

## Control Flow
Callers invoke a macro with no argument for a basic error or one argument for contextual logging through `make_error`. Bail macros format a message and immediately return `Err(...)`. With `error-backtrace`, logging behavior depends on `RUST_BACKTRACE`.

## State and Persistence
There is no persistent state. Side effects are log messages when the feature is enabled. The macros embed `file!()` and `line!()` call-site metadata.

## Dependencies and Integration Points
The module depends on `libc` error constants, `std::io`, optional `backtrace`, and logging macros. It is exported at crate level and used by API and service code that wants errno-compatible errors.

## Risks and Edge Cases
The macro TODO notes no full format-string support for base error macros; only the bail macros format. `eother!()` creates an `Other` error with empty message. With `error-backtrace`, context is logged but the returned error is still the original value, so callers do not see enriched messages unless using the zero-argument generated form.

## Test Signals
Unit tests cover errno macro kinds, context variants, custom macros, `make_error`, bail macro early returns, formatted bail messages, and success paths. Feature-enabled backtrace logging needs separate feature-specific CI to observe log behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http.rs -->
# sources/cloud-native/nydus/api/src/http.rs

## Purpose
This module defines the typed request, response, command, and error vocabulary shared between Nydus HTTP handlers and backend API services.

## Important APIs, Types, and Functions
- Command structs: `ApiMountCmd`, `ApiUmountCmd`, `DaemonConf`, `BlobCacheObjectId`, and `Config` alias.
- `ApiRequest` enumerates daemon control, mount/remount/umount, metrics, v1 config/filesystem queries, and v2 blob object operations.
- Error types include `MetricsError`, `DaemonErrorKind`, `MetricsErrorKind`, `ApiError`, and `HttpError`.
- `ApiResponsePayload` enumerates string JSON payload categories, empty responses, config maps, and v2 blob object lists.
- `ApiResult<T>` and `ApiResponse` are result aliases.
- `ErrorMessage` serializes API error codes/messages and converts into a JSON byte vector.

## Control Flow
HTTP endpoint handlers parse requests into `ApiRequest` variants and send them through an API service channel or callback. Backend services return `ApiResponsePayload` or `ApiError`; HTTP handler code maps `ApiError` into `HttpError` variants and status codes. `ErrorMessage` is serialized when producing client-facing error bodies.

## State and Persistence
The module itself has no mutable state. It defines data that can cause daemon state changes when interpreted by the service: mount operations, daemon start/exit/config, blob object create/delete, and config updates.

## Dependencies and Integration Points
It depends on serde, thiserror, channel send/recv errors, serde_json errors, and `BlobCacheEntry` from the config module. It is the central integration contract between OpenAPI documents, `http_endpoint_common.rs`, other endpoint modules, and daemon/service implementations.

## Risks and Edge Cases
`HttpError` debug formatting is noted as implicitly part of the API, so renaming variants can be a breaking change. Many payloads are raw `String` rather than strongly typed schemas, making mismatches with OpenAPI easier. `ApiMountCmd.prefetch_files` is `Option<Vec<String>>`, while the v1 OpenAPI document describes a string. Boxed send errors reduce enum size but can complicate matching.

## Test Signals
No tests are in this file. It is indirectly tested through endpoint handler tests, service tests, OpenAPI compatibility, and smoke workflows that exercise HTTP API operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_endpoint_common.rs -->
# sources/cloud-native/nydus/api/src/http_endpoint_common.rs

## Purpose
This module implements common HTTP endpoint handlers for daemon start/exit/events, backend/blobcache metrics, mount/remount/umount, and FUSE fd upgrade handoff operations.

## Important APIs, Types, and Functions
- `convert_to_response()` maps an `ApiResponse` into a `dbs_uhttp::Response`, accepting only `Empty`, `Events`, `BackendMetrics`, and `BlobcacheMetrics` payloads and converting errors through a supplied `HttpError` constructor.
- `StartHandler`, `ExitHandler`, `EventsHandler`, `MetricsBackendHandler`, `MetricsBlobcacheHandler`, `MountHandler`, `SendFuseFdHandler`, and `TakeoverFuseFdHandler` implement `EndpointHandler`.
- Handlers use `extract_query_part`, `parse_body`, `success_response`, `error_response`, and `translate_status_code` from `http_handler`.

## Control Flow
Each handler pattern-matches request method and body presence. Valid requests create an `ApiRequest` and call `kicker`, a callback into the API service. The response is converted to HTTP success/error. Mount handling additionally requires `mountpoint` query parameter and dispatches POST to `Mount`, PUT to `Remount`, and DELETE to `Umount`. Metrics handlers optionally extract `id`.

## State and Persistence
Handlers are stateless structs. They can trigger daemon state changes through `ApiRequest` variants: start, exit, mount lifecycle, and FUSE fd transfer/takeover. They do not persist data directly.

## Dependencies and Integration Points
This module depends on `dbs-uhttp`, `crate::http`, and `crate::http_handler`. It implements server-side behavior corresponding to parts of the v1 OpenAPI contract and daemon upgrade lifecycle.

## Risks and Edge Cases
`convert_to_response()` panics on unexpected successful payload variants, so incorrect service-handler pairing can crash the API server. Request validation is strict about body absence/presence; clients sending harmless bodies on PUT start/exit or DELETE mount receive bad request. Mountpoint extraction is required even before method/body matching in `MountHandler`.

## Test Signals
The module has focused unit tests for valid and invalid methods across handlers, missing mountpoint, mount POST/PUT/DELETE with bodies, metrics responses, and FUSE fd handlers. These validate request dispatch but not full status-code/error-body serialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/api/src/http_endpoint_common.rs -->
