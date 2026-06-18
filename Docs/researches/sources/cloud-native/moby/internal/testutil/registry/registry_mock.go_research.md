<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/registry_mock.go -->
# sources/cloud-native/moby/internal/testutil/registry/registry_mock.go

Purpose: implements a lightweight mock registry HTTP server with path-based handler registration. Important APIs are `Mock.RegisterHandler`, `NewMock`, `URL`, and `Close`. Control flow creates an `httptest.Server`, routes requests by registered paths or simple regex/string matching, and tracks handlers behind a mutex. State is in-memory handler mappings and the server listener. Dependencies are standard HTTP testing utilities and regexp/string matching. Risks include simplistic routing compared with a real registry and concurrency expectations around handler mutation. Test signal is useful for client behavior that only needs controlled HTTP responses.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/registry/registry_mock.go -->
