# sources/control-plane/rook/pkg/daemon/ceph/client/subvolumegroup_test.go

This focused test file validates `validatePinningValues()` for CephFS subvolume-group pinning. It is the only direct test signal in this work item for `subvolumegroup.go`.

`TestValidatePinningValues` checks accepted and rejected distributed values, accepted and rejected random values, a pair of cases intended to cover export validation, multiple pinning types at once, and the no-pinning case. The important behavior under test is that only one pinning strategy may be set and each strategy is range-limited before CLI arguments are generated.

State is pure in-memory CRD spec data; no Ceph commands are mocked here. The test integrates with the Ceph API type `CephFilesystemSubVolumeGroupSpecPinning` and `testify/assert`.

One notable risk is that the "export" cases assign `Distributed` instead of `Export`, so export-specific range checks are not actually exercised despite the comments. The file also does not test create, resize, delete, OMAP cleanup, subvolume deletion, snapshot deletion, or clone cancellation command construction.
