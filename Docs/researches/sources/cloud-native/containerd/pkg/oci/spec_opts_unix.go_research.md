# sources/cloud-native/containerd/pkg/oci/spec_opts_unix.go

Purpose: Unix non-Linux device and argument helper implementation.

Important APIs/types/functions: `WithHostDevices` appends devices returned by `HostDevices` to `s.Linux.Devices`. `WithDevices(devicePath, containerPath, permissions)` appends devices found by `getDevices` but does not add Linux cgroup device rules in this Unix non-Linux variant. `escapeAndCombineArgs(args)` joins arguments with spaces.

Control flow: options initialize the Linux section and append discovered devices. `escapeAndCombineArgs` is simple concatenation for non-Windows builds that need a compile-time symbol.

State/persistence: generated spec only; reads host device metadata.

Dependencies/integration: selected by Unix non-Linux build constraints and depends on `utils_unix.go` device helpers.

Risks: adding Linux section on non-Linux Unix platforms may be an API compatibility compromise. The simple argument combiner is not shell-safe and should not be used as Windows escaping.

Test signals: `spec_opts_unix_test.go` covers image config without env and umask behavior on Unix specs.
