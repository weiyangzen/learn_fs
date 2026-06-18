<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/main.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/main.go

Purpose: standalone containerd proxy snapshotter gRPC server.

Important flow: logs version/revision, validates CLI args as `<unix addr> <root>`, creates the socket directory, removes any existing socket path, runs `fuseoverlayfs.Supported(root)`, creates a snapshotter, wraps it with containerd `snapshotservice.FromSnapshotter`, registers the snapshots API on a gRPC server, listens on the Unix socket, sends systemd readiness/stopping notifications when `NOTIFY_SOCKET` is set, and serves.

State and integration: creates/removes Unix socket path, initializes snapshotter metadata/root directories, and serves containerd's snapshot gRPC API. Risks include `os.RemoveAll(address)` deleting non-socket paths if misconfigured, no graceful signal shutdown in this file, and support probe requiring mount privileges at startup. Test signal is integration with containerd proxy plugin configs.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/cmd/containerd-fuse-overlayfs-grpc/main.go -->
