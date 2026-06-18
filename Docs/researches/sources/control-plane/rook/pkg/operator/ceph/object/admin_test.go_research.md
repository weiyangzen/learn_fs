# sources/control-plane/rook/pkg/operator/ceph/object/admin_test.go

## Purpose
`admin_test.go` validates the object admin helpers that parse command output, choose local versus Multus execution, decide whether RGW period changes need committing, and derive Admin Ops endpoints.

## Important APIs, Types, and Functions
The suite tests `extractJSON`, `RunAdminCommandNoMultisite`, `CommitConfigChanges`, and `GetAdminOpsEndpoint`. It defines large real-world period JSON constants representing first reconcile, staged update, second reconcile without changes, and second reconcile with endpoint changes. A mock executor records `period get`, `period update`, and `period update --commit` calls.

## Control Flow, State, and Persistence
`TestExtractJson` feeds invalid strings, noisy object output, multiline objects, arrays, and arrays of objects through the extractor. `TestRunAdminCommandNoMultisite` verifies normal network mode uses the operator executor and Multus mode routes to the remote command executor. `TestCommitConfigChanges` parameterizes command outputs and failures to assert when period update and commit commands are issued. `TestGetAdminOpsEndpoint` mutates `CephObjectStore` specs to check internal service URLs, external endpoint URLs, TLS cert requirements, and advertise endpoint precedence.

## Dependencies and Integration Points
The tests use Rook's mock executor, fake Kubernetes clients, Ceph object store API types, cluster info helpers, and assertion libraries. They encode integration assumptions between `CephObjectStore.GetAdvertiseEndpointUrl()`, Admin Ops connection setup, and the multisite period commit workflow.

## Risks
The period JSON constants are intentionally large and realistic, but they still represent a finite set of RGW output shapes. The Multus test only asserts that the remote path fails with a "no pods found" error, not that command arguments and file-copy cleanup are correct. Endpoint tests cover TLS configuration rules but not CA loading or actual HTTP connection behavior.

## Test Signals
Strong signals include no commit when only ignored period fields change, commit when endpoints or config are added/removed, errors on invalid JSON and failed commands, HTTPS preference when secure port and cert are present, rejection of secure port without cert, and advertise endpoint override of internal/external defaults.
