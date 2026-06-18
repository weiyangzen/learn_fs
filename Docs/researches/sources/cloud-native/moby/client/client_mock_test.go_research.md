<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_mock_test.go -->
# sources/cloud-native/moby/client/client_mock_test.go

Purpose: supplies test-only HTTP transport and assertion helpers used across endpoint tests. It centralizes request path/method checks, JSON response generation, ping mocking for version negotiation, and daemon-like default headers.

Important APIs/functions: `assertRequest`, `assertRequestWithQuery`, `ensureBody`, `makeTestRoundTripper`, `applyDefaultHeaders`, `WithMockClient`, `WithBaseMockClient`, `errorMock`, `mockJSONResponse`, `mockPingResponse`, and `mockResponse`.

Control flow: `WithMockClient` installs an `http.Client` whose transport automatically answers `/_ping`, letting regular endpoint tests exercise negotiation. Other requests are delegated to test callbacks and normalized with non-nil bodies/default daemon headers. `WithBaseMockClient` skips ping/default headers for tests that need precise lower-level behavior.

State and integration behavior: no persisted state. The helpers emulate enough daemon behavior for client-side logic, including version headers and JSON error bodies. They depend on `testRoundTripper` from `client_options.go`, API type packages, and standard `net/http`.

Risks and test signals: if the mock diverges from real daemon response headers, tests can miss production regressions. Conversely, these helpers make route, query, body, and error assertions consistent across the package.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_mock_test.go -->
