# sources/cloud-native/containerd/pkg/oci/mounts.go

Purpose: default OCI mounts for general Unix/Linux-style containers, plus a no-op OS mount hook for non-FreeBSD builds.

Important APIs/types/functions: `defaultMounts()` returns `proc`, `tmpfs` mounts for `/dev`, `/dev/shm`, `/dev/pts`, `/run`, `sysfs`, and cgroup. Each mount includes standard options such as `nosuid`, `noexec`, `nodev`, `mode=755`, `ptmxmode=0666`, and `size=65536k`. `appendOSMounts` is a no-op in this file.

Control flow: default spec generation calls `defaultMounts` when populating Unix specs. Image config handling may call `appendOSMounts`, which only changes behavior on FreeBSD.

State/persistence: no persistence; mount entries become part of the generated OCI spec.

Dependencies/integration: uses OpenContainers runtime-spec `specs.Mount`. Integrated by `populateDefaultUnixSpec` and spec options such as `WithDevShmSize` and `WithoutMounts`.

Risks: defaults are security-sensitive. Changing mount options can affect container isolation, device behavior, or compatibility. Cgroup mount defaults may not match all cgroup v2 environments.

Test signals: spec and spec options tests validate default spec shape, `/dev/shm` sizing, and mount removal behavior.
