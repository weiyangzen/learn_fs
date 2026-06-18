# sources/cloud-native/containerd/pkg/os/mount_unix.go

Purpose: Unix non-Linux mount and unmount implementation for `RealOS`.

Important APIs/types/functions: `RealOS.Mount` delegates to `mount.Mount`; `RealOS.Unmount` delegates to `mount.Unmount`.

Control flow: direct delegation.

State/persistence: changes host mount state when called.

Dependencies/integration: build tag `!windows && !linux`; combined with platform-specific lookup implementation. Implements `OS` interface on Unix-like systems.

Risks: mount semantics and required privileges vary by platform. Errors are not wrapped with operation context.

Test signals: platform integration tests should cover successful mount/unmount and error propagation; fake OS can be used by higher-level code to avoid real mounts.
