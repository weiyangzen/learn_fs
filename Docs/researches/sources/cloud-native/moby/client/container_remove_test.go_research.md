<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove_test.go -->
# sources/cloud-native/moby/client/container_remove_test.go

Purpose: tests `ContainerRemove` error classes and route/query construction.

Important coverage: internal errors, not-found mapping, invalid ids, successful `DELETE /containers/container_id`, and remove options in query values.

Control flow and dependencies: uses mock clients and request assertions.

State and risks: no persistence. The test protects a destructive endpoint and its compatibility query names.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove_test.go -->
