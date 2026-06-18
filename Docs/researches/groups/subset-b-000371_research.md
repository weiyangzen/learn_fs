# Research Group: subset-b-000371

This grouped report covers the requested CSI Driver SMB source subset. Each section is source-tree aligned and wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/nodeserver_test.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/nodeserver_test.go

Purpose: This is the main unit/regression test suite for the SMB CSI node service paths. It validates `NodeStageVolume`, `NodePublishVolume`, `NodeUnpublishVolume`, `NodeUnstageVolume`, `NodeGetInfo`, `NodeGetCapabilities`, `NodeGetVolumeStats`, mount-point helpers, Kerberos cache helpers, and group-permission mount flag mutation.

Important APIs and fixtures: The file uses CSI request/response types from `github.com/container-storage-interface/spec/lib/go/csi`, gRPC status/codes, `testutil.TestError`, and the package fake mounter returned by `NewFakeMounter`. `matchFlakyWindowsError` allows Windows CSI proxy failures to be compared by stable substrings. Test cases build `VolumeCapability` variants for standard mounts, `VolumeMountGroup`, explicit `file_mode`/`dir_mode`, and access-mode-driven read-only behavior.

Control flow and coverage: `TestNodeStageVolume` table-drives validation errors, missing `source`, failed mkdir, in-progress lock rejection, fake mount failure, special-character passwords, metadata-substituted sources, `VolumeMountGroup`, and directory traversal rejection. `TestNodePublishVolume` covers missing fields, bind mount failures, idempotent already-mounted behavior, ephemeral publish dispatching through `NodeStageVolume`, read-only propagation from request flags, CSI access modes, and mount flags. The unpublish/unstage tests check argument validation and cleanup calls. Later tests isolate helper behavior for mount-point creation, statfs volume metrics, Kerberos option parsing, cache file naming, cache extraction, atomic symlink replacement, concurrent cache writes, idempotent bind mounts, and mode-bit widening.

State and persistence behavior: Tests create temporary directories and files under test work dirs or `/tmp`, mutate the driver's in-memory `volumeLocks`, and create Kerberos cache files/symlinks in temporary directories. The concurrent Kerberos test is a significant persistence signal because it asserts multiple volume-specific cache files can race on one `krb5cc_<uid>` symlink without `EEXIST` failures and with a valid final symlink.

Dependencies and integration points: The suite depends on OS behavior, especially Linux mount listing and symlink semantics, and conditionally skips or relaxes assertions for Windows. It verifies integration with `mount.SafeFormatAndMount`, `k8s.io/mount-utils`, CSI proxy semantics indirectly through platform-specific expected errors, and Kubernetes volume metrics via `volume.NewMetricsStatFS`.

Risks: Several assertions are platform-sensitive and encode exact error strings, which can drift across Go, Windows, CSI proxy, and mount-utils versions. Some tests use real filesystem paths and root-only mount behavior; `TestNodePublishVolumeIdempotentMount` only runs when root on non-Windows. Kerberos tests assume the process can `chown` cache files to `os.Getuid()`.

Test signals: This file is itself the highest-value node-server test signal. It includes regression coverage for directory traversal prevention, read-only bind propagation, nil mount capability handling, Kerberos atomic symlink races, and group RWX escalation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/nodeserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb.go

Purpose: Defines the SMB CSI `Driver`, deployment options, driver initialization, CSI capability registration, Kubernetes client setup, and common helper functions used by controller and node paths.

Important APIs/types/functions: `DriverOptions` carries node identity, driver name, stats cache settings, Windows unmount behavior, working mount dir, Kerberos cache settings, default delete policy, Windows HostProcess mode, and kubeconfig path. `Driver` embeds `csicommon.CSIDriver` and CSI unimplemented server structs, then stores the mounter, volume lock map, caches, Kubernetes client, and feature flags. `NewDriver` constructs caches, normalizes Kerberos defaults, initializes `volumeLocks`, and tries to create a Kubernetes client from `getKubeConfig`. `Run` logs version metadata, creates the safe mounter, registers controller/node capabilities, starts a non-blocking gRPC server, and waits. Helper functions include `GetUserNamePasswordFromSecret`, `IsCorruptedDir`, `getMountOptions`, `hasGuestMountOptions`, case-insensitive `setKeyValueInMap`, `replaceWithMap`, `validateOnDeleteValue`, `appendMountOptions`, `getRootDir`, kubeconfig helpers, `inClusterConfig`, and `validatePath`.

Control flow: Driver construction is tolerant of kubeconfig/client creation failures and logs warnings instead of aborting. `Run` is stricter and fatal-exits if version metadata or mounter creation fails. `inClusterConfig` mirrors Kubernetes client-go logic while adjusting service account token/CA paths for Windows HostProcess by prefixing `CONTAINER_SANDBOX_MOUNT_POINT`.

State and persistence behavior: The driver keeps in-memory timed caches for volume stats and deletion records using Azure cloud-provider cache utilities. Kubernetes secrets are read live through `kubeClient`; no secret material is persisted here. Path validation is stateless and rejects any slash- or backslash-separated segment equal to `..`.

Dependencies and integration points: Integrates CSI spec types, the repo's `csi-common` server, `pkg/mounter`, Kubernetes client-go, klog, mount-utils, and `sigs.k8s.io/cloud-provider-azure/pkg/cache`. Constants define StorageClass/volume context keys consumed by controller/node code and by e2e manifests.

Risks: `appendMountOptions` treats any option with a prefix matching a key as already included, so keys that are prefixes of other options can suppress intended additions. `NewDriver` can return a driver with nil `kubeClient`, which is valid for many paths but makes secret-backed ephemeral volume staging fail. `validatePath` blocks literal `..` segments but does not canonicalize SMB server/share semantics beyond segment splitting.

Test signals: `smb_test.go` covers constructor, run, helper functions, kubeconfig parsing, secret nil-client behavior, and path traversal validation. Node tests exercise constants and helpers indirectly in staging/publishing.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_darwin.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb_common_darwin.go

Purpose: Provides Darwin build-tagged implementations of cross-platform SMB mount helpers used by node server code.

Important APIs/functions: `Mount` delegates to `SafeFormatAndMount.MountSensitive`; `CleanupSMBMountPoint` and `CleanupMountPoint` delegate to `mount.CleanupMountPoint`; `preparePublishPath` and `prepareStagePath` are no-ops; `Mkdir` delegates to `os.Mkdir`.

Control flow: Darwin follows the generic mount-utils path without Linux credential-file special handling or Windows CSI proxy handling. The prepare hooks return success, leaving directory preparation to shared node logic.

State and persistence behavior: It can create directories through `Mkdir` and clean mount points through mount-utils. No platform-specific state is retained.

Dependencies and integration points: Depends only on `os` and `k8s.io/mount-utils`. It satisfies the same package-level function names used by `nodeserver.go`, selected via `//go:build darwin`.

Risks: Darwin support is thin and lacks the Linux special-character credential workaround and Windows proxy logic. Because no tests in this subset are Darwin-specific, regressions would likely be found only by cross-platform builds or manual Darwin tests.

Test signals: Covered indirectly by build-tag compilation rather than the Linux-focused unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux.go

Purpose: Provides Linux build-tagged SMB mount helpers, including a credential-file workaround for passwords that contain characters unsafe for direct CIFS mount option parsing.

Important APIs/functions: `NeedsCredentialsOption` detects the sensitive option shape `username=...`, `password=...` where password contains `"`, backtick, or comma. `Mount` writes sensitive options to a temporary `/tmp/*.smb.credentials` file and passes `credentials=<file>` when needed, otherwise delegates to `MountSensitive`. `CleanupSMBMountPoint`, `CleanupMountPoint`, `preparePublishPath`, `prepareStagePath`, and `Mkdir` provide Linux implementations for shared node code.

Control flow: The temp credentials file is created, written one option per line, closed and removed through a deferred cleanup, then passed as the sole sensitive mount option. Normal mounts flow directly to mount-utils.

State and persistence behavior: The only persistent side effect is target directory creation via `os.Mkdir`; credential files are transient and removed after `Mount` returns. Cleanup delegates to mount-utils and may remove mount directories.

Dependencies and integration points: Integrates with `nodeserver.go` sensitive option construction and `ContainsSpecialCharacter`. It depends on `/tmp` availability and Linux CIFS support for `credentials=`.

Risks: `NeedsCredentialsOption` intentionally relies on a narrow sensitive option layout; if node code changes the slice shape, special-character protection can silently stop applying. Temporary credential files exist briefly on disk and depend on default `os.CreateTemp` permissions.

Test signals: `smb_common_linux_test.go` directly covers positive and negative credential detection, including quote, backtick, and comma passwords. Node staging tests cover special password flow through failed fake mounts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux_test.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux_test.go

Purpose: Linux-specific unit tests for deciding when SMB credentials should be passed through a temporary credentials file.

Important APIs/functions: `TestNeedsCredentialsOption` calls `NeedsCredentialsOption` with combined username/password options, separated normal options, and separated passwords containing quote, backtick, or comma.

Control flow: A simple table asserts that only the exact two-element sensitive option layout with a special character in the password returns true.

State and persistence behavior: None; tests are pure and do not mount or create files.

Dependencies and integration points: Uses `testify/assert` and the Linux build-tagged implementation. It anchors behavior expected by `smb_common_linux.go` and `nodeserver.go`.

Risks: The test reflects the current narrow detector shape, so it would not catch future call sites that pass equivalent data in a different form unless test cases are expanded.

Test signals: Strong narrow signal for special-character password handling; no coverage for actual temp file creation/removal or mount-utils interaction.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_windows.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb_common_windows.go

Purpose: Provides Windows build-tagged SMB mount and cleanup helpers backed by the repo's CSI proxy mounter interface.

Important APIs/functions: `Mount` casts the safe mounter interface to `mounter.CSIProxyMounter` and calls `SMBMount`. `CleanupSMBMountPoint` calls `SMBUnmount`. `CleanupMountPoint` calls `Rmdir`. `removeDir` checks existence through `ExistsPath` and removes with `Rmdir`. `preparePublishPath` and `prepareStagePath` remove pre-created kubelet directories so Windows can create symlink/mapping paths. `Mkdir` calls `MakeDir`.

Control flow: Every operation first requires a successful type assertion to `CSIProxyMounter`; otherwise it returns a clear cast error. Prepare hooks handle the Windows-specific kubelet behavior where the publish directory may already exist and conflict with link creation.

State and persistence behavior: State is external to the process through Windows SMB global mappings and filesystem directories managed by CSI proxy. Cleanup removes mappings/directories through proxy calls.

Dependencies and integration points: Integrates tightly with `pkg/mounter.CSIProxyMounter`, Windows CSI proxy, klog, and shared node server package functions. The node server supplies `volumeID` for mapping operations.

Risks: All behavior depends on the concrete mounter implementing `CSIProxyMounter`; fake or generic mount-utils mounters fail. Removing existing stage/publish paths is intentional but high-impact if path calculation is wrong. Windows test assertions can be flaky due to CSI proxy error text drift.

Test signals: Node server tests include Windows-specific expected errors and skips, but this file itself has no dedicated Windows unit test in the subset.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_common_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_test.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/smb_test.go

Purpose: Unit tests for the common driver constructor, server startup path, helper functions, kubeconfig handling, secret retrieval failure, and path validation.

Important APIs/functions: `NewFakeDriver` constructs a test driver with default name and stats enabled. Tests cover `NewDriver`, `IsCorruptedDir`, `Run`, `getMountOptions`, `hasGuestMountOptions`, package-private `setKeyValueInMap`, `replaceWithMap`, `validateOnDeleteValue`, `appendMountOptions`, `getRootDir`, `getKubeConfig`, `GetUserNamePasswordFromSecret`, and `validatePath`.

Control flow: Most tests are table-driven. `TestRun` starts the non-blocking gRPC server in test mode on an ephemeral TCP endpoint. Kubeconfig tests create empty and valid config files and set `CONTAINER_SANDBOX_MOUNT_POINT` to exercise HostProcess error paths. Path validation tests cover forward slash, backslash, mixed separator, single dot, triple dot, and multiple directory traversal sequences.

State and persistence behavior: Creates temporary or local test files, environment variables, and a transient gRPC listener. The tests avoid live Kubernetes access except asserting nil-client secret retrieval fails.

Dependencies and integration points: Uses `testify/assert`, client-go kubeconfig parsing, filesystem APIs, and the package constants used by controller/node logic.

Risks: `TestRun` can expose network/listener sensitivity even in test mode. The kubeconfig test writes named files in the current working directory and depends on cleanup. Helper tests encode current semantics such as case-insensitive map replacement and prefix-based mount option deduplication.

Test signals: Good coverage for common helper behavior and recently important path traversal validation. It does not verify successful Kubernetes secret retrieval with a fake client.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/smb_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/version.go

Purpose: Defines build-time version metadata and renders it as structured `VersionInfo` or YAML for startup logging.

Important APIs/types/functions: Build variables `driverVersion`, `gitCommit`, and `buildDate` default to `N/A` and are intended for `-ldflags` injection. `VersionInfo` includes driver name/version, git commit, build date, Go version, compiler, and platform. `GetVersion` fills runtime fields from `runtime`. `GetVersionYAML` marshals the struct with `sigs.k8s.io/yaml` and trims surrounding whitespace.

Control flow: Version retrieval is pure except YAML marshaling error handling. `Run` in `smb.go` fatal-exits if YAML marshaling fails, which should be unlikely for this static struct.

State and persistence behavior: No persistence; state is process build metadata and runtime introspection.

Dependencies and integration points: Used by driver startup logs and tests. Build/release scripts can inject variable values to make images auditable.

Risks: Missing ldflags leave version fields as `N/A`, reducing operational traceability. JSON tags include spaces in field names, which controls YAML output labels but may surprise consumers expecting Go-style keys.

Test signals: `version_test.go` checks default values and YAML equivalence with the same marshaler.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version_test.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/version_test.go

Purpose: Unit tests for version metadata rendering.

Important APIs/functions: `TestGetVersion` compares `GetVersion(DefaultDriverName)` with expected default build values plus runtime Go/compiler/platform values. `TestGetVersionYAML` marshals `GetVersion("")` independently and compares trimmed YAML output with `GetVersionYAML("")`.

Control flow: Both tests are straightforward direct assertions.

State and persistence behavior: None; tests read runtime metadata only.

Dependencies and integration points: Uses `runtime`, `sigs.k8s.io/yaml`, `reflect`, and package constants. It protects startup log metadata consumed by `Driver.Run`.

Risks: The tests assume build variables remain at default `N/A` in unit test builds; a test environment that injects ldflags could require adjusted expectations.

Test signals: Good signal for default metadata shape and YAML serialization; no error-path coverage because marshaling the struct is expected to be stable.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/volume_lock.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/volume_lock.go

Purpose: Implements in-memory per-volume operation locking so duplicate CSI operations on the same logical key can return `Aborted` instead of racing.

Important APIs/types/functions: `volumeLocks` wraps a `sets.String` and `sync.Mutex`. `newVolumeLocks` initializes the set. `TryAcquire` atomically checks/inserts a volume ID key and returns false when already present. `Release` removes the key. `volumeOperationAlreadyExistsFmt` standardizes the node/controller error text.

Control flow: Callers acquire before a critical operation and defer release. In this subset, node staging/unstaging uses a key composed of `volumeID-targetPath`.

State and persistence behavior: State is process-local only and lost on driver restart. It protects concurrency inside one driver process but not across replicas or restarts.

Dependencies and integration points: Depends on Kubernetes `sets.String`. Integrated by node server paths and likely controller paths elsewhere in the package.

Risks: Locks require callers to consistently use the same key scheme. Because state is in-memory, operations interrupted by process exit do not leave stale locks, but concurrent operations in different pods/processes are not coordinated.

Test signals: `nodeserver_test.go` exercises lock rejection for staging and unstaging by pre-acquiring the expected key.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/volume_lock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util.go -->
# sources/control-plane/csi-driver-smb/pkg/util/util.go

Purpose: Provides small shared utilities for timed execution, bounded PowerShell command execution on Windows, and case-insensitive map updates.

Important APIs/types/functions: `MaxPathLengthWindows` is a Windows path constant. `powershellCmdSem` limits concurrent PowerShell commands to three. `ExecFunc` and `TimeoutFunc` define callback signatures. `WaitUntilTimeout` runs `execFunc` in a goroutine and returns either its error or `timeoutFunc` after a duration. `RunPowershellCmd` executes `powershell -Mta -NoProfile -Command` with optional environment additions under the semaphore. `SetKeyValueInMap` inserts or overwrites a key case-insensitively.

Control flow: `WaitUntilTimeout` uses a buffered done channel to avoid blocking the goroutine when the timeout branch wins, but it does not cancel the underlying `execFunc`. `RunPowershellCmd` acquires semaphore capacity before command creation and releases it with defer.

State and persistence behavior: Global semaphore is package-level process state. Commands inherit the environment plus provided env strings and can perform arbitrary external side effects.

Dependencies and integration points: `nodeserver.go` uses `WaitUntilTimeout` around SMB mount calls and uses `SetKeyValueInMap` for ephemeral volume context. Windows mounter code can use `RunPowershellCmd` through related packages.

Risks: Timed-out `execFunc` continues running in the background; callers must ensure the operation is safe to outlive the timeout. `RunPowershellCmd` logs command strings at high verbosity and could expose sensitive command text if callers include secrets. The semaphore bounds concurrency but has no context cancellation.

Test signals: `util_test.go` covers success, error, timeout, goroutine leak behavior after waiting, and map update semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util_test.go -->
# sources/control-plane/csi-driver-smb/pkg/util/util_test.go

Purpose: Unit tests for utility timeout behavior and case-insensitive map insertion.

Important APIs/functions: `TestWaitUntilTimeout` exercises `WaitUntilTimeout` when `execFunc` returns an error, exceeds the timeout, and completes successfully. It uses `go.uber.org/goleak` to detect leaked goroutines after delayed timeout cleanup. `TestSetKeyValueInMap` mirrors the SMB package helper tests for nil maps, new keys, existing keys, and case-insensitive replacement.

Control flow: Timeout test cases run callbacks with one-second timeouts; when an error occurs, the test sleeps to let slow goroutines finish before goleak verification.

State and persistence behavior: No filesystem persistence. Tests rely on goroutine scheduling and wall-clock sleep.

Dependencies and integration points: The timeout behavior is important for node SMB mounts, where the timeout reports failure but cannot cancel the mount operation.

Risks: Wall-clock sleeps can make the test suite slower and potentially flaky under extreme load. The test does not cover `RunPowershellCmd`, likely because it is Windows/environment dependent.

Test signals: Good signal for callback return selection and absence of permanent goroutine leaks; limited signal for command execution utilities.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/util/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/dependabot.yaml -->
# sources/control-plane/csi-driver-smb/release-tools/.github/dependabot.yaml

Purpose: Configures Dependabot for the release-tools repository copy to update GitHub Actions dependencies.

Important configuration: Uses schema `version: 2`, enables beta ecosystems, watches `github-actions` in the repository root daily, applies labels `area/dependency`, `release-note-none`, and `ok-to-test`, and limits open pull requests to ten.

Control flow: GitHub Dependabot consumes this declarative file; there is no runtime code.

State and persistence behavior: Dependabot creates PRs against repository workflow references. The file itself persists policy only.

Dependencies and integration points: Integrates with GitHub Actions, repository labeling conventions, and Kubernetes CSI PR automation.

Risks: The directory is `/`, so it assumes workflows live at the root of the repo that imports release-tools. Updates are limited to actions, not Go, Docker, or Python dependencies.

Test signals: No local tests; behavior is observable through Dependabot PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/dependabot.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/workflows/codespell.yml -->
# sources/control-plane/csi-driver-smb/release-tools/.github/workflows/codespell.yml

Purpose: GitHub Actions workflow that runs codespell on pushes and pull requests.

Important configuration: Checks out code with a pinned `actions/checkout` commit and runs pinned `codespell-project/actions-codespell` v2.2. It enables filename checking and skips binary/image patterns, sum files, `.git`, the workflow file itself, and `prow.sh`.

Control flow: Triggered on `push` and `pull_request`, with one Ubuntu job and two steps.

State and persistence behavior: No persistent state except workflow results and annotations produced by GitHub Actions.

Dependencies and integration points: Complements `verify-spelling.sh`, but uses codespell rather than misspell. It integrates with GitHub branch protection if configured.

Risks: Skipping `prow.sh` avoids noisy false positives but can hide spelling mistakes in a large user-facing script. Pinned action SHAs need periodic maintenance.

Test signals: Workflow itself is the spelling test signal for GitHub-hosted checks.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/workflows/codespell.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/workflows/trivy.yaml -->
# sources/control-plane/csi-driver-smb/release-tools/.github/workflows/trivy.yaml

Purpose: GitHub Actions workflow that scans the configured Go toolchain image for vulnerabilities with Trivy.

Important configuration: Runs on pushes to `master` and daily schedule. It reads `CSI_PROW_GO_VERSION_BUILD` from `prow.sh`, emits it as a step output, then scans `golang:<version>` with pinned `aquasecurity/trivy-action`. It fails on any vulnerability severity from UNKNOWN through CRITICAL when unfixed issues are ignored.

Control flow: Checkout, parse Go version with shell pipeline, run Trivy action.

State and persistence behavior: No local persistence. Results live in the workflow run and may fail CI.

Dependencies and integration points: Couples directly to `prow.sh` config syntax. Supports release-tools maintenance by detecting vulnerable Go base images.

Risks: The `grep|awk|sed` parser is brittle if `prow.sh` changes formatting. Scanning `golang:<version>` may not exactly match all CI images or build environments.

Test signals: CI vulnerability signal for the Go version used by release-tools.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/workflows/trivy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.prow.sh -->
# sources/control-plane/csi-driver-smb/release-tools/.prow.sh

Purpose: Prow entrypoint for testing the csi-release-tools repository itself rather than an importing CSI component.

Important behavior: Runs `verify-shellcheck.sh`, `verify-spelling.sh`, and `verify-boilerplate.sh` with the current directory as root.

Control flow: `bash -e` exits on the first failed verifier. There is no argument parsing or cleanup beyond the delegated scripts.

State and persistence behavior: Delegated verifiers may create temporary directories or containers; this wrapper keeps no state.

Dependencies and integration points: Used by Prow jobs for release-tools. It differs from normal consumers that source/use `prow.sh`.

Risks: It does not run the heavyweight Kind/e2e flow, so release-tools changes can still break importer-specific usage not covered by static checks.

Test signals: Provides shell lint, spelling, and boilerplate signals for the release-tools subtree.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/boilerplate/boilerplate.py -->
# sources/control-plane/csi-driver-smb/release-tools/boilerplate/boilerplate.py

Purpose: Scans repository files and reports those whose license boilerplate headers do not match reference templates.

Important APIs/functions: CLI arguments accept optional file names, `--rootdir`, `--boilerplate-dir`, and `--verbose`. `get_refs` loads `boilerplate.*.txt` templates by extension or basename. `file_passes` reads a file, strips Go build constraints and shell/Python shebangs, compares the top lines against the reference after normalizing one date to `YEAR`, and emits verbose diffs. `file_extension`, `normalize_files`, `get_files`, and `get_regexs` support filtering. `main` prints failing paths.

Control flow: Without explicit files, it walks the root directory while pruning skipped directories, filters by template extensions, tests each file, and prints only failures. It returns 0 even when failures are found; callers decide failure by checking non-empty output.

State and persistence behavior: Read-only scanner; no persistent changes.

Dependencies and integration points: Called by `verify-boilerplate.sh`. Template files in the same directory define supported file types. Uses Python stdlib only.

Risks: The date substitution stops after the first matching line, so unconventional headers with multiple date fields may not normalize as expected. Returning 0 for failures is intentional for shell capture but surprising if run directly.

Test signals: The verify wrapper treats any output as failure. There are no in-file unit tests despite a comment in the wrapper about unit test output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/boilerplate/boilerplate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.sh -->
# sources/control-plane/csi-driver-smb/release-tools/cloudbuild.sh

Purpose: Thin Cloud Build entrypoint that sources release-tools `prow.sh` and runs `gcr_cloud_build`.

Important behavior: Uses `/bin/bash`, sources `release-tools/prow.sh`, then invokes `gcr_cloud_build`, which configures Docker auth, optional QEMU emulation, derives `REV` from `GIT_TAG`, and runs `make push-multiarch`.

Control flow: All substantive control flow lives in `prow.sh`; this file assumes it is run from the importing repository root with `release-tools/prow.sh` available.

State and persistence behavior: Delegated function can configure Docker credentials and push images to a registry.

Dependencies and integration points: Paired with `cloudbuild.yaml` and importing repos' `.cloudbuild.sh` symlink/wrapper convention.

Risks: Sourcing `prow.sh` executes all top-level `configvar` calls and requires expected shell environment. Failures propagate directly.

Test signals: Covered indirectly by image-pushing jobs; no local unit tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.yaml -->
# sources/control-plane/csi-driver-smb/release-tools/cloudbuild.yaml

Purpose: Reusable Google Cloud Build configuration for multi-arch Kubernetes CSI image builds.

Important configuration: Sets a two-hour timeout, allows loose substitutions, runs a pinned `gcb-docker-gcloud` image with `./.cloudbuild.sh` as entrypoint, and passes `GIT_TAG`, `PULL_BASE_REF`, `REGISTRY_NAME`, and `HOME`. Default substitutions include `_GIT_TAG`, `_PULL_BASE_REF`, and `_STAGING_PROJECT`.

Control flow: Cloud Build executes one step; `.cloudbuild.sh` is expected to call `release-tools/cloudbuild.sh` or equivalent.

State and persistence behavior: Produces and pushes multi-arch images through delegated make targets.

Dependencies and integration points: Tied to Kubernetes image-pushing infrastructure, staging projects, Docker buildx behavior, and Dockerfiles accepting a `binary` build argument.

Risks: Assumes importing repos follow symlink and build-argument conventions. The builder image SHA/tag must be maintained. Registry and tag derivation depend on Prow substitutions.

Test signals: Validated by real Cloud Build image-push jobs rather than local tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/cloudbuild.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/csi-driver-smb/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: Helper script for maintainers to list supported Kubernetes CSI sidecar release versions and optionally associated Docker images for documentation updates.

Important APIs/functions: `check_gh_command` validates GitHub CLI availability. `duration_ago` formats relative ages. `parse_version` accepts `vX.Y.Z`. `end_of_life_grouped_versions` groups major/minor releases and applies CSI support policy: latest is always supported, minor releases younger than one year are supported at latest patch, and older minors with a patch newer than roughly three months are supported. `get_release_docker_image` parses release notes for a `docker pull` line. `get_versions_from_releases` shells out to `gh release list` and groups release dates. `main` parses repeated `--repo/-R`, display, and doc flags.

Control flow: For each repo, it reads releases via `gh`, computes supported patch versions, prints dates/ages, and optionally fetches release pages for Docker image lines.

State and persistence behavior: Read-only except terminal output; depends on GitHub CLI authentication/network state.

Dependencies and integration points: Uses Python stdlib plus `dateutil.relativedelta`, `gh`, GitHub release formatting, and CSI project support policy docs.

Risks: Release list column parsing assumes `gh release list` tab format and published timestamp position. `parse_version` ignores prereleases and nonstandard tags. The `--display` flag defaults true even when `--doc` is set, so doc output includes display output too.

Test signals: No automated tests; correctness is manual/documentation-support oriented.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/contrib/get_supported_version_csi-sidecar.py -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/filter-junit.go -->
# sources/control-plane/csi-driver-smb/release-tools/filter-junit.go

Purpose: Command-line tool for filtering and merging JUnit XML files so Prow/Spyglass artifacts focus on relevant test cases.

Important APIs/types/functions: Flags `-o` chooses output path and `-t` chooses a regexp for testcase names. `TestResults`, `TestSuite`, `TestCase`, and `SkipReason` model enough JUnit XML for Ginkgo v1/v2. `SkipReason` preserves empty `<skipped></skipped>` elements through custom marshal/unmarshal behavior.

Control flow: Reads each input file, tries to unmarshal as `<testsuite>`, falls back to `<testsuites><testsuite>`, appends test cases, filters names by regexp, deduplicates by testcase name, and replaces skipped-only entries with real executed entries when available. Writes indented XML to stdout or file.

State and persistence behavior: Writes one output XML file when `-o` is not `-`. It does not preserve all possible JUnit attributes, only represented fields.

Dependencies and integration points: Invoked by `prow.sh` after e2e and make-test runs to reduce duplicated skipped tests and merge step artifacts.

Risks: The stdin path uses `os.Stdin.Read(data)` with a nil slice, which reads zero bytes; stdin input is likely broken. Map-based deduplication yields nondeterministic testcase order. Unsupported JUnit fields are dropped.

Test signals: No direct tests in this subset; behavior is indirectly exercised in Prow jobs that inspect final JUnit output.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/filter-junit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/generate-patch-release-notes.sh -->
# sources/control-plane/csi-driver-smb/release-tools/generate-patch-release-notes.sh

Purpose: Maintainer automation for generating patch release changelog PRs across Kubernetes CSI repositories.

Important behavior: Requires `CSI_RELEASE_TOKEN`, `GITHUB_USER`, `gh`, and `release-notes`. The editable `releases` array lists repo/version pairs. `gen_patch_relnotes` invokes `release-notes` from previous patch tag to release branch. The main loop parses minor/patch, checks out a `CHANGELOG` branch from `upstream/release-<minor>`, prepends generated notes to `CHANGELOG-<minor>.md`, commits, force-pushes, and opens a PR with `release-note NONE`.

Control flow: Uses `set -e -x`; any failed command aborts. It computes previous patch by subtracting one from the patch number.

State and persistence behavior: Mutates local git branches, changelog files, remote branches, and GitHub PRs.

Dependencies and integration points: Depends on a particular repository layout where changelogs live under `$repo/CHANGELOG`, upstream remotes exist, and release branches are named `release-X.Y`.

Risks: Force-pushes and branch deletion are destructive to the maintainer workspace. It does not handle patch zero, existing PR updates, or conflicts. The `releases` array is empty/commented by default, requiring manual edits.

Test signals: No automated tests; intended for manual maintainer execution.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/generate-patch-release-notes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-get-kubernetes.sh -->
# sources/control-plane/csi-driver-smb/release-tools/go-get-kubernetes.sh

Purpose: Updates Go module dependencies that originate from `kubernetes/kubernetes` to a specific Kubernetes release, including required staging-module replace directives.

Important behavior: Accepts `-p` to prune unused replace directives and `-h` for help, then requires one Kubernetes `x.y.z` version. It fetches Kubernetes `go.mod`, extracts staging modules, maps each module to its `kubernetes-<version>` pseudo release, writes `go mod edit -replace` directives, discovers used `k8s.io` packages with `go list`, then runs `go get` on package versions.

Control flow: The script first sets/updates replacement modules, optionally drops unused ones, then gathers packages with `go list all` or falls back to dependency listing for `./...`.

State and persistence behavior: Mutates `go.mod` and module cache, and can change `go.sum` when users run tidy afterward.

Dependencies and integration points: Used by module-update scripts and `update-vendor.sh`. Depends on curl, Go modules, Kubernetes staging module versioning, and network access to GitHub/module proxies.

Risks: Package/module parsing is shell/sed-based and can miss unusual package layouts. The script can leave `go.mod` partly edited if later `go get` fails. It warns about complex Kubernetes fake versions but does not run tidy/vendor itself.

Test signals: No direct tests; success is validated by subsequent `go mod tidy`, vendor checks, and repo test suites.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-get-kubernetes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-modules-targeted-update.sh -->
# sources/control-plane/csi-driver-smb/release-tools/go-modules-targeted-update.sh

Purpose: Maintainer automation to update a selected list of Go modules in selected CSI repos/branches and open PRs.

Important behavior: Configures `org`, `modules`, and `releases` arrays in the script. For each repo/branch, it checks out a branch from `upstream/<branch>`, runs `go get` for each module, tidies/vendors, commits, force-pushes to origin, and creates a GitHub PR using `GITHUB_USER`.

Control flow: Uses `set -e -x`; default `releases` entries are commented, so no work occurs until edited.

State and persistence behavior: Mutates local repo branches, `go.mod`, `go.sum`, `vendor`, remote branches, and GitHub PR state.

Dependencies and integration points: Requires `gh`, Go modules, repo remotes named `upstream` and `origin`, and a workspace one directory above target repos.

Risks: Force-pushes and branch deletion can overwrite maintainer work. It does not run tests before PR creation. The generated PR title/body are generic and may need manual adjustment.

Test signals: No automated tests; correctness is validated manually and by downstream CI.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-modules-targeted-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-modules-update.sh -->
# sources/control-plane/csi-driver-smb/release-tools/go-modules-update.sh

Purpose: Batch maintainer script to update Kubernetes-related Go modules across many Kubernetes CSI repositories and create PRs.

Important behavior: Parses `-u` GitHub username and `-v` Kubernetes version, runs `gh auth login`, iterates a hardcoded repo/branch list, refreshes release-tools via `git subtree pull`, runs `go-get-kubernetes.sh -p`, retries tidy/vendor up to `MAX_RETRY`, commits dependency changes, sets origin to the user's fork, runs `make test`, pushes, and opens a PR.

Control flow: Uses nested subshell per repo and per branch. It has conflict recovery for release-tools subtree pulls by replacing the subtree from `FETCH_HEAD`.

State and persistence behavior: Performs broad git mutations, dependency updates, vendor regeneration, remote URL changes, pushes, and PR creation.

Dependencies and integration points: Depends on `gh`, GitHub auth, forks, upstream origin conventions, `make test`, release-tools subtree layout, and `go-get-kubernetes.sh`.

Risks: The retry condition syntax `while ! ./release-tools/go-get-kubernetes.sh -p "$v" && RETRY < $MAX_RETRY` appears to invoke `RETRY` as a command comparison rather than a shell arithmetic test, making retry behavior suspect. It force-pushes and changes remotes. The PR head currently uses `module-update-master` even when iterating other branches, which may be wrong for non-master branches.

Test signals: Runs `make test` per repo before pushing, but the script itself has no tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/go-modules-update.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/prow.sh -->
# sources/control-plane/csi-driver-smb/release-tools/prow.sh

Purpose: Large reusable Prow harness for Kubernetes CSI repositories. It builds components, runs unit tests, creates Kind clusters, installs CSI drivers/snapshot components, runs Kubernetes e2e and csi-sanity tests, collects logs, filters JUnit, and supports Cloud Build image publishing.

Important APIs/functions: Configuration is expressed through `configvar` defaults such as Go versions, Kind version/images, Kubernetes version, deployment repo/version, e2e repos, csi-sanity settings, and test focus/skip regexes. Utility functions include `get_versioned_variable`, `version_to_git`, `tests_enabled`, cluster-need predicates, `ensure_paths`, `run`, `run_with_go`, `install_kind`, `install_ginkgo`, `install_dep`, `git_checkout`, `git_clone`, `list_gates`, `list_api_groups`, `go_version_for_kubernetes`, `start_cluster`, `delete_cluster_inside_prow_job`, `find_deployment`, `install_csi_driver`, snapshot CRD/controller installers, `collect_cluster_info`, `start_loggers`, `patch_kubernetes`, `install_e2e`, `install_sanity`, `run_with_loggers`, `run_filter_junit`, `run_e2e`, `run_sanity`, `ascii_to_xml`, `make_test_to_junit`, `version_gt`, `main`, and `gcr_cloud_build`.

Control flow: Top-level config selects build/test behavior. `main` sets work paths, builds binaries/containers when enabled, runs unit tests through `make_test_to_junit`, installs Kind if needed, creates non-alpha and/or alpha clusters, installs snapshot components and the CSI driver, runs sanity and e2e suites according to configured test groups, exports/deletes clusters, merges JUnit steps, and returns accumulated failure status. `gcr_cloud_build` is a separate entrypoint for image pushes.

State and persistence behavior: Creates temporary work dirs under `$GOPATH/pkg`, binaries, checked-out repos, Kind clusters, Docker images/tags, Kubernetes resources, artifacts/logs/JUnit files, and pushed images in Cloud Build mode. It intentionally cleans Kind clusters in Prow jobs but leaves work directories for caller cleanup.

Dependencies and integration points: Integrates with Prow, Go toolchains through `GOTOOLCHAIN`, Makefile targets (`all`, `test`, `container`, `push-multiarch`), Docker, Kind, kubectl, Kubernetes source tree, Ginkgo, csi-test, CSI driver deployment scripts, external-snapshotter manifests, and `filter-junit.go`.

Risks: This is a high-blast-radius shell harness. Config parsing relies on shell word splitting and repo conventions. It downloads/builds external tools and repos dynamically. Cluster setup and test filtering are sensitive to Kubernetes/Kind version compatibility. Some paths assume Linux amd64. JUnit filtering inherits `filter-junit.go` limitations. Docker image loading parses Makefile `CMDS` with grep/sed.

Test signals: Used directly by CI jobs, so its strongest signal is Prow execution. Static release-tools checks cover shell syntax/lint/spelling/boilerplate. `verify-go-version.sh` reads its Go version.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/prow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/pull-test.sh -->
# sources/control-plane/csi-driver-smb/release-tools/pull-test.sh

Purpose: Prow helper for testing release-tools changes after importing them into another repository through `git subtree`.

Important behavior: Enables `GIT_NO_LAZY_FETCH=0` to work around blobless Prow checkouts, records the current release-tools directory, resets the target repo, pulls the current release-tools subtree into `$PULL_TEST_REPO_DIR`, prints recent logs, then execs the target repo's `.prow.sh`.

Control flow: `set -ex` aborts on failures. It falls through from subtree update into the consumer repo's own test script.

State and persistence behavior: Destructively resets the target repo worktree, mutates its `release-tools` subtree, and runs its CI tests.

Dependencies and integration points: Requires `PULL_TEST_REPO_DIR`, git subtree support, Prow checkout layout, and a target `.prow.sh`.

Risks: `git reset --hard` is intentional but destructive; it must run only in disposable Prow workspaces. Blobless checkout handling depends on Git behavior.

Test signals: Provides integration signal that release-tools changes still work when imported by a real CSI repo.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/pull-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/update-vendor.sh -->
# sources/control-plane/csi-driver-smb/release-tools/update-vendor.sh

Purpose: Updates vendored dependencies for repos using either dep or Go modules.

Important behavior: If `Gopkg.toml` exists, runs `dep ensure`. If `go.mod` exists, runs `release-tools/verify-go-version.sh go`, then `go mod tidy`, `go mod vendor`, and another tidy with `GO111MODULE=on`.

Control flow: Simple file-presence branch; no explicit `set -e`, but commands in grouped subshells fail through their exit status when invoked by callers that use errexit.

State and persistence behavior: Mutates dependency metadata and `vendor/`.

Dependencies and integration points: Used by maintainers and possibly Makefile targets. Integrates with `verify-go-version.sh` and Go module tooling.

Risks: No explicit failure handling or repo cleanliness check. Running in the wrong directory can update the wrong module. Dep support is legacy.

Test signals: Validated by `verify-vendor.sh` and downstream tests.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/update-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/util.sh -->
# sources/control-plane/csi-driver-smb/release-tools/util.sh

Purpose: Shared shell utility functions and color constants for release-tools verification scripts.

Important APIs/functions: `kube::util::sourced_variable` documents externally used variables for shellcheck. `sortable_date` prints sortable timestamps. `array_contains` checks membership. `trap_add` composes multiple commands on a signal. `download_file` retries curl downloads. `wait-for-jobs` waits for all background jobs and returns failure count. `join` joins arguments with a delimiter. `check-file-in-alphabetical-order` diffs a file against `LC_ALL=C sort`. Color constants are declared once and marked as sourced variables.

Control flow: Functions are sourced by other scripts and do not execute substantive work at source time beyond defining colors if unset.

State and persistence behavior: Can set traps and declare readonly color variables in the caller shell. `download_file` removes and writes destination files.

Dependencies and integration points: Used at least by `verify-shellcheck.sh`; useful for broader Kubernetes-style scripts.

Risks: `trap_add` evaluates trap command strings while building traps, requiring careful quoting by callers. `download_file` removes the destination before confirming a replacement can be downloaded.

Test signals: No direct tests; shellcheck coverage via release-tools verifiers.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/util.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-boilerplate.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-boilerplate.sh

Purpose: Verifies source files have expected Kubernetes license boilerplate headers.

Important behavior: Uses strict shell options, ensures a `python` command exists by installing an alternatives link to python3 when missing, resolves release-tools path and root, runs `boilerplate.py --verbose`, captures failing files, and exits nonzero if any are reported.

Control flow: Temporary file/trap setup is present but not used for meaningful unit test execution. Failures print each path with a message.

State and persistence behavior: May mutate `/usr/bin/python` alternatives in environments without `python`, and creates/removes a temporary file.

Dependencies and integration points: Wraps `boilerplate/boilerplate.py`; invoked by `.prow.sh` and likely Makefile verify targets.

Risks: Calling `update-alternatives` may require root and is invasive. The wrapper relies on boilerplate.py printing failures while returning zero.

Test signals: Static license header check.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-boilerplate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-go-version.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-go-version.sh

Purpose: Warns when the local Go major/minor version differs from the release-tools configured build Go version.

Important behavior: Requires a Go binary path argument, parses `go version`, sources `release-tools/prow.sh` to read `CSI_PROW_GO_VERSION_BUILD`, compares major.minor, and prints a warning block on mismatch.

Control flow: Missing argument or inability to run Go exits nonzero; version mismatch is warning-only and exits zero.

State and persistence behavior: No persistence, but sourcing `prow.sh` runs its top-level config logging.

Dependencies and integration points: Used by `update-vendor.sh` and vendor verification workflows.

Risks: The parser assumes standard `go version` output and exact major.minor match. Warning-only behavior may allow sensitive tidy/vendor changes under a different Go version.

Test signals: Provides advisory signal, not a hard gate.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-go-version.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-logcheck.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-logcheck.sh

Purpose: Runs `sigs.k8s.io/logtools/logcheck` against the repository to verify contextual klog usage.

Important behavior: Accepts optional logcheck version defaulting to `0.10.0`, resolves repo root, installs logcheck into a temporary directory with `go install`, and runs it with `-check-contextual -check-with-helpers` over `<root>/...`.

Control flow: Strict shell options abort on install or check failure. Trap removes the temporary install directory.

State and persistence behavior: Writes a temporary binary directory and uses Go module cache/network. No repo files should change.

Dependencies and integration points: Integrates with Go tooling and logcheck static analysis; useful for repos adopting contextual logging.

Risks: Requires network/module access unless cached. It scans the entire repo module pattern and can be sensitive to generated/vendor code if not excluded by module layout.

Test signals: Static logging API usage signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-logcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-shellcheck.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-shellcheck.sh

Purpose: Runs shellcheck over repository shell scripts, using either a matching host shellcheck binary or a pinned Docker image.

Important behavior: Sources `util.sh`, discovers `.sh` files excluding hidden/build/vendor/git-ignored paths, checks for host shellcheck version `0.6.0`, otherwise creates a long-lived Docker container and executes shellcheck inside it. It disables lint IDs 1090 and 2230 and aggregates all failures before exiting.

Control flow: Strict shell options plus explicit temporary disabling around shellcheck invocation to collect failures. `trap_add` cleans up the Docker container.

State and persistence behavior: May create/remove a Docker container named `k8s-shellcheck`; otherwise read-only.

Dependencies and integration points: Invoked by `.prow.sh`; depends on Docker if host shellcheck version is absent.

Risks: Pinning an old shellcheck version gives stable results but misses newer diagnostics. Docker dependency can fail in restricted CI. Discovery only covers `*.sh`, not extensionless shell entrypoints.

Test signals: Static shell lint signal for release-tools scripts.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-shellcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-spelling.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-spelling.sh

Purpose: Runs misspell over tracked repository files outside vendor.

Important behavior: Uses strict shell options, installs `github.com/client9/misspell/cmd/misspell@v0.3.4` into a temporary directory if missing, runs `git ls-files -z | grep -z -v vendor | xargs -0 misspell --`, records output, prefixes errors, and exits nonzero when spelling errors are found.

Control flow: Temporary directory is always removed by trap. Missing tool triggers a temporary Go install outside the repo module.

State and persistence behavior: Writes only the temp directory and error log; reads git tracked files.

Dependencies and integration points: Invoked by `.prow.sh`; overlaps with the GitHub Actions codespell workflow but uses a different spelling engine.

Risks: Requires Go/network if misspell is not installed. The vendor filter is a simple substring exclusion and may skip paths containing `vendor` elsewhere.

Test signals: Static spelling signal for tracked files.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-spelling.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-subtree.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-subtree.sh

Purpose: Verifies that a directory managed by `git subtree` contains no non-upstream local modifications.

Important behavior: Requires a directory argument. It finds the latest non-merge commit touching that directory with `git log --remove-empty --no-merges`; if any exists, it prints the relevant log and exits nonzero, otherwise reports a clean upstream copy.

Control flow: Simple argument validation and git query branch.

State and persistence behavior: Read-only git inspection.

Dependencies and integration points: Useful for imported `release-tools` subtrees in CSI repos, where merge commits from subtree pulls are expected but direct edits are not.

Risks: It trusts merge commits as upstream-only; a manual edit hidden in a merge commit would bypass the check, as the comment notes. It must be run from the right repo context.

Test signals: Static git-history cleanliness signal.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-subtree.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-vendor.sh -->
# sources/control-plane/csi-driver-smb/release-tools/verify-vendor.sh

Purpose: Verifies Go module and vendor content are up to date, with Prow-aware skip logic for presubmits that do not affect dependencies.

Important behavior: If `go.mod` exists, it may skip in Prow when a presubmit did not touch dependency-sensitive files/imports. Otherwise it runs `go mod tidy`, checks `go.mod`/`go.sum` cleanliness, runs `go mod vendor` when `vendor/` exists, and checks vendor cleanliness.

Control flow: Shell condition combines job type and git diff checks to decide skipping. Failures print diffs/status and exit nonzero.

State and persistence behavior: Runs tidy/vendor, which can mutate `go.mod`, `go.sum`, and `vendor`; it then fails if mutations occurred.

Dependencies and integration points: Used by CI verify targets to enforce dependency reproducibility.

Risks: The skip heuristic may miss dependency impacts outside its diff/import patterns. It references `${JOB_NAME}` with no default under non-strict shell, which is okay here but would be unsafe under nounset. Running it on a dirty worktree can conflate preexisting changes with generated drift.

Test signals: Strong dependency reproducibility signal for module-based repos.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/verify-vendor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/driver/driver.go -->
# sources/control-plane/csi-driver-smb/test/e2e/driver/driver.go

Purpose: Defines generic e2e driver interfaces and a helper for constructing Kubernetes StorageClasses for dynamic and pre-provisioned PV tests.

Important APIs/types/functions: `PVTestDriver` composes `DynamicPVTestDriver` and `PreProvisionedVolumeTestDriver`. Dynamic drivers create StorageClasses for dynamic provisioning. Pre-provisioned drivers create PVs and pre-provisioned StorageClasses. `getStorageClass` fills defaults for reclaim policy (`Delete`), binding mode (`Immediate`), and enables volume expansion.

Control flow: `getStorageClass` accepts optional pointers, fills defaults when nil, and returns a `storagev1.StorageClass` with generated name, provisioner, parameters, mount options, reclaim policy, binding mode, allowed topologies, and `AllowVolumeExpansion=true`.

State and persistence behavior: Pure object construction; persistence occurs when tests create the returned objects through Kubernetes clients.

Dependencies and integration points: Used by `smb_driver.go` and testsuites under `test/e2e`. Depends on Kubernetes core and storage API types.

Risks: Defaults affect all e2e tests using nil policies/modes. Always enabling volume expansion assumes the driver supports expansion, which SMB controller code advertises.

Test signals: No direct unit tests; validated through e2e StorageClass/PV creation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/driver/driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/driver/smb_driver.go -->
# sources/control-plane/csi-driver-smb/test/e2e/driver/smb_driver.go

Purpose: SMB-specific implementation of the e2e test driver interfaces.

Important APIs/types/functions: `SMBDriverNameVar` (`SMB_CSI_DRIVER`) overrides the provisioner. `SMBDriver` stores the driver name. `InitSMBDriver` defaults to `smb.DefaultDriverName` and logs the selected driver. `normalizeProvisioner` replaces `/` with `-` for generated object names. Methods build dynamic StorageClasses, pre-provisioned StorageClasses, and CSI PersistentVolumes. `GetParameters` returns default `skuName: Standard_LRS`.

Control flow: Dynamic and pre-provisioned StorageClass methods compose namespace/provisioner into `GenerateName` and delegate to `getStorageClass`. `GetPersistentVolume` defaults reclaim policy to Retain, optionally sets `NodeStageSecretRef`, and adds the legacy provisioner annotation.

State and persistence behavior: Pure Kubernetes object construction; cluster persistence occurs in testsuites.

Dependencies and integration points: Integrates package SMB constants, Kubernetes API types, resource parsing, and e2e tests. The PV attributes and secret references connect test objects to node/controller behavior.

Risks: `GetPreProvisionStorageClass` does not normalize provisioner in `generateName`, unlike dynamic and PV paths, so provisioner names containing `/` could produce invalid generated names. A spelling typo in `preprovsioned` affects generated PV names only.

Test signals: Exercised by all e2e dynamic/pre-provisioned tests but not unit-tested here.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/driver/smb_driver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/dynamic_provisioning_test.go -->
# sources/control-plane/csi-driver-smb/test/e2e/dynamic_provisioning_test.go

Purpose: Ginkgo e2e suite for SMB CSI dynamic provisioning behavior across Linux and Windows clusters.

Important APIs/tests: The suite creates a privileged Kubernetes e2e framework namespace, checks driver pod restarts before each test, initializes `SMBDriver`, and runs many testsuites: restart-driver volume creation (currently skipped), command/write-read dynamic volume, collocated pods, read-only volume, delete pod and remount, reclaim policy delete/retain, multiple volumes, subpath, clone, retain/archive on delete policies, resize, and CSI inline volumes with copied secrets.

Control flow: Each `ginkgo.It` constructs `testsuites.PodDetails`, `VolumeDetails`, storage class parameters, expected pod commands, and then calls the relevant testsuite `Run`. Windows handling is explicit through `convertToPowershellCommandIfNecessary`, `isWindowsCluster`, `winServerVer`, and skip helpers. Inline volume tests copy an SMB secret into the test namespace and clean it up with defer.

State and persistence behavior: Creates real Kubernetes StorageClasses, PVCs, PVs, pods/deployments, secrets, SMB backing directories/shares, and may restart the driver daemonset in the skipped test. Cleanup is delegated to testsuites.

Dependencies and integration points: Depends on the Kubernetes e2e framework, Ginkgo v2, pod security admission labels, package-level suite globals from `suite_test.go`, SMB driver object builders, and many test suite helpers.

Risks: Tests require a fully configured cluster, SMB server/secret environment, and OS-specific command behavior. Some test names include `[Windows]` even when they may skip Windows or run with Windows conversions. External issue-linked scenarios encode regression intent and can be environment-sensitive.

Test signals: This is the high-level integration signal that dynamic provisioning, mounting, reclaim policies, subdir handling, cloning, expansion, and inline volumes work end to end.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/dynamic_provisioning_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/containerd-windows.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/containerd-windows.json

Purpose: ACS Engine/vlabs template for Windows e2e clusters using containerd.

Important configuration: Kubernetes orchestrator release is parameterized/blank, `kubernetesConfig` sets `containerRuntime: containerd`, disables managed identity, and supplies a Windows containerd binary URL. One Windows agent pool uses `Standard_D4s_v3`, 128 GB OS disk, AvailabilitySet, and Windows OS type. Windows profile enables CSI proxy v1.1.1, SSH, and selects `2019-datacenter-core-ctrd-2104` image metadata.

Control flow: Consumed declaratively by cluster creation tooling; placeholders for SSH key and service principal are blank.

State and persistence behavior: Creates Azure infrastructure when used by the e2e environment.

Dependencies and integration points: Integrates with Windows CSI proxy, ACS Engine vlabs schema, Azure credentials, and Windows containerd artifacts.

Risks: Hardcoded image versions and binary URLs can age out. The placeholder admin password is unsuitable for production and must be replaced/handled by test tooling.

Test signals: Supports Windows containerd e2e lanes that exercise CSI proxy and HostProcess-related paths.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/containerd-windows.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/external.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/external.json

Purpose: ACS Engine/vlabs Linux cluster template for an "external" e2e environment variant.

Important configuration: Kubernetes 1.22, Azure network plugin, containerd runtime, cloud controller manager, rate limits, `DelegateFSGroupToCSIDriver=true`, admission plugins including `AlwaysPullImages`, and disabled in-tree Azure disk/file CSI addons. One Linux agent pool uses `Standard_DS2_v2`; SSH key, client ID, and secret are placeholders.

Control flow: Declarative template consumed by cluster provisioning.

State and persistence behavior: Creates Azure cluster resources when used.

Dependencies and integration points: Supports e2e tests that depend on external driver deployment rather than built-in Azure CSI addons.

Risks: Kubernetes 1.22 and template schema may be old relative to current Azure support. Placeholders must be substituted correctly.

Test signals: Provides infrastructure for Linux e2e lanes with external CSI driver behavior and FSGroup delegation.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/external.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux-vmss.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/linux-vmss.json

Purpose: ACS Engine/vlabs Linux VMSS cluster template for e2e runs.

Important configuration: Kubernetes 1.22, containerd, Azure network plugin, cloud controller manager, disabled Azure disk/file CSI addons, rate limits, `DelegateFSGroupToCSIDriver=true`, and admission plugins including `AlwaysPullImages`. The agent pool uses VMSS availability and `Standard_DS2_v2`.

Control flow: Declarative provisioning input with placeholders for DNS prefix, SSH key, client ID, and secret.

State and persistence behavior: Creates Azure VMSS-based Kubernetes resources when applied.

Dependencies and integration points: Intended for Linux e2e lanes, especially features needing FSGroup delegation coverage.

Risks: Version and distro defaults may become stale. Missing managed identity means service principal placeholders must be valid.

Test signals: Infrastructure signal for Linux VMSS e2e coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux-vmss.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/linux.json

Purpose: ACS Engine/vlabs Linux cluster template for older/default Linux e2e runs.

Important configuration: Kubernetes 1.17, managed identity, cloud controller manager, Azure network plugin, containerd, cloud-provider rate limits, disabled Azure disk/file CSI addons, one VMSS Ubuntu 18.04 agent pool, and placeholders for DNS prefix, SSH key, client ID, and secret.

Control flow: Declarative template consumed by provisioning scripts.

State and persistence behavior: Creates Azure Linux Kubernetes infrastructure when used.

Dependencies and integration points: Supports compatibility e2e runs on older Kubernetes/containerd/Ubuntu combinations.

Risks: Kubernetes 1.17 and Ubuntu 18.04 are old and may no longer be supported in modern Azure environments. Placeholder substitution is required.

Test signals: Legacy Linux e2e infrastructure coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/linux.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/windows.json -->
# sources/control-plane/csi-driver-smb/test/e2e/manifest/windows.json

Purpose: ACS Engine/vlabs template for Windows e2e clusters using the default Windows runtime path.

Important configuration: Kubernetes orchestrator release is blank/parameterized. One Windows agent pool uses `Standard_D2s_v3`, 128 GB OS disk, AvailabilitySet, and Windows OS. Windows profile enables CSI proxy v1.0.2, SSH, and selects AKS Windows Server 2019 core image metadata. Linux master profile and service principal placeholders are included.

Control flow: Declarative cluster provisioning input.

State and persistence behavior: Creates Azure Windows Kubernetes infrastructure when used.

Dependencies and integration points: Supports Windows e2e tests that exercise CSI proxy SMB mount/unmount and Windows path behavior.

Risks: Hardcoded CSI proxy and Windows image versions may be stale. The embedded example password must be replaced by secure provisioning.

Test signals: Infrastructure support for Windows e2e lanes.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/test/e2e/manifest/windows.json -->
