# sources/control-plane/rook/pkg/operator/ceph/object/realm/controller_test.go

Purpose: tests `CephObjectRealm` reconciliation and key/realm helper behavior with fake clients and mocked executor responses.

Important APIs/tests: `TestCephObjectRealmController`, `TestPullCephRealm`, `TestCreateRealmKeys`, `TestCreateCephRealm`, `getObjectRealmAndReconcileObjectRealm`, and `TestReconcileObjectRealm_createRealmKeys`.

Control flow: the main controller test first reconciles without a ready CephCluster and expects requeues, then adds a ready cluster plus mon secret and mocked `realm get` output to verify successful reconciliation. Pull testing creates a `<realm>-keys` Secret and calls `pullCephRealm`. Key creation tests call `createRealmKeys` directly and validate idempotency across repeated reconciles. A negative subtest checks that an existing Secret missing `secret-key` fails with the expected guidance.

State and persistence: uses fake controller-runtime clients for CRs, fake CoreV1 clients for Secrets, a fake event recorder, and mocked command output for Ceph status and realm operations.

Dependencies and integration points: integrates Rook fake clientsets, Kubernetes scheme registration for Ceph types, `exectest.MockExecutor`, `cephclient.AdminTestClusterInfo`, and Rook test helpers.

Risks: real command-line error branches and default realm behavior are only lightly covered. The test uses package-global scheme registration and globals for realm names, which can couple tests if expanded carelessly.

Test signals: coverage is strongest for readiness gating and Secret idempotency. It documents that malformed existing Secrets fail rather than being overwritten.
