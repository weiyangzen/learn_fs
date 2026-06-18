<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_list_test.go -->
# sources/cloud-native/moby/client/container_list_test.go

Purpose: tests `ContainerList` query generation and decoding.

Important coverage: internal errors, `GET /containers/json`, `all`, `size`, `limit`, filter query encoding, and JSON response decoding into container summaries.

Control flow and dependencies: table-driven mock transport cases inspect URL query values and return JSON arrays.

State and risks: no persistence. The suite protects Docker CLI-like listing behavior and the shared filter helper.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_list_test.go -->
