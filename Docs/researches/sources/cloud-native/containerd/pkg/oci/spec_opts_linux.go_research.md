# sources/cloud-native/containerd/pkg/oci/spec_opts_linux.go

Purpose: Linux-specific spec options for host devices, arbitrary devices, Linux capabilities, and command argument escaping placeholder.

Important APIs/types/functions: `WithHostDevices` appends all devices from `HostDevices` into `s.Linux.Devices`. `WithDevices(devicePath, containerPath, permissions)` recursively discovers devices from a host path, appends them to the spec, and adds matching cgroup allow rules. `WithAllCurrentCapabilities` reads the current process capabilities and applies them; `WithAllKnownCapabilities` applies all known capabilities. Linux `escapeAndCombineArgs` panics because Windows-only code should call the escaping implementation.

Control flow: device options call `setLinux` and `setResources`, then append devices and cgroup rules. Capability options delegate to `cap.Current` or `cap.Known` and then `WithCapabilities`.

State/persistence: generated spec only; reads `/dev` or device paths.

Dependencies/integration: uses `golang.org/x/sys/unix`-backed device helpers in `utils_unix.go` and `kernel.org/pub/linux/libs/security/libcap/cap`.

Risks: host-device passthrough and cgroup rules are privilege-sensitive. Recursive device discovery must avoid symlink and non-device surprises. Current capabilities depend on caller process state.

Test signals: `spec_opts_linux_test.go` covers capability set/add/drop and device discovery/follow symlink behavior.
