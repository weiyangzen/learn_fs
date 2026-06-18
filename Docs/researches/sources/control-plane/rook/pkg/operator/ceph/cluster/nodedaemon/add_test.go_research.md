# sources/control-plane/rook/pkg/operator/ceph/cluster/nodedaemon/add_test.go

## Purpose
This file tests the pod classification helper used by the node daemon controller watches.

## Important APIs, Types, And Functions
`TestIsCephPod` calls `isCephPod(labels, podName)`. It checks a pod without `rook_cluster`, a monitor canary pod with `rook_cluster`, and a normal Ceph monitor pod with `rook_cluster`.

## Control Flow And State
The test mutates a label map and pod name strings in memory. No controller, manager, or Kubernetes fake client is involved.

## Dependencies And Integration Points
It depends only on package-local node daemon code and testify assertions. It validates the watch filter used before enqueueing node reconcile requests from pod events.

## Risks And Test Signals
The test confirms canary pods are intentionally ignored so crash collectors are not started before real monitors establish `ROOK_CEPH_MON_HOST`. It does not cover the explicit crashcollector/exporter self-exclusion branches or the node/deployment watch mappings.
