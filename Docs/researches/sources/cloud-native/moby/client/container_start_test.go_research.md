<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_start_test.go -->
# sources/cloud-native/moby/client/container_start_test.go

Purpose: tests `ContainerStart` error mapping and request route.

Important coverage: daemon internal errors, invalid empty/whitespace ids, and successful `POST /containers/container_id/start`.

Control flow and dependencies: uses mock client helper and request assertions.

State and risks: no persistence. The test protects lifecycle start endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_start_test.go -->
