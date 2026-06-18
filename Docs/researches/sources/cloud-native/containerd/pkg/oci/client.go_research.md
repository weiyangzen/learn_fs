# sources/cloud-native/containerd/pkg/oci/client.go

Purpose: defines the small client/image interfaces that OCI spec generation options need, avoiding direct dependency on the full containerd client type.

Important APIs/types/functions: `Client` exposes `ImageService`, `ContentStore`, `SnapshotService(name)`, and `EventsService`. `Image` exposes `Name`, `Target`, `Labels`, `Unpack`, `RootFS`, `Size`, `Usage`, `Config`, `IsUnpacked`, `ContentStore`, and `Platform`.

Control flow: interface-only file. Spec options call these methods to fetch image config blobs, snapshot mounts, platform information, and optional mount manager extensions.

State/persistence: no state directly. Methods represent access to persisted content, snapshots, images, and event services.

Dependencies/integration: imports containerd core services, snapshotters, image metadata, containers, and OCI descriptors. Used heavily by `spec.go` and `spec_opts.go`.

Risks: interface drift can break alternate client implementations and tests. Some spec options assume `Container.Snapshotter` and `SnapshotKey` are set when rootfs lookup is needed.

Test signals: fake images and clients in `spec_opts_test.go` validate enough of this interface for image config and rootfs user lookup paths.
