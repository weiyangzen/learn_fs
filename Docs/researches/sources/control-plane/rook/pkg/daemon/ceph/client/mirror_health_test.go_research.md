# sources/control-plane/rook/pkg/daemon/ceph/client/mirror_health_test.go

Purpose: validates conversion from live mirroring data into CRD status structs.

Important test case: `TestToCustomResourceStatus` builds a healthy mirroring summary and info object with one peer. The first subcase verifies status and info are populated when snapshot schedules are empty. The second subcase passes one snapshot schedule and verifies the returned snapshot schedule status is populated.

Control flow and dependencies: tests call `toCustomResourceStatus()` directly without Kubernetes clients or command execution. They use `cephv1` status types and testify assertions.

Risks and coverage gaps: no coverage exists for `NewMirrorChecker()`, polling loop cancellation, status update functions, retry conflict handling, not-found behavior, disabled parent status checks, error detail propagation with nil live data, preserving `LastChanged`, or nil `mirrorInfo` combined with non-nil `mirrorStatus`. The tests assert presence and a few key values but not timestamps.
