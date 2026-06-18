# sources/control-plane/rook/pkg/operator/ceph/object/account/controller_test.go

## Purpose
`controller_test.go` is the behavioral test suite for the `CephObjectStoreAccount` controller. It verifies readiness gates, account identity generation, ownership protections, crash-recovery bookmarking, deletion idempotency, status updates, root-user reconciliation, and Secret management using fake Kubernetes clients and mocked RGW Admin Ops HTTP responses.

## Important APIs, Types, and Functions
The file tests public reconcile entry points and package-private helpers: `Reconcile`, `reconcileAccount`, `deleteAccount`, `updateStatus`, `updateStatusWithAccountID`, `skipRootUserCreation`, `getRootUserID`, `getRootUserDisplayName`, `generateRootUserSecretName`, and `reconcileRootUser`. It uses `cephobject.MockClient` as the go-ceph HTTP client, fake controller-runtime clients, fake client-go clients, `events.NewFakeRecorder`, and a replaceable `newMultisiteAdminOpsCtxFunc`.

## Control Flow, State, and Persistence
The main controller test builds increasingly complete fake cluster state: an account CR, CephCluster readiness state, monitor Secret, CephObjectStore, and RGW pod. The success case replaces Admin Ops initialization with a mocked client that returns 404 for missing account/user, then returns account and root-user JSON for create calls. It verifies CR status becomes `Ready`, the deterministic account ID is recorded, and the root user Secret is created. Other tests isolate state transitions: pre-creation status bookmark writes, status-based ownership proof, deletion of user then account, skipped deletion when ownership proof is missing, and removal of root-user Secrets when `skipCreate` is enabled.

## Dependencies and Integration Points
The suite covers integration between the account controller, Rook cluster readiness helpers, object store context initialization, go-ceph Admin Ops request encoding, Kubernetes status subresources, fake Secrets, and root-user Secret owner-reference behavior. It depends on go-ceph translating mocked RGW error payloads into sentinel errors, preserving the same semantics production code uses.

## Risks
The tests are HTTP-mock based, so they validate controller decisions and go-ceph request paths but not a real RGW. Several tests mutate package-level state such as `newMultisiteAdminOpsCtxFunc` and the global log level; cleanup is present for the function override but this pattern can create ordering sensitivity if tests are parallelized. The success test reads `StringData` from fake Secrets, which is convenient but differs from how Kubernetes stores Secret `Data` after API-server processing. Error-path coverage is strong for account ownership, but weaker for malformed Admin Ops success responses.

## Test Signals
High-value signals include deterministic `RGW` account ID format and stability, spec/status account ID precedence, refusal to adopt foreign accounts, `AccountAlreadyExists` conflict messaging, crash recovery after a status bookmark, idempotent deletion for missing root users/accounts, skipped deletion for foreign spec IDs, observed-generation status writes, root-user display-name truncation for generated names, and Secret cleanup when root user creation is skipped.
