<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix.go -->
# sources/cloud-native/moby/daemon/info_unix.go

Purpose: supplies Unix-specific system info/version details for cgroups, runtimes, rootless mode, storage warnings, and component versions.

Important APIs and control flow: `fillPlatformInfo` fills cgroup driver/version/capabilities, runtimes and statuses, default runtime, runc/containerd/init commits, warnings for unsupported resource controls, rootless warnings, and platform-specific fields. `fillPlatformVersion` appends containerd, runc, init, and rootlesskit/slirp4netns/vpnkit version components when available. Helpers parse init/runtime version output, query rootlesskit, determine security options, rootless/no-new-privileges/cgroup namespace state, populate containerd/runc/init versions, and expose OCI runtime features in runtime status.

State and persistence: reads daemon config, sysinfo, runtime binaries, containerd version RPCs, rootlesskit API, and OS files. It does not persist data.

Dependencies and integration: selected by `!windows` build tags. Integrates system API responses with runc options, rootlesskit client, daemon runtimes config, containerd client, and rootless helper packages.

Risks: external binary `--version` output parsing is format-sensitive, though parser tests cover common cases. Context cancellation must be propagated from containerd/init calls while other discovery errors are logged and ignored. Warning text is user-visible and therefore compatibility-sensitive.

Test signals: `info_unix_test.go` covers `parseInitVersion` and `parseRuntimeVersion`; broader system info tests cover assembled fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/info_unix.go -->
