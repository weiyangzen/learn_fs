# subset-b-000199 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_cp_test.go

Purpose: integration coverage for `docker cp` container-to-host and general path handling. The suite protects historical security and behavior regressions around path traversal, rootfs-relative paths, symlink semantics, volumes, special container files, stdout tar output, and copying from created or stopped containers.

Important APIs/types/functions: `DockerCLICpSuite`, `TearDownTest`, `OnTimeout`, constants such as `cpTestPath`, `cpFullPath`, `cpContainerContents`, and `cpHostContents`, plus tests `TestCpGarbagePath`, `TestCpRelativePath`, `TestCpAbsolutePath`, `TestCpAbsoluteSymlink`, `TestCpFromSymlinkToDirectory`, `TestCpToSymlinkToDirectory`, `TestCpSymlinkComponent`, `TestCpVolumePath`, `TestCpToStdout`, and `TestCpSymlinkFromConToHostFollowSymlink`.

Control flow: most tests create a busybox container, seed files or symlinks, wait for setup completion, run `docker cp`, and compare host-side files or symlink targets. Traversal tests create matching host paths to ensure `../../..` and absolute paths cannot escape the container rootfs. Volume tests bind local paths, copy from named volumes, bind-mounted directories, and bind-mounted files, then compare host and copied bytes. The stdout test pipes `docker cp container:/path -` into `tar -vtf -`.

State and persistence: the tests mutate temporary host directories, container root filesystems, bind mounts, Docker-managed volumes, and container metadata. They intentionally verify that copying does not alter restartability, that created containers can still provide files, and that special files such as `/etc/resolv.conf`, `/etc/hosts`, and `/etc/hostname` are copied from the live container view.

Dependencies and integration points: uses the integration CLI helpers, `icmd`, `RunCommandPipelineWithOutput`, the local daemon guard, Unix-only capabilities where required, tar, `su`, bind mounts, and busybox shell commands. It exercises archive APIs indirectly through the CLI and daemon archive/extract endpoints.

Risks: path traversal and symlink resolution are security-sensitive. Tests depending on local bind mounts, `su`, Linux symlink behavior, or volume permissions are platform/userns constrained. The tests also assume busybox command availability and timing around exited containers.

Test signals: failures indicate regressions in cp path sanitization, symlink copy-vs-follow behavior, volume archive access, special-file materialization, tar stream output, container restart state after archive access, or `-L` symlink following.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_test.go

Purpose: integration coverage for host-to-container `docker cp` behavior, matching the copy matrix implemented by the archive package and adding container-specific checks for symlink destinations and read-only targets.

Important APIs/types/functions: methods on `DockerCLICpSuite`: `TestCpToSymlinkDestination`, matrix tests `TestCpToCaseA` through `TestCpToCaseJ`, `TestCpToErrReadOnlyRootfs`, and `TestCpToErrReadOnlyVolume`. These tests depend heavily on helpers from `docker_cli_cp_utils_test.go`: `makeTestContainer`, `makeTestContentInDir`, `cpPath`, `containerCpPath`, and error comparators.

Control flow: tests create host fixture trees, create containers with optional seeded content and workdirs, run `docker cp`, then use `docker start -a` or host bind-mount inspection to verify copied bytes. The A-J cases cover file-to-new-file, file-to-missing-directory error, overwrite, file into directory, directory creation, directory-to-file error, directory under existing directory, contents-only copy with `/.`, contents-only-to-file error, and contents-only into existing directory. Symlink destination checks verify that copying to symlinks writes through to targets without replacing the link.

State and persistence: host temp directories hold source fixtures, containers receive copied content in rootfs or bind-mounted volumes, and read-only tests assert that failed writes leave expected paths absent. Some checks use repeated container starts to confirm persisted filesystem content after copy.

Dependencies and integration points: integrates Docker CLI `cp`, `run`, `create`, and `start`, busybox shell/stat behavior, bind mounts via local daemon, and archive package error strings `ErrDirNotExists` and `ErrCannotCopyDir`.

Risks: host path trailing separator and `/.` intent are easy to regress. Symlink destination behavior is especially sensitive because replacing a symlink instead of its target would alter container state and could create security issues. Read-only rootfs and read-only volume errors depend on Linux mount semantics and user namespace constraints.

Test signals: failures isolate the copy matrix contract for host-to-container operations and show whether daemon extraction follows archive package semantics, preserves symlinks correctly, and rejects writes into immutable targets.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_unix_test.go

Purpose: Unix-only coverage for ownership and permission behavior when copying from host into containers, especially `docker cp -a` and user-namespace root mapping.

Important APIs/types/functions: `TestCpToContainerWithPermissions`, `TestCpCheckDestOwnership`, and `getRootUIDGID`. The tests use `syscall.Stat_t` to inspect host-side ownership on a bind mount and parse `testEnv.DaemonInfo.DockerRootDir` to infer remapped root UID/GID.

Control flow: the permission test creates fixture content with non-default ownership and modes, creates a named container that prints `stat -c '%u %g %a'`, copies a directory into `/` with `docker cp -a`, starts the container, and compares the reported ownership/mode values. The destination ownership test bind-mounts a temp directory, copies a file into it via the container path, stats the host file, and verifies ownership equals container root, accounting for userns remapping.

State and persistence: temporary host directories and bind mounts are mutated; container rootfs receives copied files. The tests assert persisted metadata, not just byte content.

Dependencies and integration points: Linux daemon, local daemon bind mounts, Unix ownership APIs, busybox `stat`, Docker root directory naming under user namespace remapping, and the CLI archive/extract path.

Risks: assumptions about Docker root directory naming are fragile if userns storage layout changes. Host filesystems that do not support chown or mode preservation can cause false failures. These tests are intentionally excluded on Windows.

Test signals: failures indicate regressions in metadata preservation for `docker cp -a`, incorrect root ownership during extraction into bind mounts, or broken userns remapping integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_to_container_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_utils_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_cp_utils_test.go

Purpose: shared fixtures and assertions for the `docker cp` integration suite. It models file trees with regular files, directories, symlinks, ownership, and permissions, and provides path builders that keep host and container path syntax distinct.

Important APIs/types/functions: `fileType`, `fileData`, `fileData.creationCommand`, `mkFilesCommand`, `defaultFileData`, `defaultMkContentCommand`, `makeTestContentInDir`, `testContainerOptions`, `makeTestContainer`, `makeCatFileCommand`, `cpPath`, `cpPathTrailingSep`, `containerCpPath`, `containerCpPathTrailingSep`, `runDockerCp`, `getTestDir`, `isCpDirNotExist`, `isCpCannotCopyDir`, `fileContentEquals`, `symlinkTargetEquals`, `containerStartOutputEquals`, and `defaultVolumes`.

Control flow: fixture generation can happen inside a container as a shell command or on the host through Go filesystem calls. `makeTestContainer` constructs `docker run --cidfile` arguments, applies volume/workdir/read-only options, seeds content when requested, and returns the created container ID. Assertion helpers read files, read symlink targets, or start a container and compare output.

State and persistence: creates temp directories, files, symlinks, ownership/mode metadata, Docker containers, and optional volumes. `defaultVolumes` creates different mount declarations for local and remote daemons because host bind mounts are not available remotely.

Dependencies and integration points: depends on `github.com/moby/go-archive` for expected copy errors, integration `cli`, `icmd`, platform checks, and busybox shell utilities. It is the common contract between copy matrix tests and lower-level archive package semantics.

Risks: shell command generation quotes only fixture-controlled values; new arbitrary fixture data would need careful escaping. `makeTestContentInDir` assumes parent directories appear before children in `defaultFileData`. Ownership changes are skipped on Windows and can fail on restricted filesystems.

Test signals: because many cp tests use these helpers, a failure here would cascade. The helper design makes path separator, trailing slash, symlink, and metadata assumptions explicit for regression tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_cp_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_create_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_create_test.go

Purpose: integration tests for `docker create` and related container configuration persistence. The suite checks argument parsing, host config, port bindings, labels, volumes, workdir creation, entrypoint clearing, stop configuration, and invalid option handling.

Important APIs/types/functions: `DockerCLICreateSuite`; tests `TestCreateArgs`, `TestCreateHostConfig`, `TestCreateWithPortRange`, `TestCreateWithLargePortRange`, `TestCreateEchoStdout`, `TestCreateVolumesCreated`, `TestCreateLabels`, `TestCreateLabelFromImage`, `TestCreateHostnameWithNumber`, `TestCreateRM`, `TestCreateModeIpcContainer`, `TestCreateStopSignal`, `TestCreateWithWorkdir`, `TestCreateWithInvalidLogOpts`, `TestCreateUnsetEntrypoint`, and `TestCreateStopTimeout`.

Control flow: tests run `docker create` with specific CLI flags, inspect JSON or Go-template fields, then sometimes start the container to verify runtime behavior. Build-backed tests create temporary images with labels or entrypoints. Port range tests unmarshal `HostConfig.PortBindings`; labels and stop options use inspect helpers.

State and persistence: creates containers, volumes, images, labels, host config, stop signals/timeouts, workdirs, and port binding metadata. Invalid log options are expected to leave no container behind.

Dependencies and integration points: Docker CLI, inspect JSON, `network.PortMap`, build helper, fake build contexts, local daemon volume inspection, IPC mode on Linux, and Windows-specific workdir behavior via daemon OSType checks.

Risks: the large port range test touches 65,535 bindings and can be expensive. Some checks parse CLI output or inspect partial fields. Workdir verification uses `docker cp`, coupling create behavior to archive support. Platform differences around Windows busybox entrypoints and workdir creation are explicitly handled.

Test signals: failures point to CLI parsing regressions, config serialization errors, port range expansion problems, image label merge precedence bugs, invalid config cleanup failures, or changed inspect schema.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_daemon_plugins_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_daemon_plugins_test.go

Purpose: Linux daemon tests for managed plugin lifecycle, plugin state restoration, live-restore behavior, volume plugin use, plugin filters, and plugin/volume references across restarts.

Important APIs/types/functions: methods on `DockerDaemonSuite`: `TestDaemonRestartWithPluginEnabled`, `TestDaemonRestartWithPluginDisabled`, `TestDaemonKillLiveRestoreWithPlugins`, `TestDaemonShutdownLiveRestoreWithPlugins`, `TestDaemonShutdownWithPlugins`, `TestDaemonKillWithPlugins`, `TestVolumePlugin`, `TestPluginVolumeRemoveOnRestart`, `TestPluginListFilterEnabled`, and `TestPluginListFilterCapability`.

Control flow: tests start an isolated daemon, install a known plugin image with permissions, optionally disabled, restart/kill/interrupt the daemon, and inspect `plugin ls` or host processes. Volume plugin tests create a plugin-backed volume, mount it into busybox, touch/list files, and remove the volume. Filter tests install disabled plugins and assert `plugin ls --filter` output.

State and persistence: plugin installation stores plugin metadata under daemon root and starts plugin processes. Enabled/disabled flags must persist across daemon restart. Volume references keep plugins in use until volumes are removed. Live-restore determines whether plugin processes survive daemon shutdown.

Dependencies and integration points: Linux build tag, amd64 and network requirements, daemon harness, external plugin image constants, `pgrep` for plugin processes, Unix signals, Docker plugin and volume CLIs.

Risks: network availability, architecture, and external plugin image availability affect reliability. Process-name matching with `pgrep -f` can be brittle. Cleanup must disable/remove plugins even after abnormal daemon termination.

Test signals: failures indicate broken plugin metadata restoration, incorrect live-restore process ownership, improper shutdown cleanup, plugin volume mount/remove issues, or bad plugin list filtering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_daemon_plugins_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_daemon_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_daemon_test.go

Purpose: broad Linux integration coverage for daemon startup flags, restart recovery, networking, logging, TLS, mount cleanup, live-restore, runtime configuration, reloadable settings, default resource settings, and plugin cleanup edge cases.

Important APIs/types/functions: `containerdSocket`, helper functions `createInterface`, `deleteInterface`, and `testDaemonStartIpcMode`, plus many `DockerDaemonSuite` tests. Major groups include restart policy and container state tests, bridge/IPv6/network allocator tests, log level/log driver tests, HTTPS/TLS tests, mount cleanup tests, live-restore tests, max concurrency and runtime reload tests, shm/default IPC tests, and `TestFailedPluginRemove`.

Control flow: tests start isolated daemons through the daemon harness, run containers, mutate daemon config files, send signals, restart/kill daemons, and inspect Docker state, logs, host mounts, cgroups, network interfaces, and TLS connections. Some tests directly invoke `ctr` against the supervised containerd socket to simulate daemon crashes and container task state transitions.

State and persistence: heavily exercises daemon root persistence: container names, restart policy, exit codes/errors, volumes, mounts, local volume metadata, paused/running state, runtime names, log files, Unix sockets, TLS listeners, network bridges, plugin metadata, and config reload state. Temporary config files, ext4 loopback filesystems, ptys, and host network interfaces are also created.

Dependencies and integration points: Docker and dockerd binaries, daemon test harness, `client` API, Build helper, `ctr`, containerd namespace, Linux networking tools, iptables, mount utilities, TLS fixture certs, cfssl helpers, pty, cgroups, syslog/log drivers, and platform/test environment gates.

Risks: this suite has high environmental sensitivity: root privileges, local daemon, network tools, free ports, cgroup mode, snapshotter behavior, TLS library error text, and host mount namespace visibility. Many tests are timing-based around daemon restart, config reload, and live-restore reconciliation.

Test signals: failures usually indicate daemon-level regressions: state not restored after restart, resources not cleaned after crash, unsafe or broken config reload, incorrect default runtime/resource propagation, logging/TLS startup regressions, network allocator bugs, or live-restore not reconciling container state.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_daemon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_events_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_events_test.go

Purpose: integration coverage for `docker events` historical queries, filters, formatting, object types, and event emission from containers, images, plugins, copy/archive operations, resize, attach, rename, commit, push, and daemon reloads.

Important APIs/types/functions: `DockerCLIEventSuite`; tests such as `TestEventsTimestampFormats`, `TestEventsContainerEvents`, `TestEventsContainerEventsAttrSort`, `TestEventsImageTag`, `TestEventsImagePull`, `TestEventsImageImport`, `TestEventsImageLoad`, `TestEventsPluginOps`, `TestEventsFilters`, `TestEventsFilterImageName`, `TestEventsFilterLabels`, `TestEventsFilterImageLabels`, `TestEventsFilterContainer`, `TestEventsCopy`, `TestEventsResize`, `TestEventsAttach`, `TestEventsFormat`, and daemon reload tests `TestDaemonEvents` and `TestDaemonEventsWithFilters`.

Control flow: tests capture daemon time, perform Docker operations, then run `docker events --since/--until` with filters and parse output using scan utilities or JSON decoding. Some tests run event streams with timeouts. Daemon reload tests start with config files, rewrite settings, send SIGHUP, and validate daemon reload event attributes.

State and persistence: relies on daemon event history and streaming state. Operations create and remove containers, tags, imported/loaded images, plugins, volumes via cp events, and daemon config labels. Saved image tar files and temp files are cleaned up.

Dependencies and integration points: event API types, event test parsing utilities, CLI/build helpers, Docker client resize API, private registry push path, network/pull availability, plugin image availability, and daemon time helpers.

Risks: event order and timestamp granularity are sensitive; several tests sleep to avoid second-level boundary issues. Output parsing depends on stable event text formatting and sorted attributes. Network, plugin, registry, and platform gates reduce portability.

Test signals: failures indicate missing or misfiltered events, event attribute formatting regressions, incorrect event IDs/actions for images/plugins/copy operations, broken JSON format output, or bad validation of event time windows and templates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_events_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_events_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_events_unix_test.go

Purpose: Unix-only event tests for terminal output cleanliness, OOM events, live event streaming, volume/network event types and filters, and daemon reload event filtering.

Important APIs/types/functions: `TestEventsRedirectStdout`, `TestEventsOOMDisableFalse`, `TestEventsOOMDisableTrue`, `TestEventsContainerFilterByName`, `TestEventsContainerFilterBeforeCreate`, `TestVolumeEvents`, `TestNetworkEvents`, `TestEventsContainerWithMultiNetwork`, `TestEventsStreaming`, `TestEventsImageUntagDelete`, `TestEventsFilterVolumeAndNetworkType`, `TestEventsFilterVolumeID`, `TestEventsFilterNetworkID`, `TestDaemonEvents`, and `TestDaemonEventsWithFilters`.

Control flow: tests start event listeners before or after actions, perform container/network/volume/image operations, and match actions by object ID/type. OOM tests run memory-consuming containers under memory limits and wait for either process exit or observed `oom`. Streaming tests use an observer with per-action channels. Redirect tests run through a pty and scan redirected output for control characters.

State and persistence: exercises event stream subscriptions, daemon event history, memory-limited containers, OOM state, network/volume create/connect/mount/unmount/destroy records, image delete/untag events, and daemon config reload events.

Dependencies and integration points: Linux daemon, memory and swap limit support, OOM control, pty, Unix signals, event observer helpers, Build helper, network and volume CLIs, and daemon harness with config reload.

Risks: OOM tests are flaky on constrained CI and are skipped in some environments. Live streaming is timing-sensitive and can fail if observer startup races with event emission. Volume and network event ordering depends on daemon internals.

Test signals: failures indicate event delivery/filtering regressions for Unix-only resource events, missing OOM notifications, control characters in redirected events output, broken live subscription matching, or daemon reload events not carrying expected attributes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_events_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_exec_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_exec_test.go

Purpose: integration coverage for `docker exec` behavior across interactive I/O, environment propagation, exit status, paused containers, TTY/stdin handling, cgroups, exec inspect lifecycle, links, mutable network files, users, privileges, readonly containers, ulimits, startup failures, and Windows PATH preservation.

Important APIs/types/functions: `DockerCLIExecSuite`; `TestExec`, `TestExecInteractive`, `TestExecAfterContainerRestart`, daemon-suite `TestExecAfterDaemonRestart`, `TestExecEnv`, `TestExecSetEnv`, `TestExecExitStatus`, `TestExecPausedContainer`, `TestExecTTYCloseStdin`, `TestExecTTYWithoutStdin`, `TestExecParseError`, `TestExecStopNotHanging`, `TestExecCgroup`, `TestExecInspectID`, `TestLinksPingLinkedContainersOnRename`, `TestRunMutableNetworkFiles`, `TestExecWithUser`, `TestExecWithPrivileged`, `TestExecWithImageUser`, `TestExecOnReadonlyContainer`, `TestExecUlimits`, `TestExecStartFails`, and `TestExecWindowsPathNotWiped`.

Control flow: tests run sleeping/top containers, execute commands through CLI or `exec.Command`, use pipes for interactive stdin/stdout, inspect daemon fields, and sometimes call the Docker API for `ExecInspect`. Concurrency is used for cgroup consistency checks and stop-not-hanging behavior.

State and persistence: creates running containers, exec instances, environment variables, network files, cgroup state, user accounts inside images, device nodes under privileged exec, and inspectable exec IDs. It verifies exec records after completion and deletion after container removal.

Dependencies and integration points: Docker CLI, Docker API client, busybox shell tools, build helper, local daemon storage paths, platform gates for Linux/Windows, cgroups, user namespace constraints, and `icmd`.

Risks: interactive and TTY tests are timing-sensitive. Cgroup tests depend on cgroup layout and userns. Privileged exec tests require Linux capabilities. Network file mutation reads daemon storage directly and is local-daemon-only.

Test signals: failures show regressions in exec process lifecycle, environment merge rules, terminal handling, inspect persistence, cgroup placement, privilege scoping, readonly compatibility, ulimit inheritance, or platform-specific path handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_exec_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_exec_unix_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_exec_unix_test.go

Purpose: Unix-specific TTY and pty coverage for `docker exec`, including stdin close behavior and TERM environment behavior.

Important APIs/types/functions: `TestExecInteractiveStdinClose`, `TestExecTTY`, `TestExecWithTERM`, and `TestExecWithNoTERM`. The file uses `github.com/creack/pty` to execute CLI commands under a pseudo-terminal.

Control flow: tests start Linux busybox containers, run `docker exec` under pty, write commands through the pty, wait with explicit timeouts, and read buffered output. TERM tests execute shell checks that pass or fail based on whether `$TERM` is populated with `-t`.

State and persistence: only temporary running containers and exec sessions are created. No durable state is expected beyond normal test cleanup.

Dependencies and integration points: non-Windows build tag, Linux daemon, local daemon for TTY tests, pty support, busybox shell, and Docker CLI `exec -i`, `exec -it`, and `exec -t`.

Risks: pty reads can include NUL bytes or terminal echo, so output is trimmed where needed. Tests are time-sensitive and can fail if exec startup or pty flushing is slow. TERM behavior depends on CLI/daemon TTY negotiation.

Test signals: failures indicate regressions in pty-backed exec completion, TTY stdin/exit handling, or incorrect TERM injection for TTY vs non-TTY exec sessions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_exec_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_external_volume_driver_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_external_volume_driver_test.go

Purpose: integration tests for legacy external volume driver plugins using a local HTTP test server and `/etc/docker/plugins/*.spec` registration. The suite validates driver activation, create/list/get/remove/path/mount/unmount/capability calls, daemon restart behavior, conflict handling, retries, and cleanup on copy or mount failure.

Important APIs/types/functions: `volumePluginName`, `eventCounter`, `DockerExternalVolumeSuite`, `volumePlugin`, `vol`, `newVolumePlugin`, `hostVolumePath`, and tests including `TestExternalVolumeDriverNamed`, `TestExternalVolumeDriverUnnamed`, `TestExternalVolumeDriverVolumesFrom`, `TestExternalVolumeDriverDeleteContainer`, `TestExternalVolumeDriverLookupNotBlocked`, `TestExternalVolumeDriverRetryNotImmediatelyExists`, `TestExternalVolumeDriverList`, `TestExternalVolumeDriverGet`, `TestExternalVolumeDriverWithDaemonRestart`, `TestExternalVolumeDriverCapabilities`, `TestExternalVolumeDriverOutOfBandDelete`, `TestExternalVolumeDriverUnmountOnMountFail`, and `TestExternalVolumeDriverUnmountOnCp`.

Control flow: `newVolumePlugin` installs HTTP handlers for Docker volume plugin endpoints and writes a spec file pointing to the server. Tests start daemons, run containers with `--volume-driver`, inspect mount metadata, compare endpoint counters, simulate down drivers and delayed driver registration, and mutate plugin-side volume maps to mimic out-of-band deletion.

State and persistence: creates `/etc/docker/plugins` specs, host volume paths under `/var/lib/docker/volumes`, plugin in-memory volume maps, Docker volumes, containers, and daemon root state. Some tests restart the daemon and expect plugin-backed volume metadata to persist.

Dependencies and integration points: local daemon, daemon harness, Docker volume CLI/API behavior, plugin protocol MIME type, HTTP test server, busybox, `container.MountPoint`, `volumetypes.Volume`, and volume scope constants.

Risks: writes to `/etc/docker/plugins` and `/var/lib/docker/volumes` require privileged local test environments. Endpoint counters are sensitive to internal caching behavior. Down-driver and retry tests rely on timing and network connection behavior.

Test signals: failures expose regressions in external plugin discovery, serialized volume driver calls, duplicate name conflict handling, plugin response validation, daemon restart restoration, scope caching, unmount semantics, or copy-triggered mount/unmount balancing.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_external_volume_driver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_health_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_health_test.go

Purpose: integration coverage for Docker healthcheck configuration, runtime health transitions, health log inspection, CLI overrides, timeout behavior, JSON-form health commands, and unset environment variable handling.

Important APIs/types/functions: `DockerCLIHealthSuite`, helper `waitForHealthStatus`, helper `getHealth`, `TestHealth`, and `TestUnsetEnvVarHealthCheck`. It uses `container.HealthStatus` and `container.Health` from API types.

Control flow: `TestHealth` builds an image with a healthcheck that reads `/status`, creates/runs containers, waits for transitions from `starting` to `healthy`, removes/touches files through exec to force unhealthy/healthy transitions, inspects health status/logs, disables checks via CLI and Dockerfile, enables checks on an image with `HEALTHCHECK NONE`, tests timeout output, and validates JSON-form command parsing. The env-var test runs a healthcheck with an unset env var and waits for healthy.

State and persistence: health configuration is stored in image/container config. Runtime health status, failing streak, and logs are stored in container state and retrieved via inspect. Containers and test images are removed by cleanup paths.

Dependencies and integration points: Linux busybox, Docker build, `docker inspect`, `docker exec`, health monitor scheduling, stop signal handling, and API health structs.

Risks: health tests are timing-sensitive by design and poll every 100ms. `waitForHealthStatus` has a TODO noting questionable assertion logic around previous state. Short intervals and timeouts can be flaky on overloaded systems.

Test signals: failures indicate broken healthcheck parsing, scheduling, state transitions, failing streak accounting, timeout handling, inspect serialization, or CLI/Dockerfile healthcheck override semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_health_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_history_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_history_test.go

Purpose: integration tests for `docker history`, including build-layer ordering, behavior for existing and missing images, commit comments, and human/non-human size formatting.

Important APIs/types/functions: `DockerCLIHistorySuite`; tests `TestBuildHistory`, `TestHistoryExistentImage`, `TestHistoryNonExistentImage`, `TestHistoryImageWithComment`, `TestHistoryHumanOptionFalse`, and `TestHistoryHumanOptionTrue`.

Control flow: the build-history test builds an image with labels A-Z, reads history output, and expects newest layer ordering Z through A. Comment tests create and commit a container with `-m`, then parse the first history row. Size-format tests locate the `SIZE` column from the header and validate each row as either an integer byte count or human-readable value.

State and persistence: creates images and a committed container image. History output reflects image layer metadata and commit comments stored in image history.

Dependencies and integration points: Docker build helper, minimal base image selection, `docker history`, commit command, regex parsing, and CLI text table layout.

Risks: the file explicitly calls `TestBuildHistory` a heisen-test because image created timestamps and sort behavior can be unpredictable. Table parsing by whitespace and column offsets can break if CLI formatting changes.

Test signals: failures point to image history ordering regressions, missing commit comments, incorrect error behavior for missing images, or broken `--human` size rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_history_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_images_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_images_test.go

Purpose: integration coverage for `docker images` and `docker image ls`: listing, repository/tag filtering, creation-date ordering, label/since/before/dangling filters, output formatting, scratch/busybox image visibility, registry names with ports, and config default format interaction.

Important APIs/types/functions: `DockerCLIImagesSuite`, helper `getImageIDs`, and tests such as `TestImagesEnsureImageIsListed`, `TestImagesEnsureImageWithTagIsListed`, `TestImagesOrderedByCreationDate`, `TestImagesFilterLabelMatch`, `TestCommitWithFilterLabel`, `TestImagesFilterSinceAndBefore`, `TestImagesFilterSpaceTrimCase`, `TestImagesEnsureDanglingImageOnlyListedOnce`, `TestImagesEnsureOnlyHeadsImagesShown`, `TestImagesEnsureImagesFromScratchShown`, `TestImagesFilterNameWithPort`, `TestImagesFormat`, and `TestImagesFormatDefaultFormat`.

Control flow: tests tag busybox, build small images, commit containers, list images with filters and `--format`, parse IDs from tab-separated output, and compare order/visibility. Sleep calls are inserted between builds to make creation-order sorting deterministic. The default-format test writes a temporary CLI config and verifies `-q` still prints only IDs.

State and persistence: creates tags, images, dangling images, committed images, temporary CLI config directories, and failed build intermediate images. Image metadata includes labels, created timestamps, repo tags, and IDs.

Dependencies and integration points: build helper, `stringid.TruncateID`, Docker CLI config, busybox and scratch images, image filter implementation, and CLI formatter.

Risks: sleeps are needed because timestamp granularity can make ordering flaky. Some tests parse build output line positions to identify intermediate images. Failed-build dangling image assumptions depend on builder behavior. Snapshotter/buildkit changes could alter intermediate visibility.

Test signals: failures indicate image list filtering/order regressions, improper dangling handling, bad label filter matching, formatter/config precedence bugs, or repository parsing issues for names containing registry ports.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_images_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_import_test.go -->
# sources/cloud-native/moby/integration-cli/docker_cli_import_test.go

Purpose: integration tests for `docker import` from stdin, files, gzip files, bad URLs/nonexistent files, commit messages, and quoted `--change` instructions.

Important APIs/types/functions: `DockerCLIImportSuite`; tests `TestImportDisplay`, `TestImportBadURL`, `TestImportFile`, `TestImportGzipped`, `TestImportFileWithMessage`, `TestImportFileNonExistentFile`, and `TestImportWithQuotedChanges`.

Control flow: tests create or run a busybox container, export it to stdout or a temp file, optionally gzip the stream, import it, and run the resulting image. Message tests inspect `docker history` and parse the comment column. Quoted change tests import with `-c ENTRYPOINT ["/bin/sh", "-c"]` and run the result.

State and persistence: creates containers, temporary tar/gzip files, imported images, image history entries, and image config changes. Bad URL/file tests should not create usable images.

Dependencies and integration points: Docker export/import/history/run commands, gzip writer, shell pipeline helper, regex table parsing, network/DNS behavior for invalid URL errors, and Linux archive support.

Risks: accepted bad-URL error text is intentionally broad because systems can fail at different layers. History table parsing is format-sensitive. Import display tests assert exactly one newline, so CLI progress/output changes are caught.

Test signals: failures indicate regressions in import stream handling, decompression, import output format, imported image runnability, message/history persistence, error handling, or parsing of quoted `--change` directives.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/integration-cli/docker_cli_import_test.go -->
