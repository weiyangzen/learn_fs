<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect_test.go -->
# sources/cloud-native/moby/client/container_inspect_test.go

Purpose: tests `ContainerInspect` error classes and successful decoding.

Important coverage: daemon internal error, not-found classification, invalid empty/whitespace ids, expected `GET /containers/container_id/json`, optional size query behavior, and typed response fields.

Control flow and dependencies: uses mock clients, JSON responses, and gotest assertions.

State and risks: no persistence. The tests protect the common inspect endpoint used by callers before stream demultiplexing and lifecycle operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_inspect_test.go -->
