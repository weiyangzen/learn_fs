# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/drain_test.go

## Purpose

This file tests monitor PDB reconciliation under different mon counts and quorum states. It verifies that Rook creates, updates, or skips the mon PodDisruptionBudget in a way that protects quorum during node drains.

## Important APIs and Test Flow

`createMonQuorumResponse()` builds serialized `cephclient.MonStatusResponse` fixtures from mon names and quorum ranks. `createFakeClusterWithExecutor()` builds a fake mon `Cluster` with controller-runtime and client-go fake clients, a test `ClusterInfo`, and an optional executor returning the quorum fixture.

`TestReconcileMonPDB` is table-driven. Cases include disabled `ManagePodBudgets`, mon counts one and two, three healthy mons, three mons with one down, five healthy mons, and five mons with one, two, or three down. The test calls `reconcileMonPDB()`, checks whether a PDB should exist, asserts `maxUnavailable`, runs reconciliation a second time to cover idempotent no-change behavior, and deletes the PDB before the next case.

`TestGetMaxUnavailableMonPodCount` asserts the threshold helper: counts below five allow one unavailable mon pod, while five and seven allow two.

## State, Dependencies, and Integration

The tests persist PDBs in the fake controller-runtime client and use mock Ceph command output for quorum status. They depend on Rook test helpers, the Ceph client test package, Kubernetes policy API registration, and fake Kubernetes version setup.

## Risks and Test Signals

The tests strongly signal the drain-safety formula `allowedDown = baseAllowed - downMonCount`, including clamping negative results to zero. They do not cover PDB delete behavior when management becomes disabled because the implementation currently has a TODO instead of deletion. They also assume rank arrays accurately represent quorum membership, matching Ceph's quorum status contract.
