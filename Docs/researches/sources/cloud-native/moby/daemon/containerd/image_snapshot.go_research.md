<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot.go -->
# sources/cloud-native/moby/daemon/containerd/image_snapshot.go

Purpose: adapts containerd snapshots into Docker `RWLayer` operations for container create/restore/export and computes snapshot usage.

Important APIs and flow: `CreateLayer` and `CreateLayerFromImage` call `createLayer` with an optional image manifest descriptor and init mount setup. `createLayer` resolves/unpacks the parent image snapshot, creates a non-expiring per-container lease, prepares an init layer when needed, then prepares or remaps the writable snapshot. `getImageSnapshot` wraps the descriptor as an `ImageManifest`, blocks Docker AI model media types, unpacks if needed, and returns the rootfs chain ID. `rwLayer` implements mount/unmount/metadata around a snapshotter and ref-count mounter. `GetLayerByID` restores an existing snapshot and lease. `ReleaseLayer` deletes the lease synchronously. `prepareInitLayer`, `calculateSnapshotParentUsage`, and `calculateSnapshotTotalUsage` support init snapshots and size accounting.

State and persistence: creates containerd leases named by container/layer ID, active/committed snapshots, optional init snapshots, and ref-count mounter mount state. Parent snapshots come from image unpack state.

Dependencies and integration: used by daemon container lifecycle, container restore, export, disk usage, service layer-size APIs, Unix/Windows remap helpers, containerd leases/snapshots/mounts, and Docker snapshotter mounter.

Risks: non-expiring per-container leases can leak resources, as noted in comments. Many operations use `context.TODO`, limiting cancellation. If init-layer setup fails after `Prepare`, cleanup is not explicit here. `Unmount` depends on remembered or discoverable mount root and returns an error when not mounted. AI model blocking is string-prefix based on config media type.

Test signals: no direct tests in this subset; list/inspect size tests use fake snapshotter behavior. Missing high-value tests include lease cleanup on prepare/init failures and remap behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_snapshot.go -->
