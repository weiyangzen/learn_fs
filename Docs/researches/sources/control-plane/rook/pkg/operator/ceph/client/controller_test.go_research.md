# sources/control-plane/rook/pkg/operator/ceph/client/controller_test.go

Purpose: tests the CephClient controller's validation, auth entity generation, reconciliation behavior, secret status/ownership semantics, and CephX key rotation.

Important APIs/types/functions: `TestValidateClient()`, `TestGenerateClient()`, `TestCephClientController()`, `TestBuildUpdateStatusInfo()`, `TestRemoveSecretUpdateStatusInfo()`, `TestCustomSecretname()`, `TestReconcileCephClient_reconcileCephClientSecret()`, and `TestKeyRotation()` cover the main controller helpers and paths.

Control flow: tests use fake controller-runtime clients, fake Kubernetes clientsets, fake Rook clientsets, and mocked executors for Ceph commands. `TestCephClientController()` progresses from no cluster to not-ready cluster to ready cluster and verifies status/secret creation. Secret reconciliation table tests pre-create ownership variants and assert create/update/delete/error behavior. Key rotation subtests share state to model first reconcile, no-op reconcile, brownfield unknown status, requested rotations, and no extra rotation.

State and persistence behavior: fake Kubernetes state includes CephClient CRs, CephCluster CRs, mon secrets, and generated client secrets. `TestKeyRotation()` intentionally mutates the same CR and fake clients across subtests.

Dependencies and integration points: tests exercise integration between controller-runtime fake client, client-go fake clientset, Rook Ceph fake clientsets, `exectest.MockExecutor`, status reporting, and keyring rotation helpers.

Risks: shared subtest state in `TestKeyRotation()` means subtests are order-dependent and cannot run independently. Some tests use map-based caps and assert by string containment rather than exact command order, matching production nondeterminism. Fake clients may not enforce all Kubernetes API validation and owner-reference constraints.

Test signals: broad coverage of high-risk controller behavior, especially secret ownership and CephX rotation. Deletion finalizer path and reserved-name validation are less deeply exercised.
