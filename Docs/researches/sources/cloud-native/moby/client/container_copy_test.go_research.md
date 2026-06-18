<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy_test.go -->
# sources/cloud-native/moby/client/container_copy_test.go

Purpose: validates the three archive-related container operations: stat path, copy to container, and copy from container.

Important coverage: daemon errors, 404 not-found classification, invalid ids, missing path stat headers, expected `HEAD`/`PUT`/`GET /containers/container_id/archive`, path query normalization, default `noOverwriteDirNonDir=true`, request body transmission, response stream return, and close behavior.

Control flow and dependencies: tests use mock headers containing base64 JSON `container.PathStat`, inspect query/body data, and read returned `io.ReadCloser` content.

State and risks: no persistent test state. The suite is high-signal for stream ownership and Docker archive protocol compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_copy_test.go -->
