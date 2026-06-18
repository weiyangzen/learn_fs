# subset-b-000065 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/release_upgrade_linux_test.go -->
# sources/cloud-native/containerd/integration/release_upgrade_linux_test.go

## Purpose

`release_upgrade_linux_test.go` is a Linux integration suite that verifies containerd can upgrade from the latest supported 1.7 and 2.0 release binaries to the current tree while preserving CRI pod, container, image, shim, logging, and metric behavior. It starts real previous-release `containerd` processes against temporary root/state/config directories, prepares workloads through CRI, gracefully stops the old daemon, starts the current daemon on the same state, and then exercises recovery and mutation paths.

## Important APIs, Types, and Functions

- `TestUpgrade` drives version matrix coverage for `1.7` and `2.0`.
- `runUpgradeTestCase` and `runUpgradeTestCaseWithExistingConfig` own process lifecycle, config installation, cleanup, and repeated current-release restarts between verification callbacks.
- `upgradeVerifyCaseFunc`, `beforeUpgradeHookFunc`, and `setupUpgradeVerifyCase` model per-scenario setup, pre-upgrade hooks, and post-upgrade assertions.
- Scenario setup functions include `shouldRecoverAllThePodsAfterUpgrade`, `execToExistingContainer`, `shouldManipulateContainersInPodAfterUpgrade`, `shouldRecoverExistingImages`, `shouldParseMetricDataCorrectly`, and `shouldAdjustShimVersionDuringRestarting`.
- `podTCtx` wraps sandbox ID/config/runtime service and exposes `createContainer`, `containerDataDir`, `shimPid`, `dataDir`, `imageVolumeDir`, and `stop`.
- `ctrdProc` wraps a child `containerd` process and exposes CRI clients, paths, readiness polling, signal, wait, and log dumping helpers.
- Shim helpers read `bootstrap.json` or `address`, build ttrpc task clients, and check shim process shutdown after pod deletion.

## Control Flow

Each subtest downloads a previous-release binary set, writes an old config, starts previous `containerd`, waits for CRI readiness, prepares test pods/images/containers, stops the old process with `SIGTERM`, optionally runs a hook such as killing a shim, writes current config if needed, and starts the current `containerd`. Verification callbacks are run in order, and the daemon is restarted between callbacks to catch delayed recovery problems. Cleanup stops/removes pods and terminates the current daemon.

The scenario callbacks cover ready, created, exited, stopped, and killed-shim states. They verify CRI listing/status, container IO recovery, `ExecSync`, shim protocol version mismatch handling, creating/stopping/removing containers in recovered pods, data directory cleanup, image persistence, and parsing memory metrics from shims created by older releases.

## State and Persistence Behavior

Persistent state lives under the temp `root`, `state`, and CRI `rootDir` paths reused across old/current daemon restarts. The test intentionally inspects sandbox/container metadata directories, image volume directories, shim bundle files, CRI status `Info["config"]`, logs, image references, and shim sockets. It also checks that removing containers and sandboxes deletes the expected CRI directories and that existing image IDs survive upgrade.

## Dependencies and Integration Points

The file integrates with real `containerd` binaries, CRI runtime/image services from `integration/remote`, Kubernetes CRI API types, containerd task v2/v3 shim APIs, ttrpc, runtime namespaces, release config files, `images` fixtures, and Linux signals/process management. It depends on helpers from the wider integration package for CRI config builders, container options, failpoints, and image names.

## Risks and Edge Cases

The test is expensive and environment-sensitive: it downloads GitHub release artifacts, starts real daemons, uses Linux shims and sockets, sleeps for log/metric readiness, and relies on signal ordering. The shim version mismatch path is subtle because current shims may produce v3 bootstrap metadata while recovering v2 tasks. Cleanup is deliberately defensive because failed upgrades can leave running pods, mounts, sockets, and state directories.

## Test Signals

This file is itself a high-value integration signal for upgrade compatibility. Failures point to CRI state migration, shim reconnection, image store persistence, container IO restore, metric decoding, process lifecycle, or cleanup regressions across containerd releases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/release_upgrade_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/release_upgrade_utils_linux_test.go -->
# sources/cloud-native/containerd/integration/release_upgrade_utils_linux_test.go

## Purpose

`release_upgrade_utils_linux_test.go` supplies Linux-only helper functions used by the release-upgrade tests to discover and download previous containerd release binaries.

## Important APIs, Types, and Functions

- `downloadPreviousLatestReleaseBinary` resolves the latest tag for a requested release line and downloads it.
- `downloadReleaseBinary` builds the GitHub release tarball URL for `linux-$GOARCH`, performs an HTTP GET, gzip-decodes the body, and unpacks it into the target directory with containerd archive apply logic.
- `previousReleaseVersion` lists remote tags matching `refs/tags/v<line>.*`, semver-sorts them, and returns the newest.
- `gitLsRemoteCtrdTags` shells out to `git ls-remote --tags --exit-code`, parses tag refs, and skips peeled `^{}` entries.

## Control Flow

Upgrade tests call `downloadPreviousLatestReleaseBinary`, which calls `previousReleaseVersion`, then `downloadReleaseBinary`. The tag query returns all matching release tags, the helper normalizes the `refs/tags/` prefix, semver-sorts, and downloads the selected tarball.

## State and Persistence Behavior

The helpers write unpacked release binaries into a caller-provided temporary directory. They do not cache downloads or persist global state.

## Dependencies and Integration Points

The file depends on GitHub releases, `git`, Go HTTP, gzip, runtime architecture detection, `golang.org/x/mod/semver`, and `github.com/containerd/containerd/v2/pkg/archive`. It is tightly coupled to containerd release asset naming.

## Risks and Edge Cases

Network failures, GitHub rate limits, missing tags, unsupported architectures, non-200 responses, corrupt gzip streams, and release asset naming changes will fail the upgrade suite before daemon behavior is tested. The HTTP call is intentionally marked with `nolint:gosec` because it fetches a fixed public release URL.

## Test Signals

These helpers are not separately tested; their signal comes from `TestUpgrade`, which fails if tag discovery, download, or unpacking breaks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/release_upgrade_utils_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/doc.go -->
# sources/cloud-native/containerd/integration/remote/doc.go

## Purpose

`doc.go` declares package `remote` and documents it as legacy-style CRI client adapters for containerd integration tests and stress tooling.

## Important APIs, Types, and Functions

The file exports no code symbols beyond the package-level documentation and `package remote`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The file has no state or persistence behavior.

## Dependencies and Integration Points

It integrates only through Go documentation and package compilation. The implementation surface lives in `remote_image.go` and `remote_runtime.go`.

## Risks and Edge Cases

The package comment is the primary overview for these adapters; if behavior changes in the implementation, this short description must remain accurate.

## Test Signals

Compilation and documentation tooling are the only direct signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/remote_image.go -->
# sources/cloud-native/containerd/integration/remote/remote_image.go

## Purpose

`remote_image.go` adapts the upstream Kubernetes CRI image client to the older method shapes used by containerd integration tests.

## Important APIs, Types, and Functions

- `ImageService` wraps `upstreamapi.ImageManagerService`.
- `NewImageService` creates a remote image client with an endpoint and connection timeout.
- `Close` closes the upstream service and tolerates a nil receiver.
- `ListImages`, `ImageStatus`, `PullImage`, `RemoveImage`, and `ImageFsInfo` bridge legacy calls to the current CRI client.
- `PullImage` clones `ImageSpec` when a runtime handler is supplied so it can populate `RuntimeHandler` without mutating the caller's original annotations map.

## Control Flow

Every method uses `context.Background()` and delegates directly to the upstream CRI client. Response-shaping methods unwrap nested response fields such as `ImageStatusResponse.Image` and `ImageFsInfoResponse.ImageFilesystems`.

## State and Persistence Behavior

The adapter owns only the upstream client handle. It does not cache image data or persist state; image persistence is handled by the CRI implementation under test.

## Dependencies and Integration Points

It depends on `k8s.io/cri-client`, CRI API/runtime types, `grpc.CallOption` compatibility, and Go `maps.Clone`. It is used heavily by integration tests that expect pre-upstream client method signatures.

## Risks and Edge Cases

Using `context.Background()` means callers cannot cancel individual operations through this wrapper. `PullImage` must clone annotations before injecting `RuntimeHandler` to avoid test cross-contamination. Nil `ImageSpec` is passed through unchanged, so upstream validation owns that error.

## Test Signals

There is no dedicated test for this file. It is indirectly covered by image pull/list/status/remove operations in upgrade, restart, truncindex, volume, and Windows integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/remote_image.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/remote_runtime.go -->
# sources/cloud-native/containerd/integration/remote/remote_runtime.go

## Purpose

`remote_runtime.go` adapts the upstream Kubernetes CRI runtime client to the legacy integration-test interface and keeps an additional raw gRPC client connection for streaming RPCs not exposed in the same shape by the upstream abstraction.

## Important APIs, Types, and Functions

- `RuntimeService` stores an upstream `RuntimeService`, raw `RuntimeServiceClient`, and raw `grpc.ClientConn`.
- `NewRuntimeService` creates both the upstream runtime service and raw connection, cleaning up on partial failure.
- `newRuntimeClientConn` resolves endpoint/dialer with CRI utilities, sets insecure credentials, authority, context dialer, and a 16 MiB max receive size.
- `clientTargetForAddress` prefixes Unix socket paths with `passthrough:///` so gRPC does not DNS-resolve socket paths.
- Methods wrap CRI operations: version, sandbox lifecycle/resources/status/list, container lifecycle/status/resources/stats/log reopen, exec/attach/port-forward, runtime config/status, and event streaming.
- `GetContainerEvents` calls the raw streaming client directly.

## Control Flow

Most wrapper methods call the upstream service with `context.Background()` and translate request/response shape where the legacy tests expect plain IDs or statuses. `Close` joins errors from closing both the upstream service and raw gRPC connection.

## State and Persistence Behavior

The adapter keeps connection state only. Runtime, sandbox, container, log, and stats state remains in the CRI server under test.

## Dependencies and Integration Points

The file integrates `k8s.io/cri-client`, CRI runtime API, gRPC, insecure credentials, and CRI endpoint dialer utilities. It is central to integration tests that need a stable client surface while Kubernetes CRI client APIs evolve.

## Risks and Edge Cases

Per-call `context.Background()` prevents test-level cancellation through most wrapper methods. Socket targets must use `passthrough:///`; otherwise gRPC treats paths as DNS names and Unix stream calls can fail. The wrapper must close both client layers to avoid leaking sockets.

## Test Signals

`remote_runtime_test.go` specifically covers Unix socket event streaming through `newRuntimeClientConn`. Most integration tests indirectly cover the remaining wrapper methods.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/remote_runtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/remote_runtime_test.go -->
# sources/cloud-native/containerd/integration/remote/remote_runtime_test.go

## Purpose

`remote_runtime_test.go` verifies that the raw CRI runtime gRPC connection can stream container events over Unix sockets on non-Windows platforms.

## Important APIs, Types, and Functions

- `fakeRuntimeService` embeds the unimplemented CRI runtime server and implements `GetContainerEvents`.
- `TestNewRuntimeClientConnGetContainerEventsUnix` creates a temporary Unix listener, registers a fake gRPC runtime server, dials it with `newRuntimeClientConn`, and receives a created-container event.

## Control Flow

The test starts a gRPC server on a Unix socket, creates a client connection using the adapter helper, opens a `GetContainerEvents` stream, receives the first event, and checks its type.

## State and Persistence Behavior

All state is ephemeral: a Unix socket path under `/tmp`, a listener, a gRPC server, and a client connection cleaned up by `t.Cleanup`.

## Dependencies and Integration Points

It depends on gRPC, CRI runtime API streaming types, Unix sockets, and the `newRuntimeClientConn` behavior in `remote_runtime.go`.

## Risks and Edge Cases

The test specifically protects the passthrough resolver behavior for socket paths. It is skipped on Windows by build tag because Unix sockets are required.

## Test Signals

This is the direct regression signal for CRI event streaming over Unix sockets in the integration remote adapter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/remote/remote_runtime_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/restart_linux_test.go -->
# sources/cloud-native/containerd/integration/restart_linux_test.go

## Purpose

`restart_linux_test.go` adds Linux restart scenarios around sandbox recovery and large sandbox reload counts.

## Important APIs, Types, and Functions

- `TestContainerdRestartSandboxRecover` verifies ready, stopped, and unknown/failpoint sandbox states after a daemon restart.
- `TestReload100Pods` starts a separate daemon, creates 100 host-network pods, restarts the daemon, and ensures it becomes ready with that state.

## Control Flow

The sandbox recovery test creates a ready sandbox, a stopped sandbox, and a sandbox whose shim `Create` is delayed while the daemon is restarted. After restart it lists sandboxes, validates expected states, and removes them. The reload test uses the release-upgrade process helper to run an isolated daemon, creates many pods through CRI, stops and restarts the process, and checks readiness.

## State and Persistence Behavior

Both tests depend on persisted CRI sandbox metadata and runtime state across daemon restarts. `TestReload100Pods` also checks that volatile runtime state under the daemon work directory can be removed at cleanup without leaks.

## Dependencies and Integration Points

The file uses failpoint annotations from `sandbox_run_rollback_test.go`, process helpers from `release_upgrade_linux_test.go`, CRI runtime helpers, Linux signals, and filesystem cleanup.

## Risks and Edge Cases

The unknown-state path races daemon shutdown against shim creation delay. The 100-pod reload case stresses startup/recovery scaling and cleanup of many sandbox entries. Both tests can expose mount/state leaks if cleanup is incomplete.

## Test Signals

Failures indicate regressions in sandbox recovery state classification, failpoint rollback, daemon restart readiness, or large-pod reload behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/restart_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/restart_test.go -->
# sources/cloud-native/containerd/integration/restart_test.go

## Purpose

`restart_test.go` is a cross-platform integration test for recovering CRI sandboxes, containers, and images after restarting containerd.

## Important APIs, Types, and Functions

- `TestContainerdRestart` defines local `sandbox` and `container` structs for expected names, IDs, and states.
- It uses CRI helpers for sandbox/container creation, `containerdClient` to kill a sandbox task directly, `RestartContainerd`, image service list/status, and `SandboxInfo`.

## Control Flow

The test starts a ready sandbox with created/running/exited containers and a not-ready sandbox whose sandbox container is killed. Non-Windows runs also keep a running per-container-PID-namespace container in the not-ready sandbox. It pulls images, snapshots image list state, restarts containerd, lists sandboxes/containers, validates IDs and states, checks ready-sandbox CNI/IP info, removes sandboxes, and compares image metadata before and after restart.

## State and Persistence Behavior

The test validates persisted sandbox/container states, CNI result/IP info, image metadata, and repo tag/digest fields across daemon restart. Direct task kill simulates a dead sandbox while preserving CRI metadata for recovery.

## Dependencies and Integration Points

It integrates CRI runtime/image services, containerd client task APIs, Kubernetes CRI types, image fixtures, OS-specific PID namespace behavior, and daemon restart helpers.

## Risks and Edge Cases

State matching is ID-based but loops do not explicitly fail when a specific ID is absent beyond aggregate counts, so diagnostic precision may be limited. Windows lacks the per-container PID namespace case. CNI and image metadata equality are sensitive to environment and ordering, so repo tags/digests are sorted before comparison.

## Test Signals

This is a core restart regression signal for CRI sandbox/container status restoration, CNI result persistence, and image store persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/restart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/runtime_handler_test.go -->
# sources/cloud-native/containerd/integration/runtime_handler_test.go

## Purpose

`runtime_handler_test.go` verifies that a sandbox created with the configured runtime handler reports that handler consistently through CRI status and list APIs.

## Important APIs, Types, and Functions

- `TestRuntimeHandler` creates a sandbox via `PodSandboxConfigWithCleanup`, then checks `PodSandboxStatus.RuntimeHandler` and `ListPodSandbox[0].RuntimeHandler`.

## Control Flow

The test logs whether the global `--runtime-handler` flag is empty or explicit, creates a sandbox, fetches status and list results, and asserts the returned runtime handler equals the requested flag value.

## State and Persistence Behavior

It relies on CRI sandbox metadata storing the runtime handler for subsequent status/list retrieval. Cleanup is handled by the sandbox helper.

## Dependencies and Integration Points

The test uses integration-wide `runtimeHandler` flag, CRI runtime service, and Kubernetes CRI filter/status types.

## Risks and Edge Cases

It assumes the newly created sandbox is the first entry in `ListPodSandbox`, so pre-existing sandboxes could make the list assertion fragile. The test covers reporting, not actual runtime implementation differences.

## Test Signals

Failure signals a regression in CRI runtime handler persistence or response population.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/runtime_handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/runtime_handler_unpack_labels_linux_test.go -->
# sources/cloud-native/containerd/integration/runtime_handler_unpack_labels_linux_test.go

## Purpose

`runtime_handler_unpack_labels_linux_test.go` verifies that creating a container with a runtime handler using a different snapshotter triggers unpack into that snapshotter and applies image-related snapshot labels.

## Important APIs, Types, and Functions

- `TestRuntimeHandlerUnpackWithSnapshotLabels` starts an isolated daemon with overlayfs as default and erofs as a second runtime snapshotter.
- It uses containerd introspection to check erofs plugin availability, CRI image pull, containerd image rootfs chain IDs, and erofs snapshot service `Stat`.

## Control Flow

The test writes a v3 config enabling snapshot annotations, starts a daemon, skips if erofs is absent/not ready, pulls nginx, computes chain IDs, creates an overlay sandbox, asserts erofs snapshots do not exist, creates an erofs sandbox/container, then asserts each erofs snapshot has target ref, manifest digest, layer digest, and image layer labels.

## State and Persistence Behavior

The important persisted state is snapshotter metadata and labels in the erofs snapshot service. The test also verifies CRI sandbox runtime handler state and container created state.

## Dependencies and Integration Points

It integrates CRI runtime/image services, containerd client image and snapshot APIs, plugin introspection, OCI image identity chain IDs, snapshotter label constants, and the erofs snapshotter plugin.

## Risks and Edge Cases

The test is skipped when erofs is not registered or fails plugin init. It assumes overlayfs image pull does not pre-unpack erofs snapshots and that snapshot labels are available when `disable_snapshot_annotations=false`.

## Test Signals

Failures indicate runtime-handler-specific unpack selection or snapshot annotation propagation regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/runtime_handler_unpack_labels_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_clean_remove_test.go -->
# sources/cloud-native/containerd/integration/sandbox_clean_remove_test.go

## Purpose

`sandbox_clean_remove_test.go` is a Linux integration suite for sandbox cleanup edge cases involving CNI IPAM checkpoints, closed network namespaces, and nil CNI results.

## Important APIs, Types, and Functions

- `TestSandboxRemoveWithoutIPLeakage` verifies host-local IP allocation remains while a dead sandbox is only stopped/not-ready and is released when the sandbox is removed.
- `TestSandboxStopWithNilCNIResult` verifies `StopPodSandbox` succeeds when CNI setup never completed and `CNIResult` is nil, even if CNI `Del` fails.

## Control Flow

The IP leakage test verifies host-local CNI config, runs a sandbox, extracts IP and network namespace from verbose sandbox info, checks `/var/lib/cni` checkpoint files, kills the sandbox process, unmounts/removes netns, waits for NOTREADY, stops/removes the sandbox, and asserts the IP checkpoint disappears. The nil-CNI test injects failpoints to delay CNI Add and fail Del, kills containerd during CNI Add, restarts, finds the leftover not-ready sandbox by label, confirms `CNIResult` is nil, and stops/removes it.

## State and Persistence Behavior

The tests inspect persisted CNI checkpoint files, sandbox verbose info, `NetNSClosed`, `CNIResult`, netns path, and CRI sandbox state across daemon restart.

## Dependencies and Integration Points

They depend on Linux CNI host-local IPAM, `SandboxInfo`, `KillPid`, `unix.Unmount`, failpoint helpers, process environment scanning, and CRI runtime service.

## Risks and Edge Cases

The first test skips unless host-local IPAM is configured. It walks `/var/lib/cni`, manipulates namespaces, and kills sandbox processes, so host permissions and cleanup are critical. The second test relies on failpoint CNI binary process detection through `CNI_ARGS`.

## Test Signals

Failures indicate IPAM leak regressions, incorrect netns-closed handling, or overly strict CNI teardown errors when setup never produced a CNI result.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_clean_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_clean_remove_windows_test.go -->
# sources/cloud-native/containerd/integration/sandbox_clean_remove_windows_test.go

## Purpose

`sandbox_clean_remove_windows_test.go` provides Windows equivalents for sandbox IP cleanup and a raw CRI create/start/stop/remove container smoke test.

## Important APIs, Types, and Functions

- `getTestImage` maps Windows build numbers to compatible nanoserver images.
- `TestSandboxRemoveWithoutIPLeakage` verifies azure-vnet IPAM allocation is released only after sandbox removal.
- Helper functions wrap raw CRI requests for stopping/removing pods and containers.
- `TestCreateContainer` creates a Windows process-isolated sandbox and container using raw gRPC CRI calls.

## Control Flow

The IP cleanup test checks CNI config for azure-vnet IPAM, runs a sandbox, extracts the IP and HNS namespace, reads `azure-vnet-ipam.json` to find the IP allocation, kills the sandbox process, deletes the HNS namespace with `hnsdiag.exe`, waits for NOTREADY, then stops/removes and confirms IP release. The container smoke test selects a compatible nanoserver image, creates a raw sandbox, pulls the image, creates a container with CPU shares and a long-running ping command, starts and stops it, and relies on cleanup callbacks.

## State and Persistence Behavior

The file inspects HNS network namespace state, `azure-vnet-ipam.json`, verbose sandbox info, and CRI object lifecycle state.

## Dependencies and Integration Points

It integrates Windows registry build detection, hcsshim OS version constants, `hnsdiag.exe`, raw CRI gRPC client helpers, Windows CNI/IPAM files, and containerd image fixtures.

## Risks and Edge Cases

It is highly host-specific: compatible images, azure-vnet IPAM config, HNS tooling, and Windows build number mapping must all line up. The JSON walker assumes a stable azure-vnet checkpoint schema.

## Test Signals

Failures signal Windows CNI IP leak regressions or basic CRI lifecycle breakage for Windows process containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_clean_remove_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_run_linux_test.go -->
# sources/cloud-native/containerd/integration/sandbox_run_linux_test.go

## Purpose

`sandbox_run_linux_test.go` contains a Linux regression test for sandbox controller behavior when sandbox removal has a shim `Delete` failpoint.

## Important APIs, Types, and Functions

- `TestPodSandboxController_ShouldBackoffExitEventWhenFail` injects a one-shot shim `Delete` error, runs a sandbox, stops it, and removes it.

## Control Flow

The test creates a pod sandbox config for the failpoint namespace, annotates the shim `Delete` method with `1*error(retry)`, starts the sandbox through the failpoint runtime handler, stops it, and removes it. Successful remove despite the injected delete error validates that the controller backs off or tolerates the transient failure path correctly.

## State and Persistence Behavior

It focuses on transient sandbox lifecycle state, failpoint annotations, and cleanup event ordering rather than long-lived persistence.

## Dependencies and Integration Points

It relies on the Linux sandbox controller, CRI runtime service, failpoint runtime handler, and common sandbox config helpers.

## Risks and Edge Cases

This is a narrow regression test. Its value depends on the failpoint shim honoring the one-shot `Delete` error and on controller cleanup logic preserving enough state to retry/remove successfully.

## Test Signals

Failure points to sandbox controller backoff, shim delete retry, or cleanup event ordering regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_run_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_run_rollback_test.go -->
# sources/cloud-native/containerd/integration/sandbox_run_rollback_test.go

## Purpose

`sandbox_run_rollback_test.go` is a Linux failpoint-driven suite for `RunPodSandbox` rollback behavior across CNI setup failures, shim start/delete failures, restart persistence, and slow CNI operations.

## Important APIs, Types, and Functions

- Constants define failpoint runtime handler, failpoint CNI binary, shim annotation prefix, and CNI failpoint config annotation.
- Tests include `TestRunPodSandboxWithSetupCNIFailure`, `TestRunPodSandboxWithShimStartFailure`, `TestRunPodSandboxWithShimDeleteFailure`, `TestRunPodSandboxWithShimStartAndTeardownCNIFailure`, and `TestRunPodSandboxAndTeardownCNISlow`.
- `sbserverSandboxInfo` extracts verbose sandbox info from raw CRI status.
- `ensureCNIAddRunning` scans failpoint CNI process environments for the target pod name.
- `failpointConf`, `injectCNIFailpoint`, and `injectShimFailpoint` configure failure/delay injection through annotations and temporary JSON files.

## Control Flow

The tests build sandbox configs with labels and failpoint annotations, call `RunPodSandbox`, assert expected errors, list leftover sandboxes, verify NOTREADY state and metadata, optionally restart containerd, and then cleanup through `RemovePodSandbox` or stop/remove. Slow CNI tests run sandbox creation in a goroutine, wait until CNI Add is active, kill containerd with `SIGKILL`, then validate persisted partial sandbox state.

## State and Persistence Behavior

The suite intentionally leaves partial sandbox records when rollback cannot complete, then verifies those records survive restarts and retain metadata, IP/network info, netns path, and NOTREADY state. CNI failpoint configs are written to temporary files referenced by annotations.

## Dependencies and Integration Points

It integrates CRI runtime service, raw CRI status, internal pod sandbox info types, containerd failpoint parser, Linux process/env inspection helpers, daemon restart helpers, and the failpoint CNI/shim implementations.

## Risks and Edge Cases

These tests exercise race-prone failure windows. `SIGKILL` is used to avoid graceful shutdown side effects, and CNI process detection may be noisy if stale failpoint binaries run. Rollback semantics deliberately preserve records when deletion/teardown cannot be trusted.

## Test Signals

Failures identify regressions in sandbox rollback, partial-state persistence, restart recovery of failed sandboxes, or failpoint annotation validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/sandbox_run_rollback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/shim_dial_unix_test.go -->
# sources/cloud-native/containerd/integration/shim_dial_unix_test.go

## Purpose

`shim_dial_unix_test.go` verifies that shim dialing fails fast on Unix socket errors during restart/recovery rather than waiting for a stale socket to reappear.

## Important APIs, Types, and Functions

- `TestFailFastWhenConnectShim` runs normal Unix socket coverage and Linux abstract socket coverage.
- `dialFunc` abstracts shim dialers.
- `testFailFastWhenConnectShim` sets up a temporary ttrpc server, validates successful dialing, shuts the listener down, and checks `ECONNREFUSED`/`ENOENT` handling.
- `newTestListener` constructs normal `unix://` or abstract-socket addresses and cleanup functions.

## Control Flow

The test starts a ttrpc server on a socket, retries dialing until the server is accepting, disables unlink-on-close for normal sockets, shuts down the server, waits for `ECONNREFUSED`, asserts the dialer returns quickly, removes the socket directory, and asserts abstract sockets still report refused while normal sockets report missing.

## State and Persistence Behavior

Only temporary socket paths and listeners are used. The test models stale shim socket state rather than persisting containerd metadata.

## Dependencies and Integration Points

It depends on containerd shim `AnonDialer`, ttrpc server/client behavior, Unix sockets, Linux abstract sockets, and syscall error matching.

## Risks and Edge Cases

Timing is central: the test uses retries and timeouts to separate slow dials from fail-fast behavior. Abstract socket address compatibility is tied to historic shim address file formats.

## Test Signals

Failures signal regressions in shim dialer error handling that could make task manager restart recovery hang on stale or absent shim sockets.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/shim_dial_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/truncindex_test.go -->
# sources/cloud-native/containerd/integration/truncindex_test.go

## Purpose

`truncindex_test.go` verifies that CRI APIs accept unambiguous truncated IDs for images, sandboxes, and containers.

## Important APIs, Types, and Functions

- `genTruncIndex` returns the leading half of an ID.
- `TestTruncIndex` exercises image status, sandbox status/port-forward/stop/remove, container create/status/start/stats/update/exec/execsync/stop/remove/status error paths using truncated identifiers.

## Control Flow

The test pulls busybox, queries image status by truncated image ID, runs a sandbox and addresses it by truncated ID, creates a container in that sandbox, then starts, stats, updates resources, executes commands, stops/removes, and verifies post-removal status/stat calls fail.

## State and Persistence Behavior

The test relies on CRI ID indexes resolving truncated IDs while objects exist and rejecting them after removal. It exercises live runtime state and cleanup callbacks.

## Dependencies and Integration Points

It uses CRI runtime/image services, image fixtures, OS-specific resource update structs, exec/port-forward paths, and common container config helpers.

## Risks and Edge Cases

It does not test ambiguous truncated IDs, which is noted in TODOs. Because it truncates to half length, it assumes the selected IDs remain unambiguous in the test environment.

## Test Signals

Failures reveal truncindex lookup regressions across CRI image, sandbox, container, stats, exec, and resource update APIs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/truncindex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/volume_copy_up_test.go -->
# sources/cloud-native/containerd/integration/volume_copy_up_test.go

## Purpose

`volume_copy_up_test.go` verifies image-defined volume copy-up behavior and ownership preservation on Linux and Windows.

## Important APIs, Types, and Functions

- Constants describe the expected Windows `ContainerUser` SID.
- `volumeFile` and `containerVolume` describe expected volume contents.
- `TestVolumeCopyUp` checks host bind volume mappings, copied files, in-container reads, and host-visible writes.
- `TestVolumeOwnership` checks in-container and host ownership of image-defined volumes.
- `getContainerBindVolumes` reads verbose CRI container status, unmarshals runtime spec mounts, and returns destination-to-source mappings.

## Control Flow

The copy-up test creates a sandbox and container from the volume-copy-up image, starts it, defines OS-specific expected volume paths/files, reads CRI verbose status to find host bind paths, checks copied contents both through host filesystem and `ExecSync`, writes new content from inside the container, and confirms the host path changes. The ownership test starts a second image, checks ownership inside the container, maps the host path, and calls OS-specific `getOwnership`.

## State and Persistence Behavior

The tests validate generated bind mount directories and runtime spec mount metadata. They also validate that writes through the container persist to the host volume path.

## Dependencies and Integration Points

They depend on CRI runtime service, raw verbose status, OCI runtime spec mount JSON, image fixtures, OS-specific ownership helpers, and exec sync.

## Risks and Edge Cases

Path formats differ sharply by OS, including odd Linux paths with colons and Windows drive roots. The test depends on fixture image contents and helper binaries such as Windows `get_owner.exe`.

## Test Signals

Failures point to regressions in image volume detection, copy-up, bind mount injection, runtime spec reporting, host/container write propagation, or ownership handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/volume_copy_up_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/volume_copy_up_unix_test.go -->
# sources/cloud-native/containerd/integration/volume_copy_up_unix_test.go

## Purpose

`volume_copy_up_unix_test.go` provides the non-Windows host ownership helper for the volume ownership integration test.

## Important APIs, Types, and Functions

- `getOwnership` runs `stat -c %u:%g '<path>'` through `sh -c` and returns the command output.

## Control Flow

The helper formats a shell command, executes it, returns combined output on success, and propagates errors.

## State and Persistence Behavior

It reads filesystem metadata for a host path and does not mutate state.

## Dependencies and Integration Points

It integrates with `TestVolumeOwnership` in `volume_copy_up_test.go` and depends on Unix `stat` and shell quoting behavior.

## Risks and Edge Cases

The path is interpolated into a shell single-quoted string, so paths containing single quotes would break quoting. Test-generated paths normally avoid that.

## Test Signals

The helper is indirectly tested by `TestVolumeOwnership` on non-Windows platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/volume_copy_up_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/volume_copy_up_windows_test.go -->
# sources/cloud-native/containerd/integration/volume_copy_up_windows_test.go

## Purpose

`volume_copy_up_windows_test.go` provides the Windows host ownership helper for the volume ownership integration test.

## Important APIs, Types, and Functions

- `getOwnership` calls `windows.GetNamedSecurityInfo` for file owner/DACL information and returns the owner SID string.

## Control Flow

The helper queries security info for the path, extracts the owner SID, and returns its string form.

## State and Persistence Behavior

It reads Windows filesystem security metadata and does not mutate state.

## Dependencies and Integration Points

It integrates with `TestVolumeOwnership` and depends on `golang.org/x/sys/windows` security APIs.

## Risks and Edge Cases

Errors can come from missing paths, permissions, or security descriptor lookup failures. It returns the SID rather than username because the username may be unknown on the host.

## Test Signals

The helper is indirectly covered by Windows volume ownership tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/volume_copy_up_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/windows_device_test.go -->
# sources/cloud-native/containerd/integration/windows_device_test.go

## Purpose

`windows_device_test.go` verifies Windows device-class injection by exposing host GPU/display driver store content inside a container.

## Important APIs, Types, and Functions

- `TestWindowsDevice` creates a sandbox with a log directory, requests device class `GUID_DEVINTERFACE_DISPLAY_ADAPTER`, runs a command that lists `HostDriverStore`, and checks the CRI log.

## Control Flow

The test creates a sandbox, pulls a test image, creates a container with command, log path, and `WithDevice("", "class/<GUID>", "")`, starts it, waits for exit, reads the container log, and asserts expected stdout content.

## State and Persistence Behavior

It inspects the container log file written under the pod log directory. The relevant runtime state is Windows device mount injection into the container filesystem.

## Dependencies and Integration Points

It depends on Windows CRI integration helpers, device option generation, log formatting helpers, and Windows host driver store behavior.

## Risks and Edge Cases

The test assumes the display adapter class is supported and mounts `HostDriverStore/FileRepository`. Host GPU/display configuration or image shell compatibility can affect the signal.

## Test Signals

Failure indicates Windows device class handling, HCS mount injection, container execution, or CRI log capture regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/windows_device_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/windows_hostprocess_test.go -->
# sources/cloud-native/containerd/integration/windows_hostprocess_test.go

## Purpose

`windows_hostprocess_test.go` verifies Windows HostProcess container behavior, allowed identities, host command execution, host networking, stats, and argument escaping.

## Important APIs, Types, and Functions

- `hpcAction` is a callback run after a HostProcess container starts.
- Global option variables define Local Service, Local System, HostProcess, and default pause command options.
- `TestWindowsHostProcess` runs subtests for accepted users, rejected Guest user, host command execution, host network environment, OS-version image mismatch tolerance, and stats.
- `runHostProcess` creates a HostProcess pod/container and applies the callback.
- `runExecAndRemoveContainer` creates, starts, execs `cmd /c echo hello`, stops, and removes a container.
- `TestArgsEscapedImagesOnWindows` checks images with ArgsEscaped metadata on supported builds, with and without explicit container command.

## Control Flow

HostProcess subtests pull pause image, create HostProcess pods, create containers with different options, start them, optionally expect start failure, then run checks such as stats polling. ArgsEscaped coverage detects host build, creates a sandbox, pulls the ArgsEscaped image, and runs exec/remove cycles for two container config variants.

## State and Persistence Behavior

The tests exercise Windows HostProcess runtime state, CRI stats, labels/annotations in stats validation, and container lifecycle cleanup. They do not inspect persistent files beyond normal CRI state.

## Dependencies and Integration Points

They integrate hcsshim OS version constants, Windows registry, CRI runtime service, image fixtures, HostProcess pod/container config helpers, stats helper `testStats`, and Windows command execution.

## Risks and Edge Cases

The file contains an unusual assignment `_, err = t, runtimeService.StartContainer(cn)` that discards `t` and captures the start error; it compiles but is easy to misread. HostProcess availability, Windows identity rules, OS build compatibility, and image availability are major environmental factors.

## Test Signals

Failures identify regressions in HostProcess validation/execution, Windows user handling, host network behavior, stats for HostProcess containers, or ArgsEscaped command handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/windows_hostprocess_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/windows_rootfs_size_test.go -->
# sources/cloud-native/containerd/integration/windows_rootfs_size_test.go

## Purpose

`windows_rootfs_size_test.go` verifies that a requested Windows container root filesystem size is reflected in the container's C: drive free-space output.

## Important APIs, Types, and Functions

- `TestWindowsRootfsSize` creates a container with `WindowsContainerResources.RootfsSizeInBytes` set to 200 GiB and parses `dir /-C C:\` output from the container log.

## Control Flow

The test creates a sandbox with log directory, pulls pause image, creates a container that runs `cmd /c dir /-C C:\` with a log path and rootfs size resource, waits for exit, reads the log, scans for the `bytes free` line, parses the available bytes, and checks it is within 300 MiB below the requested size.

## State and Persistence Behavior

It validates runtime-created virtual disk/rootfs sizing and CRI log output. No long-lived state is intended.

## Dependencies and Integration Points

It depends on Windows CRI runtime service, Windows resources in CRI API, container logs, and command output formatting.

## Risks and Edge Cases

The parser is tied to English `dir` output and exact token positions. Some space is expected to be occupied, so the assertion uses tolerance rather than exact equality.

## Test Signals

Failure points to Windows rootfs sizing, resource propagation, container execution, or log parsing regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/windows_rootfs_size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cleanup/context.go -->
# sources/cloud-native/containerd/internal/cleanup/context.go

## Purpose

`context.go` provides a small cleanup utility that runs cleanup callbacks with a context detached from caller cancellation but bounded by a timeout.

## Important APIs, Types, and Functions

- `Do(ctx context.Context, do func(context.Context))` wraps `context.WithoutCancel(ctx)` in a 10-second timeout, calls the callback, and then cancels the timeout context.

## Control Flow

`Do` creates the derived timeout context, invokes the callback synchronously, and calls `cancel` after the callback returns.

## State and Persistence Behavior

The function does not persist state. It preserves values from the parent context while clearing cancellation/deadline/error state and adding its own 10-second deadline.

## Dependencies and Integration Points

It depends only on Go `context` and `time`. It is intended for cleanup paths that should proceed even if request contexts are already canceled.

## Risks and Edge Cases

Because the callback is synchronous, a callback that ignores context cancellation can still block longer than 10 seconds; the timeout only signals through `ctx.Done()`.

## Test Signals

`context_test.go` verifies detached cancellation, value preservation, nested cancellation, and timeout behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cleanup/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cleanup/context_test.go -->
# sources/cloud-native/containerd/internal/cleanup/context_test.go

## Purpose

`context_test.go` validates the cleanup context wrapper behavior in `internal/cleanup`.

## Important APIs, Types, and Functions

- `TestDo` covers canceled parent context, context value preservation, nested cancellation, and timeout cancellation.
- `contextError` non-blockingly returns `ctx.Err()` when the context is done.

## Control Flow

The test creates a valued context, cancels it, then runs parallel subtests. One ensures `Do` clears parent cancellation while retaining values, one ensures a nested child cancel still works, and one waits for the 10-second timeout signal and verifies the callback ran.

## State and Persistence Behavior

Only in-memory context values, cancellation channels, and test channels are used.

## Dependencies and Integration Points

It uses Go testing, context, time, and testify assertions.

## Risks and Edge Cases

The timeout subtest takes about 10 seconds by design, so it contributes fixed latency. It assumes scheduler timing allows observing the timeout within an additional second.

## Test Signals

Failures show that cleanup contexts no longer detach from parent cancellation, preserve values, or enforce the intended timeout.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cleanup/context_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/annotations/annotations.go -->
# sources/cloud-native/containerd/internal/cri/annotations/annotations.go

## Purpose

`annotations.go` centralizes CRI-related OCI annotation keys and builds the default annotation spec options for sandbox and workload containers.

## Important APIs, Types, and Functions

- Constants include container type values, sandbox/container metadata keys, sandbox CPU/memory keys, sandbox log/image keys, untrusted workload, runtime handler fallback, and Windows HostProcess annotation.
- `DefaultCRIAnnotations` returns `oci.SpecOpts` that add sandbox ID, namespace, UID, name, container type, and either sandbox log/image annotations or container name/image annotations.

## Control Flow

`DefaultCRIAnnotations` starts with common sandbox metadata, selects `sandbox` or `container` type based on the boolean argument, appends sandbox-specific or container-specific annotations, and appends the final container type annotation.

## State and Persistence Behavior

The file does not persist state itself. Its constants become OCI spec annotations written into runtime specs and consumed by runtimes, shims, and integration tests.

## Dependencies and Integration Points

It depends on CRI runtime API types, containerd CRI spec option helpers, and OCI spec option plumbing. The constants integrate with Kata, kubelet/CRI metadata expectations, HostProcess handling, and runtime handler fallback compatibility.

## Risks and Edge Cases

Annotation key changes are compatibility-sensitive because external runtimes and tests may depend on exact names. The `RuntimeHandler` annotation is deprecated and should remain only as a fallback for older CRI clients until removal.

## Test Signals

No direct unit test appears in this subset. Coverage is indirect through CRI spec generation, sandbox/container lifecycle tests, HostProcess tests, and runtime-handler behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/annotations/annotations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/doc.go -->
# sources/cloud-native/containerd/internal/cri/bandwidth/doc.go

## Purpose

`doc.go` documents package `bandwidth` as utilities for CRI bandwidth shaping.

## Important APIs, Types, and Functions

There are no code symbols beyond the package declaration and package comment.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The file has no state or persistence behavior.

## Dependencies and Integration Points

It participates in Go package documentation for the bandwidth package implemented by the adjacent files.

## Risks and Edge Cases

The description is intentionally broad; implementation specifics such as Linux `tc` shaping live elsewhere.

## Test Signals

Compilation and documentation are the only direct signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/fake_shaper.go -->
# sources/cloud-native/containerd/internal/cri/bandwidth/fake_shaper.go

## Purpose

`fake_shaper.go` provides a minimal in-memory `Shaper` implementation for tests.

## Important APIs, Types, and Functions

- `FakeShaper` stores `CIDRs` and `ResetCIDRs`.
- `Limit`, `ReconcileInterface`, and `ReconcileCIDR` return `errdefs.ErrNotImplemented`.
- `Reset` appends the CIDR to `ResetCIDRs`.
- `GetCIDRs` returns the configured `CIDRs`.

## Control Flow

Methods either mutate simple slices, return stored data, or report not implemented.

## State and Persistence Behavior

State is in-memory on the struct instance. No OS shaping or persistence occurs.

## Dependencies and Integration Points

It depends on containerd `errdefs` and Kubernetes `resource.Quantity` to satisfy the `Shaper` interface. It is intended for unit tests of code that only needs reset/list behavior.

## Risks and Edge Cases

Most methods are deliberately unimplemented, so using it in code paths expecting actual shaping will fail. `GetCIDRs` returns the slice directly, so callers could mutate it.

## Test Signals

Coverage is indirect through tests that instantiate `FakeShaper` in the broader CRI bandwidth or cleanup code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/fake_shaper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/interfaces.go -->
# sources/cloud-native/containerd/internal/cri/bandwidth/interfaces.go

## Purpose

`interfaces.go` defines the abstraction for pod network bandwidth shaping.

## Important APIs, Types, and Functions

- `Shaper` declares `Limit`, `Reset`, `ReconcileInterface`, `ReconcileCIDR`, and `GetCIDRs`.
- `Limit` takes a CIDR plus egress and ingress quantities in bits per second.

## Control Flow

The file declares an interface only; concrete control flow is in Linux, unsupported, and fake implementations.

## State and Persistence Behavior

No state is stored here. Implementations own OS or in-memory state.

## Dependencies and Integration Points

It depends on Kubernetes `resource.Quantity`. CRI networking code can use this interface without directly depending on Linux `tc` or test fake implementations.

## Risks and Edge Cases

The contract permits overlapping CIDRs and aggregate limits, so implementations must avoid assuming unique IP-only matches. Unit tests should cover both ingress and egress semantics in concrete shapers.

## Test Signals

Compile-time satisfaction by `tcShaper`, `unsupportedShaper`, and `FakeShaper` is the main direct signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/interfaces.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/linux.go -->
# sources/cloud-native/containerd/internal/cri/bandwidth/linux.go

## Purpose

`linux.go` implements the `Shaper` interface with Linux `tc` hierarchical token bucket classes and u32 filters.

## Important APIs, Types, and Functions

- `tcShaper` stores an exec interface and network interface name.
- `NewTCShaper` constructs a `tcShaper`.
- `execAndLog` runs `tc` commands and logs command/output.
- `nextClassID` parses `tc class show` output to find an unused `1:<n>` class ID below 10000.
- `hexCIDR` and `asciiCIDR` convert CIDRs between text and `tc` filter hex representation.
- `findCIDRClass` parses `tc filter show` output to find class/handle pairs for a CIDR.
- `Limit` creates HTB classes and dst/src filters for download/upload limits.
- `ReconcileInterface`, `initializeInterface`, `deleteInterface`, `ReconcileCIDR`, `Reset`, and `GetCIDRs` maintain and inspect shaping state.

## Control Flow

Callers normally call `ReconcileInterface` to ensure root qdisc `1:` exists, then `ReconcileCIDR` or `Limit` for each pod CIDR. `Limit` allocates classes and adds filters for non-nil ingress/download and egress/upload quantities. `Reset` finds all classes/handles for a CIDR and deletes filters then classes. `GetCIDRs` scans filter match lines and decodes CIDR values.

## State and Persistence Behavior

State lives in kernel traffic-control qdisc/class/filter configuration on the target interface. The Go struct only stores the interface name and exec handle. Reconciliation reads OS state and repairs missing or unexpected qdisc configuration.

## Dependencies and Integration Points

It depends on the `tc` userspace command, Linux networking, containerd lazy regex helpers and logging, Kubernetes resource quantities/sets, and `k8s.io/utils/exec`. CRI networking code uses it for pod bandwidth annotations.

## Risks and Edge Cases

Parsing `tc` output is fragile across versions; regexes attempt to handle old and new filter output but unexpected formats return errors. `hexCIDR` uses `[]byte(ip)`, so IPv4 may encode as 16-byte mapped addresses depending on `net.ParseCIDR` behavior. Partial failures in `Limit` can leave classes without filters. `ReconcileInterface` assumes enough fields in qdisc output before deleting an unexpected qdisc.

## Test Signals

No direct tests appear in this subset. Behavior is typically covered by CRI networking integration or platform-specific tests that exercise bandwidth annotations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/unsupported.go -->
# sources/cloud-native/containerd/internal/cri/bandwidth/unsupported.go

## Purpose

`unsupported.go` provides the non-Linux `Shaper` implementation.

## Important APIs, Types, and Functions

- `unsupportedShaper` is the concrete non-Linux type.
- `NewTCShaper` returns an unsupported shaper.
- `Limit`, `ReconcileInterface`, and `ReconcileCIDR` return `errdefs.ErrNotImplemented`.
- `Reset` is a no-op success.
- `GetCIDRs` returns an empty slice.

## Control Flow

All methods are simple stubs, allowing non-Linux builds to compile while reporting unsupported operations where shaping would be required.

## State and Persistence Behavior

There is no shaping state and no persistence.

## Dependencies and Integration Points

It depends on build tag `!linux`, containerd `errdefs`, and Kubernetes resource quantities. It satisfies the same `Shaper` interface used by platform-neutral code.

## Risks and Edge Cases

Callers must tolerate `ErrNotImplemented` on non-Linux platforms. `Reset` returning nil can hide cleanup requests for limits that were never applied, which is reasonable for unsupported platforms but should be documented at call sites.

## Test Signals

Compile success on non-Linux platforms and any platform-specific CRI tests provide coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/utils.go -->
# sources/cloud-native/containerd/internal/cri/bandwidth/utils.go

## Purpose

`utils.go` parses Kubernetes pod bandwidth annotations into validated ingress and egress resource quantities.

## Important APIs, Types, and Functions

- `minRsrc` and `maxRsrc` bound acceptable bandwidth values to `1k` through `1P`.
- `validateBandwidthIsReasonable` rejects values below/above those bounds.
- `ExtractPodBandwidthResources` reads `kubernetes.io/ingress-bandwidth` and `kubernetes.io/egress-bandwidth` annotations and returns parsed `resource.Quantity` pointers.

## Control Flow

If annotations are nil, the function returns nil quantities. For each supported key present, it parses the quantity string, validates bounds, and stores a pointer to the parsed value. Any parse or validation error aborts the function.

## State and Persistence Behavior

No state is stored. Returned quantities are new local values escaped to heap through pointers.

## Dependencies and Integration Points

It depends on Kubernetes `resource.ParseQuantity` and the annotation keys used by Kubernetes network bandwidth policy conventions. Callers feed these quantities into `Shaper` implementations.

## Risks and Edge Cases

Quantities are checked via `.Value()`, so unit interpretation must match bits-per-second expectations. Unknown annotations are ignored. Extremely small or large valid Kubernetes quantities are rejected by policy.

## Test Signals

No direct test is in this subset. Expected coverage comes from CRI networking tests that parse pod annotations and apply shaping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/bandwidth/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config.go -->
# sources/cloud-native/containerd/internal/cri/config/config.go

## Purpose

`config.go` defines the main CRI image, runtime, CNI, registry, decryption, server, and containerd configuration model plus validation/default-selection helpers.

## Important APIs, Types, and Functions

- Data types include `Runtime`, `ContainerdConfig`, `CniConfig`, `Mirror`, `AuthConfig`, `Registry`, `RegistryConfig`, `ImageDecryption`, `ImagePlatform`, `ImageConfig`, `RuntimeConfig`, `X509KeyPairStreaming`, `Config`, and `ServerConfig`.
- Constants define sandbox controller modes, default pause image, IO modes, implicit runtime names, and key model names.
- `ValidateImageConfig` handles registry deprecations, `config_path` conflicts, auth migration to configs, and image pull timeout parsing.
- `CheckLocalImagePullConfigs` enables local image pull when configured options are incompatible with transfer service.
- `ValidateRuntimeConfig` validates default runtime, CNI bin dir conflicts/migration, runtime cgroup/device/sandboxer/io-type settings, timeout strings, unprivileged kernel support, and CDI deprecation.
- `ValidateServerConfig` validates stream idle timeout.
- `GetSandboxRuntime`, `untrustedWorkload`, and `hostAccessingSandbox` select runtimes and enforce untrusted workload restrictions.
- `GenerateRuntimeOptions` and `getRuntimeOptionsType` marshal generic runtime option maps into runc, runhcs, or generic runtime option structs.
- `DefaultServerConfig` returns CRI server defaults.

## Control Flow

Validation functions both check and normalize config. Runtime validation ensures a default runtime exists, migrates deprecated single CNI bin dir when possible, fills missing `Sandboxer` with `podsandbox`, defaults empty IO type to `fifo`, parses configured durations, and delegates platform-specific unprivileged validation. Image validation warns on deprecated registry fields and maps legacy `auths` into `configs`.

Runtime selection first handles the untrusted workload annotation, rejects explicit conflicting runtime handlers and host namespace access, falls back to default runtime when the handler is empty, and returns the configured runtime by name. Runtime option generation round-trips the map through TOML so typed shim option structs can be populated.

## State and Persistence Behavior

The file defines TOML/JSON-serializable configuration structures. Validation mutates config in memory by filling defaults and migrating deprecated fields; persistence is handled by containerd config loading outside this file.

## Dependencies and Integration Points

It integrates with CRI API types, containerd plugin runtime identifiers, runc/runhcs/runtime option protobuf structs, deprecation warnings, CRI annotations, OCI option helpers, TOML encoding, streaming defaults, and platform-specific defaults/validation files.

## Risks and Edge Cases

Because validation mutates input, callers and tests must compare post-validation state. Deprecated registry settings interact with transfer service fallback and config path conflicts. The IO type error says `named_pipe` even though the accepted constant is `fifo`, which may confuse users. Untrusted workload rules depend on Linux sandbox security context fields and must be kept compatible with Windows handling.

## Test Signals

`config_test.go`, `config_kernel_linux_test.go`, and `streaming_test.go` cover validation errors, warnings, mutation, host-access detection, local-pull fallback, kernel-gated unprivileged settings, and streaming TLS mode selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_kernel_linux.go -->
# sources/cloud-native/containerd/internal/cri/config/config_kernel_linux.go

## Purpose

`config_kernel_linux.go` validates Linux kernel support for unprivileged port and ICMP configuration.

## Important APIs, Types, and Functions

- `kernelGreaterEqualThan` is a package variable pointing to `kernel.GreaterEqualThan` for test replacement.
- `ValidateEnableUnprivileged` checks kernel version `>= 4.11` when either `EnableUnprivilegedICMP` or `EnableUnprivilegedPorts` is enabled.

## Control Flow

If neither setting is enabled, validation succeeds without probing the kernel. If either is enabled, it checks the current kernel version and returns a wrapped probe error or a clear minimum-version error when too old.

## State and Persistence Behavior

No persistent state is changed. The package-level function variable is mutable only to support tests.

## Dependencies and Integration Points

It depends on containerd kernel version utilities and is called from `ValidateRuntimeConfig`.

## Risks and Edge Cases

Kernel probing failures block config validation. Tests must restore `kernelGreaterEqualThan` after monkey-patching to avoid cross-test contamination.

## Test Signals

`config_kernel_linux_test.go` covers disabled settings, too-old kernels, and supported kernels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_kernel_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_kernel_linux_test.go -->
# sources/cloud-native/containerd/internal/cri/config/config_kernel_linux_test.go

## Purpose

`config_kernel_linux_test.go` unit-tests Linux unprivileged ICMP/port kernel validation.

## Important APIs, Types, and Functions

- `TestValidateEnableUnprivileged` patches `kernelGreaterEqualThan` and runs table-driven cases.

## Control Flow

The test saves the original function, restores it with cleanup, then verifies validation passes when settings are disabled, fails with the expected message on kernels below 4.11, and passes on kernels at/above the minimum.

## State and Persistence Behavior

It mutates a package-level function variable during each subtest and restores it after the test.

## Dependencies and Integration Points

It depends on Linux build, containerd kernel version type, and testify assertions. It validates behavior called by `ValidateRuntimeConfig`.

## Risks and Edge Cases

Subtests share a patched package variable; they are not parallelized, which avoids data races. The test does not cover kernel probe errors.

## Test Signals

Failure indicates broken kernel gating for CRI unprivileged port/ICMP defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_kernel_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_kernel_other.go -->
# sources/cloud-native/containerd/internal/cri/config/config_kernel_other.go

## Purpose

`config_kernel_other.go` provides non-Linux no-op validation for unprivileged port and ICMP settings.

## Important APIs, Types, and Functions

- `ValidateEnableUnprivileged` returns nil on non-Linux builds.

## Control Flow

The function ignores its context and runtime config and succeeds.

## State and Persistence Behavior

No state is read or written.

## Dependencies and Integration Points

It is selected by `!linux` build tag and keeps `ValidateRuntimeConfig` platform-neutral.

## Risks and Edge Cases

Non-Linux platforms do not enforce Linux kernel prerequisites. Any platform-specific equivalent validation would need a separate implementation.

## Test Signals

Compile success on non-Linux platforms is the primary signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_kernel_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_test.go -->
# sources/cloud-native/containerd/internal/cri/config/config_test.go

## Purpose

`config_test.go` unit-tests CRI config validation, mutation, warning emission, host-access detection, and local image pull fallback.

## Important APIs, Types, and Functions

- `TestValidateConfig` table-drives runtime, image, and server config validation cases.
- `TestHostAccessingSandbox` verifies which sandbox security contexts count as host access.
- `TestCheckLocalImagePullConfigs` verifies transfer-service-incompatible image config settings force `UseLocalImagePull`.

## Control Flow

The main table invokes only the validation functions relevant to each case, checks errors or mutated expected structs, collects warnings, and compares deprecation warning sets. Host-access tests feed nil, privileged, non-privileged, and host namespace configs. Local-pull tests mutate a default image config and call the checker.

## State and Persistence Behavior

Tests operate on in-memory config structs and assert intentional mutation such as CNI bin-dir migration, sandboxer defaulting, registry auth mapping, and `UseLocalImagePull` fallback.

## Dependencies and Integration Points

It depends on CRI runtime API types, deprecation warning values, cgroup mode helper, and platform-sensitive default image config behavior.

## Risks and Edge Cases

Expected outcomes can vary by cgroup mode and OS for cgroup writable and snapshot annotation fallback. Because validation mutates inputs, missing expected mutation coverage can hide behavioral drift.

## Test Signals

The file is the primary unit signal for config validation semantics and compatibility-preserving mutations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_unix.go -->
# sources/cloud-native/containerd/internal/cri/config/config_unix.go

## Purpose

`config_unix.go` defines non-Windows default CRI image and runtime configuration.

## Important APIs, Types, and Functions

- `defaultNetworkPluginBinDirs` returns `/opt/cni/bin`.
- `DefaultImageConfig` sets default snapshotter, disables snapshot annotations by default, configures pause image, key model, pull timeout, max downloads, and stats period.
- `DefaultRuntimeConfig` builds default runc v2 TOML options and returns default CNI, runtime, security, CDI, unprivileged, and logging settings.

## Control Flow

The runtime default function unmarshals a TOML string into an options map and embeds it into the default `runc` runtime entry.

## State and Persistence Behavior

The file returns in-memory defaults; persistent config writing/loading happens elsewhere.

## Dependencies and Integration Points

It depends on containerd defaults, TOML parsing, runc v2 runtime type strings, and shared config structs in `config.go`.

## Risks and Edge Cases

Defaults are compatibility-sensitive. Notably Unix defaults enable unprivileged ports/ICMP, CDI, and disable hugetlb by default, so changes affect node behavior broadly.

## Test Signals

`config_test.go` and kernel validation tests indirectly cover these defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_windows.go -->
# sources/cloud-native/containerd/internal/cri/config/config_windows.go

## Purpose

`config_windows.go` defines Windows default CRI image and runtime configuration.

## Important APIs, Types, and Functions

- `defaultNetworkPluginBinDirs` returns `%ProgramFiles%\containerd\cni\bin`.
- `DefaultImageConfig` sets default snapshotter, stats period, max downloads, key model, pause image, and image pull progress timeout.
- `DefaultRuntimeConfig` configures Windows CNI paths and two runhcs runtimes: `runhcs-wcow-process` and `runhcs-wcow-hypervisor`.

## Control Flow

Default runtime config builds process-isolated and hypervisor-isolated runtime entries. The hypervisor runtime includes runhcs options for sandbox isolation and CPU limit scaling.

## State and Persistence Behavior

Only in-memory default config structs are returned. Paths are derived from `ProgramFiles`.

## Dependencies and Integration Points

It depends on containerd defaults, Windows environment variables/path handling, runhcs runtime type strings, and Windows-specific annotation pass-through patterns.

## Risks and Edge Cases

Defaults depend on `ProgramFiles` being set. Runtime annotation allowlists and hypervisor options must stay aligned with hcsshim/runhcs expectations.

## Test Signals

Windows integration tests and config tests indirectly validate these defaults.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/streaming.go -->
# sources/cloud-native/containerd/internal/cri/config/streaming.go

## Purpose

`streaming.go` converts CRI server streaming settings into `k8s.io/cri-streaming` configuration, including optional TLS setup.

## Important APIs, Types, and Functions

- `streamListenerMode` values are `x509KeyPairTLS`, `selfSignTLS`, and `withoutTLS`.
- `getStreamListenerMode` validates TLS flag/key/cert combinations and chooses a mode.
- `(*ServerConfig).StreamingConfig` resolves bind address/port, parses idle timeout, selects TLS mode, and returns streaming config.
- `newTLSCert` generates a self-signed certificate using hostname and interface IPs.

## Control Flow

`StreamingConfig` fills missing address with Kubernetes bind-address resolution, overlays configured idle timeout on the default streaming config, computes TLS mode, loads configured cert/key or generates a self-signed cert when TLS is enabled without files, and sets `TLSConfig` accordingly.

## State and Persistence Behavior

The function returns in-memory config. Self-signed certificates are generated at runtime and not persisted by this file.

## Dependencies and Integration Points

It depends on Go TLS/network APIs, Kubernetes network/cert utilities, and CRI streaming defaults. It is used by the CRI server streaming endpoint for exec/attach/port-forward.

## Risks and Edge Cases

Misconfigured key/cert combinations are rejected. Self-signed cert generation depends on hostname and interface address enumeration. Missing port/address handling must produce a valid `host:port` string.

## Test Signals

`streaming_test.go` validates listener mode selection for default, configured x509, self-signed, and invalid TLS combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/streaming.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/streaming_test.go -->
# sources/cloud-native/containerd/internal/cri/config/streaming_test.go

## Purpose

`streaming_test.go` unit-tests TLS mode validation for CRI streaming server configuration.

## Important APIs, Types, and Functions

- `TestValidateStreamServer` table-drives `getStreamListenerMode`.

## Control Flow

The test checks default no-TLS mode, explicit x509 key pair mode, self-signed TLS mode, key/cert set while TLS disabled, and missing key/cert pair cases. Expected-error cases assert an error and return; success cases compare the selected mode.

## State and Persistence Behavior

All state is in-memory config structs.

## Dependencies and Integration Points

It depends on `DefaultServerConfig`, `ServerConfig`, and `getStreamListenerMode`.

## Risks and Edge Cases

The test validates mode selection but does not load actual cert files or run `StreamingConfig`, so address resolution and cert generation failures are covered elsewhere only indirectly.

## Test Signals

Failures point to incorrect TLS configuration validation for CRI streaming.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/config/streaming_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/constants/constants.go -->
# sources/cloud-native/containerd/internal/cri/constants/constants.go

## Purpose

`constants.go` defines shared CRI constants for the containerd namespace and supported CRI API version.

## Important APIs, Types, and Functions

- `K8sContainerdNamespace = "k8s.io"` is the namespace used for containerd operations from CRI.
- `CRIVersion = "v1"` is the latest CRI version supported by the plugin.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The constants are compile-time values and do not persist state directly.

## Dependencies and Integration Points

These constants integrate CRI code with containerd namespaces and CRI version reporting.

## Risks and Edge Cases

Changing either constant is a compatibility-affecting API behavior change for Kubernetes integration and containerd object lookup.

## Test Signals

Coverage is indirect through CRI version responses and namespace-scoped integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/internal/cri/constants/constants.go -->
