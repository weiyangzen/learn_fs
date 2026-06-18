# sources/control-plane/csi-lib-utils/accessmodes/access_modes.go

## Purpose
This package maps Kubernetes PersistentVolume access modes to CSI `VolumeCapability.AccessMode` values, with special handling for drivers that support `SINGLE_NODE_MULTI_WRITER`.

## Important APIs, Types, And Functions
Public API is `ToCSIAccessMode(pvAccessModes, supportsSingleNodeMultiWriter)`. Internal functions are `toCSIAccessMode`, `toSingleNodeMultiWriterCapableCSIAccessMode`, and `uniqueAccessModes`.

## Control Flow
The public function selects one of two mapping tables. Both deduplicate Kubernetes access modes, reject `ReadWriteOncePod` combined with anything else, let `ReadWriteMany` take precedence, reject `ReadOnlyMany` combined with `ReadWriteOnce`, and map remaining single modes. With single-node-multi-writer support, `ReadWriteOnce` maps to `SINGLE_NODE_MULTI_WRITER` and `ReadWriteOncePod` maps to `SINGLE_NODE_SINGLE_WRITER`; otherwise both map to `SINGLE_NODE_WRITER`.

## State, Persistence, And Dependencies
The code is stateless. Dependencies are Kubernetes core/v1 access mode constants and CSI protobuf enums.

## Integration Points
CSI sidecars and drivers use it while translating Kubernetes PV semantics into CSI volume capabilities.

## Risks And Test Signals
Ordering is intentionally lost through deduplication. `ReadWriteMany` precedence means invalid combinations involving RWX are accepted as multi-writer. Errors include the original mode slice for diagnostics. Unit tests cover supported and rejected combinations.
