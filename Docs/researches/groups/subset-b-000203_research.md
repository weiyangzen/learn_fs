# subset-b-000203 research

Grouped research for the Moby integration container test files in subset B. Each file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/copy_linux_test.go -->
# sources/cloud-native/moby/integration/container/copy_linux_test.go

Purpose: Linux-only regression coverage for `docker cp` when the destination path traverses an absolute in-container symlink that is also part of a bind mount target, matching the `/var/run -> /run` class of layouts.

Important APIs and flow: `TestCopyWithAbsoluteSymlinkedMountTarget` builds a busybox image with `/sockets -> /root`, creates a host file using `testutil.TempDir`, bind-mounts it to `/sockets/docker.sock`, then calls `apiClient.CopyToContainer` with destination `/sockets/` and empty content. It uses `build.Do`, `fakecontext`, `container.Create`, `container.WithMount`, and `mounttypes.Mount`.

State and dependencies: The test creates an image, host temp file, and container metadata; cleanup is handled by test helpers. It depends on Linux behavior, bind mounts, symlink resolution, and daemon archive copy internals.

Risks and signals: It guards the security fix using `os.Root` from regressing into rejecting common absolute symlink paths. Passing signal is no error from `CopyToContainer`; failures indicate broken mount-target resolution for distro-style symlinks.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/copy_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/copy_test.go -->
# sources/cloud-native/moby/integration/container/copy_test.go

Purpose: Exercises container archive copy APIs for missing paths, non-directory paths, empty archives, UID/GID ownership mapping, symlink copy semantics, and a security regression around xz decompression.

Important APIs and flow: Tests call `CopyFromContainer`, `CopyToContainer`, `ContainerCreate`, `ImageBuild`, and `container.Exec`. `makeTestImage` builds a busybox image with `testuser:testgroup`; `makeEmptyArchive` uses `go-archive` `CopyInfoSourcePath`, `TarResource`, and `PrepareArchiveCopy`. `TestCopyFromContainer` builds a tree with files and symlinks, copies many path forms, and reads the returned tar stream with `archive/tar`. `TestCopyToContainerXZBinaryNotExecutedOnDaemon` launches a separate daemon with a secret env var, injects a fake `/usr/bin/xz` into the container image, uploads invalid xz-magic data, and asserts the container binary was not executed by dockerd.

State and dependencies: Builds temporary images and archives, creates containers, reads tar streams, and can start a child daemon for the security case. Uses platform skips for Windows and snapshotter limitations.

Risks and signals: It covers client/server path validation, archive preparation, root/user ownership propagation, symlink traversal rules, and daemon/container process boundary security. Failures may indicate API error-type drift, archive extraction regressions, or a critical decompressor execution bug.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/create_test.go -->
# sources/cloud-native/moby/integration/container/create_test.go

Purpose: Broad integration coverage for container creation validation, image identifier handling, host config validation, healthcheck constraints, platform selection, network endpoint behavior, MAC assignment, and containerd image metadata.

Important APIs and flow: Tests use `apiClient.ContainerCreate`, `ImageInspect`, `ContainerInspect`, `ContainerStart`, raw `request.Post`, and direct containerd client inspection. Cases cover missing images, image IDs with and without algorithms, links to missing containers, invalid env values, tmpfs targets, masked/readonly path defaults from `oci.DefaultSpec`, invalid healthcheck durations/retries, tmpfs overriding anonymous volumes, platform mismatch errors, `VolumesFrom`, invalid host config modes, JSON body validation, multi-endpoint API-version behavior, per-network MACs, and containerd-backed `ctr.Image`.

State and dependencies: The tests create and sometimes start containers, create networks, build no persistent custom daemon except containerd inspection through `Info().Containerd`. They depend on busybox, API versions, Linux-only behavior for proc paths/tmpfs/MACs, and containerd namespace details.

Risks and signals: This file is a high-value compatibility net for API validation and versioned behavior. It catches regressions in error typing, default OCI path persistence across start/inspect, platform manifest decisions, old/new network API contracts, and containerd metadata when snapshotter storage is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/daemon_linux_test.go -->
# sources/cloud-native/moby/integration/container/daemon_linux_test.go

Purpose: Linux daemon restart recovery tests for container startability, IPC-mode persistence, host-gateway resolution, restarting-state repair, and hard-reboot-like stale running state.

Important APIs and flow: The tests use `daemon.New`, `StartWithBusybox`, `Kill`, `Restart`, `TamperWithContainerConfig`, `ContainerInspect`, `ContainerStart`, and `ContainerWait`. `getContainerdShimPid` reads `/proc/<pid>/stat` to kill the shim. Other tests inspect `/etc/hosts`, compare `HostConfig.IpcMode`, and mutate daemon container state using `realcontainer.Container` methods.

State and dependencies: These tests create isolated dockerd instances, kill daemon/shim/container processes, alter on-disk container state, and restart daemons with different flags such as `--default-ipc-mode` and `--host-gateway-ip`. They skip remote, Windows, and sometimes rootless modes.

Risks and signals: They guard restore paths after unclean shutdowns, restart policy reconciliation, health/state persistence, and default-setting changes after restart. Failures usually imply daemon startup cannot reconcile stale runtime metadata or cannot preserve already-created container configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/daemon_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/daemon_test.go -->
# sources/cloud-native/moby/integration/container/daemon_test.go

Purpose: Cross-file daemon restart tests for cleanup after unclean daemon termination, focused on killing stuck containers and clearing stale network state.

Important APIs and flow: `TestContainerKillOnDaemonStart` starts an isolated daemon, runs a long-lived container, kills dockerd, restarts it, and checks the container is no longer running. `TestNetworkStateCleanupOnDaemonStart` adds exposed port bindings, verifies `SandboxID`, `SandboxKey`, and port mappings exist, kills dockerd, restarts, and verifies those network settings are cleared. It uses `daemon.New`, `container.Run`, `ContainerInspect`, `ContainerRemove`, and `network.MustParsePort`.

State and dependencies: The tests persist container metadata across daemon death and restart, then assert daemon startup reconciliation. They require a local, non-Windows, non-rootless daemon because they manage dockerd directly and inspect host-side network cleanup behavior.

Risks and signals: They detect stale runtime/network state after daemon crash or live-restore-like conditions. Failures can leave containers incorrectly marked running or port/network settings still attached after runtime state is gone.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/devices_windows_test.go -->
# sources/cloud-native/moby/integration/container/devices_windows_test.go

Purpose: Windows-only validation that `HostConfig.Devices` entries are propagated to HCS/hcsshim for process and Hyper-V isolation.

Important APIs and flow: `TestWindowsDevices` enumerates device string forms such as `class/<GUID>`, `class://<GUID>`, and `vpci-class-guid://<GUID>`, combines them with `container.WithWindowsDevice` and `container.WithIsolation`, creates containers, starts them, then execs a shell command that searches for `HostDriverStore/FileRepository`. It handles expected Hyper-V start failures for non-containerd runtime.

State and dependencies: Creates Windows containers with device assignments and isolation-specific host config. The observable external state is the mounted Windows driver store path. It depends on Windows daemon OS type, runtime type, and a well-known class GUID from Windows device definitions.

Risks and signals: Passing tests show device strings survive API-to-runtime translation and produce the expected mount. Failures can indicate device assignment regressions, Hyper-V support differences, or environment setup limitations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/devices_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/diff_test.go -->
# sources/cloud-native/moby/integration/container/diff_test.go

Purpose: Verifies `ContainerDiff` reports filesystem changes for running or stopped containers after creating a directory and file.

Important APIs and flow: `TestDiff` runs a container that creates `/foo/bar`, waits for it to stop, then calls `apiClient.ContainerDiff` and compares exact `FilesystemChange` entries. `TestDiffStoppedContainer` repeats the stopped-container path and includes Windows-specific expected shape, though Windows is skipped because change kinds and path prefixes differ.

State and dependencies: The tests mutate a container writable layer and then inspect diff output. They depend on busybox shell commands and storage-driver diff semantics.

Risks and signals: They catch regressions in change ordering, add/modify classification, and stopped-container diff availability. Failures are strong signals that the daemon's layer differ has changed user-visible API output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/diff_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/exec_afalg_linux_test.go -->
# sources/cloud-native/moby/integration/container/exec_afalg_linux_test.go

Purpose: Linux security integration tests ensuring restricted socket families cannot be created by exec processes under the default security profile.

Important APIs and flow: Embedded C fixtures `af_alg.c`, `af_vsock.c`, and `socketcall.c` are copied into a Debian container, compiled with `gcc`, and executed as UID 1000. `compileAndExecSocketDenied` writes source via `ExecT`, compiles, runs the binary with `ExecCreateOptions.User`, and expects exit code 1 plus EPERM/EACCES output. The `socketcall_int80` path only runs on amd64 with AppArmor or SELinux and verifies AF_ALG denial while AF_INET still succeeds.

State and dependencies: The test installs packages with `apt-get` in a running `debian:trixie-slim` container. It depends on seccomp, LSM security options, Linux headers, compiler availability, and architecture-specific syscall behavior.

Risks and signals: It catches high-impact sandbox escapes or overblocking in seccomp/LSM socket filtering, especially the ia32 `int $0x80` compatibility path that seccomp cannot inspect by argument pointer.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/exec_afalg_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/exec_linux_test.go -->
# sources/cloud-native/moby/integration/container/exec_linux_test.go

Purpose: Linux-specific exec behavior tests for initial console size and standard failed-exec exit codes.

Important APIs and flow: `TestExecConsoleSize` requires API v1.42, runs busybox, creates an exec with TTY and `ConsoleSize{Height:57, Width:123}`, runs `stty size`, and expects `57 123`. `TestFailedExecExitCode` runs invalid commands and checks exit codes 127 for executable not found and 126 for invoking a non-executable directory.

State and dependencies: Uses running containers and exec sessions only; no persistent state beyond containers cleaned by helpers. Depends on Linux TTY behavior and busybox utilities.

Risks and signals: It guards API-to-runtime terminal sizing and POSIX-compatible exit-code mapping. Failures may point to runtime exec setup regressions or changed error handling for failed process creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/exec_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/exec_test.go -->
# sources/cloud-native/moby/integration/container/exec_test.go

Purpose: Cross-platform exec API coverage for stdin EOF handling, working directory and environment propagation, exec resize validation, user/group resolution, and additional group preservation.

Important APIs and flow: Tests use `ExecCreate`, `ExecAttach`, `ExecInspect`, `ExecStart`, `ExecResize`, raw `POST /exec/<id>/resize`, and helper `container.Exec`. `TestExecWithCloseStdin` attaches to `cat`, calls `CloseWrite`, and waits for output. `TestExec` verifies exec-specific `WorkingDir` and env. `TestExecResize` covers success, raw query validation errors, unknown exec ID, and stopped-container conflict. `TestExecUser` builds images missing `/etc/group` or `/etc/passwd` and checks user parsing errors or `id` output. `TestExecWithGroupAdd` verifies group-add survives exec with a configured user.

State and dependencies: Builds temporary busybox variants, runs containers with TTY/user/group settings, and exercises raw HTTP to bypass client-side validation.

Risks and signals: The file guards attach stream lifetimes, API validation, identity lookup compatibility, and runtime exec setup. Failures can cause hangs, broken terminal resizing, or privilege/user mapping regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/export_test.go -->
# sources/cloud-native/moby/integration/container/export_test.go

Purpose: Validates container rootfs export and import, including export after daemon restart.

Important APIs and flow: `TestExportContainerAndImportImage` runs a container, waits for stop, calls `ContainerExport`, feeds the stream into `ImageImport`, decodes a `jsonstream.Message`, and compares its status to an `ImageList` result filtered by reference. `TestExportContainerAfterDaemonRestart` uses a child daemon, creates a container, restarts dockerd, and ensures `ContainerExport` still returns a stream.

State and dependencies: Creates a new image reference through import and exercises daemon metadata persistence across restart. Skips Windows and remote daemon for restart control.

Risks and signals: It detects broken export streams, image import output mismatch, and failure to export containers created before the current daemon process. It is a storage metadata and tar stream integration signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/export_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/health_test.go -->
# sources/cloud-native/moby/integration/container/health_test.go

Purpose: Tests healthcheck execution semantics: working directory inheritance, signal interaction, timeout process cleanup/logging, and start interval behavior.

Important APIs and flow: Tests create containers with `HealthConfig` fields and poll `ContainerInspect().State.Health`. `TestHealthCheckWorkdir` expects a shell healthcheck to run in `/foo`. `TestHealthKillContainer` toggles a file with `SIGUSR1` and ensures healthchecks continue after signals. `TestHealthCheckProcessKilled` expects timeout log text from a killed healthcheck. `TestHealthStartInterval` verifies fast `StartInterval` checks during `StartPeriod`, then normal `Interval` spacing after healthy. Helpers `pollForHealthCheckLog` and `pollForHealthStatus` centralize inspect polling.

State and dependencies: Uses container files under `/health` and `/tmp/health`, health log persistence, and time-sensitive polling. Windows is skipped where shell/signals do not apply.

Risks and signals: It catches regressions in health monitor scheduling, exec timeout handling, signal handling, and health status/log persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/inspect_test.go -->
# sources/cloud-native/moby/integration/container/inspect_test.go

Purpose: Container inspect API tests for annotations, network alias defaults, image manifest platform metadata, and raw JSON/size fields.

Important APIs and flow: `TestInspectAnnotations` creates a container with host config annotations and verifies inspect preserves them. `TestNetworkAliasesAreEmpty` creates containers on default network modes and expects nil aliases. `TestInspectImageManifestPlatform` runs only on Linux snapshotter storage, compares inspect `ImageManifestDescriptor.Platform` with image inspect platform, and verifies API v1.47 hides the field. `TestContainerInspectWithRaw` calls inspect with and without `Size`, unmarshals `Raw`, and checks `SizeRw`/`SizeRootFs` presence.

State and dependencies: Creates containers and reads image metadata. Platform tests rely on snapshotter mode and frozen test images.

Risks and signals: It guards versioned inspect fields, raw payload fidelity, platform manifest propagation, and nil-vs-empty network alias semantics. Failures can break API clients relying on stable JSON shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/ipcmode_linux_test.go -->
# sources/cloud-native/moby/integration/container/ipcmode_linux_test.go

Purpose: Linux IPC namespace and `/dev/shm` behavior tests for container modes, daemon defaults, config-file defaults, and older-client compatibility.

Important APIs and flow: `testIpcCheckDevExists` scans host `/proc/self/mountinfo` for a major:minor pair. `testIpcNonePrivateShareable` starts a container with `IpcMode` and checks the container's `/dev/shm` mount pair against host mountinfo. `testIpcContainer` validates `--ipc=container:<id>` works only with shareable donors. Host mode writes to `/dev/shm` and reads from the host. Daemon default tests start child daemons with `--default-ipc-mode` or config files. `TestIpcModeOlderClient` uses API v1.39 to assert legacy shareable default.

State and dependencies: Uses running containers, host `/dev/shm`, daemon restarts, and config files. Skips remote, user namespace, and rootless cases where host IPC sharing is unavailable.

Risks and signals: It catches IPC isolation/sharing regressions, daemon default persistence bugs, and API compatibility breaks for pre-1.40 clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/ipcmode_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/isolation_windows_test.go -->
# sources/cloud-native/moby/integration/container/isolation_windows_test.go

Purpose: Windows isolation coverage for process and Hyper-V containers, including lifecycle, exec, filesystem, network, environment, resource settings, volume mounts, and coexistence.

Important APIs and flow: Tests run containers with `container.WithIsolation(IsolationProcess)` or `IsolationHyperV` and long-running `ping`. Validation functions inspect `HostConfig.Isolation` and `State.Running`, exec `cmd` or `ping`, create/read files, inspect environment variables and CPU count, and check resource fields such as `CPUShares`, `NanoCPUs`, `Memory`, and `CPUCount`. Volume coverage creates a named volume and mounts it at `C:\data`; Hyper-V resource coverage checks memory configuration.

State and dependencies: Creates Windows containers, named volumes, files inside containers, and isolated runtime state. It assumes Windows images and commands are available; timeouts are longer for Hyper-V.

Risks and signals: It provides broad Windows runtime smoke and configuration persistence coverage. Failures can reveal isolation-mode regressions, HCS execution problems, resource config loss, or volume mount failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/isolation_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/kill_test.go -->
# sources/cloud-native/moby/integration/container/kill_test.go

Purpose: Tests container kill API signal validation, state transitions, restart-policy interactions, user handling, and OOMKilled inspect flags.

Important APIs and flow: `TestKillContainerInvalidSignal` sends invalid signals and asserts errors without changing running state. `TestKillContainer` covers default kill, non-killing signal, and SIGTERM. `TestKillWithStopSignalAndRestartPolicies` checks whether a kill matching `StopSignal` disables restart while a different signal allows restart policy behavior. Additional tests cover killing stopped containers, killing containers running as another user, and inspect `State.OOMKilled` after memory exhaustion.

State and dependencies: Uses running containers, restart policies, cgroup memory/swap limits, and inspect state. It skips Windows or unsupported cgroup conditions where behavior differs.

Risks and signals: It catches invalid signal validation, incorrect restart suppression, inability to signal non-root-user containers, and incorrect OOM state reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/kill_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/links_linux_test.go -->
# sources/cloud-native/moby/integration/container/links_linux_test.go

Purpose: Linux legacy-link and host-network checks for `/etc/hosts` content and linked-container names in list output.

Important APIs and flow: `TestLinksEtcHostsContentMatch` reads host `/etc/hosts`, runs a host-network container, cats `/etc/hosts` inside it, and expects exact content equality. `TestLinksContainerNames` runs two named containers, links the second to the first, lists containers filtered by the first name, and verifies the names include both the direct name and link alias path.

State and dependencies: Uses host network mode, local host filesystem, legacy links, and container list metadata. Skips remote daemon and Windows where unsupported.

Risks and signals: It guards legacy link name reporting and host network file behavior. Failures may break compatibility for old link-based workflows or indicate host-network mount/content changes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/links_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/list_test.go -->
# sources/cloud-native/moby/integration/container/list_test.go

Purpose: Container list API tests for ordering, annotations, since/before filters, image manifest platform metadata, and health summary versioning.

Important APIs and flow: `TestContainerList` removes existing containers, creates 64 containers, and expects descending creation order. `TestContainerList_Annotations` checks annotations are hidden in API v1.44 and present in v1.46. `TestContainerList_Filter` validates `since` and `before` filters around a middle container. `TestContainerList_ImageManifestPlatform` checks snapshotter-backed manifest platform fields. `pollForHealthStatusSummary` and `TestContainerList_HealthSummary` verify health appears only for API v1.52 and later.

State and dependencies: Creates many containers and one healthchecked container; uses request clients with pinned API versions. Snapshotter and Windows skips avoid unsupported metadata paths.

Risks and signals: It protects API ordering, filter semantics, versioned schema exposure, and list summary health fields. Failures directly affect CLI and API pagination/filter clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/logs_test.go -->
# sources/cloud-native/moby/integration/container/logs_test.go

Purpose: Validates container log retrieval across log drivers, TTY/no-TTY stream handling, stdout/stderr selection, and empty-tail follow behavior.

Important APIs and flow: `TestLogsFollowTailEmpty` runs a sleeping container and ensures `ContainerLogs` with stdout and `Tail: "2"` can be copied without EOF error. `TestLogs` runs `testLogs` for local and json-file drivers. Each case runs a command writing stdout and stderr, waits for stop, calls `ContainerLogs`, and either copies raw TTY output or demultiplexes with `stdcopy.StdCopy`. Windows TTY output is normalized through `termtest.StripANSICommands` with a Server 2019 special case.

State and dependencies: Creates short-lived containers using selected log drivers. Depends on daemon logging backends, stream multiplex framing, and Windows console behavior.

Risks and signals: It catches log-driver regressions, incorrect TTY stream filtering, stdout/stderr mixups, and edge cases with empty log tails.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/logs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/main_test.go -->
# sources/cloud-native/moby/integration/container/main_test.go

Purpose: Shared test harness for the `integration/container` package.

Important APIs and flow: `TestMain` configures tracing, creates the global `environment.Execution`, ensures frozen Linux images are available, prints the environment, runs tests, records tracing status, shuts tracing down, and exits with the test code. `setupTest` starts a per-test span from `baseContext`, protects shared test environment state with `environment.ProtectAll`, and registers cleanup through `testEnv.Clean`.

State and dependencies: Defines package globals `testEnv` and `baseContext`. It centralizes API client/environment access and cleanup for all tests in this package. Dependencies include `internal/testutil`, `internal/testutil/environment`, and OpenTelemetry.

Risks and signals: Any issue here impacts every container integration test. It controls image availability, environment isolation, and cleanup, so regressions can cause cross-test contamination, missing images, or incomplete tracing/cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/mounts_linux_test.go -->
# sources/cloud-native/moby/integration/container/mounts_linux_test.go

Purpose: Linux bind/volume mount integration tests for propagation, daemon-root mounts, recursive behavior, network file ownership, anonymous volumes, copy mount leakage, and recursive read-only semantics.

Important APIs and flow: Tests use `mounttypes.Mount`, raw bind strings, `syscall.Mount`, `moby/sys/mount`, `mountinfo`, `ContainerCreate`, `ContainerInspect`, `VolumeInspect`, `CopyFromContainer`, and API-versioned clients. They cover multiple mountinfo entries for one path, no chown on host network files, allowed propagation modes when mounting Docker root paths, recursive vs non-recursive bind mounts, shared/slave propagation, random anonymous volume names and labels, custom volume driver error forwarding, no extra mounts after copy, and read-only recursive defaults for API v1.44+.

State and dependencies: Creates host directories, bind mounts, submounts, volumes, and containers; cleanup unmounts host paths. Many tests skip remote/rootless/userns because host mount namespace control is required. Kernel 5.12 gates recursive read-only support.

Risks and signals: This file guards high-risk host filesystem behavior where regressions can leak mounts, mutate host ownership, break propagation, or change API-versioned read-only behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/mounts_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/nat_test.go -->
# sources/cloud-native/moby/integration/container/nat_test.go

Purpose: Network address translation tests for published ports via external address, localhost, and container-shared network namespace.

Important APIs and flow: `startServerContainer` runs a netcat listener with exposed port and explicit `PortBindings`. `TestNetworkNat` dials the host `eth0` address and reads the expected message. `TestNetworkLocalhostTCPNat` dials `localhost`. `TestNetworkLoopbackNat` runs a second container sharing the server container network namespace and connects to the host external address. `getExternalAddress` selects the first IPv4 on `eth0` when available.

State and dependencies: Uses host networking stack, published ports, netcat in busybox, and the make-test integration environment exposing `eth0`. Skips remote and some Windows/GitHub Actions cases.

Risks and signals: It catches port publishing/NAT regressions for localhost, external host IP, and loopback through shared namespaces. Failures usually indicate libnetwork, iptables, rootlesskit, or host environment issues.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/nat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/overlayfs_linux_test.go -->
# sources/cloud-native/moby/integration/container/overlayfs_linux_test.go

Purpose: Linux overlayfs regression test ensuring container diff/export/copy operations do not produce kernel warnings about undefined overlay behavior.

Important APIs and flow: A container continuously appends to `/file`. For each operation (`ContainerDiff`, `ContainerExport`, `CopyToContainer`, `CopyFromContainer`), the test reads recent kernel logs before and after using `unix.Klogctl`, computes new lines with `diffDmesg`, and fails if overlayfs warning text mentions lowerdir, upperdir, or workdir in-use with undefined behavior.

State and dependencies: Requires local non-rootless Linux daemon and kernel log read permission. It uses a live mutating container and archive generation through `go-archive`.

Risks and signals: It detects daemon operations that mount overlay internals unsafely while a container is active. Failures indicate potential storage-driver correctness or data-integrity risks beyond ordinary API output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/overlayfs_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/pause_test.go -->
# sources/cloud-native/moby/integration/container/pause_test.go

Purpose: Pause/unpause API tests for state transitions, events, Windows unsupported behavior, and stopping a paused container.

Important APIs and flow: `TestPause` runs a container, records daemon time, pauses and unpauses it, inspects `State.Paused`, then consumes `Events` filtered by container and expects pause/unpause actions through `getEventActions`. `TestPauseFailsOnWindowsServerContainers` expects not implemented for Windows process isolation. `TestPauseStopPausedContainer` pauses then stops a Linux container and waits for stopped state.

State and dependencies: Uses cgroup freezer/pause support, daemon event stream, and inspect state. Skips Windows process isolation or cgroup-driver none cases.

Risks and signals: It guards correct state persistence and event emission for pause workflows. Failures can indicate broken cgroup integration, event stream ordering, or stop handling for paused containers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/pause_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/pidmode_linux_test.go -->
# sources/cloud-native/moby/integration/container/pidmode_linux_test.go

Purpose: Linux PID namespace tests for host mode and `container:<name>` mode.

Important APIs and flow: `TestPIDModeHost` reads host `/proc/1/ns/pid`, runs a host-PID container and a default container, then compares namespace links via `container.GetContainerNS`. `TestPIDModeContainer` validates three cases: non-existing target errors at create, non-running target creates but fails at start with an internal namespace-join error, and running target starts successfully.

State and dependencies: Uses namespace symlinks, running/stopped containers, and API create/start boundaries. Skips non-Linux and remote daemon for host namespace comparisons.

Risks and signals: It protects PID namespace mode validation timing and error reporting. Failures can mean containers join wrong namespaces, reject valid deferred cases, or misclassify missing/non-running target errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/pidmode_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/remove_test.go -->
# sources/cloud-native/moby/integration/container/remove_test.go

Purpose: Container removal tests for missing bind sources, anonymous volume cleanup, running-container conflicts, force removal, invalid IDs, and auto-remove cleanup after daemon restart.

Important APIs and flow: `dPath` maps Linux paths to Windows-style daemon paths. Tests create containers with bind mounts or anonymous volumes, remove host source directories, call `ContainerRemove` with `RemoveVolumes` or `Force`, and inspect container/volume absence with not-found errors. The daemon restart test runs an auto-remove top container on a child daemon and expects it gone after restart.

State and dependencies: Mutates host temp directories, daemon volumes, container metadata, and child-daemon state. Remote and Windows skips apply for local bind/remove and multi-daemon scenarios.

Risks and signals: It guards cleanup correctness and prevents stale container/volume metadata. Failures can leave leaked volumes, make `rm` fail after host path deletion, or allow unsafe removal semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/rename_test.go -->
# sources/cloud-native/moby/integration/container/rename_test.go

Purpose: Container rename API tests for stopped/running containers, invalid names, name reuse, anonymous-to-named DNS, legacy link metadata, same-name errors, and repeated renames.

Important APIs and flow: Tests use `ContainerRename`, `ContainerInspect`, `ContainerRemove`, `NetworkCreate`, and helper `container.Run`. Link-specific tests validate `HostConfig.Links` and alias lookup paths after renaming. `TestRenameAnonymousContainer` creates a custom network, renames an anonymous container, restarts it to register service discovery, and pings by the new name. Same-name and invalid-name tests assert expected errors without changing the current container identity.

State and dependencies: Creates named containers, custom networks, links, and network DNS state. Windows/remote skips apply where legacy links or local rename-link metadata are unsupported.

Risks and signals: It protects daemon name index consistency, DNS registration, and legacy link references. Failures may cause name leaks, broken service discovery, or corrupted link metadata after rename.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/rename_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/resize_test.go -->
# sources/cloud-native/moby/integration/container/resize_test.go

Purpose: Container TTY resize API tests for successful resize, raw query validation, and invalid container state.

Important APIs and flow: `TestResize` runs a TTY container and calls `ContainerResize` with height/width. It then uses raw `POST /containers/<id>/resize?h=...&w=...` requests to send unset, empty, nonnumeric, negative, and out-of-range values that the typed client would reject earlier, expecting HTTP 400 and specific error messages. The invalid-state case resizes a created but not running container and expects a conflict.

State and dependencies: Uses running or created containers and raw API responses. No persistent external state is used.

Risks and signals: It guards API parsing and error text for resize query parameters as well as runtime state validation. Failures may break CLI/user feedback or allow invalid terminal dimensions into runtime calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/resize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/restart_test.go -->
# sources/cloud-native/moby/integration/container/restart_test.go

Purpose: Restart behavior tests for daemon restart/live-restore interactions, health monitor recovery, auto-remove restart semantics, and client-request cancellation.

Important APIs and flow: `TestDaemonRestartKillContainers` runs matrix cases over live-restore on/off and daemon kill/stop, with containers that may have restart policies and healthchecks. It restarts dockerd and verifies running state and new healthchecks. `pollForNewHealthCheck` checks health log timestamps. `TestContainerWithAutoRemoveCanBeRestarted` restarts `--rm` containers and ensures removal only after kill/stop. `TestContainerRestartWithCancelledRequest` cancels a timed restart request, listens for a restart event, and verifies the container is running.

State and dependencies: Uses child daemons, event streams, restart policies, health files, and auto-remove metadata. Windows has retry accommodation for signal timing.

Risks and signals: It catches daemon lifecycle regressions where restart requests are aborted by client cancellation, health monitors are not restored, or auto-remove containers are removed too early.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/restart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/run_cgroupns_linux_test.go -->
# sources/cloud-native/moby/integration/container/run_cgroupns_linux_test.go

Purpose: Linux cgroup namespace tests for daemon defaults, privileged behavior, explicit host/private modes, invalid modes, and old API clients.

Important APIs and flow: `testRunWithCgroupNs` starts a child daemon with a default cgroup namespace mode, runs a container, and compares daemon and container namespace links. `testCreateFailureWithCgroupNs` expects create errors. Tests cover private default, privileged exceptions on cgroup v1, host default, explicit `host`, explicit `private`, privileged plus private, invalid mode, and API v1.39 compatibility with `DOCKER_MIN_API_VERSION=1.39`.

State and dependencies: Starts isolated dockerd instances with `daemon.WithDefaultCgroupNamespaceMode`, reads namespace identifiers, and requires `requirement.CgroupNamespacesEnabled`. Skips remote/non-Linux and cgroup-version-specific cases.

Risks and signals: It guards namespace isolation defaults and backwards compatibility. Failures can mean containers receive the wrong cgroup namespace, invalid values pass validation, or older clients lose expected host-mode behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/run_cgroupns_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/run_linux_test.go -->
# sources/cloud-native/moby/integration/container/run_linux_test.go

Purpose: Linux run-path tests spanning hostname/domainname, DNS, unprivileged networking sysctls, privileged devices, console size, alternate containerd shim runtimes, legacy MAC behavior, static IPs, workdir normalization, seccomp, writable cgroups, and shm size.

Important APIs and flow: Tests use `container.Run`, `Exec`, `ContainerLogs`, `daemon.New`, custom network helpers, raw legacy create requests, and `ContainerInspect`. They create host devices with `unix.Mknod`, symlink alternate shim names into PATH, create user networks/IPAM ranges, send deprecated `MacAddress` JSON for API v1.43, inject seccomp JSON, set `writable-cgroups`, and run a daemon with `--default-shm-size`.

State and dependencies: Heavy host integration includes local daemons, host `/dev`, containerd shim binaries, sysctls, cgroups, networks, and shm mounts. Many cases skip rootless, user namespace, remote, or non-Linux modes.

Risks and signals: This file is a broad run-time regression suite for runtime setup and API compatibility. It catches wrong namespace/sysctl/device setup, runtime lookup problems, security option parsing bugs, cgroup writability changes, and default shm-size persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/run_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/stats_test.go -->
# sources/cloud-native/moby/integration/container/stats_test.go

Purpose: Container stats API tests for one-shot/no-stream response shape and not-found errors.

Important APIs and flow: `TestStats` skips unsupported cgroup/memory environments, obtains daemon `Info`, runs a container, and calls `ContainerStats` with `Stream:false` and `IncludePreviousSample` true or false. It decodes exactly one `StatsResponse`, checks memory limit equals host `MemTotal`, checks whether `PreCPUStats` is zero or populated, and expects EOF on a second decode. `TestStatsContainerNotFound` verifies not-found errors for streaming and non-streaming stats calls.

State and dependencies: Uses cgroup memory accounting and a running container. It depends on stats JSON streaming behavior and host memory reporting.

Risks and signals: It guards client-visible stats response contracts, especially EOF behavior and previous CPU sample inclusion. Failures can break monitoring clients.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/stop_linux_test.go -->
# sources/cloud-native/moby/integration/container/stop_linux_test.go

Purpose: Linux-specific stop cancellation behavior test plus log polling helper.

Important APIs and flow: `TestStopContainerWithTimeoutCancel` runs a container trapping TERM and looping, starts `ContainerStop` with a cancellable context and timeout, waits until logs contain `received TERM`, cancels the client context, expects the request to return a canceled error while the container remains running, then waits for daemon-side stop timeout to stop it. `logsContains` reads `ContainerLogs`, demultiplexes stdout with `stdcopy.StdCopy`, and polls for the marker string.

State and dependencies: Uses signal traps, container logs, goroutines, context cancellation, and daemon stop timers. It is time-sensitive but local to one container.

Risks and signals: It guards the contract that canceling the HTTP request does not cancel the daemon's already-started stop operation. Failures can leave containers killed too early or never stopped after client disconnect.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/stop_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/stop_test.go -->
# sources/cloud-native/moby/integration/container/stop_test.go

Purpose: Stop API tests for restart-policy containers, timeout semantics, and raw HTTP status codes.

Important APIs and flow: `TestStopContainerWithRestartPolicyAlways` starts containers that continually restart, waits for running/restarting, then stops them and expects stopped state. `TestStopContainerWithTimeout` runs a command that sleeps then exits 42 and checks zero/short timeout force-kill exit code versus long/negative timeout graceful exit. `TestContainerAPIPostContainerStop` sends raw `POST /containers/<id>/stop` for running, already stopped, and missing containers, checking HTTP 204, 304, and 404 plus optional state.

State and dependencies: Uses restart policies, stop timeouts, inspect state, and raw API responses. Windows timeout behavior is skipped or has longer poll constants.

Risks and signals: It guards stop semantics for restart policy suppression, negative timeout as unlimited wait, and documented HTTP status behavior. Failures impact CLI stop and API compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/stop_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/af_alg.c -->
# sources/cloud-native/moby/integration/container/testdata/af_alg.c

Purpose: C fixture used by `exec_afalg_linux_test.go` to attempt creation and use of an `AF_ALG` socket inside a container.

Important APIs and flow: The program creates a `socket(AF_ALG, SOCK_SEQPACKET, 0)`, binds it to a `sockaddr_alg` requesting SHA1 hash, accepts an operation socket, writes `hello world`, reads the hash, prints success, and exits. Each syscall failure prints with `perror` and returns nonzero.

State and dependencies: It has no persistent state; it allocates two file descriptors and closes them. It depends on Linux kernel crypto socket headers and runtime permission to create AF_ALG sockets.

Risks and signals: In the security test, successful execution would be a failure because default container policy should deny AF_ALG for unprivileged users. The fixture provides a realistic socket path beyond mere `socket()` creation by exercising bind/accept/read/write if allowed.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/af_alg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/af_vsock.c -->
# sources/cloud-native/moby/integration/container/testdata/af_vsock.c

Purpose: Minimal C fixture used to verify `AF_VSOCK` socket creation is blocked inside a default Linux container.

Important APIs and flow: The program calls `socket(AF_VSOCK, SOCK_STREAM, 0)`, reports any error with `perror("socket")`, prints success if the socket is created, closes the descriptor, and exits.

State and dependencies: No persistence; one file descriptor is created if allowed. It depends on `<linux/vm_sockets.h>` and the kernel supporting the address family.

Risks and signals: The integration test expects this binary to fail as UID 1000 under default seccomp. If it succeeds, container isolation may allow guest/host vsock access unexpectedly. If compilation fails, the test environment lacks the required Linux headers.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/af_vsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/cdi/vendor1.yaml -->
# sources/cloud-native/moby/integration/container/testdata/cdi/vendor1.yaml

Purpose: Static CDI vendor spec fixture defining one injectable device for CDI-related container integration tests outside this work item.

Important structure: The YAML declares `cdiVersion: "0.3.0"`, `kind: "vendor1.com/device"`, and one device named `foo`. Its `containerEdits.env` adds `FOO=injected`.

State and dependencies: It is read as test data by CDI tests and has no runtime behavior by itself. It depends on CDI spec directory discovery and parser support for version 0.3.0.

Risks and signals: It is intentionally small but important for testing device discovery and environment injection. Schema drift, invalid kind/name fields, or env edit changes would alter CDI test expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/cdi/vendor1.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/socketcall.c -->
# sources/cloud-native/moby/integration/container/testdata/socketcall.c

Purpose: C fixture for testing the ia32 `socketcall(2)` compatibility path from an amd64 process, especially where seccomp cannot inspect socket arguments behind a userspace pointer.

Important APIs and flow: Compile-time macros `SOCK_FAMILY` and `SOCK_TYPE` choose the socket parameters. The program allocates an argument array below 4 GB with `mmap(... MAP_32BIT ...)`, invokes `int $0x80` with syscall number 102 and operation `SYS_SOCKET`, converts negative returns to `errno`, and reports success or `perror("socket")`.

State and dependencies: It uses one low-address mmap region and closes the socket on success. It depends on x86-compatible inline assembly, Linux syscall ABI, and compiler macro injection from the test.

Risks and signals: It exercises a subtle bypass surface: seccomp argument filtering cannot see the family through `socketcall`, so LSM enforcement must deny AF_ALG while allowing AF_INET. Fixture changes could weaken that security signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration/container/testdata/socketcall.c -->
