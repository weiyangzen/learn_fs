# sources/control-plane/rook/pkg/operator/ceph/object/user/controller_test.go

## Purpose

This file tests the `CephObjectStoreUser` controller and its helper functions. It uses fake Kubernetes clients, a fake Rook clientset, mock executors, and mocked RGW admin ops HTTP responses to verify readiness gating, successful RGW user creation/update, status info generation, validation, account reference resolution, and scalar user synchronization.

## Important Test Cases and Helpers

- `TestCephObjectStoreUserController` drives the controller's reconcile path through failure and success states.
- `TestBuildUpdateStatusInfo` verifies generated status info includes the expected credential Secret name.
- `TestCreateOrUpdateCephUser` exercises `createOrUpdateCephUser` and `generateUserConfig` for default users, max buckets, capabilities, user quotas, and combined quota/capability settings.
- `TestValidateUser` verifies standalone display names can contain spaces, while account-linked display names must match IAM-compatible characters.
- `TestResolveAccountRef` covers missing account, store mismatch, not-ready account, ready account, and ready account missing an account ID.
- `TestIsUserSync` verifies display name, max bucket, and op-mask comparisons.

## Control Flow and Test Setup

The main controller test starts with a `CephObjectStoreUser`, fake scheme registration, fake controller-runtime client, fake Rook clientset, and mock executor. It first verifies reconcile requeues without a cluster and with an unready cluster. It then provisions a monitor Secret and marks the cluster ready to test the missing object-store path. After adding a `CephObjectStore`, it tests the path where the RGW object exists but no RGW pod is running. The successful case creates an RGW pod and overrides `newMultisiteAdminOpsCtxFunc` to return a mocked admin ops client that accepts the expected user, quota, and caps HTTP calls.

The cross-namespace subtest sets `spec.clusterNamespace`, changes the user namespace, and toggles `allowUsersInNamespaces` to verify the controller allows or rejects users outside the object-store namespace. It also checks the behavior when no cluster exists in the user's own namespace.

`TestCreateOrUpdateCephUser` constructs a real go-ceph admin client backed by a mock HTTP transport and asserts the exact query strings produced for create/modify/quota/caps flows. The account and validation tests use fake CR clients and small in-memory CR instances rather than full reconcile.

## State and Persistence Signals

The tests observe `.status.phase`, generated `.status.info.secretName`, and account reference return values. They also verify generated bootstrap input data to the admin ops path indirectly through HTTP request query strings. The successful reconcile checks that the user CR reaches `Ready`. The cross-namespace case verifies the API-server state and the object-store allow-list are enough to accept users in another namespace.

## Dependencies and Integration Points

The tests rely on `github.com/ceph/go-ceph/rgw/admin`, fake controller-runtime clients, fake Rook/client-go clientsets, `exectest.MockExecutor`, `cephobject.MockClient`, Rook operator test helpers, Kubernetes `scheme.Scheme`, and fake event recorders. They also depend on HTTP query encoding produced by go-ceph, which makes the mocked admin ops cases sensitive to admin client behavior.

## Risks and Gaps

- `newMultisiteAdminOpsCtxFunc` is overridden globally and restored only implicitly by process lifetime, so additional tests in the same package could be order-sensitive if they rely on the default.
- Explicit `spec.keys` reconciliation is not covered, including Secret watch mapping, Secret deletion, `.status.keys`, and RGW key exact-match behavior.
- Deletion behavior is not tested in this file.
- Generated Secret contents and owner references are not asserted in the successful reconcile.
- The tests assert exact admin ops query strings, which catches regressions in desired parameters but can be brittle if go-ceph changes parameter ordering.

## Test Signals

The file gives strong confidence that common user reconcile paths reach the expected requeue or Ready results, that quota/capability admin ops calls are formed as expected, and that account-linked display-name constraints are enforced. It leaves key-management and deletion paths as notable untested surfaces.
