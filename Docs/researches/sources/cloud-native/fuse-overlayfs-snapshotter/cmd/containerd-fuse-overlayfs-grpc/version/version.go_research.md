<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/version/version.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/version/version.go

Purpose: build-time version metadata holder for the snapshotter gRPC binary.

Important API: exports mutable package variables `Version` and `Revision`, defaulting to `<unknown>`. The Makefile sets them through `-ldflags -X`.

State and integration: compile-time/link-time metadata only. Risks are missing ldflags producing unknown version logs and mutable globals being theoretically changeable at runtime. Test signal is release/build output inspection.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/version/version.go -->
