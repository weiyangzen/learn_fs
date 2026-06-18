<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_update_test.go -->
# sources/cloud-native/moby/client/container_update_test.go

Purpose: validates `ContainerUpdate` error handling, route, and response decoding.

Important coverage: daemon internal errors, invalid ids, successful `POST /containers/container_id/update`, and returned warnings.

Control flow and dependencies: mock callbacks assert request and return JSON update responses.

State and risks: no persistence. The test protects resource update endpoint compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_update_test.go -->
