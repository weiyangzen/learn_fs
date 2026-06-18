<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause_test.go -->
# sources/cloud-native/moby/client/container_unpause_test.go

Purpose: tests `ContainerUnpause` error mapping and request route.

Important coverage: daemon internal errors, invalid empty/whitespace ids, and successful `POST /containers/container_id/unpause`.

Control flow and dependencies: mock client callback asserts method/path.

State and risks: no persistence. The test protects lifecycle endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause_test.go -->
