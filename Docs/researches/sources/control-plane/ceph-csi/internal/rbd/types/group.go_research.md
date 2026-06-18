<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/group.go -->
## sources/control-plane/ceph-csi/internal/rbd/types/group.go

**Purpose:** Defines the interface contract for journal-backed RBD volume groups. It is a type boundary that lets the RBD manager, CSI-Addons volume-group services, and concrete RBD group objects interact without importing implementation structs.

**Important APIs and types:** `journalledObject` requires `GetID`, `GetName`, `GetPool`, `GetClusterID`, and `Destroy`, modeling the common journal handle, backend name, pool, cluster, and lifecycle surface. `VolumeGroup` embeds that contract and adds `GetIOContext`, `ToCSI`, `Create`, `Delete`, `AddVolume`, `RemoveVolume`, `ListVolumes`, and crash-consistent `CreateSnapshots`.

**Control flow, state, and persistence:** This file has no executable logic. The interface comments define expected persistence behavior: group identity is stored in the CSI/journal handle and backend group name, while implementations create/delete backend RBD groups, mutate group membership, and allocate resources that must be released through `Destroy`.

**Dependencies and integration points:** It depends on `context`, go-ceph `rados.IOContext`, CSI-Addons `volumegroup.VolumeGroup`, and `util.Credentials`. Consumers are expected to use the returned IO context for librbd group operations and credentials for snapshot creation.

**Risks and test signals:** Changes here are high blast-radius because implementers across the RBD package must satisfy the interface. There are no direct tests in this file; compile-time conformance and volume-group operation tests elsewhere are the main signals. The key risk is mismatched lifecycle ownership for IO contexts and `Destroy`.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/types/group.go -->
