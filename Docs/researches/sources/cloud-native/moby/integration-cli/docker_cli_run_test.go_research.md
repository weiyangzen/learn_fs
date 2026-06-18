# sources/cloud-native/moby/integration-cli/docker_cli_run_test.go

## Purpose

`docker_cli_run_test.go` is the broad cross-platform integration suite for `docker run`. It defines `DockerCLIRunSuite` and covers the CLI contract for container creation and start, stdio, exit codes, naming, working directories, network modes, links and aliases, volumes, bind mounts, users, environment variables, capabilities, devices, DNS and host files, namespaces, restart policies, auto-removal, logging failures, mount syntax, Windows CPU and credential-spec flags, and many regression cases.

This file is effectively an end-to-end specification of `docker run` behavior at the boundary between Docker CLI, API client, daemon validation, runtime setup, network driver, storage driver, and platform-specific container runtime behavior.

## Important APIs, Types, and Helpers

The primary type is `DockerCLIRunSuite`, with `TearDownTest` and `OnTimeout` delegated to `DockerSuite`. Most tests call `cli.DockerCmd` for success paths and `dockerCmdWithError` or `icmd.RunCommand` for expected failures. The file uses `inspectField`, `inspectFieldJSON`, `inspectMountPoint`, `inspectFilter`, `waitInspect`, `readContainerFile`, `containerStorageFile`, `runSleepingContainer`, `runSleepingContainerInImage`, `deleteImages`, and platform helpers such as `dPath`, `minimalBaseImage`, `sleepCommandForDaemonPlatform`, and `getPrefixAndSlashFromDaemonPlatform`.

External packages indicate the integration breadth: `client` and `api/types/network` for API inspection and port maps, `daemon` and `testutil/daemon` for isolated daemon tests, `fakecontext` and `build` for controlled images, `specialimage` for synthetic images, `mountinfo` for host `/etc/resolv.conf` handling, and `poll` for asynchronous removal checks. Standard library dependencies include process execution, pipes, temp files, JSON, networking, path handling, concurrency, and timeouts.

Helper functions local to the file include `testRunWriteSpecialFilesAndNotCommit`, `eqToBaseDiff`, `sliceEq`, `containerRemoved`, `testReadOnlyFile`, `testRunContainerWithCgroupParent`, `testRunInvalidCgroupParent`, and `delayedReader`. These helpers encapsulate repeated checks for special-file diffs, read-only rootfs behavior, cgroup-parent validation, auto-removal polling, and slow stdin closure.

## Control Flow and Behavioral Areas

The opening tests validate basic execution: stdout from `echo`, named containers, file descriptor leakage, DNS lookup, expected exit codes, stdin pipe behavior, detached ID printing, working directory flags, and disabled networking. Link and alias tests then verify legacy `--link` behavior and user-defined bridge DNS behavior, including aliases that resolve after linked containers start or restart.

The volume section checks `--volumes-from`, anonymous volumes, bind mounts, symlinked paths, duplicate mount-point validation, copy-up behavior, read-only inheritance, named volume retention, and cleanup of anonymous volumes. It explicitly distinguishes bind mounts, named volumes, anonymous volumes, image-declared volumes, and `--mount` syntax. Later mount tests compare equivalent `--volume` and `--mount` forms, reject duplicate targets and unsupported copy modes, and verify writable volumes on a read-only root filesystem.

User, environment, and process tests validate default root identity, `-u` by name/ID/range, unknown users, concurrent `run` calls, environment passthrough/override/erase semantics, entrypoint overrides, command-not-found exit codes, invalid command invocation, invalid image references, stdin close behavior, restart policy behavior with interactive runs, and slow stdin readers.

Security and namespace sections cover privileged and unprivileged access to `mknod`, `mount`, `/sys`, `/proc`, devices, `chroot`, capability add/drop ordering, group additions, IPC/PID/NET/UTS host and container namespace sharing, read-only rootfs exceptions for Docker-managed host files, AppArmor checks, `/proc` filtering, cgroup mount read-only behavior, cgroup-parent path sanitization, and `--device-cgroup-rule`.

Networking tests are extensive. They cover host network conflicts with links and DNS flags, user-defined networks, multiple networks, network isolation and reconnection, active-container network removal failures, restart behavior across multiple networks, host/none/container network conflict rules, loopback behavior in `--net=none`, MAC address validation, port allocation, publish and expose ranges, duplicate host ports, `--add-host`, and DNS behavior in normal and host modes.

State and daemon-specific tests verify container `State.Running` and PID changes across stop/start, restart-count and max retry fields, auto-remove behavior for new and pre-1.25 APIs, goroutine leak checks for failed attach/logging paths, daemon default ulimits, TLS verify flag behavior, and Windows-only CPU and credential-spec handling.

## State and Persistence Behavior

The suite creates persistent containers, images, volumes, networks, and daemon-level state, then inspects or removes them. Many tests depend on the teardown path to clean containers, networks, and volumes after each test. Tests use `docker inspect` to verify persisted `HostConfig`, `Config`, `NetworkSettings`, restart policy, ulimits, cgroup parent, mount metadata, MAC address, CPU settings, and image metadata.

Several tests modify host or daemon-adjacent state. `TestRunDNSDefaultOptions` temporarily rewrites `/etc/resolv.conf` and restores it. `TestRunResolvconfUpdate` is skipped but documents restart-time host resolver propagation. Local daemon tests create host temp directories, bind mounts, symlinks, files with adjusted permissions, listeners on host ports, and isolated daemon instances. Named volume tests intentionally check that named volumes persist after `--rm` or `rm -v`, while anonymous inherited volumes are removed when expected.

Network tests create user-defined bridge networks and connect/disconnect running containers. Auto-removal tests use polling because daemon-side removal is asynchronous. Goroutine leak tests query the daemon API before and after failure scenarios, making daemon internal runtime state part of the signal.

## Dependencies and Integration Points

This file integrates with nearly every daemon subsystem used by `docker run`: image lookup/pull error handling, container create/start/wait/logs/inspect/remove, networking/libnetwork, volume drivers, graph/image copy-up, exec, daemon configuration, logging drivers, API version negotiation, runtime namespaces, cgroups, AppArmor, seccomp-adjacent behavior, Windows HCS options, and CLI config/env parsing.

The tests depend on standard test images such as `busybox`, `busybox:glibc`, `debian:trixie-slim`, platform default images, and generated test images. Several cases require a local Linux daemon, non-userns mode, cgroup v1, AppArmor, network access, or Windows-specific daemon modes. These requirements are expressed with `testRequires` and `skip.If`.

## Risks and Maintenance Notes

The file has high brittleness because it asserts exact text for many CLI and daemon errors, including invalid flags, mount conflicts, network conflicts, port allocation errors, and platform-specific Windows warnings. It also depends on implementation details such as cgroup v1 file paths, `/proc` layout, default Google DNS fallback values, `busybox` command availability, and daemon graph paths.

Several tests are intentionally skipped or marked unstable, signaling known drift: resolver updates, cgroup v2 gaps, BuildKit/image-volume differences, and validations that moved from CLI to daemon. Tests that bind host root, edit `/etc/resolv.conf`, create `/dev` symlinks, or bind special network files require careful local-daemon isolation. Networking tests can be timing-sensitive because DNS names, restart propagation, and network endpoint state are asynchronous.

The suite is large and multi-domain; changes to `docker run` validation can break unrelated-looking tests because validation order affects the first returned error string and exit code. Platform branches also mean a fix for Linux may leave Windows behavior uncovered or vice versa.

## Test Signals

Passing this suite signals that the CLI can translate `docker run` options into daemon API calls correctly, daemon validation rejects unsafe combinations, runtime state is created with expected mounts/namespaces/cgroups/security settings, container output and exit codes propagate, cleanup paths remove or preserve objects as designed, and cross-subsystem interactions such as networking plus DNS or read-only rootfs plus special host files remain stable.
