# sources/cloud-native/containerd/pkg/os/mount_other.go

Purpose: non-Linux, non-FreeBSD, non-Windows lookup-mount stub.

Important APIs/types/functions: `RealOS.LookupMount(path)` returns an empty `mount.Info` and `errdefs.ErrNotImplemented`.

Control flow: immediate stub return.

State/persistence: none.

Dependencies/integration: build tag `!windows && !linux && !freebsd`; preserves `OS` interface compilation on platforms where mount lookup is unsupported.

Risks: callers must handle `ErrNotImplemented`. The zero `mount.Info` must not be used after an error.

Test signals: platform compile checks and any non-supported-platform tests should verify not-implemented classification.
