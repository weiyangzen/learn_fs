# sources/control-plane/ceph-csi/internal/rbd/features/features.go

## Purpose
Detects optional librbd runtime capabilities used to advertise CSI/CSI-Addons features only when the installed native library supports them.

## Important APIs, Types, And Functions
`SupportsGroupSnapGetInfo` checks for `rbd_group_snap_get_info`, enabling VolumeGroupSnapshot support. `SupportsRBDSnapDiffByID` checks for `rbd_diff_iterate3`, enabling Snapshot Metadata service support. Package-level `sync.Once` values cache support booleans and errors.

## Control Flow
Each detector first calls `rbd_image_options_create/destroy` through cgo to force librbd to load, then calls `dlsym`. Undefined-symbol errors are treated as unsupported but non-fatal; other loader errors are returned. Results are cached for the process lifetime.

## State And Persistence
State is in-memory only: once guards, cached errors, and cached booleans. There is no disk or cluster persistence.

## Dependencies And Integration Points
Depends on cgo linking with `-lrbd`, `dlsym.go`, and string inspection of loader errors. `driver.go` uses group snapshot detection before advertising group-controller capability; `identityserver.go` uses both detectors when returning plugin capabilities.

## Risks And Test Signals
Runtime library upgrades after process start will not be observed because results are cached. Error-string matching for `undefined symbol` is environment-sensitive. `features_test.go` only logs support and fails on unexpected detection errors, making it an environment smoke test rather than deterministic feature assertion.
