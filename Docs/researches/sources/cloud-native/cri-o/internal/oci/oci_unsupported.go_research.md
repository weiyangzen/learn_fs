# sources/cloud-native/cri-o/internal/oci/oci_unsupported.go

## Purpose
Non-Linux platform fallback for runtime platform setup and Linux-specific container metadata methods.

## Behavior and Integration
Defines `InfraContainerName`, no-op `createContainerPlatform`, empty `SysProcAttr`, `os.Pipe`-backed `newPipe`, no-op conmon cgroup cleanup, empty seccomp profile accessors, nil container stats placeholder, and no-op `setSysProcAttr`.

## Risks
This preserves compilation but removes Linux cgroup, seccomp, and socketpair semantics. Any non-Linux runtime behavior relying on these features is degraded and should be treated as unsupported/limited.
