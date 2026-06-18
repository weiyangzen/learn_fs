# subset-b-000097 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_linux.go -->
# sources/cloud-native/cri-o/server/server_linux.go

## Purpose
Linux-only server support for CRI-O startup behavior that depends on kernel facilities: seccomp notifier restoration/watch handling and Go runtime thread-limit tuning.

## Important APIs, Types, And Functions
`(*Server).startSeccompNotifierWatcher(ctx)` initializes `s.seccompNotifierChan`, reconciles the configured seccomp notifier directory, restores live notifiers for still-running containers, and starts the watcher goroutine. `configureMaxThreads()` reads `/proc/sys/kernel/threads-max`, sets Go's max thread threshold to 90 percent of that value with `debug.SetMaxThreads`, and logs the result.

## Control Flow
Startup stats the notifier path. If it is an existing directory, it walks files, removes stale listener files, maps each filename to a container short ID, skips missing or non-running containers, recreates seccomp notifiers, and stores them in `s.seccompNotifiers`. If the path is absent or invalid, it removes and recreates the directory with mode `0700`. The goroutine then receives seccomp notifications, looks up the notifier by container ID, records syscalls, optionally arms an expiry callback that marks container state as seccomp-killed and stops the container, and increments the seccomp notifier metric.

## State And Persistence
Uses the filesystem notifier directory as restart state. Live notifier instances are persisted only in `s.seccompNotifiers`; container state is mutated on notifier expiry. The goroutine is long-lived and reads from an unbuffered channel.

## Dependencies And Integration Points
Depends on CRI-O seccomp notifier internals, OCI runtime state constants, server container lookup and stop paths, CRI-O metrics, logging, and Linux `/proc`.

## Risks And Test Signals
The watcher loop does not select on `ctx.Done()`, so shutdown relies on broader server teardown. It removes listener files before attempting restoration, which is intentional cleanup but risky if restoration fails. The log call for `os.RemoveAll` uses `logrus.Error` with formatting text, so the wrapped error may not render as intended. Coverage is indirect through Linux server startup and seccomp notifier integration tests; this file has no direct unit test in the subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_test.go -->
# sources/cloud-native/cri-o/server/server_test.go

## Purpose
Ginkgo/Gomega tests for high-level `server.New`, exit monitoring, shutdown, and stream server stopping behavior.

## Important APIs, Types, And Functions
Defines the `Server` spec under the shared `t.Describe` wrapper. Exercises `server.New`, `StartExitMonitor`, `Shutdown`, and `StopStreamServer` through mocks from the suite fixture.

## Control Flow
Each test resets the common mock/config fixture. Successful `New` cases cover default config, UID/GID mappings, TLS stream configuration, container restoration from storage metadata, valid stream idle timeout, and disabled hostport mapping. Failure cases pass nil config, invalid directory paths, malformed UID/GID mappings, invalid stream address/port, invalid TLS certificate paths, and invalid idle timeout. Runtime behavior tests start the exit monitor goroutine and signal its close channel, verify shutdown calls storage shutdown and creates the clean shutdown file, and stop the stream server.

## State And Persistence
Creates temp graph roots and test directories through the shared suite, writes the clean shutdown marker during `Shutdown`, and relies on mocked storage metadata for restoration state.

## Dependencies And Integration Points
Uses GoMock expectations for config/storage/CNI, `go.podman.io/storage` containers, CRI-O config, and the server package.

## Risks And Test Signals
Strong signal for constructor error handling and restoration sequencing. It does not validate the internal restored container contents, stream data paths, or seccomp watcher behavior. The duplicated "valid config path" test is equivalent to the default success case.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_test_inject.go -->
# sources/cloud-native/cri-o/server/server_test_inject.go

## Purpose
Test-only injection helper compiled with the `test` build tag.

## Important APIs, Types, And Functions
`(*StreamService).SetRuntimeServer(server *Server)` assigns the private `runtimeServer` field so tests can wire a streaming service without going through production construction paths.

## Control Flow
No branching; the setter directly mutates the `StreamService`.

## State And Persistence
Process-local test state only. It does not persist data.

## Dependencies And Integration Points
Used by `server/suite_test.go` when constructing a `k8s.io/cri-streaming` server backed by the CRI-O stream service.

## Risks And Test Signals
Because this bypasses encapsulation, it must remain test-build-only. A signature or field-name drift in `StreamService` will break tests at compile time.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_test_inject.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_unsupported.go -->
# sources/cloud-native/cri-o/server/server_unsupported.go

## Purpose
Non-Linux fallback for seccomp notifier startup.

## Important APIs, Types, And Functions
`(*Server).startSeccompNotifierWatcher(ctx)` returns nil on builds where the `!linux` tag is selected.

## Control Flow
No operation. The context is accepted only to keep the method signature shared across platforms.

## State And Persistence
No state changes and no persistence.

## Dependencies And Integration Points
Allows the server package to compile on non-Linux targets while Linux behavior lives in `server_linux.go`.

## Risks And Test Signals
Feature absence is silent. Tests on non-Linux should assert that seccomp-notifier-dependent features are gated elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/server_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/suite_test.go -->
# sources/cloud-native/cri-o/server/suite_test.go

## Purpose
Shared Ginkgo suite fixture for server package tests.

## Important APIs, Types, And Functions
Defines `TestServer`, package-level mocks and fixtures, `beforeEach`, `afterEach`, `setupSUT`, `mockNewServer`, `addContainerAndSandbox`, `mockDirs`, `createDummyState`, `createDummyConfig`, and `mockRuntimeInLibConfig`.

## Control Flow
`BeforeSuite` creates a `TestFramework` and an empty temp directory. `beforeEach` lowers logging, constructs GoMock controllers and mocks, builds a synthetic OCI manifest, initializes default CRI-O config with test paths, disables hostport mapping, creates a test sandbox/container, and initializes a streaming server. `setupSUT` calls `mockNewServer`, constructs the server, then injects storage image/runtime mocks. Cleanup removes transient files and finishes the mock controller.

## State And Persistence
Uses temp directories for graphroot, CRI-O paths, seccomp notifier path, NRI socket path, and suite scratch space. Writes optional `state.json` and `config.json` helper files in the package working directory.

## Dependencies And Integration Points
Ties together CRI-O config, sandbox and OCI container builders, memorystore, CRI streaming server, CNI mock, storage mock, runtime mock, and the common test framework.

## Risks And Test Signals
This file is foundational for many server tests; fixture drift can create misleading failures across unrelated specs. The stream service is initialized with `sut` before `sut` is assigned, then tests rely on later injection paths. The fixture gives strong constructor and storage-restoration signal but is not an integration replacement for real CRI-O daemon behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/update_runtime_config.go -->
# sources/cloud-native/cri-o/server/update_runtime_config.go

## Purpose
Implements the CRI `UpdateRuntimeConfig` RPC stub.

## Important APIs, Types, And Functions
`(*Server).UpdateRuntimeConfig(ctx, req)` returns an empty `types.UpdateRuntimeConfigResponse` and nil error.

## Control Flow
No request inspection or side effects.

## State And Persistence
No state changes, persistence, or config mutation.

## Dependencies And Integration Points
Provides the runtime service API method required by Kubernetes CRI. The implementation currently acts as compatibility plumbing.

## Risks And Test Signals
Callers may assume runtime configuration was applied even though the method is a no-op. There is no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/update_runtime_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/suite_test.go -->
# sources/cloud-native/cri-o/server/useragent/suite_test.go

## Purpose
Shared Ginkgo suite fixture for user-agent package tests.

## Important APIs, Types, And Functions
Defines `TestUseragent`, the package-global `t *TestFramework`, and suite setup/teardown hooks.

## Control Flow
Registers the Gomega fail handler, runs framework specs, initializes `TestFramework` before the suite, and tears it down afterward.

## State And Persistence
Only in-memory suite state; no persistent files are written by this fixture.

## Dependencies And Integration Points
Uses Ginkgo/Gomega and CRI-O's `test/framework` wrapper.

## Risks And Test Signals
Minimal harness code. Failures here usually indicate framework or test-runner issues rather than useragent logic bugs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/useragent.go -->
# sources/cloud-native/cri-o/server/useragent/useragent.go

## Purpose
Builds the HTTP User-Agent string CRI-O uses to identify itself.

## Important APIs, Types, And Functions
`Get()` calls `internal/version.Get(false)`, normalizes the CRI-O version to the simplest `X.Y.Z` semver substring when present, and delegates formatting to `AppendVersions`. `versionRegex` captures the first three-component version string.

## Control Flow
Version lookup errors are wrapped. The generated User-Agent includes `cri-o`, `go`, `os`, and `arch` product/version tokens.

## State And Persistence
No persistence. Reads process build/runtime metadata via CRI-O version helpers and Go runtime constants.

## Dependencies And Integration Points
Used by outbound HTTP clients or registries that need CRI-O identity headers. Integrates with `version_info.go`.

## Risks And Test Signals
Regex normalization drops build suffixes and pre-release metadata, which is intentional for header compatibility but loses detail. Tests assert the returned string contains expected product tokens, not exact version formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/useragent.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/useragent_test.go -->
# sources/cloud-native/cri-o/server/useragent/useragent_test.go

## Purpose
Tests the high-level `useragent.Get` function.

## Important APIs, Types, And Functions
Ginkgo spec under `Useragent/Get` calls `useragent.Get()`.

## Control Flow
The test asserts no error and verifies the result contains `cri-o`, `os`, and `arch`.

## State And Persistence
Read-only test; no filesystem state.

## Dependencies And Integration Points
Depends on live build/version metadata through `internal/version.Get(false)`.

## Risks And Test Signals
Good smoke signal for basic User-Agent assembly. It does not assert Go version presence, token order, semver normalization, or invalid token filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/useragent_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/version_info.go -->
# sources/cloud-native/cri-o/server/useragent/version_info.go

## Purpose
Utility for formatting validated product/version tokens into a User-Agent header suffix.

## Important APIs, Types, And Functions
`VersionInfo` stores `Name` and `Version`. `(*VersionInfo).isValid()` rejects spaces, tabs, carriage returns, newlines, and `/` in either field. `AppendVersions(base string, versions ...VersionInfo)` appends valid `name/version` tokens to an optional base string.

## Control Flow
With no versions, returns `base` unchanged. With versions, initializes an output slice with base when non-empty, skips invalid entries, and joins tokens with spaces.

## State And Persistence
Pure string transformation; no state or persistence.

## Dependencies And Integration Points
Used by `useragent.Get` and can be reused by other CRI-O HTTP clients needing RFC-friendly product tokens.

## Risks And Test Signals
Validation is intentionally narrow and does not reject empty name/version strings, non-ASCII, or other HTTP token separators. Tests cover base append behavior and newline invalidation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/version_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/version_info_test.go -->
# sources/cloud-native/cri-o/server/useragent/version_info_test.go

## Purpose
Tests `AppendVersions` formatting and invalid-entry skipping.

## Important APIs, Types, And Functions
Ginkgo specs call `useragent.AppendVersions` with normal entries, no entries, invalid name, and invalid version.

## Control Flow
Asserts exact output for `base name/0.1.0 another/0.2.0`, empty result for empty base/no versions, and empty result when newline-containing entries are skipped.

## State And Persistence
Pure unit tests with no persistence.

## Dependencies And Integration Points
Validates the lower-level formatter used by `useragent.Get`.

## Risks And Test Signals
Does not test slash, tab, carriage return, spaces, empty fields, or mixed valid and invalid entries.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/useragent/version_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/utils.go -->
# sources/cloud-native/cri-o/server/utils.go

## Purpose
Shared server helpers for label validation, environment merging, image decryption keys, mount source resolution, context-error detection, resource wait behavior, annotation filtering, and stop timeout derivation.

## Important APIs, Types, And Functions
`validateLabels`, `mergeEnvs`, `getDecryptionKeys`, `getSourceMount`, `isContextError`, `(*Server).getResourceOrWait`, `(*Server).FilterDisallowedAnnotations`, and `stopTimeoutFromContext`. Constants define `maxLabelSize` and `defaultStopTimeout`.

## Control Flow
Label validation caps combined key/value length. Environment merging prioritizes kube-provided envs and appends image envs whose keys were not set by Kubernetes. Decryption key loading walks a directory, rejects symlinks, base64-encodes key files, sorts keys through ocicrypt, and initializes a decrypt config. Mount source lookup chooses the longest mountpoint prefix. Resource waiting first checks a cache, then waits on a resource watcher, context cancellation, or a defensive timeout, returning an error that asks kubelet to retry. Annotation filtering merges runtime-allowed and workload-allowed annotations before filtering.

## State And Persistence
Reads key files and mount metadata supplied by callers. `getResourceOrWait` observes server resourceStore state and emits a stalled-stage metric. `FilterDisallowedAnnotations` mutates `toFilter` by removing disallowed entries.

## Dependencies And Integration Points
Uses OCI image spec envs, CRI key/value types, ocicrypt config utilities, containers/storage mount info, CRI-O workload/runtime config, resourceStore, log tracing, and metrics.

## Risks And Test Signals
`getSourceMount` uses a raw string prefix, so mountpoint boundary handling depends on caller input. `stopTimeoutFromContext` can produce zero or negative seconds for expired deadlines. Resource waiting intentionally withholds a ready resource after waiting to avoid kubelet response leaks. Tests cover env merge, key loading, and mount source selection; other helpers rely on integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/utils_test.go -->
# sources/cloud-native/cri-o/server/utils_test.go

## Purpose
Unit tests for selected server utility helpers.

## Important APIs, Types, And Functions
`TestMergeEnvs`, `TestGetDecryptionKeys`, and `TestGetSourceMount`.

## Control Flow
`TestMergeEnvs` covers Kubernetes override precedence, nil image or kube env inputs, empty kube keys, invalid image env strings, and empty values. `TestGetDecryptionKeys` generates an RSA key, writes it to a temp directory, and calls `getDecryptionKeys`. `TestGetSourceMount` validates longest-prefix mountpoint selection and expected errors.

## State And Persistence
Creates temp key files and in-memory mount info. No persistent repository state.

## Dependencies And Integration Points
Uses Go testing, crypto/x509 key material, OCI image spec, CRI types, and containers/storage mount info.

## Risks And Test Signals
Env test compares as a set, so order regressions may be missed even though container env order can matter. Decryption-key assertion condition appears weak because it fails only if both `err != nil` and `cc != nil`. Symlink rejection and missing-directory behavior are not covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/version.go -->
# sources/cloud-native/cri-o/server/version.go

## Purpose
Implements the CRI `Version` RPC.

## Important APIs, Types, And Functions
Constants `kubeAPIVersion = "0.1.0"` and `containerName = "cri-o"`. `(*Server).Version(ctx, req)` returns a `types.VersionResponse`.

## Control Flow
Looks up build/runtime version information via `internal/version.Get(false)`, wraps lookup errors, and returns Kubernetes API version, runtime name, CRI-O runtime version, and runtime API version `v1`.

## State And Persistence
Read-only. It reads version metadata but does not mutate server state.

## Dependencies And Integration Points
Directly serves kubelet CRI version negotiation and `crictl version` style calls.

## Risks And Test Signals
The Kubernetes API version constant is intentionally legacy per the comment. Test coverage asserts non-empty fields and exact runtime API version.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/server/version_test.go -->
# sources/cloud-native/cri-o/server/version_test.go

## Purpose
Tests the server CRI `Version` method.

## Important APIs, Types, And Functions
Ginkgo spec calls `sut.Version(context.Background(), nil)` using the shared server fixture.

## Control Flow
Setup constructs the mocked server, then the test verifies no error, non-nil response, non-empty CRI version and runtime name, and runtime API version equal to `v1`.

## State And Persistence
Uses temporary server fixture state only.

## Dependencies And Integration Points
Exercises `version.go` through the real server object but mocked storage/config dependencies.

## Risks And Test Signals
Does not assert exact `RuntimeVersion`, `Version`, or `RuntimeName` values. The duplicate runtime-name assertion likely meant to check runtime-version.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/server/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/checkcriu/checkcriu.go -->
# sources/cloud-native/cri-o/test/checkcriu/checkcriu.go

## Purpose
Tiny integration-test helper binary that verifies CRIU support for pod checkpoint/restore tests.

## Important APIs, Types, And Functions
`main()` calls `criu.CheckForCriu(criu.PodCriuVersion)` from `github.com/checkpoint-restore/go-criu/v8/utils`.

## Control Flow
If the check returns an error, `main` panics; otherwise the process exits successfully.

## State And Persistence
No persistence. Reads/probes host CRIU availability through the go-criu utility.

## Dependencies And Integration Points
Called from `test/helpers.bash` `has_criu` to skip or enable CRIU-dependent BATS tests.

## Risks And Test Signals
Panic output is acceptable for a test helper but not user-friendly. Behavior depends on host CRIU install and version.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/checkcriu/checkcriu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/checkseccomp/checkseccomp.go -->
# sources/cloud-native/cri-o/test/checkseccomp/checkseccomp.go

## Purpose
Host capability probe for seccomp support used by tests.

## Important APIs, Types, And Functions
`main()` uses `unix.Prctl` with `PR_GET_SECCOMP` and `PR_SET_SECCOMP`/`SECCOMP_MODE_FILTER`.

## Control Flow
The helper first checks whether `PR_GET_SECCOMP` avoids `EINVAL`, then checks whether attempting filter mode fails with `EINVAL`. If both kernel capabilities appear present, exits 0; otherwise exits 1.

## State And Persistence
No persistence. The `PR_SET_SECCOMP` call is passed a nil filter pointer and is used as a capability probe.

## Dependencies And Integration Points
Referenced by integration helpers as `CHECKSECCOMP_BINARY`.

## Risks And Test Signals
Seccomp probing is kernel and permission sensitive. The code intentionally treats `EINVAL` as lack of support; other errors can still lead to success depending on the first check.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/checkseccomp/checkseccomp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/cni_plugin_helper.bash -->
# sources/cloud-native/cri-o/test/cni_plugin_helper.bash

## Purpose
CNI bridge wrapper used by integration tests to validate CRI-O CNI argument passing, health/status behavior, and malformed-result handling.

## Important APIs, Types, And Functions
Handles CNI `VERSION` and `STATUS`, parses `CNI_ARGS`, writes observed arguments to `$TEST_DIR/plugin_test_args.out`, sources `$TEST_DIR/cni_plugin_helper_input.env`, invokes `/opt/cni/bin/bridge`, and optionally emits malformed JSON when `DEBUG_ARGS=malformed-result`.

## Control Flow
For `VERSION`, prints supported CNI versions and exits. For `STATUS`, returns failure when a sentinel file exists. For normal commands, it validates required CNI/Kubernetes variables, records them, consumes a one-shot env file, runs the real bridge plugin, propagates failures, and either forwards or corrupts the result.

## State And Persistence
Writes `plugin_test_args.out` and removes `cni_plugin_helper_input.env`. Reads a test-specific status sentinel and env file.

## Dependencies And Integration Points
Installed into isolated CNI bin directories by `helpers.bash` with `%TEST_DIR%` replaced. Depends on the real bridge plugin at `/opt/cni/bin/bridge`.

## Risks And Test Signals
The wrapper is path-sensitive and assumes bridge lives at `/opt/cni/bin/bridge`, even though tests copy CNI binaries elsewhere. It includes an unusual non-printing character after the STATUS block in the current source, which could affect shell parsing on strict tooling.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/cni_plugin_helper.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/common.sh -->
# sources/cloud-native/cri-o/test/common.sh

## Purpose
Common environment and image-preload helpers for CRI-O integration tests.

## Important APIs, Types, And Functions
Defines repository/test paths, binary locations, runtime and CNI defaults, security profile paths, image list, `img2dir`, `get_img`, and `get_images`.

## Control Flow
On source, computes `INTEGRATION_ROOT`, `CRIO_ROOT`, tool paths, defaults for runtime/storage/network/security config, and image CIDRs. `get_img` maps an image to an artifact directory and uses `copyimg` to import from a registry into a directory cache if absent. `get_images` preloads every image in `IMAGES`.

## State And Persistence
Persists cached image directories under `.artifacts` by default. Exports many variables consumed by BATS tests and `helpers.bash`.

## Dependencies And Integration Points
Integrates with `copyimg`, CRI-O binaries, crictl, conmon, CNI plugins, AppArmor, seccomp, CRIU, and testdata policies.

## Risks And Test Signals
The script assumes many host binaries and kernel features. Image caching reduces flakes but can hide stale image artifacts. Since it is sourced globally, variable mistakes affect every integration test.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/copyimg/copyimg.go -->
# sources/cloud-native/cri-o/test/copyimg/copyimg.go

## Purpose
Small CLI utility for integration tests to copy container images between transports and CRI-O storage.

## Important APIs, Types, And Functions
`main()` builds a `urfave/cli/v2` app with flags for debug logging, storage root/runroot/driver/options, signature policy, image name, additional name, import source, and export target. It uses `copy.Image`, containers/image signatures, storage transport, and containers/storage.

## Control Flow
After reexec handling, the CLI validates root/runroot pairing when storage image operations are requested, opens a store, configures the storage transport, parses image references, loads signature policy, creates a policy context, and then imports, tags, exports, or directly copies image references depending on supplied flags.

## State And Persistence
May create or mutate a containers/storage graphroot/runroot, add image names, and write exported image data to target transports/directories. Cleans up store and policy contexts on exit.

## Dependencies And Integration Points
Used by `common.sh` and `helpers.bash` to pre-cache and import images into per-test CRI-O storage. Integrates with `go.podman.io/image/v5` and `go.podman.io/storage`.

## Risks And Test Signals
Uses `log.Fatalf` inside the CLI action, which exits the process rather than returning errors. Flag combinations with only import or only export and no image-name are accepted but do nothing. Correct behavior is exercised by integration tests that rely on image setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/copyimg/copyimg.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/default.yaml -->
# sources/cloud-native/cri-o/test/default.yaml

## Purpose
Minimal YAML test configuration enabling sigstore attachments for default docker policy behavior.

## Important APIs, Types, And Functions
Defines `default-docker.use-sigstore-attachments: true`.

## Control Flow
Static data file; no executable flow.

## State And Persistence
No runtime state. It is configuration input for tests or image policy code.

## Dependencies And Integration Points
Likely consumed by containers/image or CRI-O registry config tests that need a default docker transport setting.

## Risks And Test Signals
Only two lines, so syntax drift is the main risk. No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/default.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/docs-validation/main.go -->
# sources/cloud-native/cri-o/test/docs-validation/main.go

## Purpose
Documentation validation tool ensuring CRI-O config TOML tags, generated config template defaults, CLI flags, and manpage docs stay synchronized.

## Important APIs, Types, And Functions
Defines `entry`, `validateTags`, `validateCli`, `openFile`, `stringInSlice`, `allEntries`, `recursiveEntries`, and exclusion/mapping tables for tags and CLI options.

## Control Flow
`main` loads default config, validates TOML tags against `cfg.WriteTemplate(true)` and `docs/crio.conf.5.md`, then validates CLI flags in `internal/criocli/criocli.go` against `docs/crio.8.md`. Reflection recursively walks config structs, follows pointers/interfaces, avoids recursive private data with a seen map, extracts TOML tags, and computes default-value strings for supported types unless value validation is excluded.

## State And Persistence
Read-only against source/docs files. Exits 1 if validation fails.

## Dependencies And Integration Points
Integrates with `pkg/config.DefaultConfig`, config template generation, CLI implementation, and docs. Uses reflection heavily.

## Risks And Test Signals
Regex matching can be brittle around formatting changes and special regex characters in values. Pointer/interface recursion must avoid nil and inaccessible values. This is itself a test/CI signal for documentation drift rather than application runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/docs-validation/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/framework/framework.go -->
# sources/cloud-native/cri-o/test/framework/framework.go

## Purpose
Small shared test framework wrapper for CRI-O Go tests.

## Important APIs, Types, And Functions
`TestFramework`, `NewTestFramework`, `NilFunc`, `Setup`, `Teardown`, `Describe`, `MustTempDir`, `MustTempFile`, `EnsureRuntimeDeps`, and `RunFrameworkSpecs`.

## Control Flow
Setup/teardown call injected callbacks and clean registered temp dirs/files. Temp helpers create OS temp paths and track them. `EnsureRuntimeDeps` creates fake `crun`, `conmon`, and `nsenter` executables in a temp dir and sets `PATH` for the test. `Describe` prefixes Ginkgo descriptions with `cri-o:`.

## State And Persistence
Creates temp files/directories and removes them at teardown. Mutates the test process environment via `GinkgoTB().Setenv`.

## Dependencies And Integration Points
Used by server and useragent tests. Depends on Ginkgo/Gomega and Go's testing package.

## Risks And Test Signals
`MustTempFile` returns a path but leaves the file handle open until garbage collection because it does not close the `*os.File`. The fake runtime dependencies are intentionally minimal and may not satisfy tests expecting real runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/framework/framework.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/helpers.bash -->
# sources/cloud-native/cri-o/test/helpers.bash

## Purpose
Primary BATS integration-test harness for launching isolated CRI-O instances, managing images, network config, runtime helpers, cleanup, feature skips, and common assertions.

## Important APIs, Types, And Functions
Key functions include `setup_test`, `crio`, `crictl`, `runtime`, `retry`, `wait_until_reachable`, `copyimg`, `setup_img`, `setup_crio`, `check_images`, `start_crio_no_setup`, `start_crio`, `cleanup_*`, `stop_crio`, `restart_crio`, `cleanup_test`, `prepare_network_conf`, `pod_ip`, `ping_pod`, `wait_for_log`, `replace_config`, runtime/workload config creators, cgroup helpers, `has_criu`, `prepare_cni_plugin`, `contains`, and `annotations_equal`.

## Control Flow
`setup_test` creates a per-test root, config/log/socket directories, NRI config, isolated CNI plugin directory, crictl config, and SELinux labeling when needed. `setup_crio` preloads images, writes default/custom CRI-O config, removes `nodev` mount options, and writes a default CNI conflist. `start_crio` launches CRI-O and verifies image availability. Cleanup tears down containers, pods, CRI-O, networks, mounts, temp directories, and optional kata processes; failure mode can preserve test artifacts. Helper functions gate tests on kernel, crictl, SELinux, AppArmor, CRIU, Buildah, cgroup version, runtime type, and CPU/memory topology.

## State And Persistence
Creates extensive per-test filesystem state under `$TESTDIR`, including CRI-O storage, runroot, config, logs, CNI configs, hooks, sockets, and crictl config. Also uses `.artifacts` image caches from `common.sh` and may touch system cgroups, AppArmor profiles, pinned namespaces, and journal logs.

## Dependencies And Integration Points
Integrates BATS, CRI-O, crictl, conmon, runtime binaries, CNI plugins, jq, Python, netstat, systemd, AppArmor/SELinux, CRIU, buildah, pinns, copyimg, and host kernel interfaces.

## Risks And Test Signals
This is high-blast-radius test infrastructure. Shell globals are heavily shared, so ordering and sourcing matter. Cleanup assumes mount paths under `$TESTDIR` and may fail if commands hang or require privileges. `wait_for_log` uses polling and regex extraction, making timing/log format flakes possible. Despite risk, it is the strongest integration signal for real CRI-O lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/helpers.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/hooks/checkhook.json -->
# sources/cloud-native/cri-o/test/hooks/checkhook.json

## Purpose
OCI hook definition used by integration tests to verify hook execution.

## Important APIs, Types, And Functions
JSON fields define `cmd` regex `.*`, `hook` path `HOOKSDIR/checkhook.sh`, and stage `prestart`.

## Control Flow
Static hook config. CRI-O/hook processing expands or replaces placeholder paths in tests and executes the hook at prestart for matching commands.

## State And Persistence
No state itself. When used, it causes the hook script to append to `HOOKSCHECK`.

## Dependencies And Integration Points
Paired with `checkhook.sh` and `helpers.bash` hook directory setup.

## Risks And Test Signals
Placeholder substitution must be correct or the hook path is invalid. Broad `cmd` matching makes the hook apply to all tested containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/hooks/checkhook.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/hooks/checkhook.sh -->
# sources/cloud-native/cri-o/test/hooks/checkhook.sh

## Purpose
Simple hook script that records hook invocation arguments and stdin.

## Important APIs, Types, And Functions
Shell script appends `$@` to `HOOKSCHECK`, reads one line from stdin, and appends that line too.

## Control Flow
Linear: echo args, read stdin, echo stdin.

## State And Persistence
Appends to the hook check file referenced by the `HOOKSCHECK` placeholder/environment used in tests.

## Dependencies And Integration Points
Executed through the OCI hooks mechanism configured by `checkhook.json`.

## Risks And Test Signals
The script assumes `HOOKSCHECK` is substituted or available. It reads only one stdin line, so multiline hook state is not captured.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/hooks/checkhook.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/cmdrunner/cmdrunner.go -->
# sources/cloud-native/cri-o/test/mocks/cmdrunner/cmdrunner.go

## Purpose
Generated GoMock implementation of `utils/cmdrunner.CommandRunner`.

## Important APIs, Types, And Functions
`MockCommandRunner`, recorder type, `NewMockCommandRunner`, `EXPECT`, and mocked methods `CombinedOutput`, `Command`, and `CommandContext`.

## Control Flow
Each mock method calls `m.ctrl.Call`; each recorder method calls `RecordCallWithMethodType`, preserving variadic arguments.

## State And Persistence
No persistence. Holds GoMock controller and expected call state in memory.

## Dependencies And Integration Points
Used by tests that need deterministic command execution behavior without invoking host commands.

## Risks And Test Signals
Generated file should not be hand-edited. Interface drift requires regeneration or compile failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/cmdrunner/cmdrunner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/config/cgmgr/cgmgr.go -->
# sources/cloud-native/cri-o/test/mocks/config/cgmgr/cgmgr.go

## Purpose
Generated GoMock implementation of CRI-O `CgroupManager`.

## Important APIs, Types, And Functions
`MockCgroupManager` and recorder methods cover container/sandbox cgroup path resolution, cgroup manager creation, stats retrieval, create/remove, conmon movement, systemd detection, and manager naming.

## Control Flow
All methods delegate to GoMock call recording and typed return extraction.

## State And Persistence
Mock expectations are in memory only. It does not touch cgroup filesystems.

## Dependencies And Integration Points
Supports tests for resource updates, stats, sandbox/container lifecycle, and conmon cgroup placement. Imports CRI-O stats, opencontainers cgroups, and OCI specs.

## Risks And Test Signals
Because it bypasses real cgroup behavior, it verifies call contracts but not kernel/systemd semantics. Regenerate when the interface changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/config/cgmgr/cgmgr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/containereventserver/containereventserver.go -->
# sources/cloud-native/cri-o/test/mocks/containereventserver/containereventserver.go

## Purpose
Generated GoMock for the CRI streaming server interface `RuntimeService_GetContainerEventsServer`.

## Important APIs, Types, And Functions
Generic `MockRuntimeService_GetContainerEventsServer[Res]` with methods `Context`, `RecvMsg`, `Send`, `SendHeader`, `SendMsg`, `SetHeader`, and `SetTrailer`.

## Control Flow
Delegates all gRPC server-stream operations to GoMock.

## State And Persistence
In-memory expectations only.

## Dependencies And Integration Points
Used by container event stream tests to verify `ContainerEventResponse` sending and gRPC metadata behavior.

## Risks And Test Signals
Mocks gRPC stream contracts but not real network backpressure or client cancellation beyond whatever context is provided by tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/containereventserver/containereventserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/containers/image/v5/types.go -->
# sources/cloud-native/cri-o/test/mocks/containers/image/v5/types.go

## Purpose
Generated GoMock for `go.podman.io/image/v5/types.ImageCloser`.

## Important APIs, Types, And Functions
`MockImageCloser` covers lifecycle, config/manifest/blob metadata, layer info, inspect, signatures, size, encryption support, references, and updated-image helpers.

## Control Flow
Each method delegates to GoMock and extracts typed return values.

## State And Persistence
No image persistence; state is held in expectations.

## Dependencies And Integration Points
Supports CRI-O image-related unit tests without opening real image sources. Imports OCI image spec, Docker reference, and containers/image types.

## Risks And Test Signals
Validates interactions with image objects but not actual manifest parsing, blob reads, or close semantics. Must be regenerated on upstream interface changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/containers/image/v5/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/containerstorage/containerstorage.go -->
# sources/cloud-native/cri-o/test/mocks/containerstorage/containerstorage.go

## Purpose
Generated GoMock implementation of `go.podman.io/storage.Store`.

## Important APIs, Types, And Functions
`MockStore` exposes the full storage store surface used by tests: image/container/layer creation, deletion, lookup, metadata, big data, directories, graph status/options, mount/unmount, diff/apply, staged layers, names, sizes, maps, shutdown, wipe, check/repair, and listing helpers.

## Control Flow
Every storage operation is mocked through `m.ctrl.Call`; recorder methods register expected calls with exact method type and arguments.

## State And Persistence
No real storage mutation. The mock represents storage state only through configured expectations and return values.

## Dependencies And Integration Points
Core test dependency for server constructor, image, runtime, and storage lifecycle tests. Imports containers/storage, graphdriver, archive, digest, idtools, and GoMock.

## Risks And Test Signals
This file is large because the upstream `Store` interface is broad. It gives precise call-order and argument signal, but cannot validate actual graphroot behavior, mount leaks, driver semantics, or on-disk metadata compatibility. Any upstream interface drift requires regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/containerstorage/containerstorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/criostorage/criostorage.go -->
# sources/cloud-native/cri-o/test/mocks/criostorage/criostorage.go

## Purpose
Generated GoMock implementations for CRI-O internal storage interfaces.

## Important APIs, Types, And Functions
Defines `MockImageServer`, `MockRuntimeServer`, and `MockStorageTransport`. Image server methods cover pull/list/status/delete/untag/pinned-images/name resolution. Runtime server methods cover pod/container creation, start/stop/delete, metadata, and work/run directories. Storage transport mocks `ResolveReference`.

## Control Flow
Standard GoMock delegation and recorder setup for each interface method.

## State And Persistence
No real storage persistence. Expectations model storage behavior in memory.

## Dependencies And Integration Points
Used widely by server tests to isolate CRI-O runtime service behavior from containers/storage and containers/image.

## Risks And Test Signals
Good for asserting CRI-O calls the storage layer correctly, but not for validating image policy, transport behavior, or storage durability. Regeneration needed on interface change.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/criostorage/criostorage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/lib/lib.go -->
# sources/cloud-native/cri-o/test/mocks/lib/lib.go

## Purpose
Generated GoMock for `pkg/config.Iface`.

## Important APIs, Types, And Functions
`MockIface` provides `GetData()` and `GetStore()` mock methods plus recorder helpers.

## Control Flow
Methods delegate to GoMock and return configured config/store values.

## State And Persistence
No persistence. It supplies test-controlled config and storage handles.

## Dependencies And Integration Points
The server constructor tests use this as the main dependency injection point for CRI-O config and storage store access.

## Risks And Test Signals
Very small interface mock; failures usually mean constructor call-order or config access changed.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/lib/lib.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/oci/oci.go -->
# sources/cloud-native/cri-o/test/mocks/oci/oci.go

## Purpose
Generated GoMock for CRI-O internal OCI `RuntimeImpl`.

## Important APIs, Types, And Functions
`MockRuntimeImpl` covers attach, exec, execsync, create/start/stop/delete, pause/unpause, checkpoint/restore, stats, port-forward, log reopen, monitor probe, streaming URL setup, status updates, and resource updates.

## Control Flow
Each runtime operation is a GoMock call with typed returns. Streaming and attach/exec methods include reader/writer and terminal-size channel parameters.

## State And Persistence
No real OCI runtime state. Expectations represent lifecycle outcomes.

## Dependencies And Integration Points
Used by server tests that need to isolate CRI-O logic from runc/crun/conmon. Imports CRI-O OCI containers, stats, OCI specs, CRI API, and CRI streaming remotecommand.

## Risks And Test Signals
Verifies server-to-runtime contracts but not runtime process behavior, conmon interaction, cgroup updates, or IO streaming correctness. Regenerate on `RuntimeImpl` changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/oci/oci.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/ociartifact/datastore/datastore.go -->
# sources/cloud-native/cri-o/test/mocks/ociartifact/datastore/datastore.go

## Purpose
Generated GoMock for OCI artifact datastore implementation.

## Important APIs, Types, And Functions
`MockImpl` covers image-name candidate resolution, image source creation/closing, docker/layout reference creation, blob reads, manifest layer info, normalized name parsing, and `io.ReadAll`.

## Control Flow
All datastore operations delegate to GoMock expectations.

## State And Persistence
No actual artifact or blob persistence.

## Dependencies And Integration Points
Supports tests for CRI-O OCI artifact fetching, especially seccomp/profile artifact paths. Imports containers/image references, manifests, image sources, and GoMock.

## Risks And Test Signals
Does not validate registry, layout, blob cache, or manifest behavior. It only verifies caller interactions and returned data handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/ociartifact/datastore/datastore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/ociartifact/ociartifact.go -->
# sources/cloud-native/cri-o/test/mocks/ociartifact/ociartifact.go

## Purpose
Generated GoMocks for OCI artifact helpers and libartifact store access.

## Important APIs, Types, And Functions
`MockImpl` covers manifest instance selection and manifest retrieval. `MockLibartifactStore` covers inspect, list, pull, remove, and system context.

## Control Flow
Each method records or satisfies GoMock expectations with typed return values.

## State And Persistence
No real artifact storage. In-memory mock state only.

## Dependencies And Integration Points
Used by tests around OCI artifact pulling/listing/removal and seccomp artifact integration. Imports digest, libimage, libartifact, manifest, and containers/image types.

## Risks And Test Signals
Cannot validate real artifact store persistence or registry semantics. Interface drift requires regeneration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/ociartifact/ociartifact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/ocicni/types.go -->
# sources/cloud-native/cri-o/test/mocks/ocicni/types.go

## Purpose
Generated GoMock for `github.com/cri-o/ocicni/pkg/ocicni.CNIPlugin`.

## Important APIs, Types, And Functions
`MockCNIPlugin` mocks GC, default network name, pod network status, setup/teardown with and without context, plugin name, status, and shutdown.

## Control Flow
Each CNI operation delegates to GoMock expectations and returns configured network results or errors.

## State And Persistence
No real CNI state, network namespace changes, or IPAM persistence.

## Dependencies And Integration Points
Used by server tests for startup status checks, CNI garbage collection, sandbox networking, and cleanup behavior.

## Risks And Test Signals
Mocks call contracts only; actual CNI plugin config parsing, bridge setup, IPAM, and namespace cleanup require integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/ocicni/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/seccompociartifact/seccompociartifact.go -->
# sources/cloud-native/cri-o/test/mocks/seccompociartifact/seccompociartifact.go

## Purpose
Generated GoMock for seccomp OCI artifact pulling implementation.

## Important APIs, Types, And Functions
`MockImpl` provides `PullData(ctx, ref, *datastore.PullOptions)` returning artifact data.

## Control Flow
Single mocked method delegates to GoMock.

## State And Persistence
No real network or artifact persistence.

## Dependencies And Integration Points
Used by tests for seccomp profile loading from OCI artifacts. Depends on CRI-O datastore artifact data types.

## Risks And Test Signals
Only verifies call behavior and returned artifact data handling; does not test registry auth, digest selection, or profile parsing.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/seccompociartifact/seccompociartifact.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/systemd/systemd.go -->
# sources/cloud-native/cri-o/test/mocks/systemd/systemd.go

## Purpose
Generated GoMock for CRI-O watchdog systemd interface.

## Important APIs, Types, And Functions
`MockSystemd` mocks `Notify(state string)` and `WatchdogEnabled()`.

## Control Flow
Methods delegate to GoMock and return configured notification status, duration, or errors.

## State And Persistence
No real systemd notification socket interaction.

## Dependencies And Integration Points
Used by watchdog tests to isolate systemd behavior.

## Risks And Test Signals
Validates watchdog code paths at the interface boundary, but not actual `sd_notify` behavior or systemd environment handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/mocks/systemd/systemd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/nri_suite_test.go -->
# sources/cloud-native/cri-o/test/nri/nri_suite_test.go

## Purpose
Suite harness and helper methods for CRI-O NRI integration tests.

## Important APIs, Types, And Functions
Defines global `crio *runtime`, `setup`, `cleanup`, `TestMain`, `setupLogging`, `testLogger`, `nriTest`, `(*nriTest).Setup`, `StartPlugins`, `Cleanup`, lifecycle helpers, `execShellScript`, and ID verification helpers.

## Control Flow
`TestMain` parses flags, skips runtime setup for `go test -list`, redirects logrus to test output, connects to CRI-O when sockets are provided, pulls images, runs tests, then disconnects. Each `nriTest` allocates a namespace, purges leftover pods/containers, creates configured test plugins, starts them, waits for synchronization when requested, and registers cleanup.

## State And Persistence
Uses live CRI-O runtime state through sockets, creates/removes pods and containers in unique namespaces, and manages in-process plugin instances.

## Dependencies And Integration Points
Integrates with the local NRI plugin implementation, containerd NRI API, runtime helpers from other NRI test files, logrus, and testify/require.

## Risks And Test Signals
Requires a running CRI-O test instance with NRI enabled. Cleanup is defensive but depends on CRI-O responsiveness. Strong integration signal for NRI event flow and runtime lifecycle.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/nri_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/nri_test.go -->
# sources/cloud-native/cri-o/test/nri/nri_test.go

## Purpose
NRI integration tests for plugin registration, synchronization, pod/container events, and container adjustment/update features.

## Important APIs, Types, And Functions
Tests include `TestPluginRegistration`, `TestPluginSynchronization`, `TestPodEvents`, `TestContainerEvents`, `TestMountInjection`, `TestEnvironmentInjection`, `TestAnnotationInjection`, `TestDeviceInjection`, `TestCpusetAdjustment`, `TestMemsetAdjustment`, `TestCpusetAdjustmentUpdate`, and `TestMemsetAdjustmentUpdate`. Helpers include `testXxxsetAdjustment`, `testXxxsetAdjustmentUpdate`, `skipTestForCondition`, and thread-safe `idgen`.

## Control Flow
Tests skip when CRI-O/NRI socket prerequisites are absent. Registration verifies configure/synchronize event stream. Synchronization starts containers before plugin startup and verifies synced pod/container IDs. Event tests create, start, stop, and remove pods/containers while matching plugin events. Injection tests install create handlers that add mounts, env, annotations, devices, cpuset/memset values, or container updates, then verify behavior from inside containers or plugin state.

## State And Persistence
Creates live pods/containers and temp directories. Mount injection writes a file from inside the container to a host temp dir. ID generator state is process-local and protected by a mutex.

## Dependencies And Integration Points
Depends on containerd NRI API adjustment/update types, runtime helpers, filesystem helper functions, CPU/memory topology helpers, and the test plugin in `plugin.go`.

## Risks And Test Signals
Timing-sensitive with 3 to 5 second event timeouts and host topology dependencies. Strong signal for CRI-O's NRI implementation and adjustment propagation, but failures can be environmental.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/nri_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/plugin.go -->
# sources/cloud-native/cri-o/test/nri/plugin.go

## Purpose
In-process NRI test plugin used by integration tests to observe events and inject container adjustments/updates.

## Important APIs, Types, And Functions
Defines `PluginOption`, `plugin`, `event`, option constructors (`WithStubOptions`, `WithTestNamespace`, `WithCreateHandler`, `WithPostCreateHandler`, `WithStopHandler`, `WithUpdateHandler`), `NewPlugin`, lifecycle methods `Start`/`Stop`, NRI callbacks, event pump/read helpers, event matching, and event factory functions.

## Control Flow
`Start` builds a containerd NRI stub with plugin name/index/socket and close callback, starts an event pump goroutine, then starts the stub. NRI callbacks filter by namespace, update in-memory pod/container maps, call optional handler hooks, emit events, and return requested adjustments or updates. `pumpEvents` buffers writes from callbacks to avoid blocking readers. Tests poll, wait, or verify ordered streams against expected event descriptors.

## State And Persistence
Maintains in-memory maps of synchronized/running pods and containers, channels for event write/read, a done channel, and a `sync.Once` stop guard. No persistent files.

## Dependencies And Integration Points
Implements containerd NRI stub callback surface and is driven by CRI-O's NRI socket. Used directly by `nri_suite_test.go` and `nri_test.go`.

## Risks And Test Signals
`Configure` returns event mask 0, relying on default/full callback behavior from the stub/runtime. `VerifyEventStream` ignores its `exact` argument and only waits for ordered expected matches, so extra events can pass. Event emission can block if `pumpEvents` has stopped while callbacks continue. It provides the core signal for NRI event ordering, namespace filtering, and adjustment propagation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/plugin.go -->
