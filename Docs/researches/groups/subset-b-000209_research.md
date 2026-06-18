# subset-b-000209 Research

Grouped research report for subset-b-000209. Each section preserves the source path in its title and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/pools/pools.go -->
# sources/cloud-native/moby/pkg/pools/pools.go

Purpose: shared allocation-reduction helpers for Moby packages. It exposes 32 KiB `BufioReader32KPool` and `BufioWriter32KPool`, an internal 32 KiB byte-slice pool, and `Copy` as an `io.CopyBuffer` convenience wrapper.

APIs and flow: `Get` resets a pooled bufio object onto the caller's reader/writer; `Put` resets it to nil before returning it. `NewReadCloserWrapper` and `NewWriteCloserWrapper` combine pooled object release with optional underlying close, with writer close flushing first.

State and dependencies: state is process-local `sync.Pool`; objects may disappear under GC. It depends on stdlib bufio/io/sync and Moby `ioutils` wrappers.

Risks and tests: callers must not use a reader/writer after `Put`/wrapper close. Flush errors are ignored during close. Tests cover pooling, reset behavior, wrappers, and buffer reuse.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/pools/pools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/pools/pools_test.go -->
# sources/cloud-native/moby/pkg/pools/pools_test.go

Purpose: unit coverage for pooled bufio readers/writers and the internal byte buffer pool.

APIs and flow: tests obtain objects from `BufioReader32KPool`/`BufioWriter32KPool`, read/write small buffers, return objects, and assert reset side effects. Custom `simpleReaderCloser` and `simpleWriterCloser` verify wrapper close propagation.

State and persistence: tests exercise in-memory pool state only; no persistent files beyond transient buffers.

Dependencies and integration: uses `gotest.tools/v3/assert` plus stdlib `bytes`, `bufio`, `io`, and `strings`.

Risks and signals: intentionally expects a panic when flushing a writer after it has been reset to nil, documenting the no-use-after-put contract. It does not assert `Copy` directly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/pools/pools_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/doc.go -->
# sources/cloud-native/moby/pkg/process/doc.go

Purpose: package documentation for `process`, describing it as basic helpers for managing individual processes.

APIs and flow: no executable API is declared here; exported behavior lives in platform-specific files and `process.go`.

State and dependencies: no state, persistence, or imports.

Integration points: this doc anchors package-level Go documentation for consumers using `go doc`.

Risks and tests: no direct tests required; behavior is covered through `process_test.go` and platform implementations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process.go -->
# sources/cloud-native/moby/pkg/process/process.go

Purpose: platform-neutral validation layer for process liveness and force-kill helpers.

APIs and flow: `Alive(pid int)` rejects pid values below 1 to avoid process-group semantics, then dispatches to platform `alive`. `Kill(pid int)` applies the same positive-PID guard and dispatches to platform `kill`.

State and dependencies: no persistent state; only formats validation errors with stdlib `fmt`.

Integration points: platform files provide Unix, Windows, Linux-zombie, and non-Linux zombie behavior.

Risks and tests: the PID guard is important because `kill(0)`, `kill(-1)`, and negative process-group IDs can affect many processes. Tests cover invalid PID liveness and current/exited process checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_linux.go -->
# sources/cloud-native/moby/pkg/process/process_linux.go

Purpose: Linux-only zombie process detection.

APIs and flow: `zombie(pid)` rejects non-positive PIDs, reads `/proc/<pid>/stat`, splits the first fields, and returns true when the third column is `Z`. Missing proc entries are treated as non-zombie rather than errors.

State and dependencies: reads procfs on demand; no cached or persisted state. Uses `os.ReadFile`, `fmt`, and `bytes.SplitN`.

Integration points: exported Unix `Zombie` delegates here on Linux.

Risks and tests: procfs format parsing is intentionally minimal. Transient process exit can return false. No direct zombie fixture test exists in the listed file set.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_nolinux.go -->
# sources/cloud-native/moby/pkg/process/process_nolinux.go

Purpose: non-Linux stub for zombie detection.

APIs and flow: build-tagged `!linux` implementation of `zombie(pid)` always returns `(false, nil)`.

State and dependencies: no imports, no filesystem reads, no persistence.

Integration points: keeps the common `Zombie` API buildable on Unix platforms where `/proc/<pid>/stat` state parsing is not implemented.

Risks and tests: callers must not assume `Zombie` gives meaningful zombie detection outside Linux. Existing tests focus on `Alive`, not this stub.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_test.go -->
# sources/cloud-native/moby/pkg/process/process_test.go

Purpose: tests for process liveness behavior.

APIs and flow: `TestAlive` checks invalid PIDs, the current process PID, and a completed child process. The exited-process case is skipped on Windows.

State and dependencies: spawns a short-lived `echo` command and observes its `ProcessState.Pid`; no persistent state.

Integration points: exercises the platform `alive` implementation through the public `Alive` wrapper.

Risks and signals: the invalid-PID cases document the process-group safety boundary. There is no explicit `Kill` or `Zombie` coverage in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_unix.go -->
# sources/cloud-native/moby/pkg/process/process_unix.go

Purpose: Unix implementation for process liveness, killing, and exported zombie checks.

APIs and flow: `alive` uses `unix.Kill(pid, 0)` on Darwin and treats `EPERM` as alive; other Unix systems check for `/proc/<pid>`. `kill` sends `SIGKILL` and ignores `ESRCH`. `Zombie` delegates to the platform `zombie` helper.

State and dependencies: relies on procfs or kernel signal APIs, with no durable state.

Integration points: shared by all non-Windows builds; Linux gets zombie parsing from `process_linux.go`.

Risks and tests: procfs presence assumptions affect non-Darwin Unix ports. `Kill` swallowing `ESRCH` makes it idempotent for already-gone processes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_windows.go -->
# sources/cloud-native/moby/pkg/process/process_windows.go

Purpose: Windows implementation of process liveness and kill.

APIs and flow: `alive` opens the process with limited query rights, calls `GetExitCodeProcess`, closes the handle, and interprets successful query as alive. On query error it compares exit code with `STATUS_PENDING`. `kill` uses `os.FindProcess` and ignores `os.ErrProcessDone`.

State and dependencies: kernel process handles are opened and closed per call; no persistence.

Integration points: satisfies the common `Alive`/`Kill` dispatch contract on Windows.

Risks and tests: test coverage skips the exited-process case on Windows. The `GetExitCodeProcess` error branch is subtle and tied to Win32 API semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/process/process_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/cgroup2_linux.go -->
# sources/cloud-native/moby/pkg/sysinfo/cgroup2_linux.go

Purpose: collect Linux cgroup v2 capability information for Docker/Moby system feature reporting.

APIs and flow: `newV2` initializes `SysInfo` as unified mode, loads the configured cgroup path through containerd cgroups v2, records controllers, and runs generic plus cgroup-v2 collectors. Per-controller functions set memory, CPU, IO, cpuset, pids, and devices booleans.

State and dependencies: reads `/proc/self/cgroup`, `/sys/fs/cgroup/...`, and cgroup controller metadata. Depends on containerd cgroups/log and Moby user namespace detection.

Integration points: Linux `New` dispatches here when `cgroups.Mode()` is unified. `WithCgroup2GroupPath` can target rootless/systemd group paths.

Risks and tests: missing controllers become warnings. `applyCPUSetCgroupInfoV2` parses `info.Cpus` for mem sets after reading mems, likely mirroring CPU availability instead of `info.Mems`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/cgroup2_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo.go -->
# sources/cloud-native/moby/pkg/sysinfo/sysinfo.go

Purpose: define the public `SysInfo` model for kernel/container runtime capability reporting.

APIs and types: `Opt` customizes `New`. `SysInfo` embeds memory, CPU, blkio, cpuset, and pids cgroup capability structs plus AppArmor, Seccomp, namespace, networking, device, unified mode, warnings, and internal cgroup mount/controller state. Cpuset helpers expose availability checks.

State and persistence: struct instances are snapshots of host state; internal maps hold parsed cgroup paths/controllers.

Dependencies and integration: platform-specific files populate this model. Consumers can inspect booleans and warnings but should not parse warning text.

Risks and tests: cpuset availability depends on parsed maps being populated; non-Linux returns mostly empty state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux.go -->
# sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux.go

Purpose: Linux cgroup v1 and generic kernel feature detection.

APIs and flow: `New` dispatches to v2 or `newV1`. v1 mount discovery caches cgroup mountinfo once, parses `/proc/self/cgroup`, maps subsystem mountpoints, then applies collectors for memory, CPU, blkio, cpuset, pids, devices, networking, AppArmor, seccomp, cgroup namespaces, and time namespaces. `parseUintList` and `isCpusetListAvailable` validate cpuset requests with a maximum bound.

State and dependencies: reads procfs, sysfs, cgroup files, and mountinfo; mountinfo is cached in package globals.

Integration points: used by Docker daemon validation/reporting paths. Depends on containerd seccomp/cgroups and Moby mountinfo.

Risks and tests: cached mountinfo assumes mounts do not change. Both v1 cpuset collection and v2 counterpart parse `info.Cpus` when building `MemSets`, which looks like a bug. Tests cover parse bounds, proc bools, cgroup file detection, and generic feature flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux_test.go -->
# sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux_test.go

Purpose: Linux unit coverage for sysinfo helper parsing and feature probes.

APIs and flow: tests verify `readProcBool`, `cgroupEnabled`, `New` generic fields, cpuset subset validation, valid/invalid `parseUintList` forms, and max-limit enforcement.

State and dependencies: uses temporary files/directories for proc/cgroup helper tests and live host state for seccomp/AppArmor/namespace expectations.

Integration points: asserts `New` aligns with the same helper functions used internally rather than fixed host expectations.

Risks and signals: live-host tests may vary by environment but compare against local helper outputs. There is no direct test for cpuset mem parsing, leaving the `MemSets` source-string issue exposed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo_other.go -->
# sources/cloud-native/moby/pkg/sysinfo/sysinfo_other.go

Purpose: non-Linux fallback for sysinfo.

APIs and flow: `New` ignores options and returns an empty `SysInfo`; `isCpusetListAvailable` always returns false with no error.

State and dependencies: no imports, filesystem access, or persistence.

Integration points: keeps packages compiling on non-Linux platforms while making Linux-specific capability detection unavailable.

Risks and tests: consumers must treat empty fields as unsupported/unknown on non-Linux. Linux-specific tests do not run for this build-tagged file.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/sysinfo/sysinfo_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/tailfile/fuzz_test.go -->
# sources/cloud-native/moby/pkg/tailfile/fuzz_test.go

Purpose: fuzz harness for the tailfile reader.

APIs and flow: consumes fuzz bytes into a requested line count and file contents, writes those bytes to a temp file, seeks to the beginning, and calls `TailFile` with the generated count.

State and dependencies: creates temporary files per fuzz case; depends on AdaLogics go-fuzz-headers for structured byte consumption.

Integration points: targets panic/error-safety around reverse scanning and arbitrary input sizes/content.

Risks and signals: the harness discards most setup errors and does not assert semantic output, so its value is crash discovery rather than correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/tailfile/fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/tailfile/tailfile.go -->
# sources/cloud-native/moby/pkg/tailfile/tailfile.go

Purpose: efficient reverse tailing for files or `SizeReaderAt` readers.

APIs and flow: `TailFile` builds a section reader over the file and scans returned tail content into byte slices. `NewTailReaderWithDelimiter` validates line count/delimiter, scans backward in 1 KiB blocks for delimiters, and returns a scoped `io.SectionReader` plus found line count. The internal scanner handles multi-byte delimiter overlap by rereading a small prefix.

State and dependencies: stateless aside from scanner position/buffer; uses `context` cancellation and `ReaderAt` reads.

Integration points: supports custom delimiters for logs beyond newline. `SizeReaderAt` matches `strings.Reader` and section readers.

Risks and tests: scanner returns borrowed scanner bytes in `TailFile`; callers should consume before next scan. Very long tokens are subject to bufio.Scanner limits. Tests cover empty files, truncated lines, delimiters, and block boundaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/tailfile/tailfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/tailfile/tailfile_test.go -->
# sources/cloud-native/moby/pkg/tailfile/tailfile_test.go

Purpose: broad correctness and benchmark coverage for reverse tailing.

APIs and flow: file-level tests cover last-N lines, requesting more lines than present, empty file, and invalid counts. `TestNewTailReader` runs parallel table tests over newline and multi-byte delimiters, varied line sizes, JSON-like log lines, empty data, and truncated final lines.

State and dependencies: uses temp files and in-memory `strings.Reader` values; no persistent state.

Integration points: confirms `TailFile` and `NewTailReaderWithDelimiter` agree with normal forward reads.

Risks and signals: validates page/block crossing behavior and page-size-like large lower inputs. Benchmark measures 10k-line tail performance.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/tailfile/tailfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/useragent/useragent.go -->
# sources/cloud-native/moby/pkg/useragent/useragent.go

Purpose: compose product/version tokens into a User-Agent string.

APIs and flow: `VersionInfo` holds name/version. `isValid` rejects empty fields and whitespace, newline, carriage-return, tab, or slash. `AppendVersions` preserves a non-empty base and appends valid `name/version` tokens separated by spaces.

State and dependencies: pure string processing using stdlib `strings`; no persistence.

Integration points: useful for HTTP clients that need additive component version metadata.

Risks and tests: invalid entries are silently skipped, so missing user-agent fragments may hide bad input. Tests cover empty fields and nominal append behavior, but not stop-character rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/useragent/useragent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/useragent/useragent_test.go -->
# sources/cloud-native/moby/pkg/useragent/useragent_test.go

Purpose: unit tests for user-agent version validation and formatting.

APIs and flow: `TestVersionInfo` checks valid name/version and empty field rejection. `TestAppendVersions` verifies base plus three version tokens format as space-separated `product/version` entries.

State and dependencies: pure in-memory tests with stdlib testing only.

Integration points: protects the public formatting contract used by HTTP callers.

Risks and signals: tests do not cover whitespace or slash stop characters, empty base behavior, or skipped invalid entries in `AppendVersions`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/useragent/useragent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/releases/versions.yaml -->
# sources/cloud-native/moby/releases/versions.yaml

Purpose: release metadata declaring Docker version channels for Moby release automation.

APIs and structure: YAML root `docker` contains `last` set to `29.5.3` and `next` set to `29.6.0`.

State and persistence: this is durable repository release state, not runtime code.

Integration points: likely consumed by release scripts or CI jobs that need current and upcoming Docker version numbers.

Risks and tests: stale values can misdrive release automation. No tests are attached in the listed file set; validation is schema/consumer dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/releases/versions.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/bug-report.yml -->
# sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/bug-report.yml

Purpose: GitHub issue form for bug reports.

Structure and flow: prelabels issues as `bug`, sets a `[Bug]` title prefix, and requires problem, expected behavior, actual behavior, reproduction steps, and environment details. Optional fields capture additional context and PR willingness.

State and dependencies: GitHub issue-form YAML only; no runtime persistence beyond submitted issue content.

Integration points: guides maintainers toward actionable reproduction and environment data for snapshotter/nydus/container runtime bugs.

Risks and tests: no automated validation in the repo; indentation and GitHub form schema correctness are the main risks. Environment field is free text, so triage still depends on reporter quality.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/bug-report.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/feature-request.yml -->
# sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/feature-request.yml

Purpose: GitHub issue form for feature requests.

Structure and flow: applies `feature` label and `[Feature]` title prefix. Requires feature description and problem/use-case; related issues and PR willingness are optional.

State and dependencies: GitHub issue metadata/template only.

Integration points: feeds product and maintainer planning with use-case-oriented requests.

Risks and tests: no repo-local schema test. The form is intentionally light, so it may omit compatibility, performance, or operational constraints needed for low-level snapshotter features.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/feature-request.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/improvement-report.yml -->
# sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/improvement-report.yml

Purpose: GitHub issue form for improvements to existing features or processes.

Structure and flow: labels issues as `improvement`, requires a problem summary and proposed improvement, and optionally captures context plus PR willingness.

State and dependencies: persistent only as GitHub issue content after submission.

Integration points: separates incremental improvement requests from bugs and net-new features.

Risks and tests: schema is not tested locally. The template has no required environment/version fields, which may limit actionable operational improvement reports.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/ISSUE_TEMPLATE/improvement-report.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/codecov.yml -->
# sources/cloud-native/nydus-snapshotter/.github/codecov.yml

Purpose: Codecov status and comment policy.

Structure and flow: disables patch status, enables project status with auto target and 0.3 percent threshold, posts comments only when coverage changes, and waits for CI without requiring CI to pass before notification.

State and dependencies: external Codecov service configuration; no runtime state in the project.

Integration points: paired with the CI coverage job uploading `coverage.txt`.

Risks and tests: comments indicate validation should be done with Codecov's validate endpoint. A loose patch policy avoids blocking small changes but can miss localized coverage regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/ci.yml -->
# sources/cloud-native/nydus-snapshotter/.github/workflows/ci.yml

Purpose: primary CI for security, build/lint/test, optimizer build, smoke, cross-build, and coverage.

Flow: runs on push and PR across all/stable branches. Jobs install Go from `go.mod`, run `govulncheck` and OSV scanner, run golangci-lint via Go install, execute `make` and `make test`, build optimizer with Rust components, run smoke tests after downloading Nydus, cross-build converter for linux/windows/darwin amd64/arm64, and upload coverage.

State/dependencies: depends on GitHub Actions, Go, Rust, containerd, Nydus release assets, Codecov token.

Integration points: exercises Makefile targets and release-critical build paths.

Risks/tests: latest Nydus release download and external scanners can introduce nondeterminism. Build job calls race tests via `make test`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/e2e.yml -->
# sources/cloud-native/nydus-snapshotter/.github/workflows/e2e.yml

Purpose: integration tests for cgroup v1 and v2 environments.

Flow: triggers on main pushes, version tags, PRs to main, daily schedule, and manual dispatch. It runs `make integration` on Ubuntu 22.04 for cgroups v1 and Ubuntu 24.04 for cgroups v2 after registry login.

State/dependencies: relies on Docker, GitHub container registry credentials, Go setup, and integration Dockerfile/entrypoint behavior.

Integration points: validates real containerd/nydus-snapshotter/nydusd behavior across kernel cgroup modes.

Risks/tests: privileged container execution and external image availability are required. `TAG` is computed but not directly consumed by the shown commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/e2e.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e-run.yml -->
# sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e-run.yml

Purpose: orchestrates Kubernetes E2E scenarios through a reusable workflow.

Flow: on main pushes, semver tags, and PRs to main, it invokes `.github/workflows/k8s-e2e.yml` three times: CRI auth, kubeconfig auth, and kubeconfig with index detection.

State/dependencies: no direct commands; delegates all state to called workflow jobs.

Integration points: keeps scenario matrix small while reusing the Kubernetes test template.

Risks/tests: failures are surfaced from the reusable workflow. Any new auth mode must be added here to enter the k8s E2E matrix.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e-run.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e.yml -->
# sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e.yml

Purpose: reusable Kubernetes E2E workflow template.

Flow: accepts `auth-type` and optional `index-detect`, checks out submodules, sets up Go, runs `./tests/helpers/kind.sh`, and on failure gathers pod YAML/descriptions/logs, secrets, containerd configs, journal logs, process lists, test-pod YAML, and Docker auth config into an uploaded artifact.

State/dependencies: requires kind, kubectl/docker behavior from helper scripts, and a `nydus-system` namespace.

Integration points: called by `k8s-e2e-run.yml` for auth and index detection coverage.

Risks/tests: failure log dump includes secrets YAML and Docker config, which is useful for debugging but sensitive in artifact retention contexts.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/k8s-e2e.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/optimizer.yml -->
# sources/cloud-native/nydus-snapshotter/.github/workflows/optimizer.yml

Purpose: end-to-end optimizer NRI plugin test.

Flow: provisions crictl, containerd, runc, CNI, builds optimizer plugin/server, installs NRI config, restarts containerd, runs an nginx pod whose entrypoint reads a file list, then verifies the optimizer output file has at least the expected number of lines.

State/dependencies: writes under `/opt/nri/optimizer/results`, installs system files, uses Rust cache and external release downloads.

Integration points: validates `cmd/optimizer-nri-plugin`, optimizer server, NRI, crictl examples, and `misc/optimizer` manifests.

Risks/tests: heavily depends on host service mutation and downloaded versions. Failure dump captures containerd journal for diagnosis.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/optimizer.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/release.yml -->
# sources/cloud-native/nydus-snapshotter/.github/workflows/release.yml

Purpose: tag-driven release packaging, GitHub release upload, multi-arch image build, and manifest publish.

Flow: builds tarballs for linux amd64/arm64/s390x/ppc64le/riscv64 and static, uploads artifacts, creates a GitHub release, downloads per-arch artifacts into `misc/snapshotter`, builds images with the latest Nydus version, pushes arch tags, then publishes a multi-arch Docker manifest.

State/dependencies: GitHub packages, actions cache/artifacts, cross GCC packages, Docker Buildx/QEMU, Nydus latest release API.

Integration points: ties Makefile packaging to Dockerfile deployment image.

Risks/tests: uses golangci-lint v1.51.2 in release while CI uses v2.1.6. Latest Nydus lookup makes image contents time-dependent.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.golangci.yml -->
# sources/cloud-native/nydus-snapshotter/.golangci.yml

Purpose: Go lint and formatting policy for golangci-lint v2.

Structure: enables staticcheck, govet, errcheck, revive, depguard, gocritic, exhaustive, prealloc, nilnil, unparam, and related linters. Excludes `misc` and vendored/ported remote packages. Formatters include gofmt and goimports.

State/dependencies: no runtime state; consumed by CI and developer lint runs.

Integration points: depguard blocks old containerd package imports and directs replacements.

Risks/tests: excluding `misc` means deployment scripts/config examples are not linted here. Errcheck excludes common cleanup calls, trading signal for less noise.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/Makefile -->
# sources/cloud-native/nydus-snapshotter/Makefile

Purpose: build, package, install, test, and integration entry point.

Targets and flow: `build` compiles `containerd-nydus-grpc` and `nydus-overlayfs`; `static`/`static-release` build static binaries; `build-optimizer` builds the NRI plugin and Rust optimizer server; package targets tar binaries and checksums; install targets place binaries/config/systemd units; test targets run vet, golangci-lint, race unit tests, coverage, smoke, and privileged integration Docker runs.

State/dependencies: writes `bin`, `package`, `_out`, system paths under sudo, and uses Go/Rust/Docker/Nydus/containerd.

Integration points: consumed by CI, release, integration, and local installs.

Risks/tests: several targets mutate host `/etc`, `/usr/local/bin`, systemd, and Docker. Version metadata comes from git state and can include `.m` dirty suffix.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/main.go -->
# sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/main.go

Purpose: main executable for the remote containerd Nydus snapshotter.

Flow: builds CLI flags, optionally prints version, fills default config, loads TOML if `--config` is set, applies CLI overrides, merges defaults, validates, prepares logging, processes global config, sets up root environment, logs startup metadata, and calls `Start`.

State/dependencies: reads config and filesystem paths, creates log directories/root, sets global logrus/containerd logging. Depends on urfave/cli, config, internal flags/logging, version, errdefs.

Integration points: systemd units, Makefile, CI, and deployment scripts invoke this binary.

Risks/tests: fatal logging exits on startup errors. CLI compatibility means command line overrides TOML, which can surprise config-only deployments.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/snapshotter.go -->
# sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/snapshotter.go

Purpose: initialize and serve the snapshotter gRPC service.

Flow: `Start` creates a cancellable context, constructs `snapshot.NewSnapshotter`, installs signal handling, initializes optional kube secret and kubelet credential providers, then calls `Serve`. `Serve` removes stale socket files only if they are sockets, registers the containerd snapshots service, listens on Unix socket, chowns it, optionally adds CRI image proxy auth, and closes snapshotter/listener on stop.

State/dependencies: owns the Unix socket path and snapshotter lifecycle; no durable data beyond socket. Depends on containerd gRPC snapshotservice, auth, signals, snapshot.

Risks/tests: refuses to overwrite non-socket files at the socket path. Listener close is expected to break `rpc.Serve` on shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/containerd-nydus-grpc/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/converter/main.go -->
# sources/cloud-native/nydus-snapshotter/cmd/converter/main.go

Purpose: build-only executable for converter package compatibility.

Flow/APIs: imports `pkg/converter` for side effects/compile validation and has an empty `main`.

State/dependencies: no runtime state; depends on converter package compiling for the target platform.

Integration points: Makefile `converter` and CI cross-build matrix use this to ensure converter code builds on linux/windows/darwin for amd64/arm64.

Risks/tests: no behavior is executed, so this catches compile-time portability but not converter runtime correctness.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/converter/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main.go -->
# sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main.go

Purpose: mount helper that filters Nydus/Kata-specific overlay options before invoking kernel overlayfs.

Flow: CLI expects `overlay <target> -o <options>`. `parseArgs` validates fs type/target and strips `extraoption=` and Kata volume options. `parseOptions` maps known mount option strings to flags and leaves overlay data options. If data nears page size, `compactLowerdirOption` computes a common directory, chdirs there, and rewrites lower/upper/work dirs relative before `syscall.Mount`.

State/dependencies: changes current working directory before mount when compacting; uses Unix mount flags.

Integration points: enabled by snapshotter config for containerd mount helper flow.

Risks/tests: mount option flag table maps some positive options to negating flags (`rw` to `MS_RDONLY`, etc.), matching legacy patterns but risky. Tests cover parsing and compaction, not actual mount syscall.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main_test.go -->
# sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main_test.go

Purpose: unit tests for overlayfs helper parsing and path compaction.

Flow: tests longest common prefix cases, lowerdir compaction with two and many layers, disjoint path fallback, real-world size savings under 4096 bytes, and option filtering for Nydus/Kata metadata.

State/dependencies: pure in-memory tests using testify; no mounts are performed.

Integration points: protects the helper logic used when containerd mount data exceeds kernel page-size limits.

Risks/signals: verifies compaction savings but not `run` chdir or syscall behavior. Invalid argument coverage is limited to fs type in the shown cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/nydus-overlayfs/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/optimizer-nri-plugin/main.go -->
# sources/cloud-native/nydus-snapshotter/cmd/optimizer-nri-plugin/main.go

Purpose: NRI plugin that starts/stops fanotify-based optimizer collection per container.

Flow: CLI sets plugin name/index/events and optimizer config. `Configure` optionally parses TOML runtime config and event mask. `StartContainer` derives repo/image tag from CRI image annotation, creates a persist dir, constructs a fanotify server for the container PID, starts it, and stores it by image name. `StopContainer` stops the matching server. `onClose` stops all servers.

State/dependencies: global config, syslog writer, and `globalFanotifyServer` map; persists accessed-file lists under configured directory.

Integration points: tested by optimizer workflow and `misc/example/optimizer-nri-plugin.conf`.

Risks/tests: map key is image name, so concurrent containers from the same image can overwrite each other. Type assertion to `NamedTagged` can panic if annotation lacks tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/optimizer-nri-plugin/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/prefetchfiles-nri-plugin/main.go -->
# sources/cloud-native/nydus-snapshotter/cmd/prefetchfiles-nri-plugin/main.go

Purpose: NRI plugin that forwards pod prefetch annotations to the Nydus system controller.

Flow: reads optional `/etc/nydus/prefetchConfig.toml`, selects Unix socket path from config or CLI, registers for `RunPodSandbox`, and when annotation `containerd.io/nydus-prefetch` exists sends it via HTTP PUT to `/api/v1/prefetch` over the Unix socket.

State/dependencies: global socket string and syslog writer; uses containerd NRI stub, go-toml, and custom HTTP transport.

Integration points: pairs with system controller socket and `misc/nri-prefetch/prefetchConfig.toml`.

Risks/tests: if config file load fails, `config.Get` is still called on a possibly nil tree, which may panic depending on library behavior. Response body close ignores error and non-200 returns error.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/cmd/prefetchfiles-nri-plugin/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/config.go -->
# sources/cloud-native/nydus-snapshotter/config/config.go

Purpose: central TOML schema, default merging, validation, CLI override, and cgroup config parsing.

APIs/types: defines daemon modes, recover policies, fs drivers, failover policies, and nested `SnapshotterConfig` sections for daemon, logging, snapshot, remote auth/mirrors, cache, metrics, system controller, cgroup, image, and experimental tarfs/stargz/index detection.

Flow/state: `LoadSnapshotterConfig` requires version 1. `MergeConfig` uses mergo defaults. `ValidateConfig` checks signature keys, root length, fs driver, recover/failover policy, thread limit, auth exclusivity, and mirror dir. `ParseParameters` applies CLI overrides. `ParseCgroupConfig` converts memory settings using total memory.

Integration points: main binary, tests, global config, daemonconfig.

Risks/tests: zero-value merge behavior means explicit false/zero TOML values can be hard to distinguish. Tests cover loading, merge, log-to-stdout override, processing, and root length.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/config_test.go -->
# sources/cloud-native/nydus-snapshotter/config/config_test.go

Purpose: unit tests for snapshotter config loading, overrides, defaults, and processing.

Flow: loads `misc/snapshotter/config.toml` and compares a full expected struct, verifies CLI root/log-to-stdout precedence, checks mergo default merge behavior, verifies derived log/cache dirs, and asserts overly long root path validation fails.

State/dependencies: reads example config from repo and may look up default binaries through `FillUpWithDefaults`.

Integration points: protects the packaged config file contract and CLI/TOML precedence.

Risks/signals: full-struct equality is sensitive to config default changes. Validation tests are selective and do not cover invalid fs drivers, auth conflict, or mirror dir errors here.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig.go

Purpose: common daemon config interface, backend config model, config dumping, snapshot-specific supplementation, mirror selection, and secret filtering.

Flow: `NewDaemonConfig` loads fscache or fuse config by fs driver. `SupplementDaemonConfig` parses image reference, rewrites docker.io host, optionally converts VPC registry, selects mirror/CA certs, fills repo/host/snapshot params/auth, or only supplements workdir for non-registry backends. `DumpConfigFile` writes atomically and optionally filters secret fields.

State/dependencies: writes JSON config files via temp+rename; calls mirror health URLs; reads global config.

Integration points: used before launching/communicating with nydusd.

Risks/tests: mirror ping logging uses `err` instead of `pingErr` in warning paths. Secret filter is reflection-based and may mishandle unexported/unexpected fields. Tests cover JSON parsing, amplify_io, and secret filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig_test.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig_test.go

Purpose: tests for FUSE daemon config JSON behavior and secret filtering.

Flow: unmarshals representative registry/backend/cache config, verifies embedded fs prefetch fields and backend fields, checks `amplify_io` pointer preserves non-zero and zero while omitting nil, and serializes a filtered config to ensure secret auth disappears while other fields survive.

State/dependencies: in-memory JSON only; uses testify require.

Integration points: protects nydusd config compatibility and backend-source safe serialization.

Risks/signals: tests do not exercise atomic file writes, mirror selection, auth fill, or supplementation paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/fscache.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/fscache.go

Purpose: fscache/EROFS nydusd configuration model and snapshot-specific supplementing.

Flow: `LoadFscacheConfig` reads JSON template and requires non-nil `Config`. `Supplement` fills registry host/repo, computes fscache ID from snapshot ID, sets `ID`, `DomainID`, nested config ID, optional workdir, and metadata bootstrap path. `FillAuth` stores registry token or base64 auth. Dump methods serialize/write JSON.

State/dependencies: reads/writes config files and logs shared-domain warning. Depends on auth and erofs helpers.

Integration points: used when fs driver is `fscache`; config is passed through nydusd APIs rather than always persisted.

Risks/tests: shared `DomainID` behavior depends on kernel >=6.1. No direct tests listed for fscache load/supplement.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/fscache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/fuse.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/fuse.go

Purpose: FUSE/vhost-user nydusd configuration model.

Flow: `LoadFuseConfig` reads JSON and requires `Device`. `Supplement` fills backend host/repo, sets device ID to `/<snapshotID>` when present, and sets blobcache work dir from params. `FillAuth` sets registry token or base64 auth. `StorageBackend`, `DumpString`, and `DumpFile` implement the common interface.

State/dependencies: reads/writes JSON config files. Depends on auth and common dump helpers.

Integration points: default `fusedev` path used by packaged configs, systemd unit, and integration tests.

Risks/tests: `params[CacheDir]` is assigned without presence check, so missing params clear work_dir. Tests cover JSON shape and amplify_io but not supplement behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirror_select_test.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirror_select_test.go

Purpose: tests mirror URL splitting and live mirror selection fallback.

Flow: table tests validate schemes/hosts for http, https, no scheme, ports, and paths. Selection tests cover no config, empty dir, mirror without ping URL, successful ping, failed ping fallback to origin, and first-fail second-no-ping selection.

State/dependencies: creates temp `hosts.toml` directories and httptest servers.

Integration points: protects registry mirror choice used during daemon config supplementation.

Risks/signals: no CA cert assertions here; no timeout behavior test. Invalid URL expect-error cases are not populated in the table.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirror_select_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors.go

Purpose: parse containerd-style registry `hosts.toml` mirror configuration with Nydus health metadata.

Flow: resolves host-specific, port-escaped, or `_default` directories; parses ordered `[host]` TOML entries by source line; supports headers, CA cert strings/arrays, skip_verify/client fields in schema, and Nydus `health_check_interval`, `failure_limit`, `ping_url`; deduplicates CA certs across hosts.

State/dependencies: reads files under mirror config root; no writes. Depends on go-toml and net/http header types.

Integration points: called by `selectMirrorHost` before nydusd backend host rewrite.

Risks/tests: `server` top-level is parsed but not used as fallback host. Relative CA path handling is not normalized. Tests cover defaults, host precedence, headers, and CA dedupe.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors_test.go -->
# sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors_test.go

Purpose: tests mirror config loading, default fallback, host precedence, headers, and CA cert collection.

Flow: constructs temp certs.d directories and hosts.toml files. Verifies nil when root missing/empty, `_default` fallback, registry-specific override, header extraction, single/array CA parsing, CA dedupe, and nil CA when absent.

State/dependencies: temp filesystem only; uses testify assert/require.

Integration points: confirms compatibility with containerd registry config layout used by snapshotter mirror rewrites.

Risks/signals: does not test malformed header/CA types or port-escaped host directory lookup.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/daemonconfig/mirrors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/default.go -->
# sources/cloud-native/nydus-snapshotter/config/default.go

Purpose: populate default snapshotter configuration.

Flow: `FillUpWithDefaults` sets version, root, socket address, daemon mode, system controller address, logging level/rotation, daemon config path/recover policy/fs driver/log rotation/failover, cache GC period, metrics intervals, and then resolves nydusd/nydus-image paths. `SetupNydusBinaryPaths` uses `exec.LookPath`.

State/dependencies: reads PATH for binary discovery; no writes.

Integration points: called by main and embedded containerd plugin initialization before validation/merge.

Risks/tests: missing binaries are silently left empty for later config/launch handling. Defaults can override zero values during mergo merge, so explicit zero settings need care.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/global.go -->
# sources/cloud-native/nydus-snapshotter/config/global.go

Purpose: cache processed configuration for packages that avoid threading `SnapshotterConfig` through every call.

APIs/flow: getter functions expose daemon mode, fs driver, log settings, paths, mirrors, system controller, skip TLS, backend source, and tarfs export flags. `ProcessConfigurations` derives cache/snapshots/config/socket/mount paths, parses daemon mode, and forces fscache to shared daemon mode. `PrepareLogDir` and `SetUpEnvironment` set log dir and create/normalize root.

State/dependencies: global package variable holds origin pointer and derived paths; creates root directory.

Integration points: consumed broadly by snapshot, daemonconfig, logging, and system controller code.

Risks/tests: global mutable state complicates tests and concurrent reconfiguration. `SetUpEnvironment` normalizes root after some derived paths may already be computed unless call order is maintained.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/config/global.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/export/snapshotter/snapshotter.go -->
# sources/cloud-native/nydus-snapshotter/export/snapshotter/snapshotter.go

Purpose: register Nydus as an in-process containerd snapshot plugin.

Flow: `init` registers plugin type `SnapshotPlugin` with ID `nydus`, default platform metadata, config type `SnapshotterConfig`, default filling, and `snapshot.NewSnapshotter` initialization.

State/dependencies: modifies containerd plugin registry at package import time. Depends on containerd plugin APIs, platforms, config, and snapshot package.

Integration points: enables embedding Nydus snapshotter directly in containerd rather than only via remote proxy plugin.

Risks/tests: root property handling appears inverted: `if root == "" { cfg.Root = root }` sets empty root only when property is absent, likely not intended. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/export/snapshotter/snapshotter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/integration/Dockerfile -->
# sources/cloud-native/nydus-snapshotter/integration/Dockerfile

Purpose: privileged integration test image containing Go, containerd, runc, Nydus tools, nerdctl, configs, and test entrypoint.

Flow: starts from Go Debian image, installs system deps and delve, downloads containerd/runc/Nydus/nerdctl by ARG versions and mirror, copies containerd and snapshotter configs, marks repo as safe for git, and sets entrypoint to `make install && /entrypoint.sh`.

State/dependencies: downloads external release artifacts and installs binaries under `/usr/local/bin`; exposes `/var/lib` volume.

Integration points: driven by Makefile `integration` and GitHub E2E workflow.

Risks/tests: default `GO_VER=1.24.0-bookworm` may diverge from go.mod/CI setup. Network/download availability and privileged host kernel features determine test reliability.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/integration/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/integration/entrypoint.sh -->
# sources/cloud-native/nydus-snapshotter/integration/entrypoint.sh

Purpose: integration test harness for containerd-nydus-snapshotter behavior across daemon modes, images, recovery, cache cleanup, OCI/stargz/referrer paths, and fscache.

Flow: defines retry helpers, process cleanup, config mutation, containerd/snapshotter reboot, cache validation, and many scenario functions that pull/run/create/remove images, kill nydusd/snapshotter, restart services, and detect Go race reports. It runs containerd and `containerd-nydus-grpc` directly in the test container.

State/dependencies: mutates `/etc/nydus/config.toml`, `/var/lib/containerd`, `/run/containerd`, snapshotter root/cache, and process table. Uses nerdctl, ctr, killall, mount/umount, nydusd, containerd.

Integration points: central to `make integration`.

Risks/tests: highly destructive inside its container namespace and privileged mounts. Some CLI flags in older helper paths (`--config-path`, `--enable-stargz`) may drift from current flag definitions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/integration/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/constant/values.go -->
# sources/cloud-native/nydus-snapshotter/internal/constant/values.go

Purpose: shared constants for daemon modes, filesystem drivers, defaults, binary names, log rotation, metrics, and failover policies.

State/API: defines string constants consumed by config, flags, defaults, and Makefile-aligned deployment configs. Defaults include root `/var/lib/containerd/io.containerd.snapshotter.v1.nydus`, socket `/run/containerd-nydus/containerd-nydus-grpc.sock`, system socket, fusedev default driver, multiple default daemon mode, and 24h cache GC.

Integration points: provides single source for CLI default text and config defaults.

Risks/tests: constants encode operational paths and policy defaults; changes affect packaged systemd/Kubernetes examples. No direct tests, but config tests assert many values.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/constant/values.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/flags/flags.go -->
# sources/cloud-native/nydus-snapshotter/internal/flags/flags.go

Purpose: urfave/cli flag definitions for `containerd-nydus-grpc`.

APIs/flow: `Args` stores parsed values for root, address, snapshotter config, nydus binaries/config, overlayfs helper, daemon mode, fs driver, log level/stdout, and version printing. `buildFlags` wires CLI flags and alias `--config-path` for `--nydusd-config`; `NewFlags` returns flags plus backing args.

State/dependencies: parse state lives in `Args`; no filesystem access.

Integration points: main config parsing consumes these args with CLI-over-TOML precedence.

Risks/tests: default text is informational only, not a parsed value. Compatibility alias can be confused with snapshotter `--config`. Test verifies alias/root/log-level parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/flags/flags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/flags/flags_test.go -->
# sources/cloud-native/nydus-snapshotter/internal/flags/flags_test.go

Purpose: basic flag construction and parsing test.

Flow: applies all urfave/cli flags to a stdlib `flag.FlagSet`, parses `--config-path`, `--root`, and `--log-level`, and asserts values land in `Args`.

State/dependencies: pure in-memory flag parsing.

Integration points: protects backward-compatible `--config-path` alias for nydusd config.

Risks/signals: does not test bool count semantics for `--log-to-stdout`, version flag, address, daemon mode, fs driver, or snapshotter `--config`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/flags/flags_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/logging/setup.go -->
# sources/cloud-native/nydus-snapshotter/internal/logging/setup.go

Purpose: initialize process logging.

Flow: `SetUp` parses log level, configures logrus output to stdout or a lumberjack rotating file, creates log directory for file mode, and installs a timestamped text formatter compatible with containerd log timestamp format. `WithContext` returns a context using the global containerd logger.

State/dependencies: mutates global logrus logger and writes rotating logs under configured directory.

Integration points: called by main before processing/starting snapshotter; tests exercise rotation.

Risks/tests: file mode requires non-nil rotation args. Global logger mutation affects package-wide tests. Rotation test writes many log lines and asserts backup count.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/logging/setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/logging/setup_test.go -->
# sources/cloud-native/nydus-snapshotter/internal/logging/setup_test.go

Purpose: tests logging setup and rotation behavior.

Flow: removes test log dir, configures stdout mode with nil rotation args, asserts file mode rejects nil rotation args, configures file mode with 1 MB max size and 5 backups, writes 100k log lines, then counts `.log.gz` backups.

State/dependencies: creates/removes local `test-rotate-logs`; mutates global logrus output.

Integration points: verifies the runtime logging setup used by `containerd-nydus-grpc`.

Risks/signals: backup count can be timing/filesystem sensitive. The test does not reset logger output after completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/internal/logging/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/container.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/example/container.yaml

Purpose: crictl example container spec running a Nydus Ubuntu image with `tail -f /dev/null`.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/container.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/containerd-config.toml -->
# sources/cloud-native/nydus-snapshotter/misc/example/containerd-config.toml

Purpose: containerd v2 example config using the Nydus proxy snapshotter and CRI runtime settings.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/containerd-config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/containerd-test-config.toml -->
# sources/cloud-native/nydus-snapshotter/misc/example/containerd-test-config.toml

Purpose: test containerd config with separate root/state/socket paths and Nydus proxy plugin address under the test root.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/containerd-test-config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/crictl.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/example/crictl.yaml

Purpose: crictl config pointing to the containerd-test socket.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/crictl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/optimizer-nri-plugin.conf -->
# sources/cloud-native/nydus-snapshotter/misc/example/optimizer-nri-plugin.conf

Purpose: optimizer NRI plugin TOML defaults for persist dir, server path, timeout, overwrite, readability, and Start/StopContainer events.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/optimizer-nri-plugin.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/pod.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/example/pod.yaml

Purpose: minimal CRI pod sandbox example with metadata, namespace, log dir, and empty Linux namespace options.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/example/pod.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/nri-prefetch/prefetchConfig.toml -->
# sources/cloud-native/nydus-snapshotter/misc/nri-prefetch/prefetchConfig.toml

Purpose: prefetch NRI plugin config setting the Nydus system controller Unix socket.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/nri-prefetch/prefetchConfig.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/containerd-config.toml -->
# sources/cloud-native/nydus-snapshotter/misc/optimizer/containerd-config.toml

Purpose: containerd optimizer test config enabling the Nydus proxy plugin and NRI plugin path/socket.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/containerd-config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/crictl.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/optimizer/crictl.yaml

Purpose: crictl optimizer test config pointing runtime and image endpoints to containerd.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/crictl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/nginx.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/optimizer/nginx.yaml

Purpose: CRI container spec for nginx optimizer test that mounts a script directory and reads a file list.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/nginx.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/sandbox.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/optimizer/sandbox.yaml

Purpose: CRI sandbox spec for the optimizer nginx test.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/sandbox.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/script/entrypoint.sh -->
# sources/cloud-native/nydus-snapshotter/misc/optimizer/script/entrypoint.sh

Purpose: optimizer test entrypoint that reads each file listed in an argument file to generate fanotify access events.

Control flow/state: this file is declarative or a small script used by local/CI examples. It configures runtime endpoints, mounted paths, plugin settings, or test workload behavior rather than implementing snapshotter library logic.

Dependencies/integration: consumed by Makefile targets, GitHub workflows, crictl/containerd/NRI, or optimizer test harnesses depending on path.

Risks/tests: examples can drift from current binary flags, socket paths, or containerd schema. Coverage is indirect through smoke, optimizer, and integration workflows rather than unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/optimizer/script/entrypoint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/Dockerfile -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/Dockerfile

Purpose: build deployment image that carries Nydus tools, kubectl, snapshotter binaries, configs, systemd unit, and deploy script artifacts.

Flow: downloads Nydus static release in a sourcer stage, downloads kubectl in another stage, then copies artifacts plus built `containerd-nydus-grpc` and `nydus-overlayfs` into `/opt/nydus-artifacts` layout. It prepares cache/tmp dirs and declares snapshotter lib/run volumes.

State/dependencies: external Nydus and Kubernetes release downloads; expects binaries in Docker build context from release workflow.

Integration points: used by release workflow to publish ghcr.io container images and by Kubernetes DaemonSet deployment.

Risks/tests: downloads amd64 Nydus tarball regardless of `TARGETARCH` in the URL, which is risky for non-amd64 image builds. Runtime behavior depends on `snapshotter.sh`.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/kustomization.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/kustomization.yaml

Purpose: base Kustomize entry for Nydus snapshotter Kubernetes deployment.

Structure: declares `nydus-snapshotter.yaml` as the only resource with kustomize v1beta1 metadata.

State/dependencies: no runtime state; consumed by `kubectl apply -k` or overlays.

Integration points: overlays for k3s and rke2 reference this base.

Risks/tests: minimal file; drift risk is only resource naming/path. Validation is by Kubernetes/kustomize tooling, not Go tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/nydus-snapshotter.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/nydus-snapshotter.yaml

Purpose: Kubernetes DaemonSet and ConfigMap for installing/running Nydus snapshotter on every node.

Flow: ConfigMap controls fs driver, volume config mode, runtime-specific snapshotter, and systemd service mode. DaemonSet runs privileged with hostNetwork/hostPID, invokes `snapshotter.sh deploy`, runs cleanup preStop, and mounts host paths for Nydus state, run socket, `/opt/nydus`, `/etc/nydus`, containerd config, local bin, and systemd units.

State/dependencies: mutates host filesystem and containerd config through mounted paths; image defaults to latest ghcr.io snapshotter.

Integration points: combined with RBAC and kustomize overlays.

Risks/tests: privileged host mutation has high blast radius. ConfigMap optional keys and host path availability determine behavior; no schema tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/base/nydus-snapshotter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-blockdev.toml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-blockdev.toml

Purpose: snapshotter config for blockdev/tarfs mode.

Flow/state: sets daemon mode `none`, fs driver `blockdev`, Nydus image path, skip SSL verify, Kata volume insertion, and enables tarfs with `image_block_with_verity` export mode.

Integration points: used for runtime stacks where Kata or block device handoff manages mounts without nydusd serving RAFS.

Risks/tests: requires kernel EROFS/tarfs support and Nydus image service compatibility. Misuse on unsupported hosts will fail at mount/runtime integration, not config parse alone.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-blockdev.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-proxy.toml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-proxy.toml

Purpose: snapshotter config for proxy fs driver mode.

Flow/state: sets daemon mode `none`, fs driver `proxy`, and enables Kata volume option injection.

Integration points: used by `nydus-snapshotter.service` and deployment paths that relay layer download/mount management to another agent.

Risks/tests: relies on downstream runtime/agent understanding the extra mount information. No direct unit test validates this file; config schema coverage is indirect.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/config-proxy.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/config.toml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/config.toml

Purpose: default packaged snapshotter configuration for fusedev mode.

Structure: version 1, standard root/socket, dedicated daemon mode, system controller enabled, nydusd paths/config, fusedev driver, failover/recover policy, cgroup memory config, log rotation, metrics, remote auth/mirrors, snapshot options, cache manager, signature validation, and experimental stargz/referrer/index/backend-source/tarfs toggles.

State/dependencies: read by main binary and tests; points to `/etc/nydus` and `/run/containerd-nydus` paths.

Integration points: systemd units, Dockerfile, Makefile install, config tests.

Risks/tests: config tests assert much of this file exactly. Operational risks include root path length, auth mode exclusivity, and feature toggles requiring matching runtime support.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter-rbac.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter-rbac.yaml

Purpose: Kubernetes RBAC for snapshotter DaemonSet.

Structure: creates `nydus-system` namespace, service account, cluster role allowing get/patch on nodes, and cluster role binding.

State/dependencies: cluster-scoped permissions persist after apply until cleanup.

Integration points: service account is referenced by the DaemonSet in base deployment.

Risks/tests: node patch permission is broad enough to affect node metadata/status-related workflows depending on use. No automated policy test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter-rbac.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.fscache.service -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.fscache.service

Purpose: systemd unit running containerd-nydus-grpc with fscache fs driver and fscache nydusd config before containerd.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.fscache.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.fusedev.service -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.fusedev.service

Purpose: systemd unit running containerd-nydus-grpc with default config before containerd.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.fusedev.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.service -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.service

Purpose: systemd unit running proxy-mode config before containerd.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydus-snapshotter.service -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config-localfs.json -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config-localfs.json

Purpose: nydusd FUSE config using localfs backend rooted in snapshotter cache, blobcache, xattrs, amplify_io, and two prefetch threads.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config-localfs.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config.fscache.json -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config.fscache.json

Purpose: nydusd fscache bootstrap template with registry backend, fscache cache type, and blob prefetch settings.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config.fscache.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config.fusedev.json -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config.fusedev.json

Purpose: default nydusd FUSE registry backend template with retry/timeouts, blobcache, xattrs, amplify_io, and aggressive prefetch.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/nydusd-config.fusedev.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/kustomization.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/kustomization.yaml

Purpose: Kustomize overlay that applies the k3s containerd config hostPath patch to the base deployment.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/mount_k3s_conf.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/mount_k3s_conf.yaml

Purpose: DaemonSet patch changing the containerd config mount to the k3s agent config directory.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/k3s/mount_k3s_conf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/rke2/kustomization.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/rke2/kustomization.yaml

Purpose: Kustomize overlay that applies the rke2 containerd config hostPath patch to the base deployment.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/rke2/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/rke2/mount_rke2_conf.yaml -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/rke2/mount_rke2_conf.yaml

Purpose: DaemonSet patch changing the containerd config mount to the rke2 agent config directory.

Control flow/state: declarative deployment/configuration artifact consumed by systemd, nydusd, or kustomize. It controls service ordering, daemon JSON templates, or hostPath patching rather than implementing Go control flow.

Dependencies/integration: tied to packaged `/etc/nydus`, `/usr/local/bin`, `/run/containerd-nydus`, Kubernetes DaemonSet, and `snapshotter.sh` deployment flows.

Risks/tests: path drift or config schema drift can break deployment. Validation is indirect through integration/release/Kubernetes workflows rather than local unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/overlays/rke2/mount_rke2_conf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/snapshotter.sh -->
# sources/cloud-native/nydus-snapshotter/misc/snapshotter/snapshotter.sh

Purpose: host deployment/cleanup script run by the Kubernetes DaemonSet image.

Flow: detects container runtime, installs artifacts, adjusts snapshotter config for fs driver, edits containerd config to add Nydus proxy plugin and snapshot annotation/layer retention options, optionally starts snapshotter through systemd, restarts/waits for services, and on cleanup removes related images/contents/snapshots, restores containerd config backup, stops service/process, and deletes installed artifacts/state.

State/dependencies: requires root, nsenter, systemctl, kubectl, ctr, host-mounted `/etc`, `/usr/local/bin`, `/var/lib/containerd`, `/run`, and `/opt/nydus`. Persists backups and installed files on host.

Integration points: base DaemonSet command and preStop hook; Dockerfile packages it.

Risks/tests: destructive cleanup and broad host mutation require careful deployment scoping. Text-based TOML edits can drift with containerd config format. `wait_service_active` always restarts the named service, including container runtime after deploy/cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/misc/snapshotter/snapshotter.sh -->
