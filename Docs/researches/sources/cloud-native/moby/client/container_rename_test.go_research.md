<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename_test.go -->
# sources/cloud-native/moby/client/container_rename_test.go

Purpose: validates `ContainerRename` error handling and request construction.

Important coverage: internal errors, invalid empty/whitespace ids, expected `POST /containers/container_id/rename`, and name query parameter.

Control flow and dependencies: mock transport inspects URL query and method/path.

State and risks: no persistence. The test protects metadata mutation behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_rename_test.go -->
