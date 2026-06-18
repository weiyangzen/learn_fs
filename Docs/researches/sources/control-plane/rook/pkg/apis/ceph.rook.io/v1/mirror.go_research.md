# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/mirror.go

Purpose: adds small helpers for mirroring specs.

Important APIs/types/functions: `MirroringPeerSpec.HasPeers` and `FSMirroringSpec.SnapShotScheduleEnabled`.

Control flow: `HasPeers` returns true when `SecretNames` is non-empty; snapshot schedule helper returns true when `SnapshotSchedules` is non-empty.

State and persistence: reads CR spec fields persisted in pool/filesystem mirroring configuration.

Dependencies/integration: used by mirror reconcilers to decide whether to configure peers or schedules.

Risks: helper only checks list length, not validity or secret existence.

Test signals: nil/empty/non-empty peer and schedule cases in API or reconciler tests.
