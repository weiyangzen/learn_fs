# sources/control-plane/rook/pkg/operator/ceph/csi/cluster_config_test.go

## Purpose
This test file exercises the legacy ceph-csi JSON config update algorithm, monitor endpoint conversion, network namespace cleanup, and CSI ConfigMap owner-reference repair.

## Important APIs, Types, and Functions
`TestUpdateCsiClusterConfig` covers many incremental updates through `updateCsiClusterConfig`: monitors, multi-cluster entries, subvolume groups, mount options, RBD rados namespaces, Multus net namespace data, read affinity, invalid input, and namespace correction. `TestMonEndpoints`, `TestUpdateNetNamespaceFilePath`, and `Test_updateCsiConfigMapOwnerRefs` cover focused helpers. `contains`, `verifyEndpointPort`, `unmarshal`, and `compareJSON` are test helpers.

## Control Flow, State, and Persistence
Tests build JSON strings, update them repeatedly, parse results, and use fake Kubernetes clients for ConfigMap owner-reference updates. The owner-ref tests create or fetch `rook-ceph-csi-config` in fake clientsets and assert resulting owner metadata.

## Dependencies and Integration Points
The tests use ceph-csi deploy API structs, Rook topology defaults, fake Kubernetes clientsets, and `k8sutil.NewOwnerInfoWithOwnerRef`.

## Risks
`compareJSON` unmarshals `exceptedJSON` into both expected and actual variables, so calls to it do not validate `actualJSON`. Many important assertions are still direct `parseCsiClusterConfig` checks, but string-shape tests using `compareJSON` are weak. Map iteration can also make monitor order nondeterministic.

## Test Signals
Useful signals include preservation of subvolume group during monitor updates, propagation of mon changes to all entries in the same namespace, IPv6 msgr2 conversion safety, clearing old holder-pod net namespace paths, and replacing stale CephCluster owner refs with the operator owner.
