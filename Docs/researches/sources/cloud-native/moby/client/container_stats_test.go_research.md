<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats_test.go -->
# sources/cloud-native/moby/client/container_stats_test.go

Purpose: validates stats request behavior and returned stream handling.

Important coverage: internal errors, invalid ids, expected `GET /containers/container_id/stats`, `stream` and `one-shot` query values, and reading returned body content.

Control flow and dependencies: mock callbacks inspect query values and provide response bodies.

State and risks: no persistence. The test protects a streaming endpoint where caller close semantics are critical.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stats_test.go -->
