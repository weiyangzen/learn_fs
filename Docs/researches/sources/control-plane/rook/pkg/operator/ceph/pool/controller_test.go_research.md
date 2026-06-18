# sources/control-plane/rook/pkg/operator/ceph/pool/controller_test.go

## Purpose

This file provides broad unit coverage for the `CephBlockPool` controller, including pool creation/deletion helpers, reconcile readiness, mirroring, deletion blocking, RBD stats config, status fields, and EC mirroring exclusions.

## Important Test Cases

- `TestCreatePool` verifies replicated, `.mgr`, and EC pool creation behavior and confirms `rbd pool init` runs only for RBD application pools.
- `TestCephPoolName` verifies default pool names and allowed spec name overrides like `.mgr` and `.nfs`.
- `TestDeletePool` verifies pool deletion, no-op deletion for absent pools, failure for non-empty pools, CRUSH rule deletion, and EC profile cleanup.
- `TestCephBlockPoolController` drives reconcile through missing cluster, unready cluster, ready cluster success, invalid mirroring config, mirroring bootstrap Secret creation, peer-token import failure/success, and mirroring-disabled behavior.
- `TestDeletionBlocked` verifies deletion-blocked conditions for missing pools, empty pools, non-empty pools, and RADOS namespace dependents.
- `TestIsAnyRadosNamespaceMirrored` checks namespace mirroring detection.
- `TestConfigureRBDStats` and `TestGenerateStatsPoolList` cover mgr/prometheus RBD stats pool-list merging, removal, deduplication, empty handling, and error behavior.
- `TestMirrorPeerKeyRotationStatus` verifies pool `.status.cephx.peerToken` tracks the cluster's RBD mirror peer cephx status.
- `TestCephBlockPoolControllerPoolReachesReady` verifies both replicated and EC pools reach Ready and have expected type info.
- `TestCanConfigurePoolMirroring` verifies EC pools are excluded from mirroring.

## Control Flow and Test Setup

Tests use `exectest.MockExecutor` to inspect and return Ceph/RBD command results, fake controller-runtime clients for CR state, fake Rook/client-go clientsets for typed resources and Secrets, and fake event recorders. Several tests create monitor Secrets to allow `LoadClusterInfo`. Mirroring tests set `POD_NAME` and `POD_NAMESPACE` and create pod/replicaset objects so owner-aware bootstrap Secret logic can run.

The reconcile test mutates the same pool object through multiple subtests, progressively enabling mirroring and peer imports. RBD stats tests replace the executor mid-test to simulate mon store success and failure. Deletion-blocking tests vary command outputs and fake RADOS namespace CRs to check condition updates.

## State and Persistence Signals

The tests observe pool `.status.phase`, `.status.info`, `.status.cephx.peerToken`, `.status.conditions`, generated peer-token Secrets, deleted-pool maps, deleted EC profile flags, and mon-store config values. Ceph persistence is modeled through command mocks and side-effect variables.

## Dependencies and Integration Points

The tests integrate with fake Kubernetes API schemes, Rook fake clientsets, Ceph API types, `cephclient.AdminTestClusterInfo`, mon store helpers, controller cleanup/mirroring helpers, and command-output fixtures. They depend on exact command argument ordering in several mock executors.

## Risks and Gaps

- Some subtests share mutated pool, client, and executor state, so future changes must be careful about ordering and reset behavior.
- Watch setup for ConfigMap/Secret events is not exercised.
- Mirror health goroutine lifecycle is mostly inferred, not deeply synchronized or inspected.
- Cleanup job creation on force-delete is not covered.
- Some mocks return generic successful output for commands they do not fully model, so certain failure branches remain uncovered.

## Test Signals

This is a high-signal test file for block-pool behavior. It validates many important lifecycle and status paths, especially deletion safety, RBD stats, and mirroring bootstrap. Remaining risk is mainly around asynchronous monitoring, watch fan-out, and cleanup job details.
