<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/check.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/check.go

Purpose: Linux support checks for using fuse-overlayfs as a snapshotter backend.

Important APIs and flow: `supportsReadonlyMultipleLowerDir` creates temporary lower and merged directories, attempts a read-only `fuse3.fuse-overlayfs` mount with two lowerdirs, unmounts it, and reports failure with context. `Supported` verifies `fuse-overlayfs` is in PATH, ensures the root directory exists, and calls the mount probe with an error hint about kernel support.

State and integration: creates/removes temporary directories, performs a real FUSE mount, and checks executable lookup. Risks include needing `/dev/fuse`, permissions, kernel features, and cleanup after mount/unmount failures. Test signal is used by the snapshotter test suite to skip unsupported environments and by the gRPC server before serving.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/check.go -->
