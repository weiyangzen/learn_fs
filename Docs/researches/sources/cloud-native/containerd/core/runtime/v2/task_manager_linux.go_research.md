# sources/cloud-native/containerd/core/runtime/v2/task_manager_linux.go

## Purpose
Emits Linux-specific runtime task manager deprecation warnings.

## APIs, Flow, State, Dependencies, Risks, And Tests
`emitPlatformWarnings` checks cgroups mode and emits `deprecation.CgroupV1` through the warning service when not running unified cgroup v2. It does not persist state.

Dependencies are `github.com/containerd/cgroups/v3`, deprecation definitions, and the warning service. Integration is plugin initialization in `task_manager.go`.

Risks are warning spam or missed deprecation notice if cgroup mode detection changes. Test signals are mocked warning service checks under cgroup v1/v2 modes.
