## sources/control-plane/ceph-csi/internal/cephfs/core/snapshot_metadata.go

Purpose: Adds metadata support for CephFS subvolume snapshots, mirroring subvolume metadata behavior.

Important APIs: `ErrSubVolSnapMetadataNotSupported`, support detection helpers, `setSnapshotMetadata`, `removeSnapshotMetadata`, `listSnapshotMetadata`, `SetAllSnapshotMetadata`, `UnsetAllSnapshotMetadata`, and `ListSnapshotMetadata`.

Control flow: Support is cached per cluster in `clusterAdditionalInfo`. Set/remove call FSAdmin snapshot metadata APIs and convert `NotImplementedError` into unsupported. Bulk functions add caller parameters plus `clusterNameKey`, and ignore missing keys on unset.

State and persistence: Metadata is stored on CephFS subvolume snapshots. This is used for snapshot-backed volumes where node user/client metadata must live on the backing snapshot rather than a real subvolume.

Dependencies and risks: Depends on go-ceph snapshot metadata APIs. `listSnapshotMetadata` calls `fsa.ListMetadata` for the subvolume rather than an obvious snapshot-specific list API, which is a risk worth verifying against go-ceph behavior. Unlike subvolume metadata, unsupported snapshot metadata errors are not swallowed in `SetAllSnapshotMetadata`, so older clusters may fail snapshot metadata updates. Tests are absent.
