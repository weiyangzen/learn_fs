# sources/cloud-native/containerd/core/runtime/v2/manager_unix.go

## Purpose
Sets the default runtime v2 task-manager platform list for non-Windows builds.

## APIs, Flow, State, Dependencies, Risks, And Tests
`defaultPlatforms` returns a single entry: `platforms.DefaultString()`. It is used by `TaskConfig` during runtime plugin registration.

There is no persistence or complex control flow. The dependency is `github.com/containerd/platforms`. Integration is with plugin metadata, which advertises supported platforms.

Risk is incorrect platform advertising if cross-platform support changes. Test signal is plugin initialization metadata on Unix builds.
