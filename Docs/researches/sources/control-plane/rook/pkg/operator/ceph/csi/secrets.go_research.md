# sources/control-plane/rook/pkg/operator/ceph/csi/secrets.go

## Purpose
`secrets.go` creates, rotates, prunes, and persists CephX credentials for CSI RBD and CephFS node/provisioner users.

## Important APIs, Types, and Functions
Constants define Ceph client base names and Kubernetes Secret names. `createCSIKeyring` determines rotation state, generates the desired Ceph client key, prunes older generations, and returns key metadata. Capability helpers define RBD/CephFS node/provisioner caps. `createOrUpdateCSISecret` writes four Kubernetes secrets. `CreateCSISecrets` orchestrates all four users and updates CephCluster CSI CephX status. Helpers include `updateCephStatusWithCephxStatus`, `getPriorKeyCount`, `getCsiKeyRotationInfo`, `getMatchingClient`, `parseCsiClient`, `deleteOldKeyGen`, `deleteCount`, `deleteOwnedCSISecretsByCephCluster`, `sortCSIClientName`, and `deduplicate`.

## Control Flow, State, and Persistence
If `SkipUserCreation` is true, owned CSI secrets are deleted and Ceph user creation is skipped. Otherwise, the file reads the CephCluster, lists existing Ceph auth entities, computes desired key generation/status, creates Ceph auth keys, deletes excess old generations, writes Kubernetes Secrets with `userID`/`userKey`, and updates `status.cephx.csi`.

## Dependencies and Integration Points
It integrates with Ceph CLI auth commands, Rook keyring secret store, CephCluster security status, Kubernetes Secrets, owner references, and Rook status reporting.

## Risks
Rotation correctness depends on parsing `client.<name>[.<generation>]`; malformed names are logged but may still enter sorting with generation zero. Deletion errors are logged but do not stop rotation after key creation. Secret creation delegates to `SecretStore.CreateSecret`, so update semantics depend on that store. Status key counts use the max across four clients.

## Test Signals
Tests cover caps, owned secret deletion, generation sorting/parsing, auth-list handling, deletion count math, old-key pruning, matching clients, and prior-key count.
