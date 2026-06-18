## sources/control-plane/ceph-csi/internal/cephfs/errors/errors.go

Purpose: Centralizes CephFS-specific sentinel errors and string constants used across core, store, controller, and node code.

Important APIs: `VolumeNotEmpty` string for CLI error matching; sentinels `ErrCloneInProgress`, `ErrClonePending`, `ErrInvalidClone`, `ErrCloneFailed`, `ErrInvalidVolID`, `ErrNonStaticVolume`, `ErrSnapNotFound`, `ErrVolumeNotFound`, `ErrInvalidCommand`, `ErrVolumeHasSnapshots`, `ErrQuiesceInProgress`, `ErrGroupNotFound`; and `IsCloneRetryError`.

Control flow and state: This file has no runtime state. It enables `errors.Is` matching across wrapped errors and maps backend conditions to CSI gRPC codes in higher layers.

Dependencies and risks: Only depends on Go `errors`. String matching for `VolumeNotEmpty` is brittle because it depends on backend/CLI wording. Adding new clone retry states requires updating `IsCloneRetryError`. Test signal comes from `clone_test.go` for clone errors; other sentinels are exercised indirectly.
