<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_nonlinux.go -->
# sources/cloud-native/containerd/pkg/blockio/blockio_nonlinux.go

Purpose: non-Linux stub for block I/O support.

Important APIs and functions: `IsEnabled` always false, `SetConfig` no-op, `ClassNameToLinuxOCI` returns nil, and `ContainerClassFromAnnotations` returns empty class.

Control flow and state: no state and no filesystem/config effects.

Dependencies and integration: keeps package API portable for callers that compile on non-Linux platforms while returning no Linux OCI blockio configuration.

Risks and test signals: callers must handle nil/empty results. This intentionally hides unsupported functionality rather than failing on non-Linux builds.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/blockio/blockio_nonlinux.go -->
