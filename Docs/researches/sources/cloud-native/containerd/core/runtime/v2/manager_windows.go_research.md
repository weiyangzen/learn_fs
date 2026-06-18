# sources/cloud-native/containerd/core/runtime/v2/manager_windows.go

## Purpose
Sets the default runtime v2 task-manager platform list for Windows builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`defaultPlatforms` returns `platforms.DefaultString()` plus `"linux/amd64"`, allowing Windows containerd configurations to advertise the native platform and Linux/amd64 support for compatible runtime scenarios.

The file has no persistent state. It integrates through `TaskConfig` plugin registration. Dependencies are limited to `github.com/containerd/platforms`.

Risks include over-advertising Linux support where no Linux runtime is configured. Test signals are Windows plugin metadata checks and platform selection integration tests.
