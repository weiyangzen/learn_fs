<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/volume.go

**Purpose:** Defines the RBD volume contract, split into snapshot-specific operations, CSI-Addons operations, and base volume lifecycle/metadata methods.

**Important APIs and types:** `snapshottableVolume` requires `NewSnapshotByID` and `PrepareVolumeForSnapshot`. `csiAddonsVolume` includes group membership, key rotation, sparsify, parent image validation/flattening, mirror resync ID repair, and `ToMirror`. `Volume` embeds `journalledObject`, both subinterfaces, and adds `Delete`, `ToCSI`, `GetCreationTime`, `GetMetadata`, and `SetMetadata`.

**Control flow, state, and persistence:** No logic is implemented here. Concrete volumes manipulate RBD images, snapshots, group membership, image metadata, encryption metadata, mirroring state, and journal entries. The parent-image handling comment defines a control policy for missing, trashed, non-mirrored, and force-flatten parent states.

**Dependencies and integration points:** It depends on CSI volume protobufs, `context`, `time`, and `util.Credentials`. It is consumed by CSI controller paths, CSI-Addons volume-group/encryption/sparsify/mirroring paths, and snapshot code.

**Risks and test signals:** This interface is broad and operationally dense; changes can break many flows. Risks include failing to flatten when required, rotating keys without metadata consistency, and returning group IDs that do not match backend membership. Tests are indirect via concrete RBD volume implementations and compile-time interface use.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume.go -->
