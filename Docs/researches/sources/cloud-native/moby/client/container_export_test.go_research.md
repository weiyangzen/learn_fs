<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_export_test.go -->
# sources/cloud-native/moby/client/container_export_test.go

Purpose: validates `ContainerExport` route, error classification, and returned stream content.

Important coverage: internal errors, invalid empty/whitespace ids, successful `GET /containers/container_id/export`, reading the returned `io.ReadCloser`, and closing it.

Control flow and dependencies: uses mock responses with body content and gotest assertions.

State and risks: no persistent state. The tests protect body ownership semantics for a streaming endpoint.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_export_test.go -->
