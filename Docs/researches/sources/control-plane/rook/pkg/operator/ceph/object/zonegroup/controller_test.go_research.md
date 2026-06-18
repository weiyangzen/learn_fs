# sources/control-plane/rook/pkg/operator/ceph/object/zonegroup/controller_test.go

## Purpose

This file tests the `CephObjectZoneGroup` controller's prerequisite checks and successful reconcile path using fake clients and mocked `radosgw-admin` command outputs.

## Important Test Cases and Fixtures

- `realmGetJSON`, `periodGetJSON`, and `zoneGroupGetJSON` simulate Ceph realm, period, and zonegroup outputs.
- `TestCephObjectZoneGroupController` covers no cluster, unready cluster, ready cluster without `CephObjectRealm`, and successful reconcile when the realm CR and Ceph realm/period/zonegroup exist.

## Control Flow and Test Setup

The test creates a `CephObjectZoneGroup` referencing `realm-a`, fake controller-runtime and Rook clients, and a mock executor. It first verifies requeue without a cluster and with an unready cluster. It then creates monitor Secret data and marks the cluster Ready; with no `CephObjectRealm` CR, reconcile returns an error and requeue. The success case adds a `CephObjectRealm`, configures mocked command outputs for `zonegroup get`, `period get`, and `realm get`, and verifies reconcile completes without requeue.

## State and Persistence Signals

The test fetches the zonegroup CR after success but does not explicitly assert `.status.phase` or observed generation. Ceph state is represented by mock command output and does not verify the create branch because `zonegroup get` succeeds.

## Dependencies and Integration Points

The test uses fake controller-runtime clients, fake Rook clientsets, `exectest.MockExecutor`, Kubernetes scheme registration, and `cephclient.AdminTestClusterInfo`. It depends on command-argument inspection inside the mock executor to simulate Ceph state.

## Risks and Gaps

Deletion behavior, invalid CR validation, malformed period JSON, missing live Ceph realm with an existing realm CR, and zonegroup creation when `zonegroup get` returns ENOENT are not covered. Status assertions are light, so regressions in phase/observed-generation updates may not be caught here.

## Test Signals

The file confirms that the controller gates work on cluster readiness, Kubernetes realm presence, live Ceph realm presence, and existing zonegroup state. It is a good readiness smoke test but not a full lifecycle test.
