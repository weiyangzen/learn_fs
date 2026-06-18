<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/lease_test.go -->
# sources/cloud-native/containerd/integration/client/lease_test.go

## Purpose
Verifies that lease resources protect snapshotter resources from garbage collection after an image is deleted, and that deleting the lease releases those resources.

## APIs, Types, And Functions
`TestLeaseResources` uses `LeasesService`, `ContentStore`, `ImageService`, `SnapshotService`, `leases.Create`, `leases.AddResource`, `leases.ListResources`, `leases.DeleteResource`, `leases.Delete`, `Pull`, `Image.Config`, `Image.RootFS`, and `identity.ChainID`.

## Control Flow And State
The test creates a random lease, pulls and unpacks the pause image using `native` or `windows` snapshotter, verifies config content and rootfs snapshot existence, adds a lease resource for the snapshot chain ID, deletes the image synchronously, verifies the config blob is gone while the snapshot remains, removes the resource, deletes the lease synchronously, and then expects the snapshot to be not found.

## Persistence And Integration Points
State spans leases, content blobs, image records, snapshotter metadata, and GC. The snapshotter name changes by OS, linking the same contract to native Linux and Windows snapshot backends.

## Risks And Test Signals
Failures signal GC retaining too much or deleting too aggressively, lease resource list drift, wrong snapshot resource type names, or OS snapshotter behavior that does not honor leases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/lease_test.go -->
