# sources/control-plane/rook/pkg/operator/ceph/controller/version.go

## Purpose
`version.go` detects and compares Ceph versions for local images, running daemons, and external clusters.

## Important APIs, Types, and Functions
`ValidateCephVersionsBetweenLocalAndExternalClusters()` reads the external mon version and validates it against the local cluster version. `GetImageVersion()` returns the version recorded in CephCluster status when it matches the current spec image. `DetectCephVersion()` runs a command-reporter Job using the desired Ceph image and `ceph --version`, then parses stdout. `CurrentAndDesiredCephVersion()` detects the desired image version and reads the least up-to-date running mon version. `ErrorCephUpgradingRequeue()` formats an upgrade wait error including the standard requeue interval.

## Control Flow, State, and Persistence
Version detection launches a Kubernetes Job through `cmdreporter`, applies mon placement without pod anti-affinity, applies command reporter annotations/labels, and waits up to 15 minutes. It does not itself persist the detected version; callers are expected to store status/labels. External validation uses Ceph CLI/client calls against monitor state.

## Dependencies and Integration Points
The file depends on `cephclient` version queries, `pkg/operator/ceph/version` parsing/validation, `cmdreporter`, Kubernetes clientsets, owner references, CephCluster placement/resources/image pull policy, and requeue constants from `controller_utils.go`.

## Risks
Detecting version requires scheduling and completing a Job, so image pull, placement, service account, or command failures block reconciliation. `GetImageVersion()` returns a timeout-like error immediately when status does not match the current image; callers must handle waiting. Current/desired comparison uses least-up-to-date mon daemon version, which is appropriate for monitor upgrade gating but not a full cluster version inventory.

## Test Signals
No direct tests are included in this subset. Related tests in `spec_test.go` exercise placement-like command reporter behavior for metrics, but version detection job success/failure, parse errors, and external version validation should have dedicated coverage elsewhere.
