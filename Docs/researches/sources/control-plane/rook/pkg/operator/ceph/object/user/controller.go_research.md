# sources/control-plane/rook/pkg/operator/ceph/object/user/controller.go

## Purpose

This file implements the `CephObjectStoreUser` controller for RGW/S3 users. It reconciles Kubernetes `CephObjectStoreUser` CRs into Ceph RGW admin-ops users, maintains generated access-key Secrets, supports explicit user keys from Kubernetes Secrets, validates account-linked IAM display names, and removes RGW users during CR deletion. The controller is part of the object store integration path and depends on a ready `CephCluster` and an initialized `CephObjectStore`.

## Important APIs, Types, and Functions

- `ReconcileObjectStoreUser` holds the controller-runtime client, scheme, clusterd context, RGW admin ops context, advertise endpoint, cluster spec/info, operator manager context, and event recorder.
- `Add`, `newReconciler`, and `add` register the controller, watch `CephObjectStoreUser` resources, watch owned generated Secrets, index `spec.keys` Secret references, and watch referenced Secrets for resource-version changes or deletion.
- `Reconcile` wraps `reconcile` with panic recovery, status failure updates, event reporting, and `reporting.ReportReconcileResult`.
- `reconcile` is the main state machine: fetch CR, add finalizer, check cluster readiness, load cluster info, initialize object-store admin context, handle deletion, generate RGW user config, resolve account references, create/update Ceph user, update `.status.keys`, reconcile generated credentials Secret, and mark Ready.
- `createOrUpdateCephUser` is the core Ceph-side idempotency path. It gets or creates the RGW user, modifies scalar fields when `isUserSync` says they drifted, reconciles user caps, sets quota, chooses target keys, and calls `reconcileUserKeys`.
- `generateUserConfig` builds `admin.User` from the CR: ID, display name, default max buckets, quota max buckets, capabilities string, and operation mask.
- `initializeObjectStoreContext` calls `object.InitializeObjectStoreContext`, enforces cross-namespace user allowance using `allowUsersInNamespaces`, stores the advertised endpoint, and records `AdminOpsContext`.
- `resolveAccountRef` loads a same-namespace `CephObjectStoreAccount`, verifies store match, requires Ready status and non-empty account ID, and returns a short requeue result while the account is absent or not ready.
- `generateCephUserSecret`, `reconcileCephUserSecret`, `generateCephUserSecretName`, and `generateStatusInfo` maintain the user-facing Kubernetes Secret and `.status.info.secretName`.
- `getSecretValue`, `generateUserKeySpec`, `reconcileUserKeys`, and `updateKeyStatus` implement explicit key pairs and status backreferences to referenced Secrets.
- `validateUser`, `clusterStoreNamespace`, `deleteUser`, `generateUserCaps`, `userInNamespaceAllowed`, and `isUserSync` are local validation/utility helpers.

## Control Flow

The controller setup first registers a direct CR watch. It also watches generated `corev1.Secret` objects owned by a `CephObjectStoreUser`, so generated credential Secret changes can be restored. For explicit key references, the controller indexes all access-key and secret-key reference names into `spec.keys.secretNames`; a Secret change or deletion maps back to all users in the same namespace that reference that Secret, forcing immediate reconciliation failures when a referenced Secret disappears.

On reconcile, missing CRs are ignored. Existing CRs receive a finalizer. The cluster namespace is `spec.clusterNamespace` when set, otherwise the user namespace. If the cluster is not ready, the controller only removes the finalizer for deleting users after the cluster has disappeared; otherwise it returns the cluster readiness requeue result. Once cluster info loads, the object store context must initialize. If initialization fails while deleting, the finalizer is removed because there is no usable object-store context to clean up; if not deleting, the reconcile requeues on object-store readiness.

For non-deleted resources, `generateUserConfig` creates the target `admin.User`. If `spec.keys` is non-empty, `generateUserKeySpec` reads all referenced Secret values and assigns explicit target keys. Validation runs after config generation and checks name, namespace, store, and IAM-compatible display names for account users. Account references add `AccountID` to the RGW user only when the account CR exists, belongs to the same store, is Ready, and has an account ID.

The Ceph-side reconcile gets the live user by ID. A missing user is created. Existing users are modified only for supported scalar fields: display name, max buckets, and op-mask. Capabilities are diffed using a generated `type=perm;` string. Quotas are always set with defaults of disabled, `-1` max size, and `-1` max objects unless specified. Key reconciliation then makes the RGW key set match the target set exactly by deleting extra keys, deleting keys whose secret values changed, and creating missing keys.

After the RGW user has reconciled, `.status.keys` is updated from the referenced Kubernetes Secret UIDs, names, namespaces, and resource versions. The generated credential Secret is then created or updated with `AccessKey`, `SecretKey`, `Endpoint`, and optionally `SSLCertSecretName`, and an owner reference to the user CR. Final status is set to Ready with the observed generation.

Deletion uses the admin ops `RemoveUser` call. `admin.ErrNoSuchUser` is treated as success. Finalizer removal follows successful Ceph deletion. The generated Secret is not explicitly deleted here; Kubernetes owner-reference garbage collection is expected to clean it up.

## State and Persistence Behavior

Persistent Kubernetes state includes the `CephObjectStoreUser` finalizer, `.status.phase`, `.status.observedGeneration`, `.status.info.secretName`, `.status.keys`, and the generated `rook-ceph-object-user-<store>-<user>` Secret. Ceph persistent state includes RGW users, user capabilities, quotas, account association, op-mask, and S3 keys. Explicit key sources are external Kubernetes Secrets referenced by `spec.keys`; their UID/resourceVersion is copied into status after successful Ceph key reconciliation.

Ceph state is reconciled with a combination of admin ops API operations: `GetUser`, `CreateUser`, `ModifyUser`, `RemoveUserCap`, `AddUserCap`, `SetUserQuota`, `GetUser` for keys, `RemoveKey`, `CreateKey`, and `RemoveUser`. The generated Secret depends on `userConfig.Keys[0]`, so the Ceph key path must always leave at least one key in `userConfig.Keys`.

## Dependencies and Integration Points

The controller integrates with controller-runtime, Rook's `opcontroller` helpers, `object.InitializeObjectStoreContext`, go-ceph RGW admin ops, Rook status reporting, Kubernetes Secrets, Rook `CephCluster`, `CephObjectStore`, and optional `CephObjectStoreAccount` CRs. It depends on `opmask.FromSlice` to normalize the CR's `spec.opMask`. It uses `k8sutil` status constants and Secret type conventions, plus `controllerutil.SetControllerReference` for generated Secret ownership.

## Risks and Edge Cases

- `generateUserKeySpec` allocates `keys := make([]admin.UserKeySpec, len(user.Spec.Keys))` and then appends entries, leaving zero-value key specs before real key specs. That can produce unintended blank keys or API errors when explicit keys are used. The tests in this file do not directly cover `generateUserKeySpec`.
- `reconcileUserKeys` allocates `syncdKeys := make([]admin.UserKeySpec, len(targetKeys))` and appends matching keys, causing initial zero-value entries to be deleted from `targetMap`; this is mostly harmless but indicates the same length-vs-capacity pattern.
- `getObjectStore` lists all object stores and matches by name only, not namespace. In multi-namespace contexts this can select the wrong store if names collide.
- `generateCephUserSecret` always indexes `userConfig.Keys[0]`; a path that yields no keys will panic. The code defends against no live keys only when target keys are empty, but malformed explicit key paths remain risky.
- Capability comparison depends on stable caps ordering from the admin API. If Ceph returns caps in a different order than the desired string, unnecessary remove/add operations may occur.
- Account reference lookup is same namespace as the user even when `spec.clusterNamespace` points elsewhere; that appears intentional but is a contract to preserve.

## Test Signals

`controller_test.go` covers missing/unready cluster behavior, missing object store, missing RGW pods, successful user reconcile through a mocked admin ops client, cross-namespace user creation with `allowUsersInNamespaces`, status secret name generation, quota and capability updates, validation of IAM-compatible display names for account-linked users, account reference error/requeue/success cases, and scalar sync comparisons. The tests provide strong signals for readiness, account validation, quotas, caps, and basic Secret generation, but they do not directly verify explicit key-pair reconciliation, generated Secret owner reference behavior, Secret watch mapping, or deletion cleanup.
