<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid.go -->
## sources/control-plane/ceph-csi/internal/util/volid.go

Purpose: composes and decomposes Ceph-CSI volume identifiers that embed encoding version, cluster ID length, cluster ID, location/pool id, and object UUID.

APIs and types: `CSIIdentifier` carries `LocationID`, private `encodingVersion`, `ClusterID`, and `ObjectUUID`. `ComposeCSIID` validates maximum length and object UUID length, defaults encoding version to 1, big-endian hex encodes version, cluster length, and location id, then joins fields with `-`. `DecomposeCSIID` parses the inverse format with underflow and exact-size checks.

State and persistence: IDs are persisted externally as CSI volume handles and later decoded to locate cluster and pool/filesystem state.

Dependencies: standard binary/hex/errors/strings.

Integration points: `GenerateVolID`, validation, controller publish secret lookup, and troubleshooting tools depend on this format.

Risks: `LocationID` is cast to `uint64` during compose and back to `int64` during decompose; negative values would round-trip through two's complement if ever supplied. `DecomposeCSIID` trusts separator positions indirectly by fixed slicing and hex decode errors rather than explicitly checking separators. Object UUID length is checked but UUID syntax is not.

Test signals: `volid_test.go` checks a representative compose/decompose round trip with non-default encoding version.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/volid.go -->
