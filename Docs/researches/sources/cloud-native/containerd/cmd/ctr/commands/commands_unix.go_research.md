# sources/cloud-native/containerd/cmd/ctr/commands/commands_unix.go

Purpose: adds Unix/Linux runtime and container flags and returns runtime-specific option structs.

Important APIs/functions: `init()` appends runc/rootfs/cgroup/resource/device flags; `getRuncOptions()` builds runc `options.Options`; `RuntimeOptions()` validates and returns runc or generic runtime options.

Control flow: runc-specific flags are only valid with runtime `io.containerd.runc.v2`. `--runc-systemd-cgroup` requires a `--cgroup` flag from other command sets. `--runtime-config-path` returns `runtimeoptions.Options` for non-runc runtimes.

State and persistence: no persistence; creates protobuf option structs for container/task creation.

Dependencies/integration: runc options protobuf, runtimeoptions v1, urfave/cli.

Risks: validation references `--cgroup`, which is not declared in this file but may be supplied by commands that combine flag sets. Miscombined flags can produce confusing validation.

Test signals: no local tests.
