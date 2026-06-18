<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service.go -->
# sources/cloud-native/moby/daemon/containerd/service.go

Purpose: defines the containerd-backed `ImageService` core state and daemon-facing service methods for image counts, disk usage, layer status, cleanup, config reload, and container layer sizes.

Important APIs and flow: `ImageService` stores containerd client, image/content stores, container store, snapshotter cache, registry services, events, prune flag, ref-count mounter, ID mapping, policy verifier, identity cache state, and test platform override. `NewService` wires these dependencies and starts identity cache refresh. `snapshotterService` caches snapshotter clients by name. `CountImages` counts unique target digests. `LayerStoreStatus`, `StorageDriver`, `Cleanup`, `ImageDiskUsage`, `layerDiskUsage`, `UpdateConfig`, and `GetContainerLayerSize` implement daemon interface behavior. `DistributionServices`, `GetLayerMountID`, and upload/download config are not implemented or empty.

State and persistence: manages in-memory service dependencies and identity cache lifecycle. Disk usage methods read snapshotter usage and content descriptors. Cleanup closes identity cache backend.

Dependencies and integration: this is the dependency hub for the other files in this subset. It integrates containerd client APIs, daemon container store, registry/distribution, events, snapshotter mounter, policy verifier, identity cache backend, and Moby error definitions.

Risks: `snapshotterServices` map is not guarded by a mutex, so concurrent first access to different snapshotters could race. Disk usage assumes the configured snapshotter and walks every image's present content. `UpdateConfig` logs unsupported max transfer settings, so daemon reload knobs do not affect containerd transfers here.

Test signals: many tests build fake `ImageService` values directly; direct coverage of service lifecycle/disk usage is limited in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/service.go -->
