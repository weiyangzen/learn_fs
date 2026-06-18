<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/parameters.go

**Purpose:** Handles CSI external-provisioner metadata parameters, removing driver-internal Kubernetes-prefixed keys and extracting volume/snapshot ownership metadata.

**Important APIs and functions:** Constants define the `csi.storage.k8s.io/` prefix and PVC/PV/snapshot metadata keys. `RemoveCSIPrefixedParameters`, `GetOwner`, `GetVolumeMetadata`, `GetVolumeMetadataKeys`, `PrepareVolumeMetadata`, `GetSnapshotMetadata`, and `GetSnapshotMetadataKeys` are the helper surface.

**Control flow, state, and persistence:** Functions are pure map transformations. `RemoveCSIPrefixedParameters` returns a new map without CSI-prefixed keys. Metadata getters scan keys and currently use `strings.Contains` against known full key strings. `PrepareVolumeMetadata` only includes non-empty values.

**Dependencies and integration points:** Depends on `strings`. It integrates with CreateVolume/CreateSnapshot request parameter handling and metadata stored on volumes/snapshots.

**Risks and test signals:** `strings.Contains` can match keys that merely contain the known key as a substring rather than exact keys. Map output order is irrelevant but nondeterministic. Tests cover prefix stripping and owner extraction only; metadata getter/preparer behavior is untested here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/parameters.go -->
