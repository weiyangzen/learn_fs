<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cdi/oci_opt.go -->
# sources/cloud-native/containerd/pkg/cdi/oci_opt.go

Purpose: provide an OCI spec option that injects requested CDI devices into a container spec.

Important APIs and functions: `WithCDIDevices(devices ...string)` returns an `oci.SpecOpts` closure. It refreshes the CDI registry and calls `cdi.InjectDevices` against the OCI spec.

Control flow and state: if no devices are requested it returns without changes. Otherwise it calls `cdi.Refresh`; refresh failures are logged as warnings but not fatal, because CDI injection can still decide whether requested devices are usable. Injection failures are wrapped and returned. There is no package-local persistent state.

Dependencies and integration: integrates `core/containers`, `pkg/oci`, containerd logging, and CDI registry behavior. It is part of container creation spec assembly.

Risks and test signals: injection can add environment variables, hooks, and mounts, so later spec options must not reset those fields. Correctness depends on CDI registry availability and caller-provided device names.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/cdi/oci_opt.go -->
