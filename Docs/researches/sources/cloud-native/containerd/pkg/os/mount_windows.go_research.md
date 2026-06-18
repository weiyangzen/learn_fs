# sources/cloud-native/containerd/pkg/os/mount_windows.go

Purpose: Windows stubs for mount operations in the `RealOS` abstraction.

Important APIs/types/functions: `RealOS.Mount`, `RealOS.Unmount`, and `RealOS.LookupMount` return `errdefs.ErrNotImplemented` with zero values where needed.

Control flow: immediate stub returns.

State/persistence: none; Windows mount-like operations are not implemented through this interface.

Dependencies/integration: selected on Windows. Keeps the cross-platform `OS` interface satisfied.

Risks: callers must not assume mount support on Windows. Higher-level code should branch on `errdefs.ErrNotImplemented` where mount operations are optional.

Test signals: Windows compile checks and behavior tests should validate not-implemented errors rather than nil success.
