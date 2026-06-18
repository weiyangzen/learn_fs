<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unsupported.go -->
# sources/cloud-native/containerd/core/mount/mount_unsupported.go

Purpose: OpenBSD unsupported mount implementation.

Important APIs/types/functions: platform stubs for `(*Mount).mount`, `Unmount`, `UnmountAll`, and `UnmountRecursive`, all returning `errdefs.ErrNotImplemented`.

Control flow: every mount/unmount entry point fails immediately.

State and persistence: no state and no filesystem changes.

Dependencies and integration points: selected by `openbsd` build tag so shared code compiles while callers can detect unsupported behavior.

Risks: any path that does not check `ErrNotImplemented` will fail on OpenBSD. `HasBindMounts` is false for OpenBSD in `mount.go`.

Test signals: no direct tests in this subset; behavior is trivial stubbing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unsupported.go -->
