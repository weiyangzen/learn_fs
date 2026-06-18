<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/snapshot.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/snapshot.go

**Purpose:** Defines the public RBD snapshot interface consumed by manager, controller, and metadata services. It extends journal identity with deletion, CSI conversion, creation time, volume-group linkage, size, and block metadata processing.

**Important APIs and types:** `MetadataCallback` sends slices of CSI `BlockMetadata`. `Snapshot` embeds `journalledObject` and requires `Delete`, `ToCSI`, `GetCreationTime`, `SetVolumeGroup`, `GetSize`, and `ProcessMetadata`, including optional delta processing against a base snapshot.

**Control flow, state, and persistence:** The interface implies backend snapshot deletion, metadata mutation for group association, journal identity lookup, and iterative block metadata scans with pagination parameters `startingOffset` and `maxResults`. Persistent state belongs to RBD snapshots, OMAP metadata, and potentially volume-group identifiers.

**Dependencies and integration points:** It depends on CSI protobuf types, `context`, `time`, and `util.Credentials`. Integration points include CSI snapshot responses, Snapshot Metadata Service callbacks, and group snapshot metadata.

**Risks and test signals:** `ProcessMetadata` has high risk around pagination, base snapshot deltas, and callback error propagation. `SetVolumeGroup` must safely update snapshot metadata with proper credentials. There are no tests here, but `snapshot_test.go` covers part of `ToCSI` behavior in the concrete RBD implementation.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/snapshot.go -->
