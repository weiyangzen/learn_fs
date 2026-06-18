<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/plugin/plugin.go -->
# sources/cloud-native/fuse-overlayfs-snapshotter/plugin/plugin.go

Purpose: in-process containerd snapshot plugin registration for fuse-overlayfs.

Important flow: registers a plugin with type `plugins.SnapshotPlugin` and ID `fuse-overlayfs`. `Config` supports optional `root_path`; init appends default platform metadata, validates config type, chooses root from containerd property or config override, exports the root, and returns `fuseoverlayfs.NewSnapshotter(root)`.

State and integration: participates in containerd plugin registry and creates snapshotter state under the selected root. Unlike the standalone gRPC server, it does not call `Supported` during init. Risks include delayed runtime failures if `fuse-overlayfs` is unavailable, root path misconfiguration, and Linux build-tag limitation. Test signal is containerd plugin initialization in deployments rather than direct tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs-snapshotter/plugin/plugin.go -->
