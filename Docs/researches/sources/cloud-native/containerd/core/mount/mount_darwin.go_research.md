<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_darwin.go -->
# sources/cloud-native/containerd/core/mount/mount_darwin.go

Purpose: Darwin-specific stub for mounting.

Important APIs/types/functions: platform `(*Mount).mount` returns `errdefs.ErrNotImplemented`.

Control flow: every call to `Mount.Mount` eventually fails with not implemented on Darwin.

State and persistence: no state and no filesystem changes.

Dependencies and integration points: selected by build constraints for Darwin. `HasBindMounts` in `mount.go` is also false for Darwin, allowing higher layers to skip bind-dependent paths.

Risks: callers must branch or tolerate `ErrNotImplemented`. Any code path assuming Unix-like `mount(2)` support will fail at runtime on Darwin.

Test signals: no direct Darwin test in this subset; behavior is simple stub logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_darwin.go -->
