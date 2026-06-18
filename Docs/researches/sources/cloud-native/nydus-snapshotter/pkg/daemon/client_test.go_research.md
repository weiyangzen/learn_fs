# Research: sources/cloud-native/nydus-snapshotter/pkg/daemon/client_test.go

This test file validates the daemon HTTP client against an in-process HTTP server bound to a Unix socket. `prepareNydusServer` creates a temporary socket, attaches it to `httptest.NewUnstartedServer`, and returns a JSON `types.DaemonInfo` payload with a known build-time version and `RUNNING` state.

`TestNydusClient_CheckStatus` verifies that `NewNydusClient` can talk over the Unix socket, decode daemon info, map the state through `DaemonState()`, and preserve build metadata. `TestUpdateConfig` exercises `PUT /api/v1/config?id=...` for shared and dedicated daemon IDs, decodes the JSON request body, and checks that server-side error payloads are surfaced in the returned error.

The tests provide useful signals for transport construction, query parameter propagation, request body marshaling, success status handling, and error parsing. They do not cover socket wait logic, request timeout behavior, mount/umount/blob endpoints, metrics decoding, or failover APIs. The mocked server replies generically to all paths in the first helper, so path-specific behavior is mainly asserted in the config update test. Persistence is limited to temporary sockets and directories; no daemon process is spawned.
