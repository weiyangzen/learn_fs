<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_test.go -->
# sources/cloud-native/moby/pkg/authorization/middleware_test.go

Purpose: basic unit tests for authorization middleware construction and response modifier creation. Tests verify plugin list behavior, plugin removal/set helpers, and wrapper types using fake plugins/plugin getters. State is in-memory middleware state and `httptest` response writers. Dependencies include `plugingetter`, gotest assertions, and HTTP testing. Risks covered are basic chain management; deeper request/response authorization behavior is covered in Unix-specific middleware/authz tests. Test signal is narrow but fast.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/middleware_test.go -->
