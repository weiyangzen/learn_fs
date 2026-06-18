# sources/control-plane/rook/pkg/operator/ceph/object/zone/controller_test.go

## Purpose

This file tests the `CephObjectZone` controller's readiness gating and successful zone creation path using fake Kubernetes clients and mocked Ceph command execution.

## Important Test Cases and Fixtures

- `zoneGroupGetJSON`, `zoneGetOutput`, and `zoneCreateJSON` model key `radosgw-admin` outputs for zonegroup and zone operations.
- `TestCephObjectZoneController` covers the full sequence of no cluster, unready cluster, missing `CephObjectZoneGroup`, and successful reconcile.
- Test overrides for `createObjectStorePoolsFunc` and `commitConfigChangesFunc` capture whether pool creation and config commit paths are reached.

## Control Flow and Test Setup

The test builds a `CephObjectZone` with metadata/data pools and a zonegroup reference, then wires a fake controller-runtime client, fake Rook clientset, mock executor, and event recorder. It first verifies reconcile requeues when no cluster exists, then with an unready cluster. After creating a monitor Secret and marking the cluster Ready, it verifies the missing zonegroup CR path requeues. The success path creates a `CephObjectZoneGroup` CR, provides mocked `zonegroup get` and `zone get` command outputs, runs reconcile, and asserts no requeue, Ready update through client state, and that pool creation and commit hooks were called.

## State and Persistence Signals

The test observes reconcile results and the fact that mocked pool creation/commit functions are invoked. It fetches the zone CR after success but primarily verifies successful completion rather than detailed `.status.phase` fields. Ceph persistence is represented only by expected command outputs from the mock executor.

## Dependencies and Integration Points

The test uses fake clients from controller-runtime and Rook, `exectest.MockExecutor`, Rook test clientsets, Kubernetes scheme registration, and a fake event recorder. It depends on global function variables in `controller.go` for test injection and restores them with deferred functions.

## Risks and Gaps

The test does not cover deletion, dependent blocking, pool-prefix decoding, custom endpoint update, shared-pool/no-pool paths, invalid pool specs, finalizer-only reconciliation, or the branch where a missing zone must be created. In the success case, mocked `zone get` returns success, so the create branch is effectively skipped even though `zoneCreateJSON` exists as a fixture.

## Test Signals

The file confirms the controller waits for cluster and zonegroup prerequisites and enters the pool/config commit path once prerequisites are available. It is a useful smoke test but not comprehensive for zone lifecycle behavior.
