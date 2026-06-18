# sources/cloud-native/moby/integration-cli/docker_cli_run_unix_test.go

## Purpose

`docker_cli_run_unix_test.go` is the non-Windows companion to the main `docker run` integration suite. It is guarded by `//go:build !windows` and focuses on Unix/Linux behaviors that require PTYs, Unix devices, cgroups, tmpfs, shm, sysctls, seccomp, AppArmor, Linux capabilities, no-new-privileges, and daemon-level seccomp profile configuration.

The file extends `DockerCLIRunSuite` and `DockerDaemonSuite` with tests that cannot be expressed portably in the cross-platform run suite. It validates the Linux kernel-facing contract of `docker run`.

## Important APIs, Types, and Helpers

There are no new suite types; methods attach to `DockerCLIRunSuite` or `DockerDaemonSuite`. The file uses `github.com/creack/pty` for interactive attach/detach tests, `github.com/moby/sys/mount` for host tmpfs setup, `github.com/moby/moby/v2/pkg/sysinfo` for CPU and memory node validation, `github.com/moby/profiles/seccomp` for default profile serialization, and `client.New` for API-level inspection of `NanoCPUs`.

Shared helpers include `cli.DockerCmd`, `dockerCmdWithError`, `inspectField`, `inspectFieldJSON`, `ensureSyscallTest`, `ensureNNPTest`, `testRequires`, and `skip.If`. The local `sysctlExists` helper checks for optional kernel sysctls before adding compatibility sysctl flags to capability tests.

## Control Flow and Behavioral Areas

The first group verifies terminal and attach behavior. `TestRunRedirectStdout` runs commands through a PTY and shell pipeline to ensure container stdout can be redirected. The attach/detach tests start interactive containers, connect with `docker attach`, write through a PTY, send default or configured escape sequences, wait for the attach command to exit, and confirm the container remains running. Config-file detach keys are tested through a temporary `$HOME/.docker/config.json`, and invalid escape sequences are checked for preservation in the stream.

Device and mount behavior is covered through recursive bind mounts, `/dev/snd` directory devices, symlinked devices, tmpfs ordering, `--tmpfs` options, default and explicit `/dev/shm` size, read-only `/dev/shm`, and PIDs/device cgroup lists. These tests inspect actual kernel mount output and cgroup files from inside containers.

Resource-control tests validate cgroup-backed CLI flags: `--cpu-quota`, `--cpu-period`, `--cpu-shares`, `--cpuset-cpus`, `--cpuset-mems`, `--blkio-weight`, memory limit, memory reservation, memory swap, swappiness, OOM exit code 137, PIDs limit, and `--cpus`/NanoCPUs. Many are skipped under cgroup v2 because the expected v1 files and semantics are not available.

Security tests cover sysctl setting and validation, custom seccomp profiles that deny specific syscalls, default seccomp profile behavior for clone/user namespace/acct/ns syscalls, 32-bit syscall allowance on amd64, setrlimit allowance, no-new-privileges preventing setuid transitions, AppArmor denial for `/proc` modifications, and daemon restart with a custom default seccomp profile.

Capability tests check that root has default effective capabilities while non-root users and `--cap-drop` lose them. Capabilities covered include CHOWN, DAC_OVERRIDE, FOWNER, SETUID, SETGID, NET_BIND_SERVICE, NET_RAW, SYS_CHROOT, and MKNOD. The tests use `syscall-test`, `busybox`, and kernel sysctls to distinguish permission failures from missing feature support.

## State and Persistence Behavior

Most tests create short-lived containers and inspect container or kernel state immediately. Some create persistent named containers to inspect `HostConfig` values after execution. PTY attach tests leave containers running until suite teardown. Host state is touched in controlled ways: temp directories are created and mounted as tmpfs, symlinks are created, `/dev/symzero` is temporarily created and removed, and custom seccomp profile JSON files are written to temp paths.

Daemon state is significant in the `DockerDaemonSuite` seccomp tests. Those tests start an isolated daemon with busybox loaded, run containers against it, and restart it with `--seccomp-profile` to verify daemon default profile persistence. Resource tests persist `HostConfig` values such as CPU quota, period, cpuset, memory, shm size, pids limit, and NanoCPUs for inspection.

## Dependencies and Integration Points

This file integrates directly with Linux kernel interfaces. It depends on `/sys/fs/cgroup/*` v1 paths, `/proc`, `/dev`, AppArmor, seccomp, user namespace availability, unprivileged user namespace clone policy, host sound devices, memory/swap controller support, pids controller support, CPU CFS quota/period support, and local daemon access. It also depends on helper images (`busybox`, `debian:trixie-slim`, `syscall-test`, `nnp-test`) and on test helpers that build or ensure those images.

The `DockerDaemonSuite` tests integrate daemon startup/restart flags with runtime enforcement, which catches differences between per-container `--security-opt seccomp=...` and daemon default seccomp policy.

## Risks and Maintenance Notes

The largest risk is cgroup-version drift. Many tests assert cgroup v1 file paths and are skipped under cgroup v2, so coverage may shrink as hosts migrate. Kernel configuration variability is another major risk: memory swap, swappiness, cpuset mems, pids limits, AppArmor, seccomp, `/dev/snd`, and unprivileged user namespaces are not uniformly available.

PTY tests can be timing-sensitive; they use sleeps between escape bytes and timeouts around `cmd.Wait`. Seccomp and capability tests assert specific stderr text such as "Operation not permitted" or "Permission denied", which can vary by runtime, libc, kernel, or image. Host mutation tests require cleanup discipline, especially `/dev/symzero` and temporary mounts.

## Test Signals

Passing tests signal that Linux-specific `docker run` options are translated into actual kernel/runtime state, not only accepted by the CLI. They verify interactive attach detachment, resource limit enforcement, tmpfs/shm/device behavior, seccomp and AppArmor policy application, no-new-privileges, daemon default seccomp profiles, and reduced effective capabilities for non-root or cap-dropped containers.
