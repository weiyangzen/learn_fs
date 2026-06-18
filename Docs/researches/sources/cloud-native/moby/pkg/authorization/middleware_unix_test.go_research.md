<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_unix_test.go -->
# sources/cloud-native/moby/pkg/authorization/middleware_unix_test.go

Purpose: Unix-focused test for `Middleware.WrapHandler` behavior with authz plugins around a daemon handler. It exercises allow/deny responses, plugin getter stubs, wrapped handler execution, and error propagation. State is in-memory HTTP request/response and plugin chain state. Dependencies include context, httptest, and plugingetter interfaces. Risks covered include plugin denial blocking handler output and successful authorization allowing response flow. Test signal validates the middleware integration boundary rather than plugin transport.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_unix_test.go -->
