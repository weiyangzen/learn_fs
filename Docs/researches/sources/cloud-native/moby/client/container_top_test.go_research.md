<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_top_test.go -->
# sources/cloud-native/moby/client/container_top_test.go

Purpose: validates `ContainerTop` error and success behavior.

Important coverage: daemon internal errors, invalid ids, expected `GET /containers/container_id/top`, argument query handling, and response decoding.

Control flow and dependencies: uses mock JSON responses and request assertions.

State and risks: no persistence. The test protects the process-list endpoint’s query shape.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_top_test.go -->
