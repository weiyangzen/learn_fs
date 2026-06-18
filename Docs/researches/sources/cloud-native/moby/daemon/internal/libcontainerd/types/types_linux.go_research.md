<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_linux.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_linux.go

Purpose: defines Linux-specific libcontainerd data types.

Important APIs and types: `Summary struct{}`, `Stats`, `InterfaceToStats`, `Resources = specs.LinuxResources`, and `Checkpoints struct{}`.

Control flow: `InterfaceToStats` wraps containerd metrics payload and read timestamp in a `Stats` value.

State and persistence: none; structs carry task metrics/resources data.

Dependencies and integration: used by `remote/client_linux.go` and daemon stats/resource-update code. Linux `Summary` is empty because process details are handled elsewhere.

Risks: `Metrics any` requires downstream type assertions for cgroup v1/v2 metrics. Alias to OCI `LinuxResources` couples Docker resource update API to runtime-spec shape.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_linux.go -->
