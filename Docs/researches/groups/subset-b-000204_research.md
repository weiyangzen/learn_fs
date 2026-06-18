# subset-b-000204 research

Grouped research report for Moby integration container update/wait tests, daemon tests and NRI fixtures, image API tests, and shared integration helper packages. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/update_linux_test.go -->
# sources/cloud-native/moby/integration/container/update_linux_test.go

Purpose: Linux-specific integration coverage for `ContainerUpdate`, verifying that resource changes are persisted in inspect data and, where possible, actually applied to cgroup files inside a running container.

Important APIs and helpers: `TestUpdateMemory`, `TestUpdateCPUQuota`, `TestUpdatePidsLimit`, `TestUpdateBlkioThrottleDevices`, `blkioTestDevice`, and `parseIOMax`. The tests use `client.ContainerUpdateOptions`, `container.Run`, `container.Exec`, daemon capability flags from `testEnv.DaemonInfo`, and direct cgroup file reads.

Control flow: each test starts a busybox container, calls `ContainerUpdate`, inspects the container to verify `HostConfig.Resources`, then reads relevant cgroup files. Memory checks branch between cgroup v1 memory and memsw files and cgroup v2 `memory.max`/`memory.swap.max`. CPU quota handles the cgroup v2 runc workaround by setting `CPUPeriod`. PIDs cases table-drive old API behavior, unset values, and cgroup `max` output. Blkio finds the root block device through `/sys/dev/block`, updates all four throttle lists, and on cgroup v2 parses `io.max`.

State and persistence: the file validates both daemon metadata persistence through `ContainerInspect` and runtime kernel state through cgroup files. Old API behavior for PIDs intentionally preserves the previous value. Blkio persistence is asserted even on cgroup v1 where in-container throttle files are not mounted.

Dependencies and integration: depends on Linux cgroups, `x/sys/unix`, `/sys`, daemon feature flags, the integration container helpers, and the Moby API client. It integrates API-level update semantics with OCI runtime/cgroup application.

Risks: tests are environment-sensitive: cgroup driver `none`, missing memory/swap/PIDs support, root filesystem on unusual devices, or cgroup namespace visibility can skip or destabilize assertions. The blkio helper assumes the filesystem backing `/` maps to a usable `/dev/<name>` path.

Test signals: strong signal that live resource updates work across cgroup v1/v2 for memory, swap, CPU quota, PIDs, and blkio throttling, including compatibility for API 1.24.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/update_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/update_test.go -->
# sources/cloud-native/moby/integration/container/update_test.go

Purpose: cross-platform integration tests for non-Linux-specific container update behavior, especially restart policy mutation.

Important APIs and helpers: `TestUpdateRestartPolicy` and `TestUpdateRestartWithAutoRemove` use `client.ContainerUpdateOptions`, `containertypes.RestartPolicy`, `container.Run`, `container.WithAutoRemove`, and polling helpers from `integration/internal/container`.

Control flow: the restart policy test starts a container configured to fail after a short sleep with `on-failure` retry count 3, updates the policy to retry 5 times, waits for final exit, and asserts both `RestartCount` and persisted `HostConfig.RestartPolicy.MaximumRetryCount`. The auto-remove test creates an auto-remove container, tries to set an `always` restart policy, and expects a conflict.

State and persistence: restart count is runtime state, while policy settings are daemon container metadata. The conflict test protects the invariant that auto-remove containers cannot later gain restart policies because removal and restart lifecycles are incompatible.

Dependencies and integration: depends on container lifecycle scheduling, restart-manager behavior, container inspect, containerd error classification through `cerrdefs.IsConflict`, and polling.

Risks: retry timing can be slower on Windows, hence the longer timeout. The first test assumes the failing command and restart manager reach a deterministic final stopped state.

Test signals: verifies update-to-restart-policy takes effect for an existing container and that daemon validation rejects auto-remove/restart-policy combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/wait_test.go -->
# sources/cloud-native/moby/integration/container/wait_test.go

Purpose: integration coverage for `ContainerWait`, including already-exited containers, blocking waits, explicit wait conditions, auto-remove, and restart-triggered exits.

Important APIs and helpers: `TestWaitNonBlocked`, `TestWaitBlocked`, `TestWaitConditions`, and `TestWaitRestartedContainer` use `client.ContainerWaitOptions`, `WaitConditionNotRunning`, `WaitConditionNextExit`, `WaitConditionRemoved`, `ContainerAttach`, `ContainerStop`, `ContainerRestart`, and internal container state polling.

Control flow: non-blocked cases run containers that have already exited and ensure wait returns the recorded status. Blocked Linux cases start a signal-trapping loop, issue stop, and require wait to unblock with the trapped exit code. Condition cases attach stdin to hold the process, start waiting, verify no premature result while running, then send a newline and assert exit code. Restart cases wait on a running process, call restart with SIGTERM, and require the wait to complete on the pre-restart exit.

State and persistence: the tests exercise daemon wait channels over container state transitions: running, exited, removed, and restarted. Auto-remove mode validates wait with removal condition when the container disappears after exit.

Dependencies and integration: depends on request client creation, busybox shell behavior, attach streams, daemon event/state propagation, Windows capability differences, and poll helpers.

Risks: signal handling and sub-second sleeps are Linux-specific in some paths. Race sensitivity is visible in comments disabling parallelism for wait-condition tests. Windows cannot catch SIGTERM in the same way.

Test signals: provides strong behavioral signal for wait result delivery, absence of premature notifications, exit-code propagation, and wait behavior across restart and removal conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/wait_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/daemon_linux_test.go -->
# sources/cloud-native/moby/integration/daemon/daemon_linux_test.go

Purpose: Linux daemon integration tests covering default bridge IPAM inference, fixed CIDR behavior, user-supplied bridges, swarm startup without nftables, and daemon shutdown with an open events connection.

Important APIs and helpers: `TestDaemonDefaultBridgeWithFixedCidrButNoBip`, `TestDaemonDefaultBridgeIPAM_Docker0`, `TestDaemonDefaultBridgeIPAM_UserBr`, `defaultBridgeIPAMTestCase`, `testDefaultBridgeIPAM`, `newHostInL3Seg`, `createBridge`, `TestSwarmNoNftables`, and `TestDaemonShutsDownQuicklyDespiteEventsConnection`.

Control flow: the IPAM tests create isolated network namespaces and optional bridge addresses, start sub-daemons with combinations of `--fixed-cidr`, `--fixed-cidr-v6`, `--bip`, `--bip6`, `--bridge`, and default address pools, then inspect the default bridge network and compare IPAM config. Link-local gateway placeholders are replaced with the kernel-assigned address before comparison. Startup-error cases assert daemon startup failure. Swarm and shutdown tests start daemons with selected firewall behavior and verify swarm init or stop timing while API connections remain open.

State and persistence: most state is kernel network namespace state: bridge devices, assigned addresses, route/sysctl side effects, and daemon-created libnetwork bridge configuration. The tests isolate that state to avoid leaking iptables or bridge rules into other integration tests.

Dependencies and integration: depends on rootful Linux network namespaces, `vishvananda/netlink`, Moby libnetwork wrappers, internal networking test utilities, daemon harness helpers, and network inspect API. It integrates daemon command-line parsing with libnetwork bridge IPAM and kernel networking.

Risks: highly environment-dependent: rootless mode skips, network namespace setup can fail, firewall backend differences matter, and exact IPAM expectations encode historical compatibility behavior. These tests are sensitive to bridge address selection rules.

Test signals: strong regression coverage for fixed-CIDR/bip compatibility, bridge address inference, IPv6 link-local handling, historical IPv4 permissiveness vs IPv6 rejection, swarm startup under firewall constraints, and graceful daemon shutdown with live event streams.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/daemon_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/daemon_test.go -->
# sources/cloud-native/moby/integration/daemon/daemon_test.go

Purpose: cross-platform daemon integration tests for daemon ID/config validation, seccomp config loading, feature flags, proxy configuration and sanitization, and live-restore behavior.

Important APIs and helpers: `TestConfigDaemonID`, `TestDaemonConfigValidation`, `TestConfigDaemonSeccompProfiles`, `TestDaemonConfigFeatures`, `TestDaemonProxy`, `TestLiveRestore`, `testLiveRestoreAutoRemove`, `testLiveRestoreVolumeReferences`, and `testLiveRestoreUserChainsSetup`.

Control flow: config tests run sub-daemons or the daemon binary with validation flags and fixture JSON files. Feature tests alter daemon config and reload or restart to inspect advertised features. Proxy tests configure proxies by environment, command-line flags, and config file, use an HTTP test server to observe whether pulls route through the proxy, and assert credentials are masked in logs and conflict errors. Live-restore tests restart or stop daemons while containers keep running, then verify auto-remove cleanup, mounted volume/image reference protection, bind-mount handling, and Docker user iptables chain reinstallation.

State and persistence: tests exercise daemon root state, config files, log output, image/container/volume references across restarts, live container processes, mount reference counts, and proxy settings surfaced through `Info`. Live-restore cases explicitly validate state reconciliation after daemon restart.

Dependencies and integration: depends on daemon harness, internal container/process helpers, HTTP test servers, seccomp fixtures, filesystem temp dirs, volumes, mounts, iptables, and Moby client APIs. It integrates command-line flags, config-file parsing, SIGHUP reloads, logging, image pulls, volume/image reference accounting, and live-restore recovery.

Risks: sub-daemon tests are skipped or constrained on Windows/rootless/remote environments. Proxy tests rely on failed pulls still reaching expected hosts. Live-restore tests are timing-sensitive around process exit, mount namespaces, and daemon restart.

Test signals: broad daemon lifecycle signal for validation behavior, secure logging, proxy precedence, live-restore cleanup, reference accounting, and runtime state restoration after daemon downtime.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/default_storage_test.go -->
# sources/cloud-native/moby/integration/daemon/default_storage_test.go

Purpose: integration tests for storage backend defaults, graphdriver persistence, and inspect API compatibility between graphdriver and containerd snapshotter modes.

Important APIs and helpers: `TestDefaultStorageDriver`, `TestGraphDriverPersistence`, and `TestInspectGraphDriverAPIBC` use the daemon harness, `Info`, `ImageInspect`, `ContainerInspect`, `client.WithAPIVersion`, and storage response types.

Control flow: default storage clears storage-driver environment overrides, starts a daemon, and checks driver status identifies containerd snapshotter mode. Persistence starts with explicit `overlay2`, loads busybox, creates a container, stops, restarts without explicit storage-driver flags, and verifies the daemon remains on the same graphdriver with image/container data intact. API compatibility table-drives current vs older API behavior and graphdriver vs snapshotter storage, then inspects image/container GraphDriver and Storage fields.

State and persistence: validates daemon root storage selection across restart, image and container metadata persistence, and API response shape stability for clients that expect `GraphDriver` or the newer `Storage.RootFS.Snapshot` field.

Dependencies and integration: depends on Linux sub-daemons, storage driver availability, busybox frozen image loading, client API version negotiation, and Moby storage response structs.

Risks: storage driver availability can vary by host. The tests intentionally clear env vars to avoid external overrides, but host filesystem/kernel support still affects `overlay2` and `vfs` behavior.

Test signals: verifies no unexpected auto-migration from graphdriver to snapshotter, default containerd snapshotter selection, and backward-compatible inspect fields across API versions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/default_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/main_test.go -->
# sources/cloud-native/moby/integration/daemon/main_test.go

Purpose: package-level test bootstrap for daemon integration tests.

Important APIs and helpers: package globals `testEnv` and `baseContext`, and `TestMain`. It calls `environment.New`, `environment.EnsureFrozenImagesLinux`, `testEnv.Print`, and OpenTelemetry span status APIs.

Control flow: `TestMain` creates a root tracing span, initializes the execution environment, ensures frozen Linux images are available, prints environment details, runs the package tests, records a tracing error on nonzero exit, and exits with the test code.

State and persistence: stores environment and context in package globals consumed by daemon tests. It may load or verify frozen images in the daemon test environment before tests execute.

Dependencies and integration: depends on Moby internal test environment helpers and OpenTelemetry. It integrates package tests with shared daemon metadata, image fixtures, and tracing.

Risks: initialization failure panics before individual tests can skip. `os.Exit` bypasses deferred cleanup in `TestMain`, so explicit span ending happens only on initialization failures in this file.

Test signals: not a behavioral test itself, but it is required infrastructure for consistent daemon integration environment setup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/migration_test.go -->
# sources/cloud-native/moby/integration/daemon/migration_test.go

Purpose: Linux integration tests for migrating from graphdriver storage to containerd snapshotters and preserving image usability through save/load after migration.

Important APIs and helpers: `TestMigrateOverlaySnapshotter`, `TestMigrateNativeSnapshotter`, `testMigrateSnapshotter`, and `TestMigrateSaveLoad`. They use daemon feature flag `containerd-migration`, env `DOCKER_MIGRATE_SNAPSHOTTER_THRESHOLD`, frozen image loading, container helpers, `ImageSave`, `ImageLoad`, and `ImageRemove`.

Control flow: migration tests start a daemon with `overlay2` or `vfs`, capture daemon ID and image count, load busybox, create a running container, then restart with migration enabled. With a container present, migration should be blocked and storage driver unchanged. After removing the container, restart with migration enabled should switch to the expected snapshotter while preserving image count and daemon ID. Save/load test migrates, saves busybox, removes all images, reloads the archive, and runs a container from the loaded image.

State and persistence: validates daemon root metadata across storage-backend migration: daemon ID, image count, image content, and container blockers. It also validates exported archive compatibility after migration.

Dependencies and integration: depends on Linux, storage drivers, containerd snapshotter support, frozen image fixtures, daemon restart semantics, and image save/load APIs.

Risks: migration behavior is gated by environment variables and active containers. Tests are slow and host-storage sensitive. They assume the selected graphdriver/snapshotter pair is available.

Test signals: strong regression signal for safe migration gating, persistence of daemon identity and images, and post-migration image execution plus archive round-trip behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/migration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/main_test.go -->
# sources/cloud-native/moby/integration/daemon/nri/main_test.go

Purpose: package-level bootstrap for NRI daemon integration tests.

Important APIs and helpers: package globals `testEnv` and `baseContext`, and `TestMain`. It calls `environment.New`, `environment.EnsureFrozenImagesLinux`, `testEnv.Print`, and OpenTelemetry span status APIs.

Control flow: initializes a tracing span, builds the shared test environment, ensures frozen Linux images are loaded or available, prints environment details, runs all NRI tests, records an error status on nonzero test exit, and exits.

State and persistence: stores execution environment and base context in package-level variables used by NRI tests that start sub-daemons and plugins.

Dependencies and integration: depends on Moby test environment helpers and OpenTelemetry. It prepares the daemon and image fixtures required by NRI integration tests.

Risks: initialization failures panic before individual tests can apply skips. Like other `TestMain` implementations using `os.Exit`, normal defer-based cleanup in `TestMain` is not available.

Test signals: infrastructure file; its success indicates the environment is suitable for the NRI test package.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/nri_test.go -->
# sources/cloud-native/moby/integration/daemon/nri/nri_test.go

Purpose: integration tests for Docker daemon NRI support, including container-create adjustments, unsupported adjustments, injected mounts, and daemon/plugin reload behavior.

Important APIs and helpers: `TestNRIContainerCreateEnvVarMod`, `TestNRIContainerCreateUnsupportedAdj`, `TestNRIContainerCreateAddMount`, and `TestNRIReload`. They use `startBuiltinPlugin`, `builtinPluginConfig`, NRI `api.ContainerAdjustment`, daemon `--nri-opts`, container helpers, and a compiled test plugin.

Control flow: the first three tests start a sub-daemon with NRI enabled on a temp socket, start an in-process plugin, then create containers. Env tests assert plugin-provided or modified environment variables are visible in inspect. Unsupported adjustment tests return hooks, CDI devices, or CPU resource changes and expect daemon create errors. Mount tests prepare a host directory and Docker volume, inject bind/volume mounts with read-only or read-write options, and exec `cat`/`touch` to validate access. Reload test builds `testdata/test_plugin.go`, updates daemon and plugin config files, reloads the daemon, and checks whether new containers receive the configured environment variable.

State and persistence: state spans NRI socket connections, plugin synchronization, daemon JSON config, plugin config files, container config/env, volume data, and reloadable daemon NRI settings.

Dependencies and integration: depends on rootful local Linux daemons, containerd NRI API/stub, Go toolchain for building the external plugin, Docker volumes, mounts, and daemon config reload.

Risks: skipped for remote, Windows, or rootless environments. The tests rely on plugin synchronization before container creation and on reload timing. Build-path assumptions for `./testdata/test_plugin.go` matter.

Test signals: verifies supported NRI env and mount adjustments, rejects unsupported adjustment families, and proves NRI can be enabled, reconfigured, and disabled through daemon reload.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/nri_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/plugin.go -->
# sources/cloud-native/moby/integration/daemon/nri/plugin.go

Purpose: in-process NRI plugin test harness used by the NRI integration tests to inject deterministic container-create adjustments.

Important APIs and types: `builtinPluginConfig`, `builtinPlugin`, `startBuiltinPlugin`, and NRI lifecycle methods `Configure`, `Synchronize`, `Shutdown`, `RunPodSandbox`, `StopPodSandbox`, `RemovePodSandbox`, `CreateContainer`, `PostCreateContainer`, `StartContainer`, `PostStartContainer`, `UpdateContainer`, `PostUpdateContainer`, `StopContainer`, `RemoveContainer`, and `onClose`.

Control flow: `startBuiltinPlugin` constructs a `stub.Stub` with plugin name/index/socket path and an on-close callback, starts it, waits for `Synchronize` to close a channel, and returns `stub.Stop`. Most lifecycle callbacks log and return nil. `CreateContainer` returns the configured `ctrCreateAdj` and no updates, making the tests control exactly what adjustment the daemon receives.

State and persistence: state is process-local: the configured adjustment, stub handle, logger, and a `sync.Once`-guarded synchronization channel. No persistent files are written by this helper.

Dependencies and integration: depends on containerd NRI `api` and `stub`, containerd logging, testing assertions, and daemon NRI socket support. It integrates the Go test process as an NRI plugin.

Risks: `Configure` rejects non-empty YAML config, so tests using this helper cannot cover plugin config parsing. If synchronization never arrives, `startBuiltinPlugin` fails via context cancellation.

Test signals: helper-only file; it enables high-signal NRI daemon tests by removing external plugin process complexity for most adjustment cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/testdata/test_plugin.go -->
# sources/cloud-native/moby/integration/daemon/nri/testdata/test_plugin.go

Purpose: standalone NRI plugin binary fixture used by reload tests to validate daemon-managed plugin discovery and plugin configuration reload.

Important APIs and types: `config`, `plugin`, `Configure`, `CreateContainer`, and `main`. The plugin uses NRI `stub.New`, `stub.Run`, `api.MustParseEventMask`, and `api.ContainerAdjustment`.

Control flow: `main` parses optional `-name` and `-idx`, constructs a stub that exits the process on close, and runs it. `Configure` parses JSON config when present and subscribes to `CreateContainer`. `CreateContainer` always injects `NRI_TEST_PLUGIN=wozere` and conditionally injects the configured env var/value pair.

State and persistence: plugin state is the in-memory parsed config from the daemon-provided plugin config file. The plugin itself persists nothing; the test writes its config externally.

Dependencies and integration: depends on containerd NRI APIs, JSON config delivered by the daemon, and executable plugin discovery from the daemon's configured plugin path.

Risks: exits with status 1 on stub setup/run errors and status 0 on close, so failures can be silent except through daemon/plugin behavior in tests. Config schema is intentionally minimal.

Test signals: verifies external plugin process startup, config parsing, event subscription, and container-create env adjustment after daemon reload.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/nri/testdata/test_plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/empty-config-1.json -->
# sources/cloud-native/moby/integration/daemon/testdata/empty-config-1.json

Purpose: daemon config validation fixture representing a completely empty config file.

Important content: the file contains no JSON tokens. It is consumed by `TestDaemonConfigValidation` with `dockerd --validate --config-file`.

Control flow: the daemon validation test passes this file path and expects output containing `configuration OK`, proving the daemon treats an empty config file as valid/no-op configuration.

State and persistence: no state is stored beyond the file's empty content. Its meaning is the absence of directives.

Dependencies and integration: depends on daemon config loading accepting zero-byte config files. It integrates with the daemon binary validation path rather than the client API.

Risks: if config parsing policy changes to require valid JSON, this fixture would become invalid. The test relies on path resolution through integration testdata.

Test signals: protects compatibility for deployments where an empty daemon config file exists.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/empty-config-1.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/empty-config-2.json -->
# sources/cloud-native/moby/integration/daemon/testdata/empty-config-2.json

Purpose: daemon config validation fixture representing an explicit empty JSON object.

Important content: the file contains `{}`. It is used by `TestDaemonConfigValidation`.

Control flow: the validation test passes the file to `dockerd --validate --config-file` and expects `configuration OK`, confirming that no-op JSON object config is accepted.

State and persistence: encodes no daemon settings and produces no persistent daemon state by itself.

Dependencies and integration: depends on daemon JSON config parser and validation command-line mode.

Risks: low; this is a compatibility fixture for the simplest valid JSON config.

Test signals: confirms empty object config remains valid and distinguishable from malformed or unknown-option fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/empty-config-2.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/invalid-config-1.json -->
# sources/cloud-native/moby/integration/daemon/testdata/invalid-config-1.json

Purpose: daemon config validation fixture containing a syntactically valid but semantically invalid unknown option.

Important content: `{"unknown-option": true}`. It is consumed by `TestDaemonConfigValidation`.

Control flow: the validation test runs the daemon binary with `--validate --config-file` and expects output indicating failure to configure the daemon from the file.

State and persistence: no runtime state should be created; the fixture is for validation rejection.

Dependencies and integration: depends on daemon config schema validation rejecting unknown directives.

Risks: if config validation becomes permissive or adds an option named `unknown-option`, the expected failure would change.

Test signals: protects strict config validation and useful failure output for unsupported daemon settings.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/invalid-config-1.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/malformed-config.json -->
# sources/cloud-native/moby/integration/daemon/testdata/malformed-config.json

Purpose: daemon config validation fixture for malformed JSON.

Important content: the file contains only `{`, an incomplete JSON object.

Control flow: `TestDaemonConfigValidation` passes this file to `dockerd --validate --config-file` and expects failure output, exercising JSON syntax error handling.

State and persistence: no daemon state should be written because parsing fails before configuration is accepted.

Dependencies and integration: depends on the daemon's JSON decoder and validation command path.

Risks: low. The exact user-facing error text may change, but the test only checks a broad failure phrase.

Test signals: ensures malformed config files are rejected during daemon validation instead of being ignored or treated as empty config.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/malformed-config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/valid-config-1.json -->
# sources/cloud-native/moby/integration/daemon/testdata/valid-config-1.json

Purpose: daemon config validation fixture containing a minimal valid setting.

Important content: `{"debug": true}`. It is consumed by `TestDaemonConfigValidation`.

Control flow: the validation test passes this file to `dockerd --validate --config-file` and expects `configuration OK`, proving recognized settings pass validation.

State and persistence: the file represents daemon debug configuration, but in validation mode it should not start or persist daemon runtime state.

Dependencies and integration: depends on daemon config schema recognizing the `debug` directive.

Risks: low, although future config schema changes could rename or deprecate the key.

Test signals: confirms the validation path accepts a simple real daemon option, complementing empty and invalid fixtures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/daemon/testdata/valid-config-1.json -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/doc.go -->
# sources/cloud-native/moby/integration/doc.go

Purpose: package documentation anchor for the top-level `integration` package.

Important APIs and types: no exported functions or types; the file only declares `package integration`.

Control flow: none. It exists so the directory has a package declaration/documentation file.

State and persistence: no runtime state or persistence behavior.

Dependencies and integration: no imports. It integrates only with Go package documentation and package discovery.

Risks: minimal. If removed, package-level docs may disappear, but behavior is unaffected.

Test signals: no direct tests; it is structural source metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/attestation_test.go -->
# sources/cloud-native/moby/integration/image/attestation_test.go

Purpose: integration tests for `GET /images/{name}/attestations` against the containerd image store, plus helpers that build a synthetic OCI layout with in-toto attestation manifests.

Important APIs and helpers: `TestImageAttestations`, `statementLayer`, `buildAttestationImage`, `writeBlob`, `writeJSON`, and `mustMarshal`. The test uses `apiClient.ImageAttestations`, `ImageAttestationsWithStatement`, `ImageAttestationsWithPredicateTypes`, and `ImageAttestationsWithPlatform`.

Control flow: the test loads an OCI image containing a normal platform image manifest and an attestation manifest with SLSA provenance and SPDX SBOM statement layers. Subtests verify default omission of statement bodies, opt-in body return, predicate-type filtering, explicit platform matching, wrong-platform not found, multi-platform query rejection through raw HTTP, unknown-image not found, and empty filter semantics.

State and persistence: image content is written into a temporary OCI layout, loaded into the daemon's image store, and removed at cleanup. Attestation metadata is represented by OCI descriptors and Docker attestation annotations pointing at the image manifest digest.

Dependencies and integration: depends on containerd snapshotter image store, BuildKit attestation annotations, OCI image-spec types, distribution reference parsing, digest calculations, raw request helpers, and the Moby image API client.

Risks: skipped outside snapshotter mode. The handcrafted OCI layout must stay aligned with daemon attestation discovery rules. Raw HTTP query construction is sensitive to API version and error text.

Test signals: strong endpoint coverage for attestation listing, statement retrieval, filtering, platform validation, and error classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/attestation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/commit_test.go -->
# sources/cloud-native/moby/integration/image/commit_test.go

Purpose: tests image commit behavior for environment inheritance and user-namespace ownership preservation.

Important APIs and helpers: `TestCommitInheritsEnv` and `TestUsernsCommit` use `ContainerCommit`, `ImageInspect`, container create/run helpers, sub-daemon user namespace remap, and `RunAttach`.

Control flow: environment inheritance commits a container with `ENV PATH=/bin`, inspects the image config, creates a second container from that image, commits with `ENV PATH=/usr/bin:$PATH`, and asserts expansion to `/usr/bin:/bin`. Userns test starts a userns-remapped daemon, creates a file owned by UID/GID 1000 in a container, commits the image, runs it, and checks `stat` output.

State and persistence: validates committed image configuration and filesystem layer ownership metadata. The userns case tests remapped storage and committed tar metadata surviving into a new container.

Dependencies and integration: depends on Linux user namespace kernel support, non-rootless local daemon, daemon harness, busybox/stat behavior, image commit, and image inspect.

Risks: skipped in Windows, remote, rootless, or missing userns environments. Environment expansion semantics are Dockerfile-like and must remain stable.

Test signals: verifies commit preserves expected config inheritance and file ownership under user namespace remapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/history_test.go -->
# sources/cloud-native/moby/integration/image/history_test.go

Purpose: integration tests for image history API, including BuildKit cross-platform image history.

Important APIs and helpers: `TestAPIImagesHistory`, `TestAPIImageHistoryCrossPlatform`, and `pullImageForPlatform`. They use internal build helpers, fake build contexts, `ImageBuild`, `ImageHistory`, `ImagePull`, and platform options.

Control flow: the basic test builds a small Dockerfile and asserts the built image ID appears in history. The cross-platform regression test selects a non-native architecture, pulls a base image for that platform, builds with BuildKit for that platform, extracts the image ID, then checks history by ID, by explicit platform, and by tag. It also asserts expected item count and non-negative layer sizes.

State and persistence: build outputs are persisted as images in the daemon store and removed during cleanup. Cross-platform state includes pulled platform-specific base image content and manifest metadata.

Dependencies and integration: depends on BuildKit builder, registry access for alpine, platform selection, fakecontext, image history API, and daemon architecture metadata.

Risks: cross-platform test is skipped on Windows but still depends on external pull availability and BuildKit behavior. The expected history length can change if builder output changes.

Test signals: protects `docker history`/image history for native and non-native platform images, especially avoiding missing snapshot errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/history_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/identity_test.go -->
# sources/cloud-native/moby/integration/image/identity_test.go

Purpose: raw HTTP integration tests for image identity fields introduced in newer API versions.

Important APIs and helpers: `TestImageListIdentity`, `TestImageListIdentityRequiresManifests`, `TestImageInspectIdentity`, `TestImageListIdentityAfterInspectWarmup`, `imageListRaw`, and `imageInspectRaw`.

Control flow: tests call versioned raw endpoints directly. List without `identity=1` must omit identity. List with `identity=1&manifests=1` scans manifest image data for object-shaped identity metadata. A missing `manifests=1` parameter must return 400. Inspect on API 1.53 checks identity shape when available. Warmup test inspects an image first, then verifies list with manifests/identity includes matching identity data.

State and persistence: no new images are created; tests read current environment images and may skip if none with identity metadata are available. They exercise cache/warmup behavior between inspect and list.

Dependencies and integration: depends on daemon API version gates, raw request helpers, JSON decoding into generic maps, and image metadata availability from the daemon store.

Risks: environment-dependent skips occur if no suitable identity-bearing images exist. Raw JSON map checks are flexible but can miss typed client regressions.

Test signals: protects API compatibility and parameter validation for image identity metadata in inspect/list responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/identity_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/import_test.go -->
# sources/cloud-native/moby/integration/image/import_test.go

Purpose: integration tests for image import robustness, platform handling, validation, and bad source errors.

Important APIs and helpers: `TestImportExtremelyLargeImageWorks`, `TestImportWithCustomPlatform`, `TestImportWithCustomPlatformReject`, and `TestImageImportBadSrc`. They use tar writers, `ImageImport`, platform options, a sub-daemon, and an HTTP test server.

Control flow: the large-image regression constructs an empty tar followed by 8GB of zero padding via `io.LimitReader` and imports it. Platform test imports empty tar streams with no platform, OS-only platform, and custom architecture, then inspects OS/arch. Reject test, in graphdriver mode, imports invalid or unsupported platforms and expects invalid-argument errors. Bad-source test checks missing full/trimmed URLs, encoded URL paths, and encoded absolute local paths.

State and persistence: import creates image records with specified references and platform metadata. The large test uses a separate daemon so it can run in parallel and avoid polluting the shared daemon.

Dependencies and integration: depends on tar import logic, platform normalization, snapshotter vs graphdriver behavior, daemon harness, HTTP source handling, and containerd error definitions.

Risks: large import is skipped on arm64 and remote/Windows contexts due to runtime cost. Reusing a single `imageRdr` across subtests is safe here only because it is an empty tar/zero reader path with no expected data reuse beyond construction assumptions.

Test signals: protects CVE-related large padding handling, custom platform import, unsupported platform rejection, and source path/URL error classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/import_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/inspect_test.go -->
# sources/cloud-native/moby/integration/image/inspect_test.go

Purpose: integration tests for image inspect response shape, descriptor fields, repo digest uniqueness, missing blob resilience, and platform-specific inspect.

Important APIs and helpers: `TestImageInspectEmptyTagsAndDigests`, `TestImageInspectUniqueRepoDigests`, `TestImageInspectDescriptor`, `TestImageInspectWithoutSomeBlobs`, and `TestImageInspectWithPlatform`.

Control flow: dangling image inspect verifies `RepoTags` and `RepoDigests` are empty arrays in typed and raw JSON. Repo digest test tags busybox multiple times and ensures repo digests are not duplicated. Descriptor test checks descriptor presence only in snapshotter mode. The missing-blob regression is currently skipped. Platform inspect loads a synthetic multi-platform image with a legacy manifest and tests default, explicit native, explicit non-native, graphdriver error, and manifest inclusion behavior.

State and persistence: tests load special OCI images, create tags, and inspect daemon image metadata. Platform tests validate descriptor platform metadata and manifest list exposure in snapshotter mode.

Dependencies and integration: depends on specialimage builders, internal image load helper, raw response capture, image inspect options, snapshotter vs graphdriver behavior, and OCI platform structs.

Risks: some behavior is mode-specific and skipped or branched. The skipped missing-blob test documents a known desired regression test but currently provides no active signal.

Test signals: strong response compatibility signal for empty arrays vs nulls, descriptor fields, manifest inclusion, and platform-specific inspect semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/list_test.go -->
# sources/cloud-native/moby/integration/image/list_test.go

Purpose: integration tests for image list filtering, size calculations, and manifest metadata exposure.

Important APIs and helpers: `TestImagesFilterMultiReference`, `TestImagesFilterUntil`, `TestImagesFilterBeforeSince`, `TestAPIImagesFilters`, `TestAPIImagesListSizeShared`, and `TestAPIImagesListManifests`.

Control flow: filter tests create tags or committed images and verify reference glob/canonical filters, since/before/until behavior, and multi-reference output trimming. Size-shared test loads two images sharing a top layer and requests shared-size calculation. Manifest test loads a multi-platform image in a sub-daemon, creates a container for one platform, checks old API behavior, then requests manifests on API 1.47 and verifies kind, availability, platform coverage, and container association.

State and persistence: creates image tags, committed images with distinct timestamps, synthetic multi-layer/multi-platform images, and a container tied to one manifest. Filter tests depend on persisted image creation timestamps and references.

Dependencies and integration: depends on client filters, fake commits, specialimage loading, daemon harness, API version negotiation, OCI platforms, and image summary response shape.

Risks: timestamp precision is truncated to seconds in the API, so order-independent assertions are needed. Manifest tests require snapshotter mode and non-Windows sub-daemons.

Test signals: broad signal for image list filter correctness, shared-size computation by ChainID, and manifest-list API behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/load_test.go -->
# sources/cloud-native/moby/integration/image/load_test.go

Purpose: integration test for loading a new image over an existing tag and preserving the old image as dangling.

Important APIs and helpers: `TestLoadDanglingImages` uses `iimage.Load`, `specialimage.MultiLayerCustom`, `ImageList`, and local `findImageByName`/`findImageById` closures.

Control flow: the test loads `namedimage:latest`, records its image ID from `ImageList`, loads a second image under the same tag with different content, lists images again, and asserts the tag points to a new ID while the old ID remains present with no repo tags.

State and persistence: validates image store reference mutation and dangling image retention after tag replacement. The old manifest/content remains reachable by ID without tags.

Dependencies and integration: depends on Linux special image generation, daemon image load behavior, image list response fields, and containerd error definitions for local helper failures.

Risks: skipped outside Linux. It assumes image list returns both tagged and dangling images under default options in the tested mode.

Test signals: protects against losing old image records when loading a replacement tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/main_test.go -->
# sources/cloud-native/moby/integration/image/main_test.go

Purpose: package-level setup and per-test cleanup helper for image integration tests.

Important APIs and helpers: globals `testEnv` and `baseContext`, `TestMain`, and `setupTest`. It calls tracing setup, `environment.New`, `environment.EnsureFrozenImagesLinux`, `environment.ProtectAll`, and `testEnv.Clean`.

Control flow: `TestMain` configures tracing, creates the execution environment, ensures frozen images, prints environment details, and runs tests. `setupTest` starts a per-test span, protects existing resources, schedules environment cleanup, and returns a context.

State and persistence: maintains shared test environment and context. `setupTest` preserves baseline images/resources and removes test-created state after each test through the environment cleaner.

Dependencies and integration: depends on Moby internal test environment and tracing helpers. It integrates all image tests with consistent frozen image availability and cleanup.

Risks: initialization failures panic. `os.Exit(m.Run())` means the tracing shutdown call after normal test completion is not reached in this file as written.

Test signals: infrastructure-only; successful setup is required for reliable image test isolation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/prune_test.go -->
# sources/cloud-native/moby/integration/image/prune_test.go

Purpose: integration tests for image prune safety, deletion order, used-image preservation, and negative label filters.

Important APIs and helpers: `TestPruneDontDeleteUsedDangling`, `TestPruneLexographicalOrder`, `TestPruneDontDeleteUsedImage`, and `TestPruneLabelFilterNegative`. They use sub-daemons, `ImagePrune`, `ImageInspect`, `ImageTag`, container helpers, special images, and filter maps.

Control flow: dangling test loads a dangling image, creates a container using it, prunes dangling images, and ensures the used image remains. Lexical order test tags busybox many times, removes latest, runs a container by image ID, prunes unused tagged images, and expects a retained tag. Used-image test table-drives single vs two tags and multiple image reference forms, then prunes with `dangling=false` and verifies only unused aliases disappear. Negative label test loads labeled and unlabeled images, prunes with `label!` and `dangling=false`, and checks only the unlabeled image is deleted and reported.

State and persistence: exercises image reference graph state, container-to-image references, labels, prune reports, and tag selection/deletion order.

Dependencies and integration: depends on local sub-daemons, snapshotter-specific digest reference behavior, specialimage labeled/dangling builders, image prune filters, and error classification.

Risks: skipped for Windows or remote daemons. Behavior differs between graphdriver and snapshotter for digest references. Prune report ordering/fields are part of asserted behavior.

Test signals: strong safety signal that prune does not delete images used by containers and correctly handles aliases, labels, and dangling state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/pull_test.go -->
# sources/cloud-native/moby/integration/image/pull_test.go

Purpose: integration tests for image pull platform validation, digest/repository verification, nonexistent image errors, and preserving old images as dangling after pull.

Important APIs and helpers: `TestImagePullPlatformInvalid`, `createTestImage`, `TestImagePullStoredDigestForOtherRepo`, `TestImagePullNonExisting`, and `TestImagePullKeepOldAsDangling`.

Control flow: invalid platform pull expects invalid-argument. `createTestImage` writes a minimal Docker schema2 manifest, config, and layer into a content store. Digest/repo test pushes that image to a local registry, pulls it once to cache content, then tries pulling the same digest under a different repository and expects not found. Nonexistent test table-drives references with implicit library/latest variants and checks error text/classification. Dangling test tags busybox as alpine, removes busybox tag, pulls alpine, and verifies the previous ID is still inspectable.

State and persistence: uses daemon image cache/content store, local registry state, manifest cache, tag references, and dangling image records.

Dependencies and integration: depends on containerd content store/client, local registry test harness, platform validation, Docker Hub-like error messages, and daemon image pull implementation.

Risks: registry/network behavior can affect tests. Nonexistent pull tests rely on external registry response conventions. Digest/repo test is skipped for remote and Windows.

Test signals: verifies security-relevant remote digest validation, platform error classification, user-facing missing-image errors, and old-image retention on pull replacement.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/pull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/remove_test.go -->
# sources/cloud-native/moby/integration/image/remove_test.go

Purpose: integration tests for image removal semantics: orphaning parent images, digest removal, platform-specific removal, and conflict/not-found errors.

Important APIs and helpers: `TestRemoveImageOrphaning`, `TestRemoveByDigest`, `TestRemoveWithPlatform`, `checkPlatformDeleted`, and `TestAPIImagesDelete`.

Control flow: orphaning test commits two images under the same reference and removes the tag, expecting the first committed image to remain and the second to disappear. Digest test removes a tag by repo digest without deleting busybox. Platform test loads a multi-platform image, removes selected platform manifests with `ImageRemoveOptions.Platforms`, verifies deleted descriptors, then removes the rest. API delete test builds an image, tags it twice, expects conflict when deleting by ID without force, expects not-found for missing tag, and removes a single tag.

State and persistence: validates image reference graph mutation, manifest/index content deletion, platform descriptor retention, tag untagging, and conflict handling when multiple tags point to an image.

Dependencies and integration: depends on specialimage multi-platform builder, build helper/fakecontext, snapshotter mode for platform deletion and repo digest behavior, string ID truncation, and Moby image remove API.

Risks: platform deletion behavior is snapshotter-only and includes a TODO about reporting platform-specific manifests when deleting the rest. Graphdriver vs snapshotter differences require skips.

Test signals: protects removal correctness for references, digests, platforms, conflict errors, and orphaned image retention.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/save_test.go -->
# sources/cloud-native/moby/integration/image/save_test.go

Purpose: integration tests for image save archive contents, OCI layout export, platform-filtered save/load, multi-image repository export, and layer directory permissions.

Important APIs and helpers: `imageSaveManifestEntry`, `tarIndexFS`, `TestSaveCheckTimes`, `TestSaveOCI`, `TestSaveAndLoadPlatform`, `TestSaveRepoWithMultipleImages`, `TestSaveDirectoryPermissions`, and `listTar`.

Control flow: `tarIndexFS` copies an archive to a temp file and uses `tar2go` for indexed reads. Time test ensures tar member modtimes are not newer than image creation or are zero for containerd export. OCI test saves images, reads `index.json`, manifests, configs, and blobs, and compares layer diff IDs and annotations. Platform round-trip pulls selected platforms, saves selected subsets, removes and reloads images, then inspects expected platforms. Multi-image test commits two tags under one repo plus busybox and validates `manifest.json`/blob coverage. Directory permission test builds a layer with owned directories, saves it, decompresses layers, and checks expected tar entries.

State and persistence: exercises image archive serialization, blob/config/manifest relationships, platform-specific content selection, repository tag grouping, and filesystem metadata in layers.

Dependencies and integration: depends on tar handling, `tar2go`, compression detection, OCI specs, digest calculations, BuildKit/build helpers, fake contexts, special images, API version gates, and image save/load APIs.

Risks: platform round-trip pulls multiple architectures from a registry and is snapshotter-sensitive. Archive details differ between graphdriver and snapshotter modes, so assertions branch. Tar content expectations may vary by storage backend whiteout/dev entries.

Test signals: broad and deep coverage of archive correctness, OCI metadata, platform filtering, multi-image save, and preserved filesystem structure.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/save_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/size_test.go -->
# sources/cloud-native/moby/integration/image/size_test.go

Purpose: API compatibility test ensuring image sizes are never reported as negative for current and minimum API versions.

Important APIs and helpers: `TestImagesSizeCompatibility` creates clients with latest and `client.MinAPIVersion`, calls `ImageList`, and checks each `image.Summary.Size`.

Control flow: for each API version case, the test creates a client from environment, lists images, requires at least one image, and asserts all sizes are `>= 0`.

State and persistence: reads existing daemon image metadata only. It relies on frozen images from package setup.

Dependencies and integration: depends on API version negotiation, client environment configuration, and image list response serialization.

Risks: if the test environment has no images, it fails rather than skips. It does not validate exact sizes, only non-negative compatibility.

Test signals: protects old-client compatibility for image size fields, specifically against historical `-1` size regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/image/tag_test.go -->
# sources/cloud-native/moby/integration/image/tag_test.go

Purpose: integration tests for image tag normalization and invalid tag rejection.

Important APIs and helpers: `TestTagUnprefixedRepoByNameOrName`, `TestTagUsingDigestAlgorithmAsName`, `TestTagValidPrefixedRepo`, `TestTagExistedNameWithoutForce`, `TestTagOfficialNames`, and `TestTagMatchesDigest`.

Control flow: tests tag busybox by name and ID into unprefixed repos, reject `sha256:sometag` ambiguity, accept several valid prefixed repository forms, allow retagging an existing tag, normalize official Docker Hub names, and reject digest references as tag targets while confirming no image is created for that digest.

State and persistence: mutates image tag references in the daemon store and inspects resulting repo tags. Invalid cases should leave no new matching reference.

Dependencies and integration: depends on image tag API, distribution reference parsing/normalization, busybox fixture, and image inspect.

Risks: official-name test comments suggest its assertion may be weak. Tag normalization rules are externally visible compatibility behavior and can be subtle.

Test signals: protects repository/tag parser behavior, ambiguous digest-algorithm name rejection, and digest-reference target rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/image/tag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/container.go -->
# sources/cloud-native/moby/integration/internal/container/container.go

Purpose: shared test helper package for creating, running, attaching to, inspecting, removing, and reading output from containers in integration tests.

Important APIs and types: `TestContainerConfig`, `NewTestConfig`, `Create`, `CreateFromConfig`, `Run`, `RunResult`, `RunAttach`, `demultiplexStreams`, `Remove`, `RemoveAll`, `Inspect`, `ContainerOutput`, and `Output`.

Control flow: `NewTestConfig` builds a busybox default command (`top` on Linux, `sleep 240` on Windows) and applies functional options. `Create` and `Run` wrap `ContainerCreate`/`ContainerStart` with assertions. `RunAttach` enables stdout/stderr attach, starts the container, demultiplexes streams until EOF or context cancellation, then inspects with a fresh background context for exit code. `demultiplexStreams` copies Docker multiplexed output in a goroutine, closes the hijacked response on completion/cancel, and waits for the copy goroutine. Removal/list/inspect/output helpers wrap common API calls.

State and persistence: creates real containers and reads logs/inspect state. The helper itself stores only transient buffers and config structs.

Dependencies and integration: depends on Moby client API, container/network types, OCI platform, `stdcopy`, test assertions, runtime GOOS, and functional options from `ops.go`.

Risks: `RunAttach` uses context cancellation to stop stream reads but always inspects with `context.Background`, so hung daemon inspect could still block. Helpers assert fatally, making them convenient but unsuitable for tests that need error inspection.

Test signals: helper code; its reliability affects many integration tests by standardizing container setup, cleanup, and output capture.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/container.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/exec.go -->
# sources/cloud-native/moby/integration/internal/container/exec.go

Purpose: shared helper for synchronous `docker exec` operations in integration tests.

Important APIs and types: `ExecResult`, `Stdout`, `Stderr`, `Combined`, `AssertSuccess`, `Exec`, and `ExecT`.

Control flow: `Exec` creates an exec instance with stdout/stderr attached and stdin closed, applies optional create-option mutators, attaches to the exec, uses `demultiplexStreams` from `container.go` to read output, then inspects the exec to return exit code and buffers. `ExecT` wraps `Exec` and fails the test on error.

State and persistence: creates transient exec instances inside existing containers and captures their output in memory. It reads daemon exec inspect state for exit code.

Dependencies and integration: depends on Moby exec API, the package stream demultiplexer, contexts, and testing interfaces.

Risks: if the context expires while output is still being copied, `Exec` returns an error and may not inspect exit code. Callers needing partial output on timeout do not get a result.

Test signals: helper-only file; many tests rely on it to validate cgroup files, mounts, and runtime state inside containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/exec.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/ns.go -->
# sources/cloud-native/moby/integration/internal/container/ns.go

Purpose: helper for retrieving a container's Linux namespace identifier/path from `docker inspect` state.

Important APIs and helpers: `GetContainerNS(ctx, t, apiClient, cID, nsName)` calls `ContainerInspect` and returns `inspect.Container.NetworkSettings.SandboxKey`.

Control flow: the function asserts inspect succeeds and then switches on `nsName`. Currently only `net` is supported; any other namespace name fails the test.

State and persistence: reads container inspect state only. It does not mutate daemon state.

Dependencies and integration: depends on Moby API client, testing assertions, and network sandbox metadata populated for containers.

Risks: despite a generic `nsName` parameter, only network namespace is implemented. Tests using other namespace names fail immediately.

Test signals: helper-only; provides a common way for network integration tests to locate container network namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/ns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/ops.go -->
# sources/cloud-native/moby/integration/internal/container/ops.go

Purpose: functional-option library for constructing `TestContainerConfig` values used by integration container helpers.

Important APIs and helpers: `ConfigOpt` plus option functions including `WithName`, `WithHostname`, `WithLinks`, `WithImage`, `WithCmd`, `WithNetworkMode`, `WithDNS`, `WithSysctls`, `WithPublishAllPorts`, `WithExposedPorts`, `WithPortMap`, `WithTty`, `WithWorkingDir`, `WithMount`, `WithVolume`, `WithBind`, `WithBindRaw`, `WithTmpfs`, `WithMacAddress`, `WithIPv4`, `WithIPv6`, `WithEndpointSettings`, `WithLogDriver`, `WithAutoRemove`, `WithPidsLimit`, `WithRestartPolicy`, `WithUser`, `WithAdditionalGroups`, `WithPrivileged`, `WithCgroupnsMode`, `WithExtraHost`, `WithPlatform`, `WithWindowsDevice`, `WithIsolation`, `WithConsoleSize`, `WithAnnotations`, `WithRuntime`, `WithCDIDevices`, `WithCapability`, `WithDropCapability`, `WithSecurityOpt`, `WithPIDMode`, `WithStopSignal`, and `WithHostConfig`.

Control flow: each option mutates one part of `TestContainerConfig`: container config, host config, networking config, endpoint settings, platform, mounts, capabilities, devices, or raw host config replacement. IP/MAC options ensure endpoint settings exist before mutation.

State and persistence: no direct daemon state; options shape subsequent `ContainerCreate` requests. Some options append to slices and may accumulate when multiple options target the same field.

Dependencies and integration: depends on Moby container/network/mount types, NAT port parsing, `netip`, and OCI platform. It integrates with `NewTestConfig`, `Create`, and `Run`.

Risks: `WithHostConfig` replaces the whole host config and can discard earlier options if applied later. Several options initialize maps/slices lazily, so order can matter when callers pass overlapping settings.

Test signals: helper-only; correctness affects a broad range of integration tests by generating API request shapes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/states.go -->
# sources/cloud-native/moby/integration/internal/container/states.go

Purpose: polling predicates for common container states in integration tests.

Important APIs and helpers: `RunningStateFlagIs`, `IsStopped`, `IsInState`, `IsSuccessful`, and `IsRemoved`.

Control flow: predicates call `ContainerInspect` and return `poll.Success`, `poll.Continue`, or `poll.Error` based on running flag, status membership, exit code, or not-found classification. `IsStopped` is a specialization for `StateExited`; `IsSuccessful` requires exit code 0; `IsRemoved` succeeds on not found.

State and persistence: reads daemon container inspect state and interprets status/exit code. It does not mutate state.

Dependencies and integration: depends on Moby client, container state types, containerd error definitions, and gotest `poll`.

Risks: polling predicates surface non-not-found inspect errors as hard errors. `IsInState` treats any listed state as success but does not check health or restart count.

Test signals: helper-only; provides consistent wait behavior across container lifecycle tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/container/states.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/image/load.go -->
# sources/cloud-native/moby/integration/internal/image/load.go

Purpose: helper for loading generated OCI image layouts into a daemon during integration tests.

Important APIs and helpers: `Load(ctx, t, apiClient, imageFunc)` where `imageFunc` is a `specialimage.SpecialImageFunc`.

Control flow: creates a temp directory, calls the special image builder to write an OCI layout and return an index, archives the directory, calls `ImageLoad` with quiet output, drains and closes the response, and returns the digest string of the first manifest in the returned index.

State and persistence: writes temporary OCI layout files and imports them into the daemon image store. The returned digest identifies the loaded image content.

Dependencies and integration: depends on specialimage builders, archive/tar helper, image load API, OCI index descriptors, and testing assertions.

Risks: assumes the generated index has at least one manifest. It drains load output but does not parse load messages, so it trusts API success.

Test signals: helper-only; enables many image integration tests to construct precise content, platform, layer, label, and attestation scenarios.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/image/load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/dns.go -->
# sources/cloud-native/moby/integration/internal/network/dns.go

Purpose: lightweight DNS test helper that generates resolv.conf content and starts a minimal UDP DNS responder.

Important APIs and constants: `DNSRespAddr`, `GenResolvConf`, and `StartDaftDNS`.

Control flow: `GenResolvConf` returns a single nameserver line. `StartDaftDNS` listens on UDP address `addr`, starts a goroutine that reads packets, unpacks DNS messages with `miekg/dns`, creates a reply with one A record for each question pointing to `DNSRespAddr`, and writes the response.

State and persistence: opens a UDP socket for the lifetime of the test and closes it through `t.Cleanup`. No persistent state is written.

Dependencies and integration: depends on `github.com/miekg/dns`, `net.ListenPacket`, and testing cleanup. It integrates with network tests requiring deterministic DNS responses.

Risks: the server ignores read/write/unpack/pack errors by continuing, so failures may manifest as client timeouts. It returns A records regardless of question type.

Test signals: helper-only; useful for validating daemon/container DNS plumbing against a predictable local resolver.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/dns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/l2disco_linux.go -->
# sources/cloud-native/moby/integration/internal/network/l2disco_linux.go

Purpose: Linux packet-capture helpers for collecting and decoding layer-2 discovery traffic such as unsolicited ARP and IPv6 neighbor advertisements.

Important APIs and types: `TimestampedPkt`, `CollectBcastARPs`, `CollectICMP6`, `collectPackets`, `UnpackUnsolARP`, and `UnpackUnsolNA`.

Control flow: collectors open AF_PACKET raw sockets on an interface, filter by ARP or ICMPv6 ethertype, start a goroutine reading packets with timestamps, and return a stop function that closes the socket and returns collected packets. `UnpackUnsolARP` parses Ethernet/ARP fields and returns sender hardware/protocol addresses for broadcast gratuitous ARP-like packets. `UnpackUnsolNA` parses Ethernet/IPv6/ICMPv6 neighbor advertisement and target link-layer option.

State and persistence: keeps captured packets in memory until stop. It opens raw sockets and reads live kernel network traffic.

Dependencies and integration: depends on Linux syscalls, `x/sys/unix`, `net`, `netip`, `encoding/binary`, and interface names from network tests.

Risks: Linux-only and requires permissions for raw packet sockets. Packet parsing is intentionally narrow and returns errors for unexpected lengths/types/options. Collection goroutine behavior depends on closing the socket to unblock reads.

Test signals: helper-only; enables tests to assert that network drivers emit expected L2 discovery packets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/l2disco_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/network.go -->
# sources/cloud-native/moby/integration/internal/network/network.go

Purpose: shared wrappers for network create, inspect, and remove operations in integration tests.

Important APIs and helpers: `createNetwork`, `Create`, `CreateNoError`, `Inspect`, `InspectNoError`, and `RemoveNoError`.

Control flow: `createNetwork` builds `client.NetworkCreateOptions`, applies option functions, calls `NetworkCreate`, and returns the network ID. `Create` exposes the error-returning form. `CreateNoError`, `InspectNoError`, and `RemoveNoError` wrap client calls with test assertions.

State and persistence: creates and removes daemon network objects and reads network inspect state. The helper itself persists no state.

Dependencies and integration: depends on Moby API client network methods, network create/inspect option types, and gotest assertions.

Risks: assertion wrappers are unsuitable for tests that need to inspect expected errors. `Create` returns ID only, not the full create response warnings.

Test signals: helper-only; centralizes network setup and teardown for integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/network.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/ops.go -->
# sources/cloud-native/moby/integration/internal/network/ops.go

Purpose: functional options for constructing `client.NetworkCreateOptions` in integration tests.

Important APIs and helpers: `WithDriver`, `WithIPv4`, `WithIPv6`, `WithIPv4Disabled`, `WithIPv6Disabled`, `WithInternal`, `WithConfigOnly`, `WithConfigFrom`, `WithAttachable`, `WithScope`, `WithMacvlan`, `WithMacvlanPassthru`, `WithIPvlan`, `WithOption`, `WithIPAM`, `WithIPAMRange`, and `WithIPAMConfig`.

Control flow: each option mutates create options by setting flags, driver names, options map entries, or IPAM config. `WithIPAMRange` parses subnet/iprange/gateway strings into `netip` values and delegates to `WithIPAMConfig`.

State and persistence: no direct state; options shape subsequent network creation and can cause daemon network objects to persist if used by create helpers.

Dependencies and integration: depends on Moby network API types, `netip`, and client network create options. It integrates with `network.Create` and tests for bridge/macvlan/ipvlan/IPAM behavior.

Risks: parsing helpers use `MustParse`, so invalid input panics. Options that set `Options` maps can overwrite previous map values if not careful, especially `WithMacvlan`.

Test signals: helper-only; ensures tests build network create requests consistently.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/ops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/states.go -->
# sources/cloud-native/moby/integration/internal/network/states.go

Purpose: polling predicate for network removal.

Important APIs and helpers: `IsRemoved(ctx, apiClient, networkID)` returns a gotest poll check.

Control flow: the predicate calls `NetworkInspect`. If the network is not found it returns success; any other error is a poll error; an existing network returns continue.

State and persistence: reads daemon network state only.

Dependencies and integration: depends on Moby network API client, containerd error classification, and gotest poll.

Risks: only distinguishes not-found from all other errors. It does not validate that dependent endpoints are gone beyond inspect failure.

Test signals: helper-only; used to wait for asynchronous network deletion.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/network/states.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/process/wait.go -->
# sources/cloud-native/moby/integration/internal/process/wait.go

Purpose: polling predicate for waiting until an OS process is no longer alive.

Important APIs and helpers: `NotAlive(pid int)` returns a gotest poll check that uses `system.IsProcessAlive`.

Control flow: each poll call checks the PID. If alive, it continues; if not alive, it succeeds.

State and persistence: reads host process state only. It does not signal or reap processes.

Dependencies and integration: depends on Moby internal system process helper and gotest poll.

Risks: PID reuse can theoretically produce false continues if another process reuses the PID before the check. The helper assumes `IsProcessAlive` captures platform-specific process existence correctly.

Test signals: helper-only; supports live-restore tests waiting for container processes to exit while the daemon is stopped.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/process/wait.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/requirement/requirement.go -->
# sources/cloud-native/moby/integration/internal/requirement/requirement.go

Purpose: shared requirement helpers for conditionally running integration tests based on environment capabilities.

Important APIs and helpers: `HasHubConnectivity(t)` plus platform-specific functions implemented in companion files.

Control flow: `HasHubConnectivity` calls `testutil.CheckHubConnectivity`, logs the error through `t.Logf` when unavailable, and returns a boolean.

State and persistence: no persistent state; it performs network/environment probing.

Dependencies and integration: depends on Moby internal testutil connectivity checks and testing logging. It is intended for skip decisions in tests requiring Docker Hub.

Risks: connectivity checks can be flaky due to network conditions, proxy configuration, or registry availability. Returning bool leaves skip/fail policy to callers.

Test signals: helper-only; improves test gating for external registry dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/requirement/requirement.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/requirement/requirement_linux.go -->
# sources/cloud-native/moby/integration/internal/requirement/requirement_linux.go

Purpose: Linux-specific requirement helpers for cgroup namespaces and overlayfs/overlay2 support.

Important APIs and helpers: `CgroupNamespacesEnabled`, `overlayFSSupported`, and `Overlay2Supported`.

Control flow: `CgroupNamespacesEnabled` checks for `/proc/self/ns/cgroup`. `overlayFSSupported` runs `modprobe overlay` and treats success as support. `Overlay2Supported` parses a kernel version and returns true for kernels newer than or equal to 4.0, or RHEL/CentOS 3.10 kernels with the supported patch level.

State and persistence: reads procfs and may load the overlay kernel module through `modprobe`, changing kernel module state.

Dependencies and integration: depends on `os.Stat`, `exec.Command`, and kernel version comparison helpers from Moby daemon graphdriver overlay2 package.

Risks: `modprobe overlay` may require privileges and can have side effects. Kernel-version logic encodes distribution-specific compatibility assumptions.

Test signals: helper-only; used to skip or gate tests requiring cgroup namespaces or overlay2.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/requirement/requirement_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/requirement/requirement_windows.go -->
# sources/cloud-native/moby/integration/internal/requirement/requirement_windows.go

Purpose: Windows stubs for requirement helpers that are Linux-specific.

Important APIs and helpers: `overlayFSSupported` and `Overlay2Supported`.

Control flow: both functions return false unconditionally on Windows.

State and persistence: no state is read or written.

Dependencies and integration: no imports. Build tag `windows` selects this file for Windows builds.

Risks: any test using these helpers on Windows will see overlay support as unavailable, which is appropriate for overlay2-specific Linux behavior.

Test signals: helper-only; ensures requirement package compiles and produces conservative answers on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/requirement/requirement_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/swarm/service.go -->
# sources/cloud-native/moby/integration/internal/swarm/service.go

Purpose: shared helpers for starting swarm-mode daemons, creating service specs/services, polling, and executing commands in service tasks.

Important APIs and helpers: `ServicePoll`, `NetworkPoll`, `NewSwarm`, `ServiceSpecOpt`, `CreateService`, `CreateServiceSpec`, `ServiceWithMode`, `ServiceWithInit`, `ServiceWithImage`, `ServiceWithCommand`, `ServiceWithConfig`, `ServiceWithSecret`, `ServiceWithReplicas`, `ServiceWithMaxReplicas`, `ServiceWithPlacementConstraints`, `ServiceWithName`, `ServiceWithNetwork`, `ServiceWithEndpoint`, `ServiceWithSysctls`, `ServiceWithCapabilities`, `ServiceWithPidsLimit`, `ServiceWithMemorySwap`, `ServiceWithMemorySwappiness`, `GetRunningTasks`, `ExecTask`, and resource-initialization helpers.

Control flow: `NewSwarm` starts a daemon with busybox, creates a client, and initializes swarm. Spec options ensure nested task/container/resources/placement fields exist before mutation. `CreateService` builds a spec and calls `ServiceCreate`. `GetRunningTasks` lists tasks filtered by service and running state. `ExecTask` finds the container ID from a task status, creates an exec, attaches it, and starts it.

State and persistence: creates a real daemon in swarm mode, swarm services, tasks, networks, configs/secrets references, and exec sessions. Spec helpers mutate in-memory service specs.

Dependencies and integration: depends on swarm API types, daemon harness, environment execution, client service/task/node APIs, poll settings, and container exec APIs.

Risks: helpers assert/fail directly and are not suited for expected-error tests. Swarm convergence is asynchronous, so callers must combine service creation with polling predicates from `states.go`.

Test signals: helper-only; centralizes service creation and task interaction for swarm integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/swarm/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/swarm/states.go -->
# sources/cloud-native/moby/integration/internal/swarm/states.go

Purpose: polling predicates for swarm task and node states.

Important APIs and helpers: `NoTasksForService`, `NoTasks`, `RunningTasksCount`, `JobComplete`, and `HasLeader`.

Control flow: task predicates call `TaskList` with relevant filters, inspect desired/current states, and return poll success or continue. `JobComplete` handles replicated-job and global-job modes by counting completed tasks against service replicas or node count, while continuing on pending/running tasks and erroring on failed tasks. `HasLeader` lists manager nodes and succeeds when a reachable leader is present.

State and persistence: reads swarm task/service/node state but does not mutate it. It interprets orchestrator convergence and job completion.

Dependencies and integration: depends on swarm API types, client task/node APIs, filters, errdefs, and gotest poll.

Risks: swarm state is eventually consistent; predicates must be used with suitable timeouts. `JobComplete` errors on any failed task, which is correct for tests expecting successful jobs but not for negative-job tests.

Test signals: helper-only; provides high-level readiness/completion checks for swarm integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/swarm/states.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/system/goroutines.go -->
# sources/cloud-native/moby/integration/internal/system/goroutines.go

Purpose: polling helpers for daemon goroutine-count stability and leak checks.

Important APIs and helpers: `WaitForStableGoroutineCount`, `StableGoroutineCount`, `CheckGoroutineCount`, and `getGoroutineNumber`.

Control flow: `getGoroutineNumber` calls `SystemInfo` and extracts `NGoroutines`. `StableGoroutineCount` stores the first observed count and succeeds only when subsequent polls match it, otherwise updates the count and continues. `WaitForStableGoroutineCount` wraps that predicate and returns the stabilized count. `CheckGoroutineCount` succeeds when the current count equals the expected value and continues otherwise.

State and persistence: reads daemon system info only. The expected/stable count is kept in caller-provided or local memory between poll attempts.

Dependencies and integration: depends on Moby `SystemAPIClient`, system info response, and gotest poll settings.

Risks: goroutine counts naturally fluctuate in busy daemons, so tests must choose timeouts and quiet conditions carefully. Equality checks are strict and can be flaky if background activity is expected.

Test signals: helper-only; supports integration tests that need to detect goroutine leaks or wait for daemon quiescence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/internal/system/goroutines.go -->
