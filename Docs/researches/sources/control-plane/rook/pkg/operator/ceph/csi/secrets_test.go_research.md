# sources/control-plane/rook/pkg/operator/ceph/csi/secrets_test.go

## Purpose
This test file validates CSI CephX capability definitions, key-generation parsing/sorting/pruning, auth-list inspection, and deletion of Rook-owned CSI secrets.

## Important APIs, Types, and Functions
Tests include caps checks, `Test_deleteOwnedCSISecretsByCephCluster`, `TestSortCsiClientName`, `TestDeleteOldKeyGen`, `TestGetCsiKeyRotationInfo`, `TestGetCSIKeyInfoAndDeleteOldKey`, `Test_getMatchingClient`, `TestParseCsiClient`, `TestGetPriorKeyCount`, and `Test_deleteCount`. `loadTestClusterDetails` builds fake cluster context/info/spec.

## Control Flow, State, and Persistence
Mock executors return fake `ceph auth ls` JSON and record `auth del` calls. Fake Kubernetes clientsets hold Secrets and verify owner-based deletion. Pure helpers are tested with table-driven inputs.

## Dependencies and Integration Points
The tests use Rook fake exec, fake Kubernetes clientsets, keyring helpers, Ceph auth JSON output, and Kubernetes API error handling.

## Risks
`sortCSIClientName` appends entries even when parsing fails, with suffix zero; tests do not cover this malformed-entry ordering directly. `CreateCSISecrets` full orchestration and status update conflicts are not directly exercised. Some expected auth lists preserve input order before sorting, which is acceptable for `getMatchingClient` but not a sorted contract.

## Test Signals
Signals cover least-privilege capability strings, secret owner protection, numeric generation ordering, no-delete boundaries, timeout/invalid JSON auth-list errors, exact old-key deletion order, many malformed client-name cases, and deletion math.
