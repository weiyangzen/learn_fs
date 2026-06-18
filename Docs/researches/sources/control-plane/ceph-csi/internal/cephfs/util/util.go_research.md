# sources/control-plane/ceph-csi/internal/cephfs/util/util.go

Purpose: tiny CephFS utility definitions shared by CephFS store and node/controller code.

Important APIs/types/functions: defines `type VolumeID string` for CephFS-specific volume identifiers and package variable `RadosNamespace = "csi"` for storing CSI-specific CephFS objects and keys.

Control flow: none beyond package initialization.

State and persistence: `RadosNamespace` is mutable package state, so tests or initialization code can override it. It represents the default namespace used for Ceph-side CSI metadata, not local process persistence.

Dependencies and integration points: `VolumeID` is used by mountinfo filename formatting and CephFS core path helpers. `RadosNamespace` aligns CephFS metadata with Ceph-CSI OMAP/journal conventions.

Risks: global mutable namespace can create cross-test contamination or surprising runtime behavior if changed after objects are constructed. The package does not validate namespace values.

Test signals: no direct tests are needed for the type alias, but code that overrides `RadosNamespace` should restore it to avoid leaking state between tests.
