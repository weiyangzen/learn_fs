# Research: sources/cloud-native/moby/daemon/command/daemon_linux_test.go

## sources/cloud-native/moby/daemon/command/daemon_linux_test.go

Purpose: Linux-specific tests for listener socket activation and userns remap interaction with containerd snapshotter.

`TestLoadListenerNoAddr` uses a two-phase `reexec` setup to create a file descriptor, set `LISTEN_PID`/`LISTEN_FDS`, exec into a child, call `loadListeners` with `fd://`, and assert no error. This approximates systemd socket activation more accurately than running in one test process. `TestC8dSnapshotterWithUsernsRemap` is table-driven and checks that no-remap leaves config unchanged, userns remap without explicit snapshotter disables `containerd-snapshotter` and remaps containerd namespaces, explicit snapshotter plus userns returns the expected error, and explicit snapshotter without remap stays enabled.

State includes process environment, a temporary inherited Unix socket fd, reexec child process output, and mutated daemon config structs. Dependencies include unix syscalls, reexec, config, JSON, go-cmp, and gotest assertions. Risks covered are socket activation regressions and an important storage/userns incompatibility. Gaps include TCP/unix listeners without addresses and deeper rootless/containerd startup behavior.
