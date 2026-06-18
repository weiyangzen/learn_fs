# sources/control-plane/rook/pkg/operator/ceph/client/controller.go

Purpose: implements the controller-runtime reconciler for `CephClient` custom resources, creating/updating Ceph auth clients and associated Kubernetes Secrets, handling deletion, status, and CephX key rotation.

Important APIs/types/functions: `ReconcileCephClient` stores controller client, scheme, cluster context/info, operator context, and event recorder. `Add()`, `newReconciler()`, and `add()` register the controller and watches for `CephClient` and owned Secrets. `Reconcile()` wraps `reconcile()` with reporting. Core methods include `createOrUpdateClient()`, `reconcileCephClientSecret()`, `deleteClient()`, `ValidateClient()`, `genClientEntity()`, `getClientName()`, `generateClientName()`, `updateStatus()`, `generateStatusInfo()`, and `generateCephUserSecretName()`.

Control flow: reconcile fetches the CR, adds finalizer, initializes status when absent, waits for a ready CephCluster, loads cluster info, handles deletion by deleting the Ceph auth entity and removing finalizer, validates caps/name, detects monitor Ceph version, determines whether CephX key rotation is needed, creates or updates the auth user and secret, and updates CR status to Ready with cephx status and secret info. Secret reconciliation handles create, update-if-owned, or delete-if-owned when `RemoveSecret` is set.

State and persistence behavior: persistent state includes Ceph auth users/caps/keys, Kubernetes Secrets containing the key under client name plus CSI `userID`/`userKey`, finalizers on `CephClient`, and status fields including phase, observed generation, info, and CephX status. `RemoveSecret` allows auth user management without preserving the generated Secret.

Dependencies and integration points: integrates with controller-runtime, Rook Ceph client command helpers (`AuthGetKey`, `AuthGetOrCreateKey`, `AuthUpdateCaps`, `AuthRotate`, `AuthDelete`), cluster readiness/load helpers, keyring rotation helpers, Kubernetes Secret ownership helpers, and reporting/events.

Risks: caps are generated from a Go map, so command argument order is nondeterministic. `ValidateClient()` rejects reserved names but does not deeply validate cap syntax. `createOrUpdateClient()` calls `AuthGetKey()` and falls back to `AuthGetOrCreateKey()` on any error, so non-not-found errors may be treated as create attempts. Secret update/delete safety depends on owner reference helpers. Status updates use retry but may leave failure status if create/update fails after partial Ceph auth changes.

Test signals: `controller_test.go` covers validation, entity generation, reconcile success/wait paths, status info, custom secret names, secret ownership behavior, and end-to-end key rotation scenarios with mocked Ceph commands.
