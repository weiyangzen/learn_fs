<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume_group_snapshot.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/volume_group_snapshot.go

**Purpose:** Defines the interface for inspecting and managing RBD volume group snapshots, preserving journal identity while exposing CSI conversion and member snapshot listing.

**Important APIs and types:** `VolumeGroupSnapshot` embeds `journalledObject` and requires `Delete`, `ToCSI`, `GetCreationTime`, and `ListSnapshots`. `ToCSI` returns CSI `VolumeGroupSnapshot`, while `ListSnapshots` exposes the member `Snapshot` interfaces.

**Control flow, state, and persistence:** This file has no executable logic. Implementations are expected to delete backend group snapshot state, read journal identity, produce CSI response objects, and enumerate member snapshots created under a crash-consistent group snapshot.

**Dependencies and integration points:** It depends on CSI protobuf types, `context`, and `time`. The interface is used by RBD manager and CSI group snapshot controller paths.

**Risks and test signals:** The key risks are incomplete member snapshot lists, stale journal data after deletion, and incorrect creation timestamps in CSI responses. Direct tests are absent; coverage must come from concrete group snapshot manager tests and compile-time conformance.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/volume_group_snapshot.go -->
