<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_test.go -->
# sources/cloud-native/moby/client/container_diff_test.go

Purpose: validates `ContainerDiff` error handling and success decoding.

Important coverage: internal server error mapping, invalid container ids through shared validation, expected `GET /containers/container_id/changes`, and JSON decoding of filesystem changes.

Control flow and dependencies: uses `WithMockClient`, `errorMock`, `mockJSONResponse`, and request assertions.

State and risks: no persistent state. The route/method assertion protects compatibility with the daemon changes endpoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_diff_test.go -->
