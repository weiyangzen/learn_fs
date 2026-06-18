<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop_test.go -->
# sources/cloud-native/moby/client/container_stop_test.go

Purpose: tests `ContainerStop` error handling, connection failure classification, and request construction.

Important coverage: internal errors, invalid ids, connection failures through `IsErrConnectionFailed`, successful `POST /containers/container_id/stop`, and timeout/signal query values.

Control flow and dependencies: uses mock and failing transports plus gotest assertions.

State and risks: no persistence. The test protects shutdown behavior and shared network error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop_test.go -->
