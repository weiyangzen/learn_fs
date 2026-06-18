# sources/control-plane/rook/pkg/operator/ceph/csi/ceph_connection_test.go

## Purpose
This test file validates `CephConnection` CR generation for the ceph-csi-operator integration.

## Important APIs, Types, and Functions
`TestCreateUpdateCephConnection` exercises `CreateUpdateCephConnection` with fake cluster info, a fake controller-runtime client, and optional `CephRBDMirror` objects. `TestCephConnectionDefaultTopology` checks default CRUSH label expansion. `TestReadAffinityEnabled` table-tests the Ceph version gate.

## Control Flow, State, and Persistence
Tests set `POD_NAMESPACE`, register Ceph and ceph-csi API types in the shared scheme, call the upsert API, and read the resulting `CephConnection` object from the fake API server. State persists only in the fake client.

## Dependencies and Integration Points
The tests depend on `clienttest.CreateTestClusterInfo`, Rook client scheme registration, ceph-csi-operator API structs, and topology default labels.

## Risks
The test mutates a package/global scheme with `AddKnownTypes`, which can leak across tests in the same package. It verifies the count and contents of default labels but not monitor endpoint ordering, ownership, namespace env failure, or update-over-existing behavior with changed specs.

## Test Signals
Strong signals are mirror daemon count propagation, default read-affinity topology, and the Ceph `20.2.0` disablement. Additional useful coverage would include existing object update and list failures.
