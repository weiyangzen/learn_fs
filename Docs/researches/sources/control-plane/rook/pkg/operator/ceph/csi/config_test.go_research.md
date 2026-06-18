# sources/control-plane/rook/pkg/operator/ceph/csi/config_test.go

## Purpose
This test file verifies `ClientProfile` creation for RBD rados namespaces and CephFS subvolume groups, plus CephFS mount option parsing.

## Important APIs, Types, and Functions
`TestCreateUpdateClientProfile` constructs test cluster info with `CSIDriverSpec.CephFS.KernelMountOptions`, creates both profile types, and fetches them from a fake controller-runtime client. `TestParseMountOptions` table-tests `parseMountOptions`.

## Control Flow, State, and Persistence
The test sets `POD_NAMESPACE`, registers ceph-csi profile types, creates profiles with fake clients, and asserts persisted CR fields. Mount parsing tests are pure in-memory.

## Dependencies and Integration Points
Dependencies include ceph-csi-operator API types, Rook fake cluster info, Rook scheme registration, and Kubernetes `types.NamespacedName`.

## Risks
The test covers create paths but not update-over-existing behavior or error paths. It only validates kernel options, leaving the `FuseMountOptions` branch untested. The test double-registers namespace/name setup, which is harmless but noisy.

## Test Signals
Signals include correct RBD `RadosNamespace`, CephFS `SubVolumeGroup`, CephFS metadata rados namespace pointer, and parsing of one or more comma-separated `key=value` mount options.
