# sources/cloud-native/cri-o/server/inspect_ginkgo_test.go

Purpose: Ginkgo tests for the extended inspect HTTP mux, focused on route registration and HTTP status behavior.

Important APIs and functions: initializes `sut.GetExtendInterfaceMux(false)` with `httptest.ResponseRecorder`; exercises `/info`, `/containers/{id}`, `/pause/{id}`, and `/unpause/{id}` through real HTTP requests.

Control flow: each case prepares the shared test server, mock runtime/config, container/sandbox state, serves one request through the chi mux, and asserts the response status.

State and persistence: mutates in-memory sandbox and container stores, plus container state objects, but does not persist runtime data. It validates error handling when sandboxes are removed after containers are registered.

Dependencies and integration: integrates server test framework helpers, mocked runtime behavior, `net/http/httptest`, chi, Ginkgo/Gomega, and `oci.ContainerState`.

Risks: success for pause/unpause is not deeply asserted because mocked runtime update failures drive 500 cases; the tests primarily protect HTTP status mapping and route presence.

Test signals: confirms `/info` success, valid and invalid `/containers` outcomes, route-not-found behavior for missing IDs, pause state conflict behavior, and unpause state conflict/update-error behavior.
