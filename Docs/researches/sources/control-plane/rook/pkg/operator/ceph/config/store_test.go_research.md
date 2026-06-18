# sources/control-plane/rook/pkg/operator/ceph/config/store_test.go

## Purpose
`store_test.go` validates the monitor config Secret behavior and the public env/flag helpers from `store.go`.

## Important APIs, Types, and Functions
`TestStore` builds a fake clientset, `clusterd.Context`, and minimal owner info, then exercises `Store.CreateOrUpdate()` with one-monitor and three-monitor `ClusterInfo` fixtures. The local `assertConfigStore` helper reads `rook-ceph-config`, splits `mon_host` and `mon_initial_members`, and checks that every monitor ID and endpoint is represented. `TestEnvVarsAndFlags` asserts that `StoredMonHostEnvVars()` and `StoredMonHostEnvVarFlags()` point at the same Secret keys.

## Control Flow, State, and Persistence
The tests persist Secret state only in the fake Kubernetes client. `TestStore` first creates the Secret with one monitor, updates it with three monitors, then mutates endpoint strings to v1-style `1.2.3.4:6789` and repeats. `mon1EndpointsEnabled` doubles expected endpoint count because split host entries include both v1 and v2 forms when legacy endpoints are supplied.

## Dependencies and Integration Points
The tests depend on `testop.New()` fake Kubernetes clients, `clienttest.CreateTestClusterInfo()`, `cephclient.NewMinimumOwnerInfoWithOwnerRef()`, and the Secret API. They are direct unit coverage for daemon env integration.

## Risks
Assertions read `Secret.StringData`, which fake-client behavior preserves, while real Kubernetes stores Secret data under `Data` after admission. That makes the test less representative of a round trip through an API server. The test does not exercise owner-reference failures, Kubernetes update conflicts, malformed monitor data, missing internal monitor entries, or the create-then-update real-client behavior.

## Test Signals
Strong signals are Secret creation/update and env/flag consistency. Missing signals include real API-server serialization, Secret `Data` validation, and failure paths for create, get, update, or owner-reference setup.
