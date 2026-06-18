# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/health_test.go

## Purpose

This file is the main test suite for monitor health, failover, scaling, out-of-quorum tracking, and external monitor reconciliation. It provides behavioral coverage for the most failure-prone logic in `health.go`.

## Important APIs and Test Flow

`TestCheckHealth` validates error returns before cluster info and mon count are initialized, then exercises health reconciliation, failover, replacement mon creation, deployment counts, and orphan PVC cleanup. `TestRemoveExtraMon` verifies extra-mon selection for duplicate nodes, arbitrary removal, and stretch-cluster zone rules. `TestScheduleFailoverImmediately` confirms deleted assigned nodes trigger immediate failover while unscheduled or existing-node mons do not. `TestTrackMonsOutOfQuorum` persists out-of-quorum state into the mon endpoints ConfigMap and clears it when the mon returns.

`TestEvictMonOnSameNode` creates fake running pods and verifies duplicate-node detection triggers a failover to a new mon. `TestHostNetworkFailover` covers whether the old mon should be scaled down during failover under default networking, host networking, and host-network migration cases. `TestScaleMonDeployment` checks direct replica toggling.

`TestCheckHealthNotFound` covers a mon in `ClusterInfo` missing from Ceph's mon map, expecting replacement and ConfigMap update. `TestAddRemoveMons` covers scaling from one to five, down to three, and the guard preventing reduction from two mons to one. `TestAddOrRemoveExternalMonitor` covers external-cluster monitor map refresh. `TestUpdateMonTimeout`, `TestUpdateMonInterval`, and `TestNewHealthChecker` cover health-loop configuration.

The three `TestExternalMons_*` cases cover external mon IDs not in spec, in spec but not quorum, and in spec and quorum, including interactions with downscale/upscale and endpoint ConfigMap persistence.

## State, Dependencies, and Integration

The tests use fake client-go and controller-runtime clients, temporary config dirs, mock Ceph executors, fake `CephCluster` objects, stubbed `waitForMonitorScheduling`, and the `UpdateDeploymentAndWaitStub`. They inspect Deployments, Pods, PVCs, ConfigMaps, and `ClusterInfo` maps.

## Risks and Test Signals

These tests are strong integration-style unit signals for monitor safety. They catch errors in one-mon-at-a-time removal, endpoint persistence, duplicate-node placement, external mon filtering, and timeout configuration. Risks are global hook mutation (`updateDeploymentAndWait`, `waitForMonitorScheduling`, `MonOutTimeout`) and reliance on canned quorum responses that may miss malformed Ceph output behavior.
